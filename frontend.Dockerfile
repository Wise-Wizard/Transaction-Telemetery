FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    netcat-openbsd \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt flask

# Copy frontend code
COPY frontend/ ./frontend/

# Create a directory for scripts
RUN mkdir -p /app/scripts

# Create startup script
COPY scripts/start-frontend.sh /app/scripts/
RUN chmod +x /app/scripts/start-frontend.sh

# Expose frontend port
EXPOSE 5001

# Set the entrypoint
ENTRYPOINT ["/app/scripts/start-frontend.sh"]
