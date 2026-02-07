# Worker Dockerfile (Heavy Lifting)
FROM python:3.10-slim

WORKDIR /app

# Install critical system dependencies for Zero-RIP flow
# ghostscript: For potential PDF/EPS processing and alternative ripping
# potrace: For vectorization
# libgl1/libglib2.0: For OpenCV
RUN apt-get update && apt-get install -y \
    ghostscript \
    potrace \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ .

# Run Celery Worker
CMD ["celery", "-A", "worker.celery", "worker", "--loglevel=info"]
