#!/bin/bash
set -e

# Wait for the backend to be ready
echo "Waiting for backend to be ready..."
while ! nc -z ${BACKEND_HOST:-backend} ${BACKEND_PORT:-8000}; do
  echo "Backend is not ready yet - sleeping"
  sleep 1
done
echo "Backend is ready!"

# Start the frontend server
echo "Starting the frontend server..."
cd /app/frontend
exec python server.py
