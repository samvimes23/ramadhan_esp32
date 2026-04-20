# Use a stable Python base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HA_TOKEN=""
ENV HA_URL="http://192.168.1.22:8123/api/services/media_player/play_media"
ENV HA_ENTITY_ID="media_player.bedroom_speaker"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    cron \
    curl \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create log directory and files
RUN mkdir -p logs && \
    touch logs/fajr_update_status.json logs/fajr_auto_update.log adhan.log adhan_update.log

# Make scripts executable
RUN chmod +x scripts/*.sh

# Expose the Web UI port
EXPOSE 8090

# Use the entrypoint script to start services
ENTRYPOINT ["/app/docker-entrypoint.sh"]
