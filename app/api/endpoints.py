from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from app.models.models import User, Transaction, BusinessRelationship
from app.database.operations import GraphOperations
from app.api.graph_data import GraphDataService
from app.services.analytics import GraphAnalyticsService
from app.utils.generate_data import generate_and_save_data
from typing import List, Dict, Any, Optional

router = APIRouter()

@router.post("/users", response_model=Dict[str, Any])
async def create_user(user: User):
    """
    Create a new user in the graph database
    """
    result = GraphOperations.create_user(user)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to create user")

    # Detect and create relationships after adding a new user
    GraphOperations.detect_and_create_relationships()

    return {"message": "User created successfully", "user_id": user.id}

@router.post("/transactions", response_model=Dict[str, Any])
async def create_transaction(transaction: Transaction):
    """
    Create a new transaction in the graph database
    """
    result = GraphOperations.create_transaction(transaction)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to create transaction")

    # Detect and create relationships after adding a new transaction
    GraphOperations.detect_and_create_relationships()

    return {"message": "Transaction created successfully", "transaction_id": transaction.id}

@router.get("/users", response_model=List[Dict[str, Any]])
async def get_all_users(skip: int = 0, limit: int = 100):
    """
    Get all users from the graph database
    """
    users = GraphOperations.get_all_users(skip=skip, limit=limit)
    return users

@router.get("/transactions", response_model=List[Dict[str, Any]])
async def get_all_transactions(skip: int = 0, limit: int = 100):
    """
    Get all transactions from the graph database
    """
    transactions = GraphOperations.get_all_transactions(skip=skip, limit=limit)
    return transactions

@router.get("/relationships/user/{user_id}", response_model=Dict[str, Any])
async def get_user_relationships(user_id: str):
    """
    Get all relationships of a user
    """
    relationships = GraphOperations.get_user_relationships(user_id)
    if not relationships:
        raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")

    return relationships

@router.get("/relationships/transaction/{transaction_id}", response_model=Dict[str, Any])
async def get_transaction_relationships(transaction_id: str):
    """
    Get all relationships of a transaction
    """
    relationships = GraphOperations.get_transaction_relationships(transaction_id)
    if not relationships:
        raise HTTPException(status_code=404, detail=f"Transaction with ID {transaction_id} not found")

    return relationships

@router.post("/business-relationships", response_model=Dict[str, Any])
async def create_business_relationship(relationship: BusinessRelationship):
    """
    Create a new business relationship between two users
    """
    result = GraphOperations.create_business_relationship(relationship)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to create business relationship")

    return {
        "message": "Business relationship created successfully",
        "source_id": relationship.source_id,
        "target_id": relationship.target_id,
        "relationship_type": relationship.relationship_type
    }

@router.get("/business-relationships/user/{user_id}", response_model=Dict[str, Any])
async def get_business_relationships(user_id: str):
    """
    Get all business relationships of a user
    """
    relationships = GraphOperations.get_business_relationships(user_id)
    if not relationships:
        raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")

    return relationships

@router.post("/detect-relationships", response_model=Dict[str, Any])
async def detect_relationships():
    """
    Detect and create relationships between users and transactions
    """
    GraphOperations.detect_and_create_relationships()
    return {"message": "Relationships detected and created successfully"}

@router.get("/stats", response_model=Dict[str, int])
async def get_stats():
    """
    Get statistics about the graph database (counts of nodes and relationships)
    """
    try:
        # Execute separate queries for robustness
        user_result = db.execute_query("MATCH (u:User) RETURN count(u) as count")
        user_count = user_result[0]["count"] if user_result else 0
        
        tx_result = db.execute_query("MATCH (t:Transaction) RETURN count(t) as count")
        tx_count = tx_result[0]["count"] if tx_result else 0
        
        # Use a more specific match for relationships to ensure it hits the count store if possible
        # or just count all relationships
        rel_result = db.execute_query("MATCH ()-[r]->() RETURN count(r) as count")
        rel_count = rel_result[0]["count"] if rel_result else 0
        
        return {
            "users": user_count,
            "transactions": tx_count,
            "relationships": rel_count
        }
    except Exception as e:
        print(f"Error fetching stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")

