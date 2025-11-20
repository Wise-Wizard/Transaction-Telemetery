from app.database.connection import db
from app.models.models import User, Transaction, BusinessRelationship
from app.database.operations import GraphOperations
import time
from datetime import datetime, timedelta

def init_database():
    """Initialize the database with test data"""
    print("Initializing database with test data...")

    # Create constraints and indexes
    create_constraints()

    # Create test users
    users = create_test_users()

    # Create test business entities
    business_entities = create_test_business_entities()

    # Create test transactions
    transactions = create_test_transactions(users)

    # Create test business relationships
    business_relationships = create_test_business_relationships()

    # Detect and create relationships
    GraphOperations.detect_and_create_relationships()

    print("Database initialization completed!")
    return {
        "users": users,
        "business_entities": business_entities,
        "transactions": transactions,
        "business_relationships": business_relationships
    }

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

def create_test_users():
    """Create test users (individuals)"""
    users = [
        User(
            id="user1",
            name="John Doe",
            email="john.doe@example.com",
            phone="+1234567890",
            address="123 Main St, City, Country",
            payment_methods=["card_1", "bank_1"],
            entity_type="individual"
        ),
        User(
            id="user2",
            name="Jane Smith",
            email="jane.smith@example.com",
            phone="+1987654321",
            address="456 Oak St, City, Country",
            payment_methods=["card_2", "bank_2"],
            entity_type="individual"
        ),
        User(
            id="user3",
            name="Bob Johnson",
            email="bob.johnson@example.com",
            phone="+1234567890",  # Same phone as John Doe
            address="789 Pine St, City, Country",
            payment_methods=["card_3", "bank_1"],  # Shared payment method with John Doe
            entity_type="individual"
        ),
        User(
            id="user4",
            name="Alice Brown",
            email="alice.brown@example.com",
            phone="+1555555555",
            address="123 Main St, City, Country",  # Same address as John Doe
            payment_methods=["card_4"],
            entity_type="individual"
        ),
        User(
            id="user5",
            name="Charlie Davis",
            email="charlie.davis@example.com",
            phone="+1777777777",
            address="101 Maple St, City, Country",
            payment_methods=["card_5", "bank_3"],
            entity_type="individual"
        )
    ]

    created_users = []
    for user in users:
        GraphOperations.create_user(user)
        created_users.append(user)
        print(f"Created user: {user.name} (ID: {user.id})")

    return created_users

def create_test_business_entities():
    """Create test business entities (companies)"""
    one_year_ago = datetime.now() - timedelta(days=365)
    two_years_ago = datetime.now() - timedelta(days=730)
    five_years_ago = datetime.now() - timedelta(days=1825)

    business_entities = [
        User(
            id="company1",
            name="Acme Corporation",
            email="info@acme.com",
            phone="+18001234567",
            address="100 Corporate Blvd, Business City, Country",
            entity_type="company",
            company_name="Acme Corporation",
            company_id="ACM123456",
            tax_id="TAX123456",
            incorporation_date=five_years_ago,
            industry="Technology",
            directors=["user1", "user2"],  # John Doe and Jane Smith are directors
            shareholders=[
                {"id": "user3", "percentage": 25.0},  # Bob Johnson owns 25%
                {"id": "user4", "percentage": 15.0}   # Alice Brown owns 15%
            ]
        ),
        User(
            id="company2",
            name="TechStart Inc",
            email="info@techstart.com",
            phone="+18009876543",
            address="200 Innovation Way, Tech Valley, Country",
            entity_type="company",
            company_name="TechStart Inc",
            company_id="TSI789012",
            tax_id="TAX789012",
            incorporation_date=two_years_ago,
            industry="Software",
            directors=["user2"],  # Jane Smith is a director
            shareholders=[
                {"id": "user1", "percentage": 30.0},  # John Doe owns 30%
                {"id": "company1", "percentage": 40.0}  # Acme Corporation owns 40%
            ],
            parent_entity_id="company1"  # Subsidiary of Acme Corporation
        ),
        User(
            id="company3",
            name="Global Logistics Ltd",
            email="info@globallogistics.com",
            phone="+18005551234",
            address="300 Shipping Lane, Port City, Country",
            entity_type="company",
            company_name="Global Logistics Ltd",
            company_id="GLL345678",
            tax_id="TAX345678",
            incorporation_date=one_year_ago,
            industry="Logistics",
            directors=["user5", "user3"],  # Charlie Davis and Bob Johnson are directors
            shareholders=[
                {"id": "user5", "percentage": 60.0}  # Charlie Davis owns 60%
            ]
        )
    ]

    created_entities = []
    for entity in business_entities:
        GraphOperations.create_user(entity)
        created_entities.append(entity)
        print(f"Created business entity: {entity.name} (ID: {entity.id})")

    return created_entities

