# AI Companion - Development Guide

## Project Structure

```
ai_companions/
├── backend/                 # Python FastAPI backend
│   ├── main.py             # API entry point
│   ├── init_db.py          # Database initialization
│   ├── requirements.txt    # Python dependencies
│   ├── database/           # Database models and connections
│   ├── services/           # Core business logic services
│   │   ├── llm_service.py      # Gemini LLM integration
│   │   ├── memory_service.py   # Faiss + vector embeddings
│   │   ├── emotion_service.py  # Emotion detection
│   │   ├── stt_service.py      # Whisper speech-to-text
│   │   ├── tts_service.py      # Piper text-to-speech
│   │   ├── call_service.py     # Call management
│   │   └── agent_service.py    # AI agent management
│   └── models/             # Data models and schemas
├── frontend/               # Flutter mobile app
│   ├── lib/
│   │   ├── main.dart       # App entry point
│   │   ├── core/           # Core utilities, themes, services
│   │   └── features/       # Feature-based modules
│   │       ├── home/       # Agent selection
│   │       ├── call/       # Call interface
│   │       └── history/    # Call history
│   └── pubspec.yaml        # Flutter dependencies
├── docker-compose.yml      # Container orchestration
├── start.sh               # Quick start script (Linux/Mac)
├── start.bat              # Quick start script (Windows)
└── README.md              # This file
```

## Quick Start

### Windows
```bash
.\start.bat
```

### Linux/Mac
```bash
chmod +x start.sh
./start.sh
```

### Manual Setup

1. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Add your GEMINI_API_KEY to .env
python init_db.py
uvicorn main:app --reload
```

2. **Frontend Setup**
```bash
cd frontend
flutter pub get
flutter run
```

## Configuration

### Environment Variables (backend/.env)
```env
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=sqlite:///companion.db
WHISPER_MODEL_PATH=./models/whisper/ggml-base.bin
PIPER_MODELS_DIR=./models/piper
TTS_OUTPUT_DIR=./audio_cache
```

### API Endpoints

- **GET /agents** - Get available AI agents
- **POST /calls/start** - Start a call with an agent
- **POST /calls/{call_id}/message** - Send text message
- **POST /calls/{call_id}/voice** - Send voice message
- **PUT /calls/{call_id}/end** - End call
- **GET /history/{user_id}/agents** - Get agent history
- **GET /health** - Health check

## Development Features

### Backend Services

1. **LLM Service** - Gemini API integration for conversational AI
2. **Memory Service** - Faiss vector database for conversation memory
3. **Emotion Service** - Keyword-based emotion detection
4. **STT Service** - Whisper.cpp speech-to-text
5. **TTS Service** - Piper text-to-speech
6. **Call Service** - Call session management
7. **Agent Service** - AI agent personality management

### Frontend Features

1. **Modern Call UI** - Phone-like calling interface
2. **Agent Selection** - Choose from different AI personalities
3. **Call History** - View past conversations by agent and date
4. **Voice/Text Chat** - Support for both voice and text messages
5. **Real-time Audio** - STT and TTS integration

## Architecture Highlights

### Modular Design
- Each service is independent and replaceable
- Clean separation between frontend and backend
- Docker containerization for easy deployment

### Scalability
- Stateless API design
- Vector database for efficient memory retrieval
- Background task processing for audio

### Emotional Intelligence
- Emotion detection from user messages
- Empathetic response generation
- Compatibility scoring between users and agents

### Multi-language Support
- English, Hindi, Bengali, and regional Indian languages
- Language-specific TTS models
- Multilingual emotion detection

## AI Agents

### Default Agents
1. **Aria** - Caring & empathetic companion
2. **Maya** - Playful & energetic companion  
3. **Priya** - Romantic & gentle companion
4. **Shreya** - Wise & supportive companion

### Personality System
- Each agent has unique personality traits
- Customizable system prompts
- Compatibility scoring with users
- Conversation history per agent

## Docker Deployment

```bash
# Start all services
docker-compose up --build

# Start in background
docker-compose up -d

# Stop services
docker-compose down
```

## Troubleshooting

### Common Issues

1. **Backend won't start**
   - Check Python version (3.11+ required)
   - Verify all dependencies installed
   - Check .env file configuration

2. **Flutter build errors**
   - Run `flutter doctor` to check setup
   - Run `flutter clean && flutter pub get`
   - Check device/emulator connection

3. **Models not working**
   - Run `python download_models.py` in backend
   - Check model file paths in .env
   - Verify model file downloads completed

4. **Audio not working**
   - Check microphone permissions
   - Verify audio file formats supported
   - Check TTS model availability

## API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Production Deployment

### Docker Compose Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes
```bash
kubectl apply -f k8s/
```

### Manual Production Setup
1. Set up reverse proxy (Nginx)
2. Configure SSL certificates
3. Set production environment variables
4. Set up monitoring and logging
5. Configure auto-scaling

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes following code style
4. Add tests if applicable
5. Submit pull request

## License

This project is for educational and personal use. Please respect API usage limits and terms of service for external services used.
