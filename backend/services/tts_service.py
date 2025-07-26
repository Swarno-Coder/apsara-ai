import os
import tempfile
import uuid
import logging
from typing import Optional, Dict
import asyncio
import json

logger = logging.getLogger(__name__)

class TTSService:
    def __init__(self):
        """Initialize Text-to-Speech service using Piper TTS"""
        self.piper_executable = os.getenv("PIPER_EXECUTABLE", "piper")
        self.models_dir = os.getenv("PIPER_MODELS_DIR", "./models/piper")
        self.output_dir = os.getenv("TTS_OUTPUT_DIR", "./audio_cache")
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Voice models for different languages and personalities
        self.voice_models = {
            "english": {
                "female_warm": "en_US-amy-medium.onnx",
                "female_cheerful": "en_US-lessac-medium.onnx", 
                "female_soft": "en_US-libritts-medium.onnx",
                "female_confident": "en_US-ljspeech-medium.onnx",
                "default": "en_US-lessac-medium.onnx"
            },
            "hindi": {
                "female_warm": "hi_IN-female-medium.onnx",
                "default": "hi_IN-female-medium.onnx"
            },
            "bengali": {
                "female_warm": "bn_IN-female-medium.onnx", 
                "default": "bn_IN-female-medium.onnx"
            }
        }
        
        # Cache for generated audio files
        self.audio_cache = {}
    
    async def synthesize(self, text: str, agent_id: str, language: str = "english", 
                        voice_style: str = "default") -> str:
        """Convert text to speech and return audio file URL"""
        if not text or len(text.strip()) == 0:
            raise ValueError("No text provided for synthesis")
        
        try:
            # Generate cache key
            cache_key = self._generate_cache_key(text, agent_id, language, voice_style)
            
            # Check if already cached
            if cache_key in self.audio_cache:
                cached_path = self.audio_cache[cache_key]
                if os.path.exists(cached_path):
                    return self._get_audio_url(cache_key)
            
            # Get appropriate voice model
            voice_model = self._get_voice_model(language, voice_style)
            
            # Generate speech
            audio_path = await self._run_piper_synthesis(text, voice_model, cache_key)
            
            # Cache the result
            self.audio_cache[cache_key] = audio_path
            
            return self._get_audio_url(cache_key)
            
        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}")
            raise Exception(f"Speech synthesis failed: {str(e)}")
    
    async def _run_piper_synthesis(self, text: str, voice_model: str, cache_key: str) -> str:
        """Run Piper TTS synthesis"""
        try:
            # Prepare output file path
            audio_filename = f"{cache_key}.wav"
            audio_path = os.path.join(self.output_dir, audio_filename)
            
            # Check if Piper is available
            if self._is_piper_available():
                return await self._run_piper_command(text, voice_model, audio_path)
            else:
                return await self._fallback_synthesis(text, audio_path)
                
        except Exception as e:
            logger.error(f"Piper synthesis execution failed: {e}")
            raise
    
    def _is_piper_available(self) -> bool:
        """Check if Piper TTS is available"""
        try:
            import subprocess
            result = subprocess.run([self.piper_executable, "--help"], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    async def _run_piper_command(self, text: str, voice_model: str, output_path: str) -> str:
        """Run Piper TTS command"""
        model_path = os.path.join(self.models_dir, voice_model)
        
        if not os.path.exists(model_path):
            logger.warning(f"Voice model not found: {model_path}, using fallback")
            return await self._fallback_synthesis(text, output_path)
        
        try:
            # Build Piper command
            cmd = [
                self.piper_executable,
                "--model", model_path,
                "--output_file", output_path
            ]
            
            # Run synthesis
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate(input=text.encode('utf-8'))
            
            if process.returncode == 0 and os.path.exists(output_path):
                return output_path
            else:
                error_msg = stderr.decode('utf-8') if stderr else "Unknown error"
                raise Exception(f"Piper failed: {error_msg}")
                
        except Exception as e:
            logger.error(f"Piper command execution failed: {e}")
            return await self._fallback_synthesis(text, output_path)
    
    async def _fallback_synthesis(self, text: str, output_path: str) -> str:
        """Fallback synthesis method when Piper is not available"""
        try:
            # Try using system TTS if available
            return await self._system_tts_synthesis(text, output_path)
        except:
            # Create a placeholder audio file
            return await self._create_placeholder_audio(text, output_path)
    
    async def _system_tts_synthesis(self, text: str, output_path: str) -> str:
        """Use system TTS as fallback"""
        try:
            # For Windows, use SAPI
            if os.name == 'nt':
                return await self._windows_tts(text, output_path)
            # For macOS, use say command
            elif os.uname().sysname == 'Darwin':
                return await self._macos_tts(text, output_path)
            # For Linux, try espeak or festival
            else:
                return await self._linux_tts(text, output_path)
                
        except Exception as e:
            logger.error(f"System TTS failed: {e}")
            return await self._create_placeholder_audio(text, output_path)
    
    async def _windows_tts(self, text: str, output_path: str) -> str:
        """Windows SAPI TTS"""
        try:
            import subprocess
            
            # Use PowerShell with SAPI
            ps_script = f"""
            Add-Type -AssemblyName System.Speech
            $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
            $synth.SetOutputToWaveFile('{output_path}')
            $synth.Speak('{text.replace("'", "''")}')
            $synth.Dispose()
            """
            
            process = await asyncio.create_subprocess_exec(
                "powershell", "-Command", ps_script,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            
            if os.path.exists(output_path):
                return output_path
            else:
                raise Exception("Windows TTS failed to create audio file")
                
        except Exception as e:
            logger.error(f"Windows TTS failed: {e}")
            raise
    
    async def _macos_tts(self, text: str, output_path: str) -> str:
        """macOS say command TTS"""
        try:
            # Convert to AIFF first, then to WAV
            temp_aiff = output_path.replace('.wav', '.aiff')
            
            process = await asyncio.create_subprocess_exec(
                "say", "-o", temp_aiff, text,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            
            if os.path.exists(temp_aiff):
                # Convert AIFF to WAV using ffmpeg or sox if available
                try:
                    convert_process = await asyncio.create_subprocess_exec(
                        "ffmpeg", "-i", temp_aiff, output_path,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    await convert_process.communicate()
                    os.remove(temp_aiff)
                except:
                    # If conversion fails, rename AIFF to WAV
                    os.rename(temp_aiff, output_path)
                
                return output_path
            else:
                raise Exception("macOS TTS failed")
                
        except Exception as e:
            logger.error(f"macOS TTS failed: {e}")
            raise
    
    async def _linux_tts(self, text: str, output_path: str) -> str:
        """Linux TTS using espeak"""
        try:
            process = await asyncio.create_subprocess_exec(
                "espeak", "-w", output_path, text,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            
            if os.path.exists(output_path):
                return output_path
            else:
                raise Exception("Linux TTS failed")
                
        except Exception as e:
            logger.error(f"Linux TTS failed: {e}")
            raise
    
    async def _create_placeholder_audio(self, text: str, output_path: str) -> str:
        """Create a placeholder audio file when TTS is not available"""
        try:
            # Create a simple beep tone as placeholder
            import numpy as np
            import wave
            
            # Generate a simple tone
            duration = min(len(text) * 0.1, 5.0)  # Max 5 seconds
            sample_rate = 44100
            frequency = 440  # A note
            
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            wave_data = np.sin(frequency * 2 * np.pi * t) * 0.3  # Low volume
            
            # Add fade in/out
            fade_samples = int(sample_rate * 0.1)
            wave_data[:fade_samples] *= np.linspace(0, 1, fade_samples)
            wave_data[-fade_samples:] *= np.linspace(1, 0, fade_samples)
            
            # Convert to 16-bit integers
            wave_data = (wave_data * 32767).astype(np.int16)
            
            # Save as WAV file
            with wave.open(output_path, 'w') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 2 bytes per sample
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(wave_data.tobytes())
            
            return output_path
            
        except ImportError:
            # If numpy/wave not available, create empty file
            with open(output_path, 'wb') as f:
                f.write(b'')  # Empty file
            return output_path
        except Exception as e:
            logger.error(f"Placeholder audio creation failed: {e}")
            # Create empty file as last resort
            with open(output_path, 'wb') as f:
                f.write(b'')
            return output_path
    
    def _get_voice_model(self, language: str, voice_style: str) -> str:
        """Get appropriate voice model for language and style"""
        language = language.lower()
        
        if language in self.voice_models:
            models = self.voice_models[language]
            if voice_style in models:
                return models[voice_style]
            else:
                return models["default"]
        else:
            # Default to English
            models = self.voice_models["english"]
            return models.get(voice_style, models["default"])
    
    def _generate_cache_key(self, text: str, agent_id: str, language: str, voice_style: str) -> str:
        """Generate cache key for audio file"""
        import hashlib
        
        # Create unique key based on content
        content = f"{text}_{agent_id}_{language}_{voice_style}"
        hash_object = hashlib.md5(content.encode('utf-8'))
        return hash_object.hexdigest()
    
    def _get_audio_url(self, cache_key: str) -> str:
        """Get URL for audio file"""
        return f"/audio/{cache_key}"
    
    async def get_audio_file(self, audio_id: str) -> str:
        """Get path to audio file by ID"""
        if audio_id in self.audio_cache:
            return self.audio_cache[audio_id]
        
        # Check if file exists in output directory
        audio_path = os.path.join(self.output_dir, f"{audio_id}.wav")
        if os.path.exists(audio_path):
            return audio_path
        
        raise FileNotFoundError(f"Audio file not found: {audio_id}")
    
    async def get_available_voices(self) -> Dict:
        """Get list of available voice models"""
        available_voices = {}
        
        for language, voices in self.voice_models.items():
            available_voices[language] = []
            for voice_style, model_file in voices.items():
                model_path = os.path.join(self.models_dir, model_file)
                is_available = os.path.exists(model_path)
                
                available_voices[language].append({
                    "style": voice_style,
                    "model": model_file,
                    "available": is_available
                })
        
        return available_voices
    
    async def cleanup_old_cache(self, max_age_days: int = 7):
        """Clean up old cached audio files"""
        import time
        
        current_time = time.time()
        max_age_seconds = max_age_days * 24 * 60 * 60
        
        cleaned_count = 0
        
        for cache_key, file_path in list(self.audio_cache.items()):
            try:
                if os.path.exists(file_path):
                    file_age = current_time - os.path.getmtime(file_path)
                    
                    if file_age > max_age_seconds:
                        os.remove(file_path)
                        del self.audio_cache[cache_key]
                        cleaned_count += 1
                else:
                    # Remove from cache if file doesn't exist
                    del self.audio_cache[cache_key]
                    
            except Exception as e:
                logger.error(f"Error cleaning cache file {file_path}: {e}")
        
        logger.info(f"Cleaned {cleaned_count} old audio cache files")
        return cleaned_count
