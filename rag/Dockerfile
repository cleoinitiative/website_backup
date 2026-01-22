# CLEO Tech Help Chatbot Backend
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run ingestion to populate vector store (optional - can be run separately)
# RUN python ingest.py

# Expose port (Railway provides PORT env var)
EXPOSE 8000

# Start the application - use shell form to expand $PORT
CMD python -m uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}
