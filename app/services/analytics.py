from app.database.connection import db
from typing import List, Dict, Any, Optional
from app.utils.serializers import serialize_neo4j_object

class GraphAnalyticsService:
    """Service for performing graph analytics operations"""

    @staticmethod
    def find_shortest_path(source_id: str, target_id: str, relationship_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Find the shortest path between two nodes in the graph
        
        Args:
            source_id: ID of the source node
            target_id: ID of the target node
            relationship_types: Optional list of relationship types to consider
                                If None, all relationship types are considered
        
        Returns:
            Dictionary containing the path information
        """
        # Build the relationship type filter if provided
        rel_filter = ""
        if relationship_types:
            rel_types = "|".join([f"`{rel}`" for rel in relationship_types])
            rel_filter = f"[:{rel_types}]"
        
        # Query to find the shortest path
        query = f"""
        MATCH (source {{id: $source_id}}), (target {{id: $target_id}}),
              p = shortestPath((source)-[{rel_filter}*]-(target))
        RETURN p, length(p) as path_length
        """
        
        parameters = {
            "source_id": source_id,
            "target_id": target_id
        }
        
        result = db.execute_query(query, parameters)
        
        if not result:
            return {
                "found": False,
                "message": f"No path found between {source_id} and {target_id}"
            }
        
        # Extract path information
        path = result[0]["p"]
        path_length = result[0]["path_length"]
        
        # Format the path for the response
        nodes = []
        relationships = []
        
        # Extract nodes from the path
        for node in path.nodes:
            nodes.append(serialize_neo4j_object(node))
        
        # Extract relationships from the path
        for rel in path.relationships:
            relationships.append({
                "type": rel.type,
                "source_id": rel.start_node["id"],
                "target_id": rel.end_node["id"],
                "properties": serialize_neo4j_object(rel)
            })
        
        return {
            "found": True,
            "path_length": path_length,
            "nodes": nodes,
            "relationships": relationships
        }
    
    @staticmethod
    def cluster_transactions(min_cluster_size: int = 2, max_distance: int = 2) -> List[Dict[str, Any]]:
        """
        Cluster transactions based on their connections
        
        Args:
            min_cluster_size: Minimum number of transactions in a cluster
            max_distance: Maximum distance between transactions to be considered in the same cluster
        
        Returns:
            List of transaction clusters
        """
        # Query to find transaction clusters
        query = f"""
        MATCH (t1:Transaction)
        CALL {{
            WITH t1
            MATCH (t1)-[*1..{max_distance}]-(t2:Transaction)
            WHERE t1.id <> t2.id
            RETURN t2
        }}
        WITH t1, collect(DISTINCT t2) AS connected_transactions
        WHERE size(connected_transactions) >= {min_cluster_size - 1}
        RETURN t1, connected_transactions
        """
        
        result = db.execute_query(query)
        
        # Process results to form clusters
        clusters = []
        processed_transactions = set()
        
        for record in result:
            t1 = record["t1"]
            t1_id = t1["id"]
            
            # Skip if this transaction is already in a cluster
            if t1_id in processed_transactions:
                continue
            
            # Create a new cluster
            cluster = {
                "center_transaction": serialize_neo4j_object(t1),
                "transactions": [serialize_neo4j_object(t1)],
                "size": 1 + len(record["connected_transactions"])
            }
            
            # Add connected transactions to the cluster
            for t2 in record["connected_transactions"]:
                t2_id = t2["id"]
                cluster["transactions"].append(serialize_neo4j_object(t2))
                processed_transactions.add(t2_id)
            
            # Add the center transaction to processed set
            processed_transactions.add(t1_id)
            
            # Add cluster to results
            clusters.append(cluster)
        
        return clusters
    
    @staticmethod
    def get_graph_metrics() -> Dict[str, Any]:
        """
        Calculate various metrics for the graph
        
        Returns:
            Dictionary containing graph metrics
        """
        # Query to get basic graph metrics
        query = """
        MATCH (n)
        OPTIONAL MATCH (u:User)
        OPTIONAL MATCH (t:Transaction)
        OPTIONAL MATCH (c:User {entity_type: 'company'})
        OPTIONAL MATCH ()-[r]-()
        RETURN 
            count(DISTINCT n) AS total_nodes,
            count(DISTINCT u) AS user_count,
            count(DISTINCT t) AS transaction_count,
            count(DISTINCT c) AS company_count,
            count(DISTINCT r) AS relationship_count
        """
        
        basic_metrics = db.execute_query(query)[0]
        
        # Query to get relationship type counts
        rel_query = """
        MATCH ()-[r]-()
        RETURN type(r) AS relationship_type, count(r) AS count
        ORDER BY count DESC
        """
        
        rel_counts = db.execute_query(rel_query)
        relationship_counts = {record["relationship_type"]: record["count"] for record in rel_counts}
        
        # Query to find most connected nodes
        connected_query = """
        MATCH (n)
        OPTIONAL MATCH (n)-[r]-()
        WITH n, count(r) AS connection_count
        ORDER BY connection_count DESC
        LIMIT 5
        RETURN n.id AS node_id, n.name AS node_name, labels(n) AS node_type, connection_count
        """
        
        connected_nodes = db.execute_query(connected_query)
        most_connected = [
            {
                "id": record["node_id"],
                "name": record.get("node_name", record["node_id"]),
                "type": record["node_type"][0] if record["node_type"] else "Unknown",
                "connection_count": record["connection_count"]
            }
            for record in connected_nodes
        ]
        
        return {
            "total_nodes": basic_metrics["total_nodes"],
            "user_count": basic_metrics["user_count"],
            "transaction_count": basic_metrics["transaction_count"],
            "company_count": basic_metrics["company_count"],
            "relationship_count": basic_metrics["relationship_count"],
            "relationship_type_counts": relationship_counts,
            "most_connected_nodes": most_connected
        }
