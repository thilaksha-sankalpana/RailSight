r"""
Startup script for TCDAFS Backend Server
Place at: TCDAFS_Project/run_server.py (project root, NOT in Backend/)

Usage:
    .\.venv\Scripts\Activate
    python run_server.py
"""
import os
import sys
from pathlib import Path

# Get project root (where this script is)
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

def read_use_csv_from_env():
    """Read USE_CSV_FALLBACK setting from .env file"""
    env_path = project_root / "backend" / ".env"
    
    if not env_path.exists():
        return False  # Default to database mode if .env doesn't exist
    
    try:
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('USE_CSV_FALLBACK'):
                    # Extract value after =
                    value = line.split('=', 1)[1].strip()
                    return value.lower() in ('true', '1', 'yes')
    except Exception as e:
        print(f"⚠️  Could not read .env file: {e}")
        return False
    
    return False

def check_prerequisites():
    """Check if all required files and folders exist."""
    issues = []
    
    print(f"📂 Project root: {project_root}")
    
    # Read USE_CSV setting from .env
    USE_CSV = read_use_csv_from_env()
    
    print(f"🔧 Mode: {'CSV Fallback' if USE_CSV else 'PostgreSQL Database'}")
    print(f"📂 Checking structure...\n")
    
    # Check for backend folder (lowercase!)
    backend_dir = project_root / "backend"
    backend_upper = project_root / "Backend"
    
    if backend_upper.exists() and not backend_dir.exists():
        issues.append(
            "❌ Folder named 'Backend' found but should be 'backend' (lowercase)\n"
            "   Run: python fix_backend_name.py\n"
            "   Or manually rename 'Backend' to 'backend' in File Explorer"
        )
        return issues
    
    if not backend_dir.exists():
        issues.append("❌ backend folder not found!")
        return issues
    
    # Check for .env file first (important!)
    env_path = backend_dir / ".env"
    if not env_path.exists():
        env_txt = backend_dir / ".env.txt"
        if env_txt.exists():
            issues.append(
                f"⚠️  .env file not found. Copy .env.txt to .env:\n"
                f"   copy backend\\.env.txt backend\\.env"
            )
        else:
            issues.append("❌ Neither .env nor .env.txt found in backend/")
    else:
        print("✅ Found .env configuration file")
    
    # Check for model file (optional - warn but don't block)
    model_path = project_root / "model_artifacts" / "best_model.joblib"
    if not model_path.exists():
        issues.append(
            f"⚠️  Model file not found at {model_path}\n"
            "   You can train it later: python Model/train_model_with_refs.py\n"
            "   Server will start but forecasting won't work without the model"
        )
    else:
        print("✅ ML model found")
    
    # Check for Data folder ONLY if using CSV mode
    if USE_CSV:
        print("📊 CSV Mode enabled - checking for Data folder...")
        data_dir = project_root / "Data"
        if not data_dir.exists():
            data_dir = project_root / "data"
        
        if not data_dir.exists():
            issues.append("❌ Data folder not found! Should be 'Data' or 'data'")
        else:
            required_csvs = [
                "tickets.csv", "trains.csv", "routes.csv", 
                "train_models.csv", "compartments.csv", "holidays.csv"
            ]
            
            missing_csvs = []
            for csv_file in required_csvs:
                csv_path = data_dir / csv_file
                if not csv_path.exists():
                    missing_csvs.append(csv_file)
            
            if missing_csvs:
                issues.append(f"❌ Missing CSV files: {', '.join(missing_csvs)}")
            else:
                print("✅ All required CSV files found")
    else:
        print("✅ Using PostgreSQL database (CSV fallback disabled)")
        print("   Data folder not required")
    
    # Check backend/__init__.py
    init_file = backend_dir / "__init__.py"
    if not init_file.exists():
        print("⚠️  backend/__init__.py missing (creating it...)")
        try:
            init_file.touch()
            print("   ✅ Created backend/__init__.py")
        except Exception as e:
            issues.append(f"   ❌ Failed to create __init__.py: {e}")
    else:
        print("✅ backend/__init__.py exists")
    
    return issues

def main():
    print("🚂 TCDAFS Backend Server Startup")
    print("=" * 50)
    
    # Check prerequisites
    issues = check_prerequisites()
    
    if issues:
        print("\n⚠️  Issues detected:\n")
        for issue in issues:
            print(issue)
        
        # Only fail on critical errors (❌), not warnings (⚠️)
        critical_errors = [issue for issue in issues if "❌" in issue]
        
        if critical_errors:
            print("\n❌ Cannot start server. Fix the critical issues (❌) above first.")
            print("\nQuick fix commands:")
            print("1. Verify you're in project root: cd 'D:\\ADDS\\TCDAFS Project'")
            print("2. Create/check .env: notepad backend\\.env")
            print("3. If using CSV mode, ensure Data folder exists: mkdir Data")
            print("4. Train model (optional): python Model\\train_model_with_refs.py")
            sys.exit(1)
        else:
            print("\n⚠️  Warnings present, but attempting to start...")
    else:
        print("\n✅ All prerequisites met!")
    
    print("\n" + "=" * 50)
    print("🚀 Starting FastAPI server...")
    print("=" * 50)
    print("📡 Server will be at: http://localhost:8000")
    print("📖 API docs at: http://localhost:8000/docs")
    print("Press CTRL+C to stop\n")
    
    # Start uvicorn
    try:
        import uvicorn
        # Use lowercase 'backend' for module import regardless of folder name
        uvicorn.run(
            "backend.app:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except ImportError:
        print("\n❌ uvicorn not installed. Install dependencies:")
        print("   pip install -r backend/requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server startup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()