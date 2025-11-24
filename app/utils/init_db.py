from app.database.connection import db
from app.utils.generate_data import generate_and_save_data

def init_database():
    """Initialize the database with test data"""
    print("Initializing database with test data...")
    
    # Generate 100k transactions as requested
    # We use 1000 users and 50 companies to create a realistic graph
    result = generate_and_save_data(
        num_users=1000,
        num_companies=50,
        num_transactions=100000,
        detect_relationships=True
    )

    print("Database initialization completed!")
    return result

if __name__ == "__main__":
    # Connect to the database
    db.connect()

    try:
        # Initialize the database
        init_database()
    finally:
        # Close the database connection
        db.close()
