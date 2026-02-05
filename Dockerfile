# Use standard Python image for long-running process
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    RAILWAY_VOLUME_MOUNT_PATH="/app/data"

# Set working directory
WORKDIR /app

# Install git (needed for pip install git+...)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create data directory for volume
RUN mkdir -p /app/data

# Copy Mudrex SDK
COPY mudrex-sdk/mudrex ./mudrex-sdk/mudrex

# Copy application code
COPY config.py .
COPY strategy.py .
COPY mudrex_adapter.py .
COPY supertrend_mudrex_bot.py .
COPY main.py .

# Run the bot
CMD ["python", "main.py"]
