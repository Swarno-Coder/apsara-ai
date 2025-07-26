#!/usr/bin/env python3
"""
Model downloader script for AI Companion app
Downloads Whisper and Piper models for offline use
"""

import os
import requests
import urllib.request
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_file(url: str, destination: str, description: str = ""):
    """Download a file with progress indication"""
    try:
        logger.info(f"Downloading {description}: {url}")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        
        # Download file
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(destination, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        print(f"\rProgress: {progress:.1f}%", end='', flush=True)
        
        print(f"\n✅ Downloaded {description} successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to download {description}: {e}")
        return False

def download_whisper_models():
    """Download Whisper models"""
    logger.info("Downloading Whisper models...")
    
    whisper_models = {
        "base": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin",
        "small": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin",
    }
    
    whisper_dir = Path("models/whisper")
    whisper_dir.mkdir(parents=True, exist_ok=True)
    
    for model_name, url in whisper_models.items():
        destination = whisper_dir / f"ggml-{model_name}.bin"
        if not destination.exists():
            success = download_file(url, str(destination), f"Whisper {model_name} model")
            if not success:
                logger.warning(f"Failed to download Whisper {model_name} model")
        else:
            logger.info(f"Whisper {model_name} model already exists")

def download_piper_models():
    """Download Piper TTS models"""
    logger.info("Downloading Piper TTS models...")
    
    # Piper models (these are example URLs - replace with actual Piper model URLs)
    piper_models = {
        "en_US-lessac-medium": {
            "model": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx",
            "config": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json"
        },
        "en_US-amy-medium": {
            "model": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/amy/medium/en_US-amy-medium.onnx",
            "config": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/amy/medium/en_US-amy-medium.onnx.json"
        }
    }
    
    piper_dir = Path("models/piper")
    piper_dir.mkdir(parents=True, exist_ok=True)
    
    for model_name, urls in piper_models.items():
        # Download model file
        model_dest = piper_dir / f"{model_name}.onnx"
        if not model_dest.exists():
            success = download_file(urls["model"], str(model_dest), f"Piper {model_name} model")
            if not success:
                continue
        
        # Download config file
        config_dest = piper_dir / f"{model_name}.onnx.json"
        if not config_dest.exists():
            download_file(urls["config"], str(config_dest), f"Piper {model_name} config")

def download_sentence_transformer_model():
    """Download sentence transformer model for embeddings"""
    logger.info("Downloading sentence transformer model...")
    
    try:
        from sentence_transformers import SentenceTransformer
        
        # Download and cache the model
        model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("✅ Sentence transformer model downloaded successfully")
        
    except ImportError:
        logger.warning("sentence-transformers not available, skipping model download")
    except Exception as e:
        logger.error(f"❌ Failed to download sentence transformer model: {e}")

def create_model_info():
    """Create model info file"""
    model_info = {
        "whisper": {
            "models": ["base", "small"],
            "path": "models/whisper/",
            "format": "ggml-{model}.bin"
        },
        "piper": {
            "models": ["en_US-lessac-medium", "en_US-amy-medium"],
            "path": "models/piper/",
            "format": "{model}.onnx"
        },
        "embeddings": {
            "model": "all-MiniLM-L6-v2",
            "type": "sentence-transformers"
        }
    }
    
    import json
    with open("models/model_info.json", "w") as f:
        json.dump(model_info, f, indent=2)
    
    logger.info("✅ Model info file created")

def main():
    """Main function to download all models"""
    logger.info("🚀 Starting model download process...")
    
    # Create models directory
    Path("models").mkdir(exist_ok=True)
    
    # Download models
    download_whisper_models()
    download_piper_models()
    download_sentence_transformer_model()
    
    # Create model info
    create_model_info()
    
    logger.info("🎉 Model download process completed!")
    
    # Verify downloads
    whisper_base = Path("models/whisper/ggml-base.bin")
    if whisper_base.exists():
        logger.info(f"✅ Whisper base model ready ({whisper_base.stat().st_size / 1024 / 1024:.1f} MB)")
    
    piper_models = list(Path("models/piper").glob("*.onnx"))
    if piper_models:
        logger.info(f"✅ {len(piper_models)} Piper TTS models ready")
    
    logger.info("🎯 All models are ready for the AI Companion app!")

if __name__ == "__main__":
    main()
