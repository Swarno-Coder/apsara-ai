@echo off
REM Backend testing script for Windows

echo 🧪 Starting AI Companion Backend Tests
echo ======================================

REM Change to backend directory
cd backend
if errorlevel 1 (
    echo ❌ Could not change to backend directory
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo ❌ Virtual environment not found. Please run setup first.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install test dependencies
echo 📦 Installing test dependencies...
pip install -r requirements-test.txt

REM Run database initialization
echo 🗄️ Initializing test database...
python init_db.py

REM Run tests with coverage
echo 🏃 Running tests...
echo.

REM Unit tests
echo 1️⃣ Running unit tests...
pytest tests/test_backend.py::TestDatabase -v

echo.
echo 2️⃣ Running service tests...
pytest tests/test_backend.py::TestServices -v

echo.
echo 3️⃣ Running API tests...
pytest tests/test_backend.py::TestAPI -v

echo.
echo 4️⃣ Running WebSocket tests...
pytest tests/test_backend.py::TestWebSocket -v

echo.
echo 5️⃣ Running integration tests...
pytest tests/test_backend.py::TestIntegration -v

echo.
echo 6️⃣ Running performance tests...
pytest tests/test_backend.py::TestPerformance -v

echo.
echo 📊 Generating coverage report...
pytest tests/ --cov=. --cov-report=html --cov-report=term-missing

echo.
echo ✅ Backend tests completed!
echo 📄 Coverage report available in htmlcov/index.html

pause
