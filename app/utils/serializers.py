from datetime import datetime
from neo4j.time import DateTime
from neo4j.graph import Node, Relationship
from typing import Any, Dict, List, Union

def serialize_neo4j_object(obj: Any) -> Any:
    """
    Recursively convert Neo4j objects to Python native types
    """
    if isinstance(obj, DateTime):
        # Convert Neo4j DateTime to Python datetime
        return datetime(
            year=obj.year,
            month=obj.month,
            day=obj.day,
            hour=obj.hour,
            minute=obj.minute,
            second=obj.second,
            microsecond=obj.nanosecond // 1000
        )
    elif isinstance(obj, Node):
        # Convert Neo4j Node to dictionary
        result = dict(obj)
        # Convert any Neo4j types in the node properties
        for key, value in result.items():
            result[key] = serialize_neo4j_object(value)
        return result
    elif isinstance(obj, Relationship):
        # Convert Neo4j Relationship to dictionary
        result = {
            "type": obj.type,
            "properties": dict(obj)
        }
        # Convert any Neo4j types in the relationship properties
        for key, value in result["properties"].items():
            result["properties"][key] = serialize_neo4j_object(value)
        return result
    elif isinstance(obj, dict):
        # Recursively convert dictionary values
        return {key: serialize_neo4j_object(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        # Recursively convert list items
        return [serialize_neo4j_object(item) for item in obj]
    elif hasattr(obj, "__dict__"):
        # For other objects with __dict__
        result = {}
        for key, value in obj.__dict__.items():
            # Skip private attributes
            if not key.startswith("_"):
                result[key] = serialize_neo4j_object(value)
        return result
    else:
        # Return other types as is
        return obj
