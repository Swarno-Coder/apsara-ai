# 🤖 AI Companion - Voice-Enabled Chat Application

A full-stack AI companion application with seamless voice communication, emotion analysis, and real-time chat capabilities.

## 🏗️ Architecture

### Backend (Python/FastAPI)
- **Main API Server** (`main.py`) - Core REST API endpoints
- **Voice Service** (`voice_service.py`) - Microservice for STT/TTS processing
- **WebSocket Service** - Real-time voice communication
- **Middleware Layer** - Request logging, rate limiting, security
- **Database Layer** - SQLite with async support
- **Service Layer** - Modular services (Agent, Cache, Emotion, etc.)

### Frontend (Flutter/Dart)
- **Cross-platform UI** - Web, iOS, Android support
- **WebSocket Client** - Real-time communication
- **Voice Recording** - Microphone integration
- **Audio Playback** - TTS audio streaming
- **State Management** - Riverpod for reactive state

### Key Features
- 🎤 **Voice Chat** - Seamless STT → LLM → TTS pipeline
- 😊 **Emotion Analysis** - Real-time emotion detection
- 🔄 **WebSocket Communication** - Low-latency voice streaming
- 📱 **Cross-Platform** - Web, mobile, desktop
- 🧪 **Comprehensive Testing** - Unit, integration, performance tests
- 🚀 **Microservices** - Scalable architecture
- 🛡️ **Security** - Rate limiting, validation, CORS

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Flutter 3.0+
- Node.js (optional, for dev tools)
- Git

### One-Command Setup
```bash
# Windows
setup.bat

# Linux/Mac (create similar script)
chmod +x setup.sh && ./setup.sh
```

### Manual Setup

#### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt

# Initialize database
python init_db.py

# Start main API server
python main.py

# Start voice service (separate terminal)
python voice_service.py
```

#### Frontend Setup
```bash
cd frontend

# Get dependencies
flutter pub get

# Run code generation
flutter packages pub run build_runner build

# Start web app
flutter run -d chrome

# Or for mobile development
flutter run
```

## 🎯 Usage

### Starting the Application
```bash
# Start all services
start_all.bat

# Or individually:
start_backend.bat      # API server (port 8000)
start_voice_service.bat # Voice processing (port 8001)
start_frontend.bat     # Flutter app
```

### API Endpoints

#### Main API (Port 8000)
```
GET  /health                    # Health check
GET  /agents                    # List available agents
GET  /agents/{id}               # Get specific agent
POST /calls/start               # Start a call
POST /calls/{id}/message        # Send message
PUT  /calls/{id}/end            # End call
GET  /history/{user_id}/agents  # Call history
WS   /ws/call/{call_id}         # WebSocket for voice
```

#### Voice Service (Port 8001)
```
POST /stt/transcribe            # Speech-to-text
POST /tts/synthesize            # Text-to-speech
POST /voice/process             # Full pipeline
GET  /stt/models                # Available STT models
GET  /tts/voices                # Available voices
```

### WebSocket Communication

Connect to voice chat:
```javascript
ws://localhost:8000/ws/call/{call_id}?user_id={user_id}
```

Message format:
```json
{
  "type": "audio|text|control",
  "content": "base64_audio_or_text",
  "user_id": "user123",
  "agent_id": "agent456",
  "call_id": "call789"
}
```

## 🧪 Testing

### Backend Tests
```bash
cd backend

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Specific test categories
pytest tests/test_backend.py::TestAPI -v
pytest tests/test_backend.py::TestWebSocket -v
pytest tests/test_backend.py::TestServices -v
```

### Frontend Tests
```bash
cd frontend

# Run Flutter tests
flutter test

# Run with coverage
flutter test --coverage

# Analyze code
flutter analyze
```

### Performance Testing
```bash
# Backend performance
pytest tests/test_backend.py::TestPerformance -v

