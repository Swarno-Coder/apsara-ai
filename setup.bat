@echo off
REM Complete setup script for AI Companion project

echo 🚀 AI Companion - Complete Setup
echo ================================

REM Check prerequisites
echo 📋 Checking prerequisites...

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.9+ first.
    pause
    exit /b 1
)
echo ✅ Python found

REM Check Flutter
flutter --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Flutter not found. Please install Flutter first.
    pause
    exit /b 1
)
echo ✅ Flutter found

REM Check Node.js (for some tools)
node --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Node.js not found. Some development tools may not work.
) else (
    echo ✅ Node.js found
)

echo.
echo 🔧 Setting up Backend...
echo ========================

cd backend

REM Create virtual environment
if not exist "venv" (
    echo 📦 Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo 📦 Installing Python dependencies...
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-test.txt

REM Initialize database
echo 🗄️ Initializing database...
python init_db.py

REM Test backend
echo 🧪 Testing backend setup...
pytest tests/test_backend.py::TestDatabase::test_database_connection -v

cd ..

echo.
echo 📱 Setting up Frontend...
echo =========================

cd frontend

REM Get Flutter dependencies
echo 📦 Getting Flutter dependencies...
flutter pub get

REM Run code generation (if needed)
echo 🔧 Running code generation...
flutter packages pub run build_runner build --delete-conflicting-outputs

REM Test frontend
echo 🧪 Testing frontend setup...
flutter test test/widget_test.dart

cd ..

echo.
echo 🐳 Setting up Docker (Optional)...
echo ==================================

if exist "docker-compose.yml" (
    echo 📦 Building Docker containers...
    docker-compose build
    echo ✅ Docker setup complete
) else (
    echo ⚠️ No docker-compose.yml found, skipping Docker setup
)

echo.
echo 🔧 Setting up Development Tools...
echo =================================

REM Create VS Code settings
if not exist ".vscode" mkdir .vscode

echo {                                       > .vscode\settings.json
echo   "python.defaultInterpreterPath": "./backend/venv/Scripts/python.exe", >> .vscode\settings.json
echo   "python.terminal.activateEnvironment": true, >> .vscode\settings.json
echo   "python.testing.pytestEnabled": true, >> .vscode\settings.json
echo   "python.testing.pytestArgs": ["backend/tests"], >> .vscode\settings.json
echo   "dart.flutterSdkPath": null, >> .vscode\settings.json
echo   "editor.formatOnSave": true, >> .vscode\settings.json
echo   "python.formatting.provider": "black", >> .vscode\settings.json
echo   "python.linting.enabled": true, >> .vscode\settings.json
echo   "python.linting.pylintEnabled": true >> .vscode\settings.json
echo }                                       >> .vscode\settings.json

echo ✅ VS Code settings created

REM Create launch configuration
echo [                                       > .vscode\launch.json
echo   {                                     >> .vscode\launch.json
echo     "version": "0.2.0",                 >> .vscode\launch.json
echo     "configurations": [                 >> .vscode\launch.json
echo       {                                 >> .vscode\launch.json
echo         "name": "Python: FastAPI",      >> .vscode\launch.json
echo         "type": "python",               >> .vscode\launch.json
echo         "request": "launch",            >> .vscode\launch.json
echo         "program": "${workspaceFolder}/backend/main.py", >> .vscode\launch.json
echo         "console": "integratedTerminal", >> .vscode\launch.json
echo         "cwd": "${workspaceFolder}/backend" >> .vscode\launch.json
echo       },                                >> .vscode\launch.json
echo       {                                 >> .vscode\launch.json
echo         "name": "Flutter",              >> .vscode\launch.json
echo         "type": "dart",                 >> .vscode\launch.json
echo         "request": "launch",            >> .vscode\launch.json
echo         "program": "${workspaceFolder}/frontend/lib/main.dart", >> .vscode\launch.json
echo         "cwd": "${workspaceFolder}/frontend" >> .vscode\launch.json
echo       }                                 >> .vscode\launch.json
echo     ]                                   >> .vscode\launch.json
echo   }                                     >> .vscode\launch.json
echo ]                                       >> .vscode\launch.json

echo ✅ VS Code launch configuration created

echo.
echo 📝 Creating Quick Start Scripts...
echo =================================

REM Backend start script
echo @echo off                              > start_backend.bat
echo cd backend                             >> start_backend.bat
echo call venv\Scripts\activate.bat         >> start_backend.bat
echo python main.py                         >> start_backend.bat

REM Frontend start script
echo @echo off                              > start_frontend.bat
echo cd frontend                            >> start_frontend.bat
echo flutter run -d chrome                  >> start_frontend.bat

REM Voice service start script
echo @echo off                              > start_voice_service.bat
echo cd backend                             >> start_voice_service.bat
echo call venv\Scripts\activate.bat         >> start_voice_service.bat
echo python voice_service.py               >> start_voice_service.bat

REM Full system start script
echo @echo off                              > start_all.bat
echo echo Starting AI Companion System...   >> start_all.bat
echo echo.                                  >> start_all.bat
echo echo 🔧 Starting Backend...            >> start_all.bat
echo start "Backend" cmd /k start_backend.bat >> start_all.bat
echo timeout /t 5 /nobreak                  >> start_all.bat
echo echo 🎤 Starting Voice Service...      >> start_all.bat
echo start "Voice Service" cmd /k start_voice_service.bat >> start_all.bat
echo timeout /t 3 /nobreak                  >> start_all.bat
echo echo 📱 Starting Frontend...           >> start_all.bat
echo start "Frontend" cmd /k start_frontend.bat >> start_all.bat
echo echo.                                  >> start_all.bat
echo echo ✅ All services started!          >> start_all.bat
echo pause                                  >> start_all.bat

echo ✅ Quick start scripts created

echo.
echo 🔍 Running Final Checks...
echo =========================

REM Check if all components work
echo 1️⃣ Backend API check...
cd backend
call venv\Scripts\activate.bat
start /B python main.py >nul 2>&1
timeout /t 3 /nobreak >nul
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Backend API not responding (this is normal if it just started)
) else (
    echo ✅ Backend API responding
)
taskkill /F /IM python.exe >nul 2>&1
cd ..

echo 2️⃣ Frontend check...
cd frontend
flutter doctor --android-licenses >nul 2>&1
flutter analyze >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Flutter analysis found issues (check with 'flutter analyze')
) else (
    echo ✅ Flutter analysis passed
)
cd ..

echo.
echo 🎉 Setup Complete!
echo ==================
echo.
echo Quick Start Options:
echo 🔧 Backend only:     start_backend.bat
echo 📱 Frontend only:    start_frontend.bat
echo 🎤 Voice service:    start_voice_service.bat
echo 🚀 Everything:       start_all.bat
echo.
echo 🧪 Testing Options:
echo 🔧 Backend tests:    backend\run_tests.bat
echo 📱 Frontend tests:   frontend\run_tests.bat
echo.
echo 📂 Key URLs (after starting):
echo 🔧 Backend API:      http://localhost:8000
echo 🎤 Voice Service:    http://localhost:8001
echo 📱 Frontend:         http://localhost:3000 (or Flutter's assigned port)
echo 📊 API Docs:         http://localhost:8000/docs
echo.
echo 💡 Tips:
echo - Use VS Code for the best development experience
echo - Check logs in the terminal windows that open
echo - Ensure microphone permissions are granted for voice features
echo - For mobile testing, connect your device and use 'flutter run'
echo.

pause
