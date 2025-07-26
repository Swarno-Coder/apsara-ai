@echo off
REM AI Companion App - Quick Start Script for Windows

echo 🚀 Starting AI Companion App Setup...

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is required but not installed
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Check if Flutter is installed
flutter --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Flutter is required but not installed
    echo Please install Flutter from https://flutter.dev/docs/get-started/install
    pause
    exit /b 1
)

echo ✅ Requirements check passed

REM Create necessary directories
echo 📁 Creating necessary directories...
if not exist "data" mkdir data
if not exist "models\whisper" mkdir models\whisper
if not exist "models\piper" mkdir models\piper
if not exist "audio_cache" mkdir audio_cache
if not exist "logs" mkdir logs

REM Setup backend
echo 🐍 Setting up Python backend...
cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
pip install -r requirements.txt

REM Copy environment file
if not exist ".env" (
    copy .env.example .env
    echo 📝 Created .env file - please add your API keys
)

REM Initialize database
echo 🗄️ Initializing database...
python init_db.py

cd ..

REM Setup frontend
echo 📱 Setting up Flutter frontend...
cd frontend
flutter pub get
cd ..

echo ✅ Setup complete!
echo.
echo 📋 To start the application:
echo 1. Backend: cd backend ^&^& venv\Scripts\activate ^&^& uvicorn main:app --reload
echo 2. Frontend: cd frontend ^&^& flutter run
echo.
echo 💡 Make sure to add your GEMINI_API_KEY in backend\.env
echo.
echo Press any key to start the backend server...
pause

REM Start backend server
cd backend
call venv\Scripts\activate.bat
echo Starting backend server at http://localhost:8000
uvicorn main:app --reload --host 0.0.0.0 --port 8000
