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
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN sed -i 's/from torchvision.transforms.functional_tensor import rgb_to_grayscale/from torchvision.transforms.functional import rgb_to_grayscale/' /usr/local/lib/python3.10/site-packages/basicsr/data/degradations.py

# Copy application code
COPY backend/ backend/
# Also copy worker code
COPY worker/ worker/

# Run Celery Worker
CMD ["celery", "-A", "worker.celery_app", "worker", "--loglevel=info", "--pool=solo"]
