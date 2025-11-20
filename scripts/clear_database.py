"""
Script to clear all data from the Neo4j database
"""
from app.database.connection import db

def clear_database():
    """Clear all nodes and relationships from the database"""
    print("Connecting to Neo4j database...")
    db.connect()
    
    try:
        print("Clearing all data from the database...")
        # Delete all relationships and nodes
        query = "MATCH (n) DETACH DELETE n"
        db.execute_query(query)
        print("All data has been cleared from the database.")
        
        # Verify that the database is empty
        verify_query = "MATCH (n) RETURN count(n) as node_count"
        result = db.execute_query(verify_query)
        node_count = result[0]["node_count"]
        
        if node_count == 0:
            print("Verification successful: Database is empty.")
        else:
            print(f"Warning: Database still contains {node_count} nodes.")
            
    except Exception as e:
        print(f"Error clearing database: {e}")
    finally:
        db.close()
        print("Database connection closed.")

if __name__ == "__main__":
    clear_database()
