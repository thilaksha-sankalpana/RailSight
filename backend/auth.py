# backend/auth.py
"""
Authentication module with secure password verification
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel
import os
import logging

logger = logging.getLogger(__name__)

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    logger.warning("⚠️ SECRET_KEY not set! Using insecure default. Set SECRET_KEY in production!")
    SECRET_KEY = "your-secret-key-change-this-in-production"

ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ============= PYDANTIC SCHEMAS =============
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

# ============= PASSWORD UTILITIES =============
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash using bcrypt
    
    Args:
        plain_password: Plain text password from user
        hashed_password: Bcrypt hash from database
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False

def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt
    
    Args:
        password: Plain text password
        
    Returns:
        Bcrypt hash string
    """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

# ============= JWT TOKEN UTILITIES =============
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token
    
    Args:
        data: Payload data (must include 'sub' for subject/email)
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "iat": now})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> TokenData:
    """
    Decode and verify JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        TokenData object with email and role
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        
        if email is None:
            raise credentials_exception
        
        token_data = TokenData(email=email, role=payload.get("role"))
        return token_data
        
    except JWTError as e:
        logger.error(f"JWT decode error: {e}")
        raise credentials_exception

# ============= USER AUTHENTICATION =============
def authenticate_user(email: str, password: str, db: Session):
    """
    ✅ FIXED: Authenticate user with email and password
    
    Args:
        email: User email address
        password: Plain text password
        db: Database session
        
    Returns:
        UserProfile object if authenticated, False otherwise
    """
    from backend.models import UserProfile
    
    logger.info(f"🔍 Login attempt: {email}")
    
    # Query user by email - explicitly load all columns
    user = db.query(UserProfile).filter(UserProfile.email == email).first()
    
    # Dummy hash for timing attack prevention
    dummy_hash = "$2b$12$dummyhashtopreventtimingattackvulnerability"
    
    # Check if user exists
    if not user:
        logger.warning(f"❌ User not found: {email}")
        # Verify against dummy hash to maintain consistent timing
        verify_password(password, dummy_hash)
        return False
    
    # Check if user is active
    if not user.is_active:
        logger.warning(f"❌ User inactive: {email}")
        verify_password(password, dummy_hash)
        return False
    
    # Check if password hash exists using getattr for safety
    password_hash = getattr(user, 'password_hash', None)
    if not password_hash:
        logger.error(f"❌ User {email} has no password hash (id: {user.id})")
        verify_password(password, dummy_hash)
        return False
    
    # Verify password
    if not verify_password(password, password_hash):
        logger.warning(f"❌ Invalid password for: {email}")
        return False
    
    logger.info(f"✅ Login successful: {email} (Role: {user.role})")
    return user

# ============= DEPENDENCY FUNCTIONS =============
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Get current user from JWT token
    
    Args:
        token: JWT token from Authorization header
        
    Returns:
        UserProfile object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    from backend.db import SessionLocal
    from backend.models import UserProfile
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decode token
    token_data = decode_access_token(token)
    
    # Get user from database
    db = SessionLocal()
    try:
        user = db.query(UserProfile).filter(
            UserProfile.email == token_data.email
        ).first()
        
        if user is None:
            raise credentials_exception
        
        return user
    finally:
        db.close()

async def get_current_active_user(current_user = Depends(get_current_user)):
    """
    Ensure user is active
    
    Args:
        current_user: User from get_current_user dependency
        
    Returns:
        Active UserProfile object
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    return current_user

# ============= ROLE-BASED ACCESS CONTROL =============
def require_admin(current_user = Depends(get_current_active_user)):
    """
    Require admin role
    
    Args:
        current_user: Active user from get_current_active_user
        
    Returns:
        UserProfile with admin role
        
    Raises:
        HTTPException: If user is not admin
    """
    from backend.models import UserRole
    
    user_role = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
    
    if user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

def require_role(*allowed_roles: str):
    """
    Flexible role checker - allows multiple roles
    
    Usage:
        @app.get("/endpoint", dependencies=[Depends(require_role("admin", "manager"))])
    
    Args:
        allowed_roles: Variable number of role strings
        
    Returns:
        Dependency function
    """
    def role_checker(current_user = Depends(get_current_active_user)):
        user_role = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
        
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
            )
        return current_user
    
    return role_checker

# ============= EMAIL VALIDATION =============
def validate_railway_email(email: str) -> bool:
    """
    Validate that email is from railway.lk domain
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email ends with @railway.lk, False otherwise
    """
    if not email:
        return False
    return email.lower().endswith("@railway.lk")

def ensure_railway_email(email: str):
    """
    Ensure email is from railway.lk domain
    
    Args:
        email: Email address to validate
        
    Raises:
        HTTPException: If email is not from railway.lk domain
    """
    if not validate_railway_email(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email must be from @railway.lk domain"
        )

# ============= USER CREATION HELPER =============
def create_user(
    email: str,
    password: str,
    full_name: str,
    role: str = "operator",
    contact_number: Optional[str] = None,
    db: Optional[Session] = None
):
    """
    Helper function to create new user with hashed password
    
    Args:
        email: User email (must be @railway.lk)
        password: Plain text password
        full_name: Full name
        role: User role (default: operator)
        contact_number: Optional phone number
        db: Database session
        
    Returns:
        Created UserProfile object
        
    Raises:
        HTTPException: If validation fails
    """
    from backend.models import UserProfile, UserRole
    import uuid
    
    if db is None:
        raise ValueError("Database session is required")
    
    # Validate email domain
    ensure_railway_email(email)
    
    # Check if user already exists
    existing = db.query(UserProfile).filter(UserProfile.email == email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    password_hash = get_password_hash(password)
    
    # Create user
    new_user = UserProfile(
        id=uuid.uuid4(),
        email=email,
        password_hash=password_hash,
        full_name=full_name,
        contact_number=contact_number,
        role=UserRole[role],
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"✅ User created: {email} ({role})")
    return new_user