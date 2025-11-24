from app.database.connection import db
from app.utils.generate_data import generate_and_save_data

def init_database():
    """Initialize the database with test data"""
    print("Initializing database with test data...")
    
    # Generate data
    # User requested: 1000 users, 100k transactions
    data = generate_and_save_data(
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
