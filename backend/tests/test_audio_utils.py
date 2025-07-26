import pytest
import numpy as np
from audio_utils import (
    normalize_audio, 
    convert_to_wav, 
    audio_from_bytes,
    resample_audio,
    split_audio_chunks
)

def test_normalize_audio():
    """Test audio normalization"""
    # Create test audio data
    audio_data = np.array([0.5, -0.8, 0.3, -0.2])
    normalized = normalize_audio(audio_data)
    
    # Check that it's normalized to [-1, 1] range
    assert np.max(np.abs(normalized)) <= 1.0
    assert normalized.dtype == np.float32

def test_convert_to_wav():
    """Test WAV conversion"""
    audio_data = np.array([0.1, 0.2, 0.3, 0.4], dtype=np.float32)
    wav_bytes = convert_to_wav(audio_data, 16000)
    
    assert isinstance(wav_bytes, bytes)
    assert len(wav_bytes) > 0

def test_audio_from_bytes():
    """Test loading audio from bytes"""
    # Create test audio and convert to bytes
    original_audio = np.array([0.1, 0.2, 0.3, 0.4], dtype=np.float32)
    wav_bytes = convert_to_wav(original_audio, 16000)
    
    # Load back from bytes
    loaded_audio, sample_rate = audio_from_bytes(wav_bytes)
    
    assert sample_rate == 16000
    assert len(loaded_audio) == len(original_audio)

def test_resample_audio():
    """Test audio resampling"""
    audio_data = np.array([0.1, 0.2, 0.3, 0.4] * 100, dtype=np.float32)
    
    # Resample from 44100 to 16000
    resampled = resample_audio(audio_data, 44100, 16000)
    
    # Should be shorter due to downsampling
    assert len(resampled) < len(audio_data)

def test_split_audio_chunks():
    """Test audio chunking"""
    audio_data = np.array(range(100), dtype=np.float32)
    chunks = split_audio_chunks(audio_data, chunk_size=10)
    
    assert len(chunks) == 10
    assert len(chunks[0]) == 10
