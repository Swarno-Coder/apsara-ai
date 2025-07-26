import os
from dotenv import load_dotenv

load_dotenv()

# Server Configuration
HOST = "0.0.0.0"
PORT = 8000
DEBUG = True

# OpenRouter API Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "anthropic/claude-3.5-sonnet"

# Firebase Configuration
FIREBASE_CONFIG_PATH = os.getenv("FIREBASE_CONFIG_PATH", "models/firebase-credentials.json")
FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "models/firebase-credentials.json")
FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")

# Audio Configuration
SAMPLE_RATE = 16000
CHUNK_SIZE = 1024
AUDIO_FORMAT = "wav"
MAX_AUDIO_LENGTH = 30  # seconds

# Model Paths
MODELS_DIR = "models"
WHISPER_MODEL_PATH = os.path.join(MODELS_DIR, "whisper.cpp")
PIPER_MODEL_PATH = os.path.join(MODELS_DIR, "piper_model")
EMOTION_MODEL_PATH = os.path.join(MODELS_DIR, "emotion_model.onnx")
PIPER_VOICES_DIR = os.path.join(MODELS_DIR, "piper_voices")
FAISS_INDEX_PATH = os.path.join(MODELS_DIR, "faiss_index")

# Memory Configuration
MAX_MEMORY_ITEMS = 1000
EMBEDDING_DIMENSION = 768
TOP_K_MEMORIES = 5

# Agent Configuration
DEFAULT_AGENT_PERSONALITY = "friendly and empathetic"
MAX_RESPONSE_LENGTH = 500

# Emotion Labels
EMOTION_LABELS = ["neutral", "happy", "sad", "angry", "fear", "surprise", "disgust"]
