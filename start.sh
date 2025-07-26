#!/bin/bash

# AI Companion App - Quick Start Script

echo "🚀 Starting AI Companion App Setup..."

# Check if required tools are installed
check_requirements() {
    echo "📋 Checking requirements..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 is required but not installed"
        exit 1
    fi
    
    # Check Flutter
    if ! command -v flutter &> /dev/null; then
        echo "❌ Flutter is required but not installed"
        echo "Please install Flutter from https://flutter.dev/docs/get-started/install"
        exit 1
    fi
    
    # Check Docker (optional)
    if ! command -v docker &> /dev/null; then
        echo "⚠️  Docker not found - Docker deployment won't be available"
    fi
    
    echo "✅ Requirements check passed"
}

# Setup backend
setup_backend() {
    echo "🐍 Setting up Python backend..."
    
    cd backend
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    pip install -r requirements.txt
    
    # Copy environment file
    if [ ! -f ".env" ]; then
        cp .env.example .env
        echo "📝 Created .env file - please add your API keys"
    fi
    
    # Initialize database
    echo "🗄️  Initializing database..."
    python init_db.py
    
    cd ..
    echo "✅ Backend setup complete"
}

# Setup frontend
setup_frontend() {
    echo "📱 Setting up Flutter frontend..."
    
    cd frontend
    
    # Get Flutter dependencies
    flutter pub get
    
    # Check Flutter setup
    flutter doctor
    
    cd ..
    echo "✅ Frontend setup complete"
}

# Create necessary directories
create_directories() {
    echo "📁 Creating necessary directories..."
    
    mkdir -p data
    mkdir -p models/whisper
    mkdir -p models/piper
    mkdir -p audio_cache
    mkdir -p logs
    
    echo "✅ Directories created"
}

# Download models (optional)
download_models() {
    echo "📥 Do you want to download AI models? (This may take a while) [y/N]"
    read -r response
    
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo "⬇️  Downloading models..."
        cd backend
        python download_models.py
        cd ..
        echo "✅ Models downloaded"
    else
        echo "⚠️  Models not downloaded - some features may not work offline"
    fi
}

# Start development servers
start_dev_servers() {
    echo "🚀 Starting development servers..."
    
    # Start backend in background
    echo "Starting backend server..."
    cd backend
    source venv/bin/activate
    uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    cd ..
    
    # Wait a moment for backend to start
    sleep 3
    
    # Check if backend is running
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ Backend server started successfully"
    else
        echo "❌ Backend server failed to start"
        kill $BACKEND_PID 2>/dev/null
        exit 1
    fi
    
    echo "🎯 Setup complete!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Backend is running at: http://localhost:8000"
    echo "2. To start the Flutter app:"
    echo "   cd frontend"
    echo "   flutter run"
    echo ""
    echo "3. To view API documentation: http://localhost:8000/docs"
    echo ""
    echo "4. To stop the backend server:"
    echo "   kill $BACKEND_PID"
    echo ""
    echo "💡 Make sure to add your GEMINI_API_KEY in backend/.env"
    
    # Keep script running
    echo "Press Ctrl+C to stop the backend server"
    wait $BACKEND_PID
}

# Main execution
main() {
    check_requirements
    create_directories
    setup_backend
    setup_frontend
    download_models
    start_dev_servers
}

# Run main function
main
