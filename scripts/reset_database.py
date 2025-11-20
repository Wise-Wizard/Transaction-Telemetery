"""
Script to reset the database by clearing all data and loading new sample data
"""
import time
from scripts.clear_database import clear_database
from scripts.load_sample_data import load_sample_data

def reset_database():
    """Reset the database by clearing all data and loading new sample data"""
    print("=== Starting Database Reset Process ===")
    
    # Step 1: Clear the database
    print("\n=== Step 1: Clearing the database ===")
    clear_database()
    
    # Wait a moment to ensure all operations are complete
    print("\nWaiting for database operations to complete...")
    time.sleep(2)
    
    # Step 2: Load sample data
    print("\n=== Step 2: Loading sample data ===")
    load_sample_data()
    
    print("\n=== Database Reset Complete ===")
    print("The database has been reset with new sample data.")

if __name__ == "__main__":
    reset_database()
