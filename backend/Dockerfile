FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    cmake \
    curl \
    wget \
    git \
    ffmpeg \
    espeak \
    espeak-data \
    libespeak-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install additional audio processing libraries
RUN pip install --no-cache-dir \
    librosa \
    soundfile \
    pydub \
    torch \
    torchaudio

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data /app/models /app/audio_cache

# Set permissions
RUN chmod +x /app/init_db.py

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "-c", "import asyncio; from init_db import init_database; asyncio.run(init_database())", "&&", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
