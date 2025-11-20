#!/bin/bash
set -e

# Wait for Neo4j to be ready
echo "Waiting for Neo4j to be ready..."
while ! nc -z ${NEO4J_HOST:-neo4j} ${NEO4J_PORT:-7687}; do
  echo "Neo4j is not ready yet - sleeping"
  sleep 1
done
echo "Neo4j is ready!"

# Initialize the database if AUTO_INIT_DB is set to true
if [ "${AUTO_INIT_DB:-false}" = "true" ]; then
  echo "Auto-initializing the database..."
  python -m app.utils.init_db
  echo "Database initialization completed!"
fi

# Start the backend API server
echo "Starting the backend API server..."
exec python -m app.main
