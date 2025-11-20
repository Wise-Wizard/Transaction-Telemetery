#!/bin/bash
set -e

# This script can be run manually to initialize the database
# Usage: docker-compose exec backend /app/scripts/init-db.sh

echo "Manually initializing the database..."
python -m app.utils.init_db
echo "Database initialization completed!"
