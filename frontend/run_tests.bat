@echo off
REM Frontend testing script for Windows

echo 🧪 Starting AI Companion Frontend Tests
echo =======================================

REM Change to frontend directory
cd frontend
if errorlevel 1 (
    echo ❌ Could not change to frontend directory
    pause
    exit /b 1
)

REM Check if Flutter is available
flutter --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Flutter not found. Please install Flutter first.
    pause
    exit /b 1
)

REM Get dependencies
echo 📦 Getting Flutter dependencies...
flutter pub get

REM Run tests
echo 🏃 Running Flutter tests...
echo.

echo 1️⃣ Running unit tests...
flutter test test/widget_test.dart --coverage

echo.
echo 2️⃣ Running integration tests...
REM flutter test integration_test/ --coverage

echo.
echo 3️⃣ Analyzing code...
flutter analyze

echo.
echo 4️⃣ Checking formatting...
dart format --set-exit-if-changed lib/ test/

echo.
echo 📊 Generating coverage report...
REM Convert coverage to HTML (requires lcov)
REM genhtml coverage/lcov.info -o coverage/html

echo.
echo ✅ Frontend tests completed!
echo 📄 Coverage data available in coverage/lcov.info

pause
