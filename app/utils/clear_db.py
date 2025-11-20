from app.database.connection import db

def clear_database():
    """Clear all data from the database"""
    print("Clearing all data from the database...")
    
    # Delete all relationships
    db.execute_query("MATCH ()-[r]-() DELETE r")
    print("All relationships deleted.")
    
    # Delete all nodes
    db.execute_query("MATCH (n) DELETE n")
    print("All nodes deleted.")
    
    print("Database cleared successfully!")

if __name__ == "__main__":
    # Connect to the database
    db.connect()
    
    try:
        # Clear the database
        clear_database()
    finally:
        # Close the database connection
        db.close()
