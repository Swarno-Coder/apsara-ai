#!/bin/bash

# Backend testing script

echo "🧪 Starting AI Companion Backend Tests"
echo "======================================"

# Change to backend directory
cd backend || exit 1

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Activate virtual environment
source venv/Scripts/activate || source venv/bin/activate

# Install test dependencies
echo "📦 Installing test dependencies..."
pip install -r requirements-test.txt

# Run database initialization
echo "🗄️  Initializing test database..."
python init_db.py

# Run tests with coverage
echo "🏃 Running tests..."
echo ""

# Unit tests
echo "1️⃣  Running unit tests..."
pytest tests/test_backend.py::TestDatabase -v -m unit

echo ""
echo "2️⃣  Running service tests..."
pytest tests/test_backend.py::TestServices -v

echo ""
echo "3️⃣  Running API tests..."
pytest tests/test_backend.py::TestAPI -v

echo ""
echo "4️⃣  Running WebSocket tests..."
pytest tests/test_backend.py::TestWebSocket -v

echo ""
echo "5️⃣  Running integration tests..."
pytest tests/test_backend.py::TestIntegration -v -m integration

echo ""
echo "6️⃣  Running performance tests..."
pytest tests/test_backend.py::TestPerformance -v

echo ""
echo "📊 Generating coverage report..."
pytest tests/ --cov=. --cov-report=html --cov-report=term-missing

echo ""
echo "✅ Backend tests completed!"
echo "📄 Coverage report available in htmlcov/index.html"

# Keep terminal open on Windows
read -p "Press any key to continue..."