@router.get("/graph-data")
async def get_graph_data(limit: int = Query(1000, ge=1, le=10000)):
    """
    Get nodes and edges from the graph database in a format suitable for visualization
    
    Args:
        limit: Maximum number of nodes to return (default: 1000, max: 10000)
    """
    from fastapi.responses import JSONResponse

    # Create a simple function to convert Neo4j DateTime objects to strings
    def convert_neo4j_types(obj):
        from neo4j.time import DateTime
        from datetime import datetime

        if isinstance(obj, DateTime):
            # Convert Neo4j DateTime to string
            return f"{obj.year}-{obj.month:02d}-{obj.day:02d}T{obj.hour:02d}:{obj.minute:02d}:{obj.second:02d}"
        elif isinstance(obj, datetime):
            # Convert Python datetime to string
            return obj.isoformat()
        elif isinstance(obj, dict):
            # Recursively convert dictionary values
            return {key: convert_neo4j_types(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            # Recursively convert list items
            return [convert_neo4j_types(item) for item in obj]
        else:
            # Return other types as is
            return obj

    # Get the data and convert Neo4j types
    data = GraphDataService.get_graph_data(limit=limit)
    converted_data = convert_neo4j_types(data)

    return JSONResponse(content=converted_data)

@router.get("/analytics/shortest-path", response_model=Dict[str, Any])
async def find_shortest_path(
    source_id: str,
    target_id: str,
    relationship_types: Optional[List[str]] = Query(None)
):
    """
    Find the shortest path between two nodes in the graph

    Args:
        source_id: ID of the source node
        target_id: ID of the target node
        relationship_types: Optional list of relationship types to consider

    Returns:
        Dictionary containing the path information
    """
    try:
        result = GraphAnalyticsService.find_shortest_path(source_id, target_id, relationship_types)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding shortest path: {str(e)}")

@router.get("/analytics/transaction-clusters", response_model=List[Dict[str, Any]])
async def cluster_transactions(
    min_cluster_size: int = Query(2, ge=2),
    max_distance: int = Query(2, ge=1, le=5)
):
    """
    Cluster transactions based on their connections

    Args:
        min_cluster_size: Minimum number of transactions in a cluster (default: 2)
        max_distance: Maximum distance between transactions to be considered in the same cluster (default: 2)

    Returns:
        List of transaction clusters
    """
    try:
        result = GraphAnalyticsService.cluster_transactions(min_cluster_size, max_distance)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clustering transactions: {str(e)}")

@router.get("/analytics/graph-metrics", response_model=Dict[str, Any])
async def get_graph_metrics():
    """
    Calculate various metrics for the graph

    Returns:
        Dictionary containing graph metrics
    """
    try:
        result = GraphAnalyticsService.get_graph_metrics()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating graph metrics: {str(e)}")

@router.get("/export/json")
async def export_graph_json():
    """
    Export the graph data as JSON

    Returns:
        JSON file with all graph data
    """
    from fastapi.responses import JSONResponse

    try:
        # Get the data and convert Neo4j types
        data = GraphDataService.get_graph_data()
        converted_data = convert_neo4j_types(data)

        # Add metadata
        converted_data["metadata"] = {
            "exported_at": GraphOperations.get_current_timestamp(),
            "format": "json",
            "version": "1.0"
        }

        return JSONResponse(
            content=converted_data,
            headers={
                "Content-Disposition": "attachment; filename=graph_export.json"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting graph data: {str(e)}")

@router.get("/export/csv")
async def export_graph_csv():
    """
    Export the graph data as CSV files (nodes.csv and edges.csv)

    Returns:
        ZIP file containing nodes.csv and edges.csv
    """
    import io
    import csv
    import zipfile
    from fastapi.responses import StreamingResponse

    try:
        # Get the graph data
        data = GraphDataService.get_graph_data()

        # Create in-memory file-like objects for CSV files
        nodes_buffer = io.StringIO()
        edges_buffer = io.StringIO()

        # Create CSV writers
        nodes_writer = csv.writer(nodes_buffer)
        edges_writer = csv.writer(edges_buffer)

        # Write nodes CSV header
        nodes_writer.writerow(["id", "type", "label", "properties"])

        # Write nodes data
        for node in data["nodes"]:
            node_data = node["data"]
            # Convert properties to a string representation
            properties = ",".join([f"{k}:{v}" for k, v in node_data.items()
                                  if k not in ["id", "type", "label"]])
            nodes_writer.writerow([
                node_data["id"],
                node_data["type"],
                node_data.get("label", ""),
                properties
            ])

        # Write edges CSV header
        edges_writer.writerow(["id", "source", "target", "relationship", "properties"])

        # Write edges data
        for edge in data["edges"]:
            edge_data = edge["data"]
            # Convert properties to a string representation
            properties = ",".join([f"{k}:{v}" for k, v in edge_data.get("properties", {}).items()])
            edges_writer.writerow([
                edge_data["id"],
                edge_data["source"],
                edge_data["target"],
                edge_data["relationship"],
                properties
            ])

        # Create a ZIP file in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            # Add CSV files to the ZIP
            zip_file.writestr("nodes.csv", nodes_buffer.getvalue())
            zip_file.writestr("edges.csv", edges_buffer.getvalue())

        # Reset buffer position
        zip_buffer.seek(0)

        # Return the ZIP file as a streaming response
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={
                "Content-Disposition": "attachment; filename=graph_export.zip"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting graph data as CSV: {str(e)}")

@router.post("/generate-data", response_model=Dict[str, Any])
async def generate_data(
    background_tasks: BackgroundTasks,
    num_users: int = Query(10, ge=1, le=1000),
    num_companies: int = Query(5, ge=1, le=500),
    num_transactions: int = Query(20, ge=1, le=100000),
    detect_relationships: bool = Query(True),
    run_in_background: bool = Query(False)
):
    """
    Generate test data for the graph database

    Args:
        num_users: Number of users to generate (default: 10, max: 1000)
        num_companies: Number of companies to generate (default: 5, max: 500)
        num_transactions: Number of transactions to generate (default: 20, max: 100000)
        detect_relationships: Whether to detect and create relationships (default: True)
        run_in_background: Whether to run the data generation in the background (default: False)

    Returns:
        Message indicating the status of the data generation
    """
    if run_in_background:
        # Run the data generation in the background
        background_tasks.add_task(
            generate_and_save_data,
            num_users=num_users,
            num_companies=num_companies,
            num_transactions=num_transactions,
            detect_relationships=detect_relationships
        )
        return {
            "message": "Data generation started in the background",
            "parameters": {
                "num_users": num_users,
                "num_companies": num_companies,
                "num_transactions": num_transactions,
                "detect_relationships": detect_relationships
            }
        }
    else:
        # Run the data generation synchronously
        try:
            result = generate_and_save_data(
                num_users=num_users,
                num_companies=num_companies,
                num_transactions=num_transactions,
                detect_relationships=detect_relationships
            )
            return {
                "message": "Data generation completed successfully",
                "parameters": {
                    "num_users": num_users,
                    "num_companies": num_companies,
                    "num_transactions": num_transactions,
                    "detect_relationships": detect_relationships
                },
                "counts": {
                    "users": len(result["users"]),
                    "companies": len(result["companies"]),
                    "transactions": len(result["transactions"]),
                    "relationships": len(result["relationships"])
                }
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating data: {str(e)}")
