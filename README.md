# User & Transaction Graph Environment

A comprehensive system to visualize relationships between users, companies, and transactions using graph database technology (Neo4j). This tool helps identify connections and patterns in financial transactions and business relationships, capable of handling large datasets (100,000+ transactions).

## Features

- **Scalable Graph Database**: Neo4j integration supporting 100,000+ transactions.
- **Interactive Visualization**: Dynamic, web-based graph visualization using Cytoscape.js with performance optimizations.
- **Bulk Data Generation**: Efficiently generate large datasets for testing scalability.
- **API Pagination**: Optimized API endpoints with pagination for users and transactions.
- **Rich Relationship Detection**: Automatically detects shared attributes (email, phone, address) and transaction links.
- **Business Logic**: Models complex business relationships (Parent-Child, Director, Shareholder).
- **Analytics**: Shortest path finding, transaction clustering, and graph metrics.
- **Export**: Export data to JSON, CSV, or image.

## Quick Start

The easiest way to get started is to use Docker Compose:

```bash
# Start the application
./start.sh
```

This will start the Neo4j database, backend API, and frontend visualization server.
*Note: The first startup might take a minute to initialize the database.*

### Access Points

- **Frontend**: [http://localhost:5001](http://localhost:5001)
- **Backend API**: [http://localhost:8000](http://localhost:8000)
- **Neo4j Browser**: [http://localhost:7474](http://localhost:7474) (credentials: `neo4j`/`password`)

## Data Generation (Scalability Testing)

To generate a large dataset (e.g., 100,000 transactions), use the API:

```bash
curl -X POST "http://localhost:8000/api/generate-data?num_users=1000&num_companies=500&num_transactions=100000&run_in_background=true"
```

*Note: Generating 100k transactions runs in the background and may take a few minutes.*

## API Documentation

Full API documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs).

### Key Endpoints

- **Data Generation**: `POST /api/generate-data`
- **Users**: `GET /api/users?skip=0&limit=100`
- **Transactions**: `GET /api/transactions?skip=0&limit=100`
- **Graph Data**: `GET /api/graph-data?limit=1000` (Visualization data)
- **Analytics**: `GET /api/analytics/shortest-path`, `GET /api/analytics/transaction-clusters`

## Project Structure

- `app/`: Backend FastAPI application
  - `api/`: API endpoints
  - `database/`: Neo4j database operations
  - `models/`: Pydantic models
  - `utils/`: Helper scripts (data generation, serialization)
- `frontend/`: Flask frontend application
- `static/`: Static assets (JS, CSS)
- `scripts/`: Helper scripts for Docker and database management
- `docker-compose.yml`: Docker Compose configuration

## Requirements

- Docker & Docker Compose
- Python 3.11+ (if running locally without Docker)