def create_test_transactions(_):
    """Create test transactions between users and companies"""
    transactions = [
        # Transactions between individuals
        Transaction(
            id="tx1",
            sender_id="user1",
            receiver_id="user2",
            amount=100.0,
            currency="USD",
            ip_address="192.168.1.1",
            device_id="device_1"
        ),
        Transaction(
            id="tx2",
            sender_id="user2",
            receiver_id="user3",
            amount=50.0,
            currency="USD",
            ip_address="192.168.1.2",
            device_id="device_2"
        ),
        Transaction(
            id="tx3",
            sender_id="user3",
            receiver_id="user4",
            amount=75.0,
            currency="USD",
            ip_address="192.168.1.1",  # Same IP as tx1
            device_id="device_3"
        ),
        Transaction(
            id="tx4",
            sender_id="user4",
            receiver_id="user5",
            amount=200.0,
            currency="USD",
            ip_address="192.168.1.3",
            device_id="device_2"  # Same device as tx2
        ),
        Transaction(
            id="tx5",
            sender_id="user5",
            receiver_id="user1",
            amount=150.0,
            currency="USD",
            ip_address="192.168.1.4",
            device_id="device_4"
        ),
        # Transactions between companies and individuals
        Transaction(
            id="tx6",
            sender_id="company1",
            receiver_id="user1",
            amount=5000.0,
            currency="USD",
            ip_address="192.168.2.1",
            device_id="device_5",
            metadata={"purpose": "salary payment"}
        ),
        Transaction(
            id="tx7",
            sender_id="company2",
            receiver_id="user2",
            amount=4500.0,
            currency="USD",
            ip_address="192.168.2.2",
            device_id="device_6",
            metadata={"purpose": "salary payment"}
        ),
        Transaction(
            id="tx8",
            sender_id="user3",
            receiver_id="company3",
            amount=10000.0,
            currency="USD",
            ip_address="192.168.2.3",
            device_id="device_7",
            metadata={"purpose": "investment"}
        ),
        # Transactions between companies
        Transaction(
            id="tx9",
            sender_id="company1",
            receiver_id="company2",
            amount=50000.0,
            currency="USD",
            ip_address="192.168.3.1",
            device_id="device_8",
            metadata={"purpose": "capital investment"}
        ),
        Transaction(
            id="tx10",
            sender_id="company2",
            receiver_id="company3",
            amount=25000.0,
            currency="USD",
            ip_address="192.168.3.2",
            device_id="device_9",
            metadata={"purpose": "service payment"}
        )
    ]

    created_transactions = []
    for transaction in transactions:
        GraphOperations.create_transaction(transaction)
        created_transactions.append(transaction)
        print(f"Created transaction: {transaction.id} (Amount: {transaction.amount} {transaction.currency})")

    return created_transactions

def create_test_business_relationships():
    """Create explicit business relationships beyond what's automatically detected"""
    business_relationships = [
        # Legal entity relationship
        BusinessRelationship(
            source_id="user1",
            target_id="company1",
            relationship_type="LEGAL_ENTITY_OF",
            details={"position": "Founder", "established_date": datetime.now().isoformat()}
        ),
        # Additional director relationship
        BusinessRelationship(
            source_id="user5",
            target_id="company2",
            relationship_type="DIRECTOR_OF",
            details={"position": "Advisory Director", "appointed_date": datetime.now().isoformat()}
        ),
        # Composite relationship with high strength
        BusinessRelationship(
            source_id="user1",
            target_id="company2",
            relationship_type="COMPOSITE",
            strength=0.9,
            details={
                "relationship_types": ["SHAREHOLDER_OF", "LEGAL_ENTITY_OF", "DIRECTOR_OF"],
                "description": "Founder, major shareholder, and key decision maker"
            }
        )
    ]

    created_relationships = []
    for relationship in business_relationships:
        try:
            GraphOperations.create_business_relationship(relationship)
            created_relationships.append(relationship)
            print(f"Created business relationship: {relationship.source_id} -{relationship.relationship_type}-> {relationship.target_id}")
        except Exception as e:
            print(f"Error creating relationship: {e}")

    return created_relationships

if __name__ == "__main__":
    # Connect to the database
    db.connect()

    try:
        # Initialize the database
        init_database()
    finally:
        # Close the database connection
        db.close()
