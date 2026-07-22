FROM python:3.13-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Install system dependencies for OpenCV and media rendering
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy complete project codebase
COPY . /app

EXPOSE 8000

# Run FastAPI via Uvicorn listening on dynamic $PORT
CMD ["sh", "-c", "python3 -m uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
