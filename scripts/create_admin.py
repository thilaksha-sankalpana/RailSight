# scripts/create_admin.py - IMPROVED v2.1
"""
Create admin user for TCDAFS with password hashing.
Modes:
 - Default: insert profile row into `user_profiles` (will fail if FK to auth.users exists)
 - --use-supabase: create auth user via Supabase Admin API then insert profile with returned id
"""
import os
import sys
import uuid
import argparse
from pathlib import Path
from getpass import getpass
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# optional: requests for Supabase Admin API
try:
    import requests
except ImportError:
    requests = None

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment
load_dotenv(project_root / "backend" / ".env")

# Attempt to import your project's get_password_hash; otherwise use fallback
try:
    from backend.auth import get_password_hash
except Exception:
    # fallback using passlib
    try:
        from passlib.hash import bcrypt
        def get_password_hash(pw: str) -> str:
            return bcrypt.hash(pw)
    except Exception:
        def get_password_hash(pw: str) -> str:
            raise RuntimeError(
                "No get_password_hash available. Install passlib or provide backend.auth.get_password_hash"
            )

DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("DB_URL")
SUPABASE_URL = os.getenv("SUPABASE_URL")  # e.g. https://<ref>.supabase.co
SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # must be kept secret

if not DATABASE_URL:
    print("❌ DATABASE_URL not set in backend/.env")
    sys.exit(1)

def validate_email(email: str) -> bool:
    if not email.endswith("@railway.lk"):
        print("❌ Email must be from @railway.lk domain (example: admin@railway.lk)")
        return False
    return True

def create_supabase_user(email: str, password: str, full_name: str):
    """Create an auth user using Supabase Admin API. Returns user_id (UUID) on success."""
    if requests is None:
        raise RuntimeError("requests library is required to call Supabase Admin API. Install with `pip install requests`.")
    if not SUPABASE_URL or not SERVICE_ROLE_KEY:
        raise RuntimeError("SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not set in environment.")
    payload = {
        "email": email,
        "password": password,
        "email_confirm": True,
        "user_metadata": {"full_name": full_name},
        "app_metadata": {"provider": "email"}
    }
    url = f"{SUPABASE_URL.rstrip('/')}/auth/v1/admin/users"
    headers = {
        "apikey": SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
        "Content-Type": "application/json"
    }
    resp = requests.post(url, json=payload, headers=headers, timeout=15)
    if resp.status_code not in (200, 201):
        raise RuntimeError(f"Failed to create auth user: {resp.status_code} {resp.text}")
    data = resp.json()
    return data.get("id")

def insert_profile(conn, user_id, email, password_hash, full_name, contact_number):
    conn.execute(
        text("""
            INSERT INTO public.user_profiles
            (id, email, password_hash, full_name, contact_number, role, is_active, created_at, updated_at)
            VALUES (:id, :email, :password_hash, :full_name, :contact_number, :role, :is_active, NOW(), NOW())
        """),
        {
            "id": user_id,
            "email": email,
            "password_hash": password_hash,
            "full_name": full_name,
            "contact_number": contact_number,
            "role": "admin",
            "is_active": True
        }
    )

