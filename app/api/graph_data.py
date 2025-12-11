from app.database.connection import db
from app.utils.serializers import serialize_neo4j_object
from typing import Dict, List, Any
from datetime import datetime

class GraphDataService:
    @staticmethod
    def get_graph_data(limit: int = 1000) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get nodes and edges from the graph database in a format suitable for Cytoscape.js
        """
        # Get nodes (users and transactions) with limit
        nodes = GraphDataService._get_all_nodes(limit)

        # Get edges (relationships) connected to these nodes
        # We need to fetch edges only for the nodes we retrieved to avoid dangling edges
        node_ids = [node["data"]["id"] for node in nodes]
        edges = GraphDataService._get_all_edges(node_ids)

        return {
            "nodes": nodes,
            "edges": edges
        }

    @staticmethod
    def _get_all_nodes(limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Get nodes (users and transactions) from the graph database.
        Prioritizes the latest transactions and their connected users to ensure a connected graph.
        """
        query = """
        MATCH (t:Transaction)
        WITH t ORDER BY t.timestamp DESC LIMIT $limit
        MATCH (sender:User)-[:SENT]->(t)-[:RECEIVED_BY]->(receiver:User)
        WITH collect(t) + collect(sender) + collect(receiver) as nodes
        UNWIND nodes as n
        RETURN DISTINCT n
        """

        result = db.execute_query(query, {"limit": limit})

        nodes = []
        for record in result:
            node = record["n"]
            node_data = serialize_neo4j_object(node)

            # Convert datetime objects to strings
            for key, value in node_data.items():
                if isinstance(value, datetime):
                    node_data[key] = value.isoformat()

            # Create Cytoscape.js node format
            cytoscape_node = {
                "data": {
                    "id": node_data["id"],
                    "type": list(node.labels)[0] if node.labels else "Unknown",  # First label (User or Transaction)
                }
            }

            # Add label based on node type
            if "User" in node.labels:
                cytoscape_node["data"]["label"] = node_data.get("name", "Unknown User")
                # Add user-specific properties
                for key in ["email", "phone", "address", "entity_type", "company_name"]:
                    if key in node_data:
                        cytoscape_node["data"][key] = node_data[key]
            elif "Transaction" in node.labels:
                # Format transaction label
                amount = node_data.get("amount", 0)
                currency = node_data.get("currency", "USD")
                cytoscape_node["data"]["label"] = f"Transaction: {amount} {currency}"

                # Add transaction-specific properties
                for key in ["amount", "currency", "timestamp", "status", "ip_address", "device_id"]:
                    if key in node_data:
                        if key == "timestamp" and isinstance(node_data[key], datetime):
                            cytoscape_node["data"][key] = node_data[key].isoformat()
                        else:
                            cytoscape_node["data"][key] = node_data[key]

            nodes.append(cytoscape_node)

        return nodes

    @staticmethod
    def _get_all_edges(node_ids: List[str] = None) -> List[Dict[str, Any]]:
        """
        Get edges (relationships) from the graph database
        """
        if node_ids:
            query = """
            MATCH (source)-[r]->(target)
            WHERE source.id IN $node_ids AND target.id IN $node_ids
            RETURN source.id AS source_id, target.id AS target_id, type(r) AS relationship_type, properties(r) AS properties
            """
            params = {"node_ids": node_ids}
        else:
            query = """
            MATCH (source)-[r]->(target)
            RETURN source.id AS source_id, target.id AS target_id, type(r) AS relationship_type, properties(r) AS properties
            """
            params = {}

        result = db.execute_query(query, params)

        edges = []
        for record in result:
            # Create Cytoscape.js edge format
            edge_id = f"{record['source_id']}-{record['relationship_type']}-{record['target_id']}"

            # Process properties to handle datetime objects
            properties = record["properties"]
            for key, value in properties.items():
                if isinstance(value, datetime):
                    properties[key] = value.isoformat()

            cytoscape_edge = {
                "data": {
                    "id": edge_id,
                    "source": record["source_id"],
                    "target": record["target_id"],
                    "relationship": record["relationship_type"],
                    "label": record["relationship_type"].replace("_", " "),
                    "properties": properties
                }
            }

            edges.append(cytoscape_edge)


        return edges

    @staticmethod
    def get_user_graph_data(user_ids: List[str], depth: int = 1) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get graph data for specific users and their related transactions/relationships
        
        Args:
            user_ids: List of user IDs to fetch data for
            depth: Relationship depth (currently supports depth=1)
        
        Returns:
            Dictionary with 'nodes' and 'edges' arrays in Cytoscape format
        """
        if not user_ids:
            return {"nodes": [], "edges": []}
        
        # Get user nodes and their transactions
        nodes = GraphDataService._get_user_nodes(user_ids)
        
        # Get edges for these nodes
        node_ids = [node["data"]["id"] for node in nodes]
        edges = GraphDataService._get_all_edges(node_ids)
        
        return {
            "nodes": nodes,
            "edges": edges
        }
    
    @staticmethod
    def _get_user_nodes(user_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get specific users and their related transactions
        """
        query = """
        // Get selected users
        MATCH (u:User)
        WHERE u.id IN $user_ids
        
        // Get transactions where selected users are involved
        OPTIONAL MATCH (sender:User)-[:SENT]->(t:Transaction)-[:RECEIVED_BY]->(receiver:User)
        WHERE sender.id IN $user_ids OR receiver.id IN $user_ids
        
        // Return all distinct nodes
        WITH u, t, sender, receiver
        UNWIND [u, t, sender, receiver] as node
        WITH DISTINCT node
        WHERE node IS NOT NULL
        RETURN node as n
        """
        
        result = db.execute_query(query, {"user_ids": user_ids})
        
        nodes = []
        for record in result:
            node = record["n"]
            node_data = serialize_neo4j_object(node)
            
            # Convert datetime objects to strings
            for key, value in node_data.items():
                if isinstance(value, datetime):
                    node_data[key] = value.isoformat()
            
            # Create Cytoscape.js node format
            cytoscape_node = {
                "data": {
                    "id": node_data["id"],
                    "type": list(node.labels)[0] if node.labels else "Unknown",
                }
            }
            
            # Add label based on node type
            if "User" in node.labels:
                cytoscape_node["data"]["label"] = node_data.get("name", "Unknown User")
                # Add user-specific properties
                for key in ["email", "phone", "address", "entity_type", "company_name"]:
                    if key in node_data:
                        cytoscape_node["data"][key] = node_data[key]
            elif "Transaction" in node.labels:
                # Format transaction label
                amount = node_data.get("amount", 0)
                currency = node_data.get("currency", "USD")
                cytoscape_node["data"]["label"] = f"Transaction: {amount} {currency}"
                
                # Add transaction-specific properties
                for key in ["amount", "currency", "timestamp", "status", "ip_address", "device_id"]:
                    if key in node_data:
                        if key == "timestamp" and isinstance(node_data[key], datetime):
                            cytoscape_node["data"][key] = node_data[key].isoformat()
                        else:
                            cytoscape_node["data"][key] = node_data[key]
            
            nodes.append(cytoscape_node)
        
        return nodes