# Frontend performance  
flutter test test/widget_test.dart
```

## 🏛️ Project Structure

```
companion/
├── backend/                    # Python backend
│   ├── main.py                # Main FastAPI app
│   ├── voice_service.py       # Voice processing microservice
│   ├── database/              # Database layer
│   │   └── database.py        # Async SQLite operations
│   ├── models/                # Pydantic models
│   │   └── schemas.py         # Data schemas
│   ├── services/              # Business logic
│   │   ├── websocket_service.py   # WebSocket management
│   │   ├── agent_service.py       # Agent operations
│   │   ├── emotion_service.py     # Emotion analysis
│   │   ├── cache_service.py       # Redis/memory cache
│   │   ├── stt_service.py         # Speech-to-text
│   │   ├── tts_service.py         # Text-to-speech
│   │   └── llm_service.py         # LLM integration
│   ├── middleware/            # Request middleware
│   │   └── request_middleware.py  # Logging, rate limiting
│   ├── tests/                 # Backend tests
│   │   └── test_backend.py    # Comprehensive test suite
│   ├── requirements.txt       # Python dependencies
│   └── requirements-test.txt  # Test dependencies
├── frontend/                  # Flutter frontend
│   ├── lib/
│   │   ├── main.dart         # App entry point
│   │   ├── core/             # Core functionality
│   │   │   ├── models/       # Data models
│   │   │   ├── services/     # API services
│   │   │   │   └── websocket_service.dart # WebSocket client
│   │   │   └── theme/        # App theming
│   │   └── features/         # Feature modules
│   │       ├── home/         # Home screen
│   │       ├── call/         # Voice call interface
│   │       ├── chat/         # Text chat
│   │       └── history/      # Call history
│   ├── test/                 # Flutter tests
│   │   └── widget_test.dart  # Widget tests
│   └── pubspec.yaml          # Flutter dependencies
├── setup.bat                 # Complete setup script
├── start_all.bat            # Start all services
└── README.md                # This file
```

## 🔧 Configuration

### Environment Variables
Create `.env` files in backend/:
```env
# Database
DATABASE_URL=sqlite:///companion.db

# API Keys
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_key

# Services
REDIS_URL=redis://localhost:6379
VOICE_SERVICE_URL=http://localhost:8001

# Security
JWT_SECRET_KEY=your_secret_key
CORS_ORIGINS=["http://localhost:3000"]
```

### Voice Models
- **STT**: Whisper (base, small, medium, large)
- **TTS**: Built-in voices + custom models
- **Languages**: English, Hindi, Bengali, Telugu, Tamil, etc.

## 🚀 Deployment

### Docker Deployment
```bash
# Build containers
docker-compose build

# Start services
docker-compose up -d

# Scale voice service
docker-compose up -d --scale voice-service=3
```

### Cloud Deployment
- **Backend**: Deploy to AWS Lambda, Google Cloud Run, or Azure Functions
- **Frontend**: Deploy to Vercel, Netlify, or host as PWA
- **Database**: Use PostgreSQL or MongoDB for production
- **Voice Service**: Scale with Kubernetes or container orchestration

## 🛡️ Security Features

- **Rate Limiting**: Prevent API abuse
- **CORS Protection**: Secure cross-origin requests
- **Input Validation**: Pydantic models for type safety
- **Error Handling**: Graceful error management
- **Request Logging**: Comprehensive audit trails
- **Authentication**: JWT token support (optional)

## 📊 Monitoring

### Health Checks
```bash
# Backend health
curl http://localhost:8000/health

# Voice service health
curl http://localhost:8001/health

# Metrics
curl http://localhost:8001/metrics
```

### Logging
- **Request/Response**: Middleware logging
- **WebSocket Events**: Connection lifecycle
- **Service Metrics**: Performance monitoring
- **Error Tracking**: Exception handling

## 🔄 Development Workflow

### Backend Development
```bash
# Start with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run tests on file changes
pytest-watch tests/

# Format code
black .
isort .
```

### Frontend Development
```bash
# Hot reload
flutter run

# Debug mode
flutter run --debug

# Build for production
flutter build web
flutter build apk
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Code Standards
- **Python**: Black formatting, type hints, docstrings
- **Dart**: Effective Dart guidelines, documentation
- **Testing**: Minimum 80% coverage
- **API**: OpenAPI documentation

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

#### Backend Not Starting
```bash
# Check Python version
python --version  # Should be 3.9+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check database
python init_db.py
```

#### Frontend Build Issues
```bash
# Clean and reinstall
flutter clean
flutter pub get

# Check Flutter doctor
flutter doctor
```

#### WebSocket Connection Fails
```bash
# Check backend is running
curl http://localhost:8000/health

# Check CORS settings
# Verify firewall/antivirus not blocking WebSocket
```

#### Voice Features Not Working
```bash
# Check microphone permissions
# Verify audio device availability
# Test voice service separately
curl -X POST http://localhost:8001/health
```

## 📞 Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Documentation**: `/docs` endpoint when running
- **API Reference**: `http://localhost:8000/docs`

## 🎯 Roadmap

- [ ] Multi-language support
- [ ] Advanced emotion AI
- [ ] Voice cloning
- [ ] Real-time translation
- [ ] Mobile app stores
- [ ] Advanced analytics
- [ ] Custom agent creation
- [ ] Video calling support

---

Made with ❤️ for seamless AI companionship
