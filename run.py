# run.py

import subprocess
import sys
import os
import webbrowser
import time
import threading

def check_requirements():
    """Check and install required packages"""
    required_packages = [
        'streamlit',
        'pandas',
        'numpy',
        'sqlalchemy',
        'bcrypt',
        'librosa',
        'sounddevice',
        'plotly'
    ]
    
    optional_packages = [
        'tensorflow'
    ]
    
    print("\nChecking installed packages...")
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))  # Handle packages with hyphens
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} not found")
            missing_packages.append(package)
    
    # Install missing required packages
    if missing_packages:
        print(f"\nInstalling {len(missing_packages)} missing packages...")
        for package in missing_packages:
            try:
                print(f"  Installing {package}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package], 
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"  ✓ {package} installed")
            except subprocess.CalledProcessError:
                print(f"  ✗ Failed to install {package}")
    
    print("\nChecking optional packages...")
    for package in optional_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✓ {package} (optional)")
        except ImportError:
            print(f"  ⚠ {package} not found (optional - using fallback)")
            print(f"    Note: ML features will use mock predictions")

def init_database():
    """Initialize database"""
    try:
        # Create database directory if not exists
        if not os.path.exists('database'):
            os.makedirs('database')
        
        from database.db_manager import DatabaseManager
        db = DatabaseManager()
        print("  ✓ Database initialized successfully")
        return True
    except Exception as e:
        print(f"  ✗ Database initialization failed: {e}")
        return False

def create_project_structure():
    """Create necessary directories"""
    directories = ['database', 'auth', 'models', 'utils', 'pages']
    for dir_name in directories:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"  ✓ Created directory: {dir_name}")

def open_browser():
    """Open browser after a short delay"""
    time.sleep(3)
    webbrowser.open('http://localhost:8501')

def main():
    """Run the application"""
    print("=" * 60)
    print("   SPEECH-DRIVEN EMOTION RECOGNITION SYSTEM")
    print("   Real-Time Satisfaction Performance Tracking")
    print("   for Call Centers")
    print("=" * 60)
    
    # Create project structure
    print("\n📁 Creating project structure...")
    create_project_structure()
    
    # Check requirements
    print("\n📦 Checking requirements...")
    check_requirements()
    
    # Initialize database
    print("\n🗄️ Initializing database...")
    if not init_database():
        print("\n⚠️ Warning: Could not initialize database. Using SQLite fallback.")
    
    print("\n" + "=" * 60)
    print("   ✅ SYSTEM READY")
    print("=" * 60)
    print("\n🌐 Starting Streamlit application...")
    print("📍 Access the application at: http://localhost:8501")
    print("\n🔐 Default admin credentials:")
    print("   Username: admin")
    print("   Password: Admin@123")
    print("\n💡 Tips:")
    print("   - First-time users need to register and wait for admin approval")
    print("   - Admin can approve users from the User Management page")
    print("   - Real-time analytics update every 30 seconds")
    print("\n⚠️ Press Ctrl+C to stop the application")
    print("=" * 60)
    
    # Open browser automatically
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Run Streamlit
    try:
        subprocess.run([
            "streamlit", "run", "app.py",
            "--server.port=8501",
            "--server.address=localhost",
            "--browser.gatherUsageStats=False"
        ])
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure all files are in the correct directories")
        print("2. Run: pip install --upgrade streamlit")
        print("3. Check if Python 3.11 is properly installed")

if __name__ == "__main__":
    main()