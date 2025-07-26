import numpy as np
import librosa
import soundfile as sf
from typing import Union, Tuple
import io
import base64

def normalize_audio(audio_data: np.ndarray, target_sample_rate: int = 16000) -> np.ndarray:
    """Normalize audio data to target sample rate and format."""
    # Ensure mono channel
    if len(audio_data.shape) > 1:
        audio_data = np.mean(audio_data, axis=1)
    
    # Normalize amplitude
    audio_data = audio_data / np.max(np.abs(audio_data))
    
    return audio_data.astype(np.float32)

def convert_to_wav(audio_data: np.ndarray, sample_rate: int = 16000) -> bytes:
    """Convert audio data to WAV format."""
    buffer = io.BytesIO()
    sf.write(buffer, audio_data, sample_rate, format='WAV', subtype='PCM_16')
    buffer.seek(0)
    return buffer.read()

def audio_from_bytes(audio_bytes: bytes) -> Tuple[np.ndarray, int]:
    """Load audio from bytes."""
    buffer = io.BytesIO(audio_bytes)
    audio_data, sample_rate = sf.read(buffer)
    return audio_data, sample_rate

def resample_audio(audio_data: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
    """Resample audio to target sample rate."""
    if orig_sr != target_sr:
        audio_data = librosa.resample(audio_data, orig_sr=orig_sr, target_sr=target_sr)
    return audio_data

def split_audio_chunks(audio_data: np.ndarray, chunk_size: int = 1024) -> list:
    """Split audio into chunks for streaming."""
    chunks = []
    for i in range(0, len(audio_data), chunk_size):
        chunk = audio_data[i:i + chunk_size]
        chunks.append(chunk)
    return chunks

def encode_audio_base64(audio_data: np.ndarray, sample_rate: int = 16000) -> str:
    """Encode audio as base64 string."""
    wav_bytes = convert_to_wav(audio_data, sample_rate)
    return base64.b64encode(wav_bytes).decode('utf-8')

def decode_audio_base64(audio_b64: str) -> Tuple[np.ndarray, int]:
    """Decode audio from base64 string."""
    audio_bytes = base64.b64decode(audio_b64)
    return audio_from_bytes(audio_bytes)
