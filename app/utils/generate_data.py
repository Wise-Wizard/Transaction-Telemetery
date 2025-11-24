"""
Data generation script for the User & Transaction Graph Environment.
This script can be used to generate custom test data with various parameters.
"""

from app.database.connection import db
from app.models.models import User, Transaction, BusinessRelationship
from app.database.operations import GraphOperations
import random
import string
import time
from datetime import datetime, timedelta
import argparse
import sys

def generate_random_string(length=10):
    """Generate a random string of fixed length"""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))

def generate_random_email():
    """Generate a random email address"""
    domains = ["example.com", "test.com", "company.org", "business.net"]
    username = generate_random_string(8)
    domain = random.choice(domains)
    return f"{username}@{domain}"

def generate_random_phone():
    """Generate a random phone number"""
    return f"+1{random.randint(1000000000, 9999999999)}"

def generate_random_address():
    """Generate a random address"""
    street_numbers = list(range(100, 1000))
    street_names = ["Main St", "Oak Ave", "Pine Rd", "Maple Ln", "Cedar Blvd"]
    cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]
    states = ["NY", "CA", "IL", "TX", "AZ"]
    
    street_number = random.choice(street_numbers)
    street_name = random.choice(street_names)
    city = random.choice(cities)
    state = random.choice(states)
    
    return f"{street_number} {street_name}, {city}, {state}"

def generate_random_payment_method():
    """Generate a random payment method ID"""
    method_types = ["card", "bank", "wallet", "crypto"]
    method_type = random.choice(method_types)
    method_id = random.randint(1000, 9999)
    return f"{method_type}_{method_id}"

def generate_users(num_users=10):
    """Generate random users"""
    users = []
    
    for i in range(num_users):
        user_id = f"user_{i+1}"
        name = f"User {i+1}"
        email = generate_random_email()
        phone = generate_random_phone()
        address = generate_random_address()
        
        # Generate 1-3 payment methods
        num_payment_methods = random.randint(1, 3)
        payment_methods = [generate_random_payment_method() for _ in range(num_payment_methods)]
        
        user = User(
            id=user_id,
            name=name,
            email=email,
            phone=phone,
            address=address,
            payment_methods=payment_methods,
            entity_type="individual"
        )
        
        users.append(user)
        
    return users

def generate_companies(num_companies=5, users=None):
    """Generate random companies"""
    companies = []
    industries = ["Technology", "Finance", "Healthcare", "Retail", "Manufacturing", "Energy"]
    
    for i in range(num_companies):
        company_id = f"company_{i+1}"
        company_name = f"Company {i+1} Inc"
        email = f"info@company{i+1}.com"
        phone = generate_random_phone()
        address = generate_random_address()
        
        # Random incorporation date between 1-10 years ago
        years_ago = random.randint(1, 10)
        incorporation_date = datetime.now() - timedelta(days=365 * years_ago)
        
        # Assign directors and shareholders if users are provided
        directors = []
        shareholders = []
        
        if users:
            # Assign 1-3 directors
            num_directors = min(len(users), random.randint(1, 3))
            directors = [user.id for user in random.sample(users, num_directors)]
            
            # Assign 1-5 shareholders
            num_shareholders = min(len(users), random.randint(1, 5))
            shareholder_users = random.sample(users, num_shareholders)
            
            total_percentage = 100.0
            for j, user in enumerate(shareholder_users):
                # Last shareholder gets the remaining percentage
                if j == len(shareholder_users) - 1:
                    percentage = total_percentage
                else:
                    # Random percentage between 5% and 50%
                    percentage = min(total_percentage - 5 * (len(shareholder_users) - j - 1), 
                                    random.randint(5, 50))
                    total_percentage -= percentage
                
                shareholders.append({"id": user.id, "percentage": percentage})
        
        company = User(
            id=company_id,
            name=company_name,
            email=email,
            phone=phone,
            address=address,
            entity_type="company",
            company_name=company_name,
            company_id=f"CMP{random.randint(100000, 999999)}",
            tax_id=f"TAX{random.randint(100000, 999999)}",
            incorporation_date=incorporation_date,
            industry=random.choice(industries),
            directors=directors,
            shareholders=shareholders
        )
        
        companies.append(company)
        
    return companies

def generate_transactions(num_transactions=20, users=None, companies=None):
    """Generate random transactions between users and companies"""
    transactions = []
    entities = []
    
    if users:
        entities.extend(users)
    if companies:
        entities.extend(companies)
    
    if not entities:
        return transactions
    
    for i in range(num_transactions):
        # Select random sender and receiver
        sender = random.choice(entities)
        receiver = random.choice(entities)
        
        # Make sure sender and receiver are different
        while sender.id == receiver.id:
            receiver = random.choice(entities)
        
        # Generate random amount between $10 and $10,000
        amount = round(random.uniform(10, 10000), 2)
        
        # Generate random IP address
        ip_parts = [str(random.randint(1, 255)) for _ in range(4)]
        ip_address = ".".join(ip_parts)
        
        # Generate random device ID
        device_id = f"device_{random.randint(1, 10)}"
        
        # Generate random metadata
        purposes = ["payment", "transfer", "investment", "salary", "dividend", "loan", "refund"]
        metadata = {"purpose": random.choice(purposes)}
        
        transaction = Transaction(
            id=f"tx_{i+1}",
            sender_id=sender.id,
            receiver_id=receiver.id,
            amount=amount,
            currency="USD",
            ip_address=ip_address,
            device_id=device_id,
            metadata=metadata
        )
        
        transactions.append(transaction)
        
    return transactions

