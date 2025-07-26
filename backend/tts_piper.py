import subprocess
import tempfile
import os
from typing import Optional
import numpy as np
from audio_utils import convert_to_wav
import config

class PiperTTSWrapper:
    def __init__(self, voices_dir: str = config.PIPER_VOICES_DIR):
        self.voices_dir = voices_dir
        self.sample_rate = config.SAMPLE_RATE
        self.emotion_voices = {
            "neutral": "en_US-ljspeech-medium.onnx",
            "happy": "en_US-amy-medium.onnx", 
            "sad": "en_US-ryan-medium.onnx",
            "angry": "en_US-danny-low.onnx",
            "fear": "en_US-lessac-medium.onnx",
            "surprise": "en_US-libritts-high.onnx",
            "disgust": "en_US-ljspeech-medium.onnx"
        }
    
    def synthesize_speech(self, text: str, emotion: str = "neutral") -> bytes:
        """Synthesize speech with emotional voice using Piper TTS"""
        try:
            # Select voice based on emotion
            voice_model = self.emotion_voices.get(emotion, self.emotion_voices["neutral"])
            voice_path = os.path.join(self.voices_dir, voice_model)
            
            if not os.path.exists(voice_path):
                print(f"Voice model not found: {voice_path}, using default")
                voice_path = os.path.join(self.voices_dir, self.emotion_voices["neutral"])
                
                if not os.path.exists(voice_path):
                    print("No voice models found, returning empty audio")
                    return b""
            
            # Create temporary output file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                output_path = temp_file.name
            
            # Run Piper TTS
            cmd = [
                "piper",
                "--model", voice_path,
                "--output_file", output_path
            ]
            
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input=text)
            
            if process.returncode == 0 and os.path.exists(output_path):
                # Read the generated audio file
                with open(output_path, 'rb') as f:
                    audio_bytes = f.read()
                
                # Clean up
                os.unlink(output_path)
                return audio_bytes
            else:
                print(f"Piper TTS error: {stderr}")
                if os.path.exists(output_path):
                    os.unlink(output_path)
                return b""
                
        except Exception as e:
            print(f"TTS synthesis error: {e}")
            return b""
    
    def synthesize_to_numpy(self, text: str, emotion: str = "neutral") -> np.ndarray:
        """Synthesize speech and return as numpy array"""
        audio_bytes = self.synthesize_speech(text, emotion)
        if audio_bytes:
            try:
                from audio_utils import audio_from_bytes
                audio_data, _ = audio_from_bytes(audio_bytes)
                return audio_data
            except Exception as e:
                print(f"Audio conversion error: {e}")
                return np.array([])
        return np.array([])
    
    def get_available_voices(self) -> list:
        """Get list of available voice models"""
        voices = []
        if os.path.exists(self.voices_dir):
            for file in os.listdir(self.voices_dir):
                if file.endswith('.onnx'):
                    voices.append(file)
        return voices

# Global instance
tts_engine = PiperTTSWrapper()