def create_admin(use_supabase: bool = False):
    print("🔐 TCDAFS Admin User Creation")
    print("=" * 60)
    email = input("Email (@railway.lk): ").strip()
    if not email:
        print("❌ Email cannot be empty")
        sys.exit(1)
    if not validate_email(email):
        sys.exit(1)
    full_name = input("Full Name: ").strip()
    if not full_name:
        print("❌ Full name cannot be empty")
        sys.exit(1)
    contact_number = input("Contact Number (optional): ").strip() or None
    password = getpass("Password: ")
    password_confirm = getpass("Confirm Password: ")
    if password != password_confirm:
        print("❌ Passwords do not match")
        sys.exit(1)
    if len(password) < 8:
        print("❌ Password must be at least 8 characters long")
        sys.exit(1)
    password_hash = get_password_hash(password)
    engine = create_engine(DATABASE_URL, echo=False)
    try:
        with engine.begin() as conn:
            # check existing email
            existing = conn.execute(
                text("SELECT id FROM public.user_profiles WHERE email = :email"),
                {"email": email}
            ).fetchone()
            if existing:
                print(f"❌ Email '{email}' already exists in user_profiles (id: {existing[0]})")
                return
            if use_supabase:
                print("→ Creating auth user in Supabase (Admin API)...")
                user_id = create_supabase_user(email, password, full_name)
                if not user_id:
                    raise RuntimeError("Supabase Admin API returned no user id.")
                print(f"→ Supabase auth user created with id: {user_id}")
            else:
                # generate uuid locally (WARNING: will fail if FK to auth.users exists)
                user_id = str(uuid.uuid4())
                print("→ Generated UUID for profile (note: this will fail if user_profiles.id FK to auth.users exists)")
            # insert profile
            insert_profile(conn, user_id, email, password_hash, full_name, contact_number)
        print("\n✅ Admin user created successfully!")
        print(f"User ID: {user_id}")
        print(f"Email: {email}")
        print(f"Full Name: {full_name}")
        print("Role: admin")
    except Exception as e:
        print(f"\n❌ Failed to create admin user: {e}")
        import traceback; traceback.print_exc()
        sys.exit(1)

def list_users():
    engine = create_engine(DATABASE_URL, echo=False)
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT id, email, full_name, role, is_active, 
                           CASE WHEN password_hash IS NOT NULL THEN 'Yes' ELSE 'No' END as has_password,
                           created_at 
                    FROM public.user_profiles 
                    ORDER BY created_at DESC
                """)
            )
            rows = result.fetchall()
            if not rows:
                print("No users found")
                return
            print("\n📋 Existing Users:")
            print("-" * 100)
            print(f"{'ID':<36} {'Email':<30} {'Full Name':<20} {'Role':<10} {'Active':<6} {'HasPwd':<7} {'Created'}")
            print("-" * 100)
            for r in rows:
                uid, email, full_name, role, is_active, has_password, created_at = r
                status = "✓" if is_active else "✗"
                created = created_at.strftime("%Y-%m-%d") if created_at else "N/A"
                print(f"{uid:<36} {email:<30} {full_name:<20} {role:<10} {status:<6} {has_password:<7} {created}")
            print("-" * 100)
    except Exception as e:
        print(f"❌ Failed to list users: {e}")
        import traceback; traceback.print_exc()

def reset_password():
    engine = create_engine(DATABASE_URL, echo=False)
    print("🔑 Password Reset")
    email = input("Email to reset: ").strip()
    if not email:
        print("❌ Email cannot be empty")
        return
    try:
        with engine.begin() as conn:
            row = conn.execute(text("SELECT id, full_name FROM public.user_profiles WHERE email = :email"), {"email": email}).fetchone()
            if not row:
                print(f"❌ User with email '{email}' not found")
                return
            user_id, full_name = row
            print(f"Resetting password for: {full_name} ({email})")
            new_password = getpass("New Password: ")
            confirm_password = getpass("Confirm Password: ")
            if new_password != confirm_password:
                print("❌ Passwords do not match")
                return
            if len(new_password) < 8:
                print("❌ Password must be at least 8 characters long")
                return
            password_hash = get_password_hash(new_password)
            conn.execute(
                text("UPDATE public.user_profiles SET password_hash = :password_hash, updated_at = NOW() WHERE id = :user_id"),
                {"password_hash": password_hash, "user_id": user_id}
            )
            print("✅ Password reset successfully")
    except Exception as e:
        print(f"❌ Failed to reset password: {e}")
        import traceback; traceback.print_exc()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TCDAFS User Management")
    parser.add_argument("--list", action="store_true", help="List all users")
    parser.add_argument("--reset", action="store_true", help="Reset user password")
    parser.add_argument("--use-supabase", action="store_true", help="Create auth user via Supabase Admin API first")
    args = parser.parse_args()

    if args.list:
        list_users()
    elif args.reset:
        reset_password()
    else:
        create_admin(use_supabase=args.use_supabase)