def generate_business_relationships(users=None, companies=None):
    """Generate business relationships between users and companies"""
    relationships = []
    
    if not users or not companies:
        return relationships
    
    relationship_types = ["LEGAL_ENTITY_OF", "DIRECTOR_OF", "SHAREHOLDER_OF", "COMPOSITE"]
    
    # Generate 5-10 random business relationships
    num_relationships = random.randint(5, 10)
    
    for _ in range(num_relationships):
        user = random.choice(users)
        company = random.choice(companies)
        relationship_type = random.choice(relationship_types)
        
        details = {}
        if relationship_type == "LEGAL_ENTITY_OF":
            positions = ["Founder", "CEO", "CFO", "CTO", "COO"]
            details = {"position": random.choice(positions), "established_date": datetime.now().isoformat()}
        elif relationship_type == "DIRECTOR_OF":
            details = {"position": "Director", "appointed_date": datetime.now().isoformat()}
        elif relationship_type == "SHAREHOLDER_OF":
            details = {"percentage": random.randint(1, 100)}
        elif relationship_type == "COMPOSITE":
            details = {
                "relationship_types": ["SHAREHOLDER_OF", "LEGAL_ENTITY_OF"],
                "description": "Multiple relationship types combined"
            }
        
        relationship = BusinessRelationship(
            source_id=user.id,
            target_id=company.id,
            relationship_type=relationship_type,
            strength=random.uniform(0.1, 1.0),
            details=details
        )
        
        relationships.append(relationship)
        
    return relationships

def create_constraints():
    """Create constraints and indexes in Neo4j"""
    # Create constraint on User.id
    db.execute_query("CREATE CONSTRAINT user_id IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE")
    
    # Create constraint on Transaction.id
    db.execute_query("CREATE CONSTRAINT transaction_id IF NOT EXISTS FOR (t:Transaction) REQUIRE t.id IS UNIQUE")
    
    # Create index on User.email
    db.execute_query("CREATE INDEX user_email IF NOT EXISTS FOR (u:User) ON (u.email)")
    
    # Create index on User.phone
    db.execute_query("CREATE INDEX user_phone IF NOT EXISTS FOR (u:User) ON (u.phone)")
    
    # Create index on Transaction.ip_address
    db.execute_query("CREATE INDEX transaction_ip IF NOT EXISTS FOR (t:Transaction) ON (t.ip_address)")
    
    # Create index on Transaction.device_id
    db.execute_query("CREATE INDEX transaction_device IF NOT EXISTS FOR (t:Transaction) ON (t.device_id)")

def generate_and_save_data(num_users=10, num_companies=5, num_transactions=20, detect_relationships=True):
    """Generate and save data to the database"""
    print("Generating and saving data to the database...")
    
    # Create constraints and indexes
    create_constraints()
    
    # Generate users
    users = generate_users(num_users)
    for user in users:
        GraphOperations.create_user(user)
        print(f"Created user: {user.name} (ID: {user.id})")
    
    # Generate companies
    companies = generate_companies(num_companies, users)
    for company in companies:
        GraphOperations.create_user(company)
        print(f"Created company: {company.name} (ID: {company.id})")
    
    # Generate transactions
    print(f"Generating {num_transactions} transactions...")
    
    # Process transactions in batches to avoid memory issues
    batch_size = 1000
    total_transactions_count = 0
    
    for i in range(0, num_transactions, batch_size):
        current_batch_size = min(batch_size, num_transactions - i)
        print(f"Generating batch {i//batch_size + 1} ({current_batch_size} transactions)...")
        
        batch_transactions = generate_transactions(current_batch_size, users, companies)
        
        # Fix IDs to be unique across batches
        for j, tx in enumerate(batch_transactions):
            tx.id = f"tx_{i + j + 1}"
            
        GraphOperations.create_transactions_bulk(batch_transactions)
        total_transactions_count += len(batch_transactions)
        print(f"Saved batch {i//batch_size + 1}")
        
    # Generate business relationships
    relationships = generate_business_relationships(users, companies)
    for relationship in relationships:
        try:
            GraphOperations.create_business_relationship(relationship)
            print(f"Created business relationship: {relationship.source_id} -{relationship.relationship_type}-> {relationship.target_id}")
        except Exception as e:
            print(f"Error creating relationship: {e}")
    
    # Detect and create relationships
    if detect_relationships:
        print("Detecting and creating additional relationships...")
        GraphOperations.detect_and_create_relationships()
    
    print("Data generation completed!")
    return {
        "users_count": len(users),
        "companies_count": len(companies),
        "transactions_count": total_transactions_count,
        "relationships_count": len(relationships)
    }

def main():
    """Main function to run the script"""
    parser = argparse.ArgumentParser(description='Generate test data for the User & Transaction Graph Environment')
    parser.add_argument('--users', type=int, default=10, help='Number of users to generate (default: 10)')
    parser.add_argument('--companies', type=int, default=5, help='Number of companies to generate (default: 5)')
    parser.add_argument('--transactions', type=int, default=20, help='Number of transactions to generate (default: 20)')
    parser.add_argument('--no-detect', action='store_true', help='Skip relationship detection')
    
    args = parser.parse_args()
    
    # Connect to the database
    db.connect()
    
    try:
        # Generate and save data
        generate_and_save_data(
            num_users=args.users,
            num_companies=args.companies,
            num_transactions=args.transactions,
            detect_relationships=not args.no_detect
        )
    except Exception as e:
        print(f"Error generating data: {e}")
        sys.exit(1)
    finally:
        # Close the database connection
        db.close()

if __name__ == "__main__":
    main()
