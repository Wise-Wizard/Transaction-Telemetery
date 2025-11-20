.PHONY: build start stop restart logs clean generate-data init-db help

# Default target
help:
	@echo "User & Transaction Graph Environment"
	@echo ""
	@echo "Available commands:"
	@echo "  make build         - Build all Docker containers"
	@echo "  make start         - Start all Docker containers"
	@echo "  make stop          - Stop all Docker containers"
	@echo "  make restart       - Restart all Docker containers"
	@echo "  make logs          - View logs from all containers"
	@echo "  make clean         - Stop and remove all containers, networks, and volumes"
	@echo "  make generate-data - Generate custom test data"
	@echo "  make init-db       - Initialize the database with test data"
	@echo "  make help          - Show this help message"

# Build all Docker containers
build:
	docker-compose build

# Start all Docker containers
start:
	docker-compose up -d

# Stop all Docker containers
stop:
	docker-compose down

# Restart all Docker containers
restart:
	docker-compose restart

# View logs from all containers
logs:
	docker-compose logs -f

# Stop and remove all containers, networks, and volumes
clean:
	docker-compose down -v

# Generate custom test data
generate-data:
	@echo "Generating custom test data..."
	@echo "You can customize the parameters by setting USERS, COMPANIES, and TRANSACTIONS variables:"
	@echo "  make generate-data USERS=20 COMPANIES=10 TRANSACTIONS=50"
	@docker-compose exec backend /app/scripts/generate-data.sh --users=$(USERS) --companies=$(COMPANIES) --transactions=$(TRANSACTIONS)

# Initialize the database with test data
init-db:
	@echo "Initializing the database with test data..."
	@docker-compose exec backend /app/scripts/init-db.sh
