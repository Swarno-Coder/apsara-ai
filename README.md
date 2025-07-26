# AI Companion App

A modular AI girlfriend companion application designed for emotional support and companionship.

## Features

- **Single Calling Interface**: Call-like UI for interacting with AI agents
- **Multiple AI Agents**: Different personalities with separate conversation histories
- **Real-time Voice**: Speech-to-text and text-to-speech capabilities
- **Emotion Detection**: Empathetic responses based on user emotion analysis
- **Multi-language Support**: English, Hindi, Bengali, and regional Indian languages
- **Cross-platform**: Flutter app for Android, iOS, Web, and Desktop
- **Scalable Backend**: Python microservices with Docker/Kubernetes deployment

## Architecture

### Backend Services (Python FastAPI)
- **API Gateway**: Main orchestrator for all services
- **Agent Service**: Manages AI agents and their personalities
- **Call Service**: Handles voice/text conversations
- **Memory Service**: Vector embeddings and conversation history
- **Emotion Service**: Emotion detection and analysis
- **STT Service**: Speech-to-text using Whisper.cpp
- **TTS Service**: Text-to-speech using Piper TTS

### Frontend (Flutter)
- **Call Interface**: Modern calling UI with agent selection
- **History View**: Left sidebar with agent list and call histories
- **Voice Controls**: Recording, playback, and call management

### Data Storage
- **SQLite**: User data, agent profiles, call sessions
- **Faiss**: Vector database for semantic search
- **File Storage**: Audio recordings and TTS cache

## Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
flutter pub get
flutter run
```

### Docker
```bash
docker-compose up --build
```

## Configuration

1. Set up environment variables:
   - `GEMINI_API_KEY`: Google Gemini API key
   - `DATABASE_URL`: SQLite database path
   - `WHISPER_MODEL_PATH`: Path to Whisper model
   - `PIPER_MODEL_PATH`: Path to Piper TTS model

2. Initialize database:
   ```bash
   python backend/init_db.py
   ```

## Usage

1. Launch the app
2. Select an AI agent from the list
3. Tap the call button to start a conversation
4. Use voice or text to communicate
5. View call history in the sidebar

## Development

- Each service is modular and can be updated independently
- Use the provided Docker setup for consistent development environment
- Follow the coding guidelines in `.github/copilot-instructions.md`

## Deployment

The app is designed for scalable deployment using Docker and Kubernetes. See the `deployment/` directory for configuration files.
