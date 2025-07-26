# Emotional AI Assistant Backend

A modular FastAPI backend for an emotional voice assistant with real-time audio streaming.

## Features

- **Real-time Audio Processing**: WebSocket-based audio streaming and processing
- **Speech-to-Text**: Using Whisper.cpp for accurate transcription
- **Emotion Detection**: Text and audio-based emotion classification
- **LLM Integration**: OpenRouter API for intelligent responses
- **Text-to-Speech**: Piper TTS with emotional voice synthesis
- **Memory Management**: FAISS vector database with Firebase backup
- **Agent Personalities**: Multiple AI agent types with distinct personalities
- **User Authentication**: Firebase Auth integration

## Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── websocket_handler.py    # WebSocket connection management
├── stt_whispercpp.py      # Speech-to-text using Whisper.cpp
├── emotion_classifier.py   # Emotion detection from text/audio
├── llm_openrouter.py      # OpenRouter API client
├── tts_piper.py           # Piper TTS integration
├── firebase_interface.py  # Firebase authentication and storage
├── faiss_memory.py        # FAISS vector memory management
├── agent_manager.py       # AI agent personality management
├── audio_utils.py         # Audio processing utilities
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
└── models/                # Model files directory
    ├── whisper.cpp/       # Whisper models
    ├── piper_voices/      # Piper TTS voices
    ├── emotion_model.onnx # Emotion classification model
    └── faiss_index/       # FAISS index files
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file:

```env
OPENROUTER_API_KEY=your_openrouter_api_key
FIREBASE_PROJECT_ID=your_firebase_project_id
FIREBASE_CREDENTIALS_PATH=models/firebase-credentials.json
```

### 3. Model Setup

Download and place the following models in the `models/` directory:

- **Whisper.cpp**: Download from [whisper.cpp releases](https://github.com/ggerganov/whisper.cpp)
- **Piper Voices**: Download from [Piper TTS](https://github.com/rhasspy/piper)
- **Emotion Model**: ONNX emotion classification model (optional)

### 4. Firebase Setup

1. Create a Firebase project
2. Enable Authentication and Firestore
3. Download service account credentials to `models/firebase-credentials.json`

## Running the Server

```bash
python main.py
```

The server will start on `http://localhost:8000`

## API Endpoints

### WebSocket
- `ws://localhost:8000/ws` - Main WebSocket endpoint for real-time communication

### REST API
- `GET /` - Root endpoint with API information
- `GET /health` - Health check
- `GET /agents` - List available AI agents
- `GET /agents/{agent_id}` - Get specific agent details
- `GET /user/profile?user_id={user_id}` - Get user profile
- `POST /user/profile?user_id={user_id}` - Update user profile
- `GET /user/history?user_id={user_id}&limit={limit}` - Get chat history
- `GET /user/memory-stats?user_id={user_id}` - Get memory statistics
- `DELETE /user/memories?user_id={user_id}` - Clear user memories

## WebSocket Message Types

### Client → Server

**Authentication:**
```json
{
  "type": "auth",
  "token": "firebase_id_token"
}
```

**Audio Chunk:**
```json
{
  "type": "audio_chunk",
  "audio_data": "base64_encoded_audio",
  "is_final": false
}
```

**Text Message:**
```json
{
  "type": "text_message",
  "text": "Hello, how are you?"
}
```

**Set Agent:**
```json
{
  "type": "set_agent",
  "agent_id": "friendly_assistant"
}
```

**Get Agents:**
```json
{
  "type": "get_agents"
}
```

**Get History:**
```json
{
  "type": "get_history",
  "limit": 10
}
```

### Server → Client

**Authentication Success:**
```json
{
  "type": "auth_success",
  "user": {
    "uid": "user_id",
    "email": "user@example.com",
    "name": "User Name"
  }
}
```

**Status Updates:**
```json
{
  "type": "status",
  "message": "Processing audio..."
}
```

**Transcription:**
```json
{
  "type": "transcription",
  "text": "Hello, how are you?"
}
```

**Emotion Detection:**
```json
{
  "type": "emotion",
  "emotion": "happy",
  "confidence": 0.8
}
```

**LLM Response:**
```json
{
  "type": "llm_response",
  "text": "I'm doing great! How can I help you today?"
}
```

**TTS Audio:**
```json
{
  "type": "tts_audio",
  "audio_data": "base64_encoded_wav_audio"
}
```

**Agents List:**
```json
{
  "type": "agents_list",
  "agents": [
    {
      "id": "friendly_assistant",
      "name": "Friendly Assistant",
      "personality": "friendly and empathetic"
    }
  ]
}
```

**Error:**
```json
{
  "type": "error",
  "message": "Error description"
}
```

## Agent Personalities

The system includes several built-in agent personalities:

1. **Friendly Assistant** - Warm, empathetic, and supportive
2. **Professional Advisor** - Direct, knowledgeable, and efficient
3. **Creative Companion** - Imaginative, inspiring, and artistic
4. **Mindful Guide** - Calm, wise, and focused on mental wellness

## Audio Processing Pipeline

1. **Audio Input** → WebSocket chunks (base64 encoded)
2. **Speech-to-Text** → Whisper.cpp transcription
3. **Emotion Detection** → Text/audio emotion analysis
4. **Memory Retrieval** → FAISS similarity search
5. **LLM Processing** → OpenRouter API response generation
6. **Text-to-Speech** → Piper TTS with emotional voice
7. **Storage** → Firebase + FAISS memory storage

## Development

### Adding Custom Agents

```python
agent_manager.add_custom_agent("custom_agent", {
    "name": "Custom Agent",
    "personality": "helpful and knowledgeable",
    "system_prompt": "You are a custom AI assistant...",
    "voice_style": "professional",
    "emotional_responses": {
        "happy": "Great to hear!",
        "sad": "I'm here to help.",
        # ... other emotions
    }
})
```

### Testing

Run tests with:
```bash
pytest tests/
```

## Production Deployment

1. Set up proper environment variables
2. Configure CORS for your frontend domain
3. Use a production WSGI server like Gunicorn
4. Set up proper logging and monitoring
5. Configure Firebase security rules
6. Use HTTPS for WebSocket connections

## License

Open source - see LICENSE file for details.
