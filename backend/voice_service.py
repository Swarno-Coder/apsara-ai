from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import aiofiles
import tempfile
import os
import logging
from typing import Optional, List
import uuid
from datetime import datetime

from services.stt_service import STTService
from services.tts_service import TTSService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Voice Processing Microservice", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class STTRequest(BaseModel):
    audio_data: str  # base64 encoded audio
    language: str = "en"
    model: str = "whisper-base"

class STTResponse(BaseModel):
    transcript: str
    confidence: float
    processing_time: float
    language_detected: str

class TTSRequest(BaseModel):
    text: str
    voice_model: str = "default"
    language: str = "en"
    speed: float = 1.0
    pitch: float = 1.0

class TTSResponse(BaseModel):
    audio_data: str  # base64 encoded audio
    duration: float
    processing_time: float
    voice_model_used: str

# Initialize services
stt_service = STTService()
tts_service = TTSService()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    try:
        await stt_service.initialize()
        await tts_service.initialize()
        logger.info("✅ Voice processing services initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "services": {
            "stt": stt_service.is_ready(),
            "tts": tts_service.is_ready()
        }
    }

@app.post("/stt/transcribe", response_model=STTResponse)
async def transcribe_audio(request: STTRequest):
    """Speech-to-text transcription"""
    try:
        start_time = datetime.now()
        
        # Decode audio data
        import base64
        audio_bytes = base64.b64decode(request.audio_data)
        
        # Transcribe audio
        result = await stt_service.transcribe_audio(
            audio_bytes,
            language=request.language,
            model=request.model
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return STTResponse(
            transcript=result["transcript"],
            confidence=result.get("confidence", 0.9),
            processing_time=processing_time,
            language_detected=result.get("language", request.language)
        )
        
    except Exception as e:
        logger.error(f"STT transcription error: {e}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@app.post("/stt/transcribe-file")
async def transcribe_audio_file(
    file: UploadFile = File(...),
    language: str = "en",
    model: str = "whisper-base"
):
    """Speech-to-text transcription from audio file"""
    try:
        start_time = datetime.now()
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Transcribe audio file
            result = await stt_service.transcribe_file(
                temp_file_path,
                language=language,
                model=model
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return STTResponse(
                transcript=result["transcript"],
                confidence=result.get("confidence", 0.9),
                processing_time=processing_time,
                language_detected=result.get("language", language)
            )
            
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
            
    except Exception as e:
        logger.error(f"STT file transcription error: {e}")
        raise HTTPException(status_code=500, detail=f"File transcription failed: {str(e)}")

@app.post("/tts/synthesize", response_model=TTSResponse)
async def synthesize_speech(request: TTSRequest):
    """Text-to-speech synthesis"""
    try:
        start_time = datetime.now()
        
        # Synthesize speech
        result = await tts_service.generate_speech(
            text=request.text,
            voice_model=request.voice_model,
            language=request.language,
            speed=request.speed,
            pitch=request.pitch
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Encode audio as base64
        import base64
        audio_b64 = base64.b64encode(result["audio_data"]).decode('utf-8')
        
        return TTSResponse(
            audio_data=audio_b64,
            duration=result.get("duration", 0.0),
            processing_time=processing_time,
            voice_model_used=result.get("voice_model", request.voice_model)
        )
        
    except Exception as e:
        logger.error(f"TTS synthesis error: {e}")
        raise HTTPException(status_code=500, detail=f"Speech synthesis failed: {str(e)}")

@app.get("/stt/models")
async def get_stt_models():
    """Get available STT models"""
    return {
        "models": await stt_service.get_available_models(),
        "default": "whisper-base"
    }

@app.get("/tts/voices")
async def get_tts_voices():
    """Get available TTS voices"""
    return {
        "voices": await tts_service.get_available_voices(),
        "default": "default"
    }

@app.get("/stt/languages")
async def get_supported_languages():
    """Get supported languages for STT"""
    return {
        "languages": [
            {"code": "en", "name": "English"},
            {"code": "hi", "name": "Hindi"},
            {"code": "bn", "name": "Bengali"},
            {"code": "te", "name": "Telugu"},
            {"code": "ta", "name": "Tamil"},
            {"code": "gu", "name": "Gujarati"},
            {"code": "kn", "name": "Kannada"},
            {"code": "ml", "name": "Malayalam"},
            {"code": "pa", "name": "Punjabi"},
            {"code": "ur", "name": "Urdu"},
        ]
    }

@app.post("/voice/process")
async def process_voice_pipeline(
    audio_data: str,
    target_voice: str = "default",
    source_language: str = "en",
    target_language: str = "en"
):
    """Complete voice processing pipeline: STT -> Processing -> TTS"""
    try:
        start_time = datetime.now()
        
        # Step 1: Speech-to-Text
        stt_result = await stt_service.transcribe_audio(
            base64.b64decode(audio_data),
            language=source_language
        )
        
        transcript = stt_result["transcript"]
        
        # Step 2: Process transcript (could include translation, emotion analysis, etc.)
        # For now, just pass through
        processed_text = transcript
        
        # Step 3: Text-to-Speech
        tts_result = await tts_service.generate_speech(
            text=processed_text,
            voice_model=target_voice,
            language=target_language
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Encode output audio
        import base64
        output_audio = base64.b64encode(tts_result["audio_data"]).decode('utf-8')
        
        return {
            "transcript": transcript,
            "processed_text": processed_text,
            "output_audio": output_audio,
            "processing_time": processing_time,
            "pipeline_steps": ["stt", "processing", "tts"]
        }
        
    except Exception as e:
        logger.error(f"Voice pipeline error: {e}")
        raise HTTPException(status_code=500, detail=f"Voice processing failed: {str(e)}")

@app.get("/metrics")
async def get_metrics():
    """Get service metrics"""
    return {
        "stt_service": await stt_service.get_metrics(),
        "tts_service": await tts_service.get_metrics(),
        "uptime": datetime.now(),
        "memory_usage": "N/A",  # Could integrate actual memory monitoring
        "cpu_usage": "N/A"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
