import os
import sys
from pathlib import Path

# Get project root
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

def check_backend():
    """Check if backend is running"""
    import requests
    
    api_url = os.getenv("API_URL", "http://localhost:8000")
    
    try:
        response = requests.get(f"{api_url}/", timeout=2)
        if response.status_code == 200:
            return True
    except:
        return False
    
    return False

def main():
    print("🚂 TCDAFS Dashboard Startup")
    print("=" * 60)
    
    # Check if backend is running
    if not check_backend():
        print("\n⚠️  WARNING: Backend API not responding at http://localhost:8000")
        print("   Make sure the backend is running:")
        print("   → python run_server.py")
        print("\n   Continue anyway? (y/n): ", end="")
        
        response = input().lower()
        if response != 'y':
            print("❌ Dashboard startup cancelled")
            sys.exit(1)
    else:
        print("✅ Backend API is running")
    
    print("\n" + "=" * 60)
    print("🚀 Starting Dash Dashboard...")
    print("=" * 60)
    print("📡 Dashboard will be at: http://localhost:8050")
    print("Press CTRL+C to stop\n")
    
    try:
        from frontend.app_full import app
        app.run(debug=True, host="0.0.0.0", port=8050)
    except ImportError as e:
        print(f"\n❌ Failed to import dashboard: {e}")
        print("\n💡 Make sure you've installed frontend dependencies:")
        print("   pip install -r frontend/requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"\n❌ Dashboard startup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
