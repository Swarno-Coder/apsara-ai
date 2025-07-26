import os
import tempfile
import uuid
import logging
from typing import Optional
from fastapi import UploadFile
import asyncio

logger = logging.getLogger(__name__)

class STTService:
    def __init__(self):
        """Initialize Speech-to-Text service using Whisper.cpp"""
        self.whisper_model_path = os.getenv("WHISPER_MODEL_PATH", "./models/whisper/ggml-base.bin")
        self.whisper_executable = os.getenv("WHISPER_EXECUTABLE", "whisper")
        self.supported_languages = [
            "en", "hi", "bn", "mr", "ta", "te", "gu", "kn", "ml", "or", "pa", "ur"
        ]
    
    async def transcribe(self, audio_file: UploadFile, language: str = "auto") -> str:
        """Transcribe audio file to text"""
        if not audio_file:
            raise ValueError("No audio file provided")
        
        try:
            # Save uploaded file temporarily
            temp_audio_path = await self._save_temp_audio(audio_file)
            
            # Transcribe using Whisper
            transcription = await self._run_whisper_transcription(temp_audio_path, language)
            
            # Clean up temp file
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
            
            return transcription.strip()
            
        except Exception as e:
            logger.error(f"Error during transcription: {e}")
            raise Exception(f"Transcription failed: {str(e)}")
    
    async def _save_temp_audio(self, audio_file: UploadFile) -> str:
        """Save uploaded audio file to temporary location"""
        # Create temp file with appropriate extension
        file_extension = self._get_file_extension(audio_file.filename)
        temp_filename = f"audio_{uuid.uuid4().hex[:8]}{file_extension}"
        temp_path = os.path.join(tempfile.gettempdir(), temp_filename)
        
        # Save file
        with open(temp_path, "wb") as temp_file:
            content = await audio_file.read()
            temp_file.write(content)
        
        return temp_path
    
    def _get_file_extension(self, filename: Optional[str]) -> str:
        """Get file extension from filename"""
        if not filename:
            return ".wav"
        
        ext = os.path.splitext(filename)[1].lower()
        if ext in ['.wav', '.mp3', '.m4a', '.ogg', '.flac']:
            return ext
        return ".wav"
    
    async def _run_whisper_transcription(self, audio_path: str, language: str) -> str:
        """Run Whisper transcription"""
        try:
            # Check if using Whisper.cpp or OpenAI Whisper
            if self._is_whisper_cpp_available():
                return await self._run_whisper_cpp(audio_path, language)
            else:
                return await self._run_openai_whisper(audio_path, language)
                
        except Exception as e:
            logger.error(f"Whisper transcription failed: {e}")
            # Fallback to basic transcription
            return await self._fallback_transcription(audio_path)
    
    def _is_whisper_cpp_available(self) -> bool:
        """Check if Whisper.cpp is available"""
        try:
            # Check if whisper executable exists
            import subprocess
            result = subprocess.run([self.whisper_executable, "--help"], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    async def _run_whisper_cpp(self, audio_path: str, language: str) -> str:
        """Run Whisper.cpp for transcription"""
        import subprocess
        
        # Build command
        cmd = [
            self.whisper_executable,
            "-m", self.whisper_model_path,
            "-f", audio_path,
            "--output-txt"
        ]
        
        # Add language if specified and supported
        if language != "auto" and language in self.supported_languages:
            cmd.extend(["-l", language])
        
        # Run transcription
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                # Whisper.cpp outputs to a text file
                output_file = audio_path + ".txt"
                if os.path.exists(output_file):
                    with open(output_file, 'r', encoding='utf-8') as f:
                        transcription = f.read()
                    os.remove(output_file)  # Clean up
                    return transcription
                else:
                    # Parse from stdout if available
                    return stdout.decode('utf-8')
            else:
                raise Exception(f"Whisper.cpp failed: {stderr.decode('utf-8')}")
                
        except Exception as e:
            logger.error(f"Whisper.cpp execution failed: {e}")
            raise
    
    async def _run_openai_whisper(self, audio_path: str, language: str) -> str:
        """Run OpenAI Whisper (Python package) for transcription"""
        try:
            import whisper
            
            # Load model (use cached model)
            model_name = os.getenv("WHISPER_MODEL_SIZE", "base")
            model = whisper.load_model(model_name)
            
            # Set language
            whisper_language = None
            if language != "auto" and language in self.supported_languages:
                whisper_language = language
            
            # Transcribe
            result = model.transcribe(audio_path, language=whisper_language)
            text = result["text"]
            
            # Ensure we return a string
            if isinstance(text, list):
                return " ".join(str(item) for item in text)
            return str(text)
            
        except ImportError:
            logger.error("OpenAI Whisper package not available")
            raise Exception("Whisper package not installed")
        except Exception as e:
            logger.error(f"OpenAI Whisper transcription failed: {e}")
            raise
    
    async def _fallback_transcription(self, audio_path: str) -> str:
        """Fallback transcription method when Whisper is not available"""
        logger.warning("Using fallback transcription - returning placeholder")
        
        # In a real implementation, you might:
        # 1. Use a simpler speech recognition library
        # 2. Call an external API
        # 3. Return an error message
        
        # For now, return a placeholder indicating the service needs setup
        return "Audio transcription service needs configuration. Please set up Whisper.cpp or OpenAI Whisper."
    
    async def detect_language(self, audio_file: UploadFile) -> str:
        """Detect language from audio file"""
        try:
            # Save temporary file
            temp_path = await self._save_temp_audio(audio_file)
            
            if self._is_whisper_cpp_available():
                # Use Whisper.cpp for language detection
                cmd = [
                    self.whisper_executable,
                    "-m", self.whisper_model_path,
                    "-f", temp_path,
                    "--language", "auto",
                    "--detect-language"
                ]
                
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                
                if process.returncode == 0:
                    # Parse language from output
                    output = stdout.decode('utf-8')
                    # Look for language detection in output
                    for line in output.split('\n'):
                        if 'detected language:' in line.lower():
                            return line.split(':')[-1].strip()
            
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            return "en"  # Default to English
            
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return "en"  # Default fallback
    
    def get_supported_formats(self) -> list:
        """Get list of supported audio formats"""
        return [
            "audio/wav",
            "audio/mp3", 
            "audio/m4a",
            "audio/ogg",
            "audio/flac",
            "audio/webm"
        ]
    
    def validate_audio_file(self, audio_file: UploadFile) -> bool:
        """Validate if audio file is supported"""
        if not audio_file.content_type:
            return False
        
        return audio_file.content_type in self.get_supported_formats()
    
    async def get_audio_duration(self, audio_file: UploadFile) -> float:
        """Get duration of audio file in seconds"""
        try:
            import librosa
            
            temp_path = await self._save_temp_audio(audio_file)
            
            # Load audio and get duration
            y, sr = librosa.load(temp_path)
            duration = librosa.get_duration(y=y, sr=sr)
            
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            return duration
            
        except ImportError:
            logger.warning("librosa not available for duration calculation")
            return 0.0
        except Exception as e:
            logger.error(f"Error calculating audio duration: {e}")
            return 0.0
