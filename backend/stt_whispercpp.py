import subprocess
import tempfile
import os
from typing import Optional
import numpy as np
from audio_utils import audio_from_bytes, normalize_audio
import config

class WhisperCPPWrapper:
    def __init__(self, model_path: str = config.WHISPER_MODEL_PATH):
        self.model_path = model_path
        self.sample_rate = config.SAMPLE_RATE
        
    def transcribe_audio(self, audio_data: np.ndarray) -> str:
        """Transcribe audio using whisper.cpp"""
        try:
            # Create temporary WAV file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                # Normalize and save audio
                normalized_audio = normalize_audio(audio_data, self.sample_rate)
                import soundfile as sf
                sf.write(temp_file.name, normalized_audio, self.sample_rate)
                
                # Run whisper.cpp
                cmd = [
                    os.path.join(self.model_path, 'main'),
                    '-m', os.path.join(self.model_path, 'ggml-base.bin'),
                    '-f', temp_file.name,
                    '--output-txt'
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                # Clean up temp file
                os.unlink(temp_file.name)
                
                if result.returncode == 0:
                    # Read output file
                    output_file = temp_file.name + '.txt'
                    if os.path.exists(output_file):
                        with open(output_file, 'r') as f:
                            transcription = f.read().strip()
                        os.unlink(output_file)
                        return transcription
                    
                return ""
                
        except Exception as e:
            print(f"Whisper transcription error: {e}")
            return ""
    
    def transcribe_from_bytes(self, audio_bytes: bytes) -> str:
        """Transcribe audio from bytes"""
        try:
            audio_data, sample_rate = audio_from_bytes(audio_bytes)
            if sample_rate != self.sample_rate:
                from audio_utils import resample_audio
                audio_data = resample_audio(audio_data, sample_rate, self.sample_rate)
            return self.transcribe_audio(audio_data)
        except Exception as e:
            print(f"Transcription from bytes error: {e}")
            return ""

# Global instance
whisper_cpp = WhisperCPPWrapper()
