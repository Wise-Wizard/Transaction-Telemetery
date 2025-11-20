#!/bin/bash
set -e

# This script can be run manually to generate custom test data
# Usage: docker-compose exec backend /app/scripts/generate-data.sh [options]

# Default values
USERS=10
COMPANIES=5
TRANSACTIONS=20
DETECT=true

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --users=*)
      USERS="${1#*=}"
      shift
      ;;
    --companies=*)
      COMPANIES="${1#*=}"
      shift
      ;;
    --transactions=*)
      TRANSACTIONS="${1#*=}"
      shift
      ;;
    --no-detect)
      DETECT=false
      shift
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--users=N] [--companies=N] [--transactions=N] [--no-detect]"
      exit 1
      ;;
  esac
done

# Build the command
CMD="python -m app.utils.generate_data --users $USERS --companies $COMPANIES --transactions $TRANSACTIONS"
if [ "$DETECT" = "false" ]; then
  CMD="$CMD --no-detect"
fi

# Run the command
echo "Generating data with the following parameters:"
echo "- Users: $USERS"
echo "- Companies: $COMPANIES"
echo "- Transactions: $TRANSACTIONS"
echo "- Detect relationships: $DETECT"
echo ""
echo "Running command: $CMD"
echo ""

eval $CMD
