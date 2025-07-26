#!/usr/bin/env python3
"""
Startup script for the Emotional AI Assistant Backend
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        sys.exit(1)
    print(f"✓ Python {sys.version.split()[0]} detected")

def check_models_directory():
    """Check if models directory exists and warn about missing models"""
    models_dir = Path("models")
    if not models_dir.exists():
        print("⚠ Models directory not found - creating it")
        models_dir.mkdir(exist_ok=True)
    
    # Check for key model files
    whisper_dir = models_dir / "whisper.cpp"
    if not whisper_dir.exists():
        print("⚠ Whisper.cpp not found in models/whisper.cpp/")
    
    piper_dir = models_dir / "piper_voices"
    if not piper_dir.exists():
        print("⚠ Piper voices not found in models/piper_voices/")
    
    firebase_creds = models_dir / "firebase-credentials.json"
    if not firebase_creds.exists():
        print("⚠ Firebase credentials not found in models/firebase-credentials.json")

def check_environment():
    """Check environment variables"""
    required_env = ["OPENROUTER_API_KEY"]
    missing_env = []
    
    for env_var in required_env:
        if not os.getenv(env_var):
            missing_env.append(env_var)
    
    if missing_env:
        print(f"⚠ Missing environment variables: {', '.join(missing_env)}")
        print("Create a .env file or set these variables")
        return False
    
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting Emotional AI Assistant Backend...")
    try:
        subprocess.run([sys.executable, "main.py"])
    except KeyboardInterrupt:
        print("\n👋 Shutting down server...")
    except Exception as e:
        print(f"❌ Server error: {e}")

def main():
    """Main startup function"""
    print("🤖 Emotional AI Assistant Backend Setup")
    print("=" * 40)
    
    # Check Python version
    check_python_version()
    
    # Check models
    check_models_directory()
    
    # Check environment
    env_ok = check_environment()
    
    # Install dependencies
    deps_ok = install_dependencies()
    
    if not deps_ok:
        print("\n❌ Setup failed - cannot continue")
        sys.exit(1)
    
    if not env_ok:
        print("\n⚠ Environment warnings - server may not work properly")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    print("\n✓ Setup complete!")
    print("\nServer will be available at:")
    print("  HTTP: http://localhost:8000")
    print("  WebSocket: ws://localhost:8000/ws")
    print("  Docs: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop the server")
    print("-" * 40)
    
    # Start server
    start_server()

if __name__ == "__main__":
    main()
