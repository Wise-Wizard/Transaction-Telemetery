#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== User & Transaction Graph Environment ===${NC}"
echo -e "${BLUE}Starting the application...${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Docker is not installed. Please install Docker and Docker Compose before running this script.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}Docker Compose is not installed. Please install Docker Compose before running this script.${NC}"
    exit 1
fi

# Build and start the containers
echo -e "${BLUE}Building and starting containers...${NC}"
docker-compose up -d --build

# Wait for services to be ready
echo -e "${BLUE}Waiting for services to be ready...${NC}"
echo -e "${YELLOW}This may take a minute or two...${NC}"

# Wait for Neo4j to be ready
echo -e "${BLUE}Waiting for Neo4j...${NC}"
until docker-compose exec -T neo4j curl -s http://localhost:7474 > /dev/null; do
    echo -n "."
    sleep 2
done
echo -e "\n${GREEN}Neo4j is ready!${NC}"

# Wait for backend to be ready
echo -e "${BLUE}Waiting for backend API...${NC}"
until docker-compose exec -T backend curl -s http://localhost:8000 > /dev/null; do
    echo -n "."
    sleep 2
done
echo -e "\n${GREEN}Backend API is ready!${NC}"

# Wait for frontend to be ready
echo -e "${BLUE}Waiting for frontend...${NC}"
until docker-compose exec -T frontend curl -s http://localhost:5001 > /dev/null; do
    echo -n "."
    sleep 2
done
echo -e "\n${GREEN}Frontend is ready!${NC}"

# Print success message
echo -e "\n${GREEN}=== Application is now running! ===${NC}"
echo -e "${BLUE}Access the application at:${NC}"
echo -e "  - Frontend: ${GREEN}http://localhost:5001${NC}"
echo -e "  - Backend API: ${GREEN}http://localhost:8000${NC}"
echo -e "  - Neo4j Browser: ${GREEN}http://localhost:7474${NC}"
echo -e "    (Neo4j credentials: neo4j/password)"
echo -e "\n${BLUE}To generate custom test data:${NC}"
echo -e "  docker-compose exec backend /app/scripts/generate-data.sh --users=20 --companies=10 --transactions=50"
echo -e "\n${BLUE}To stop the application:${NC}"
echo -e "  docker-compose down"
echo -e "\n${BLUE}To view logs:${NC}"
echo -e "  docker-compose logs -f"
