"""
Script to load sample data into the Neo4j database
"""
from app.database.connection import db
from app.models.models import User, Transaction, BusinessRelationship
from app.database.operations import GraphOperations
from datetime import datetime, timedelta
import uuid

def load_sample_data():
    """Load sample data into the database"""
    print("Connecting to Neo4j database...")
    db.connect()
    
    try:
        print("Loading sample data into the database...")
        
        # Create sample users (individuals)
        individuals = create_individuals()
        
        # Create sample companies
        companies = create_companies()
        
        # Create sample transactions
        transactions = create_transactions(individuals, companies)
        
        # Create business relationships
        business_relationships = create_business_relationships(individuals, companies)
        
        # Detect and create automatic relationships
        print("Detecting and creating automatic relationships...")
        GraphOperations.detect_and_create_relationships()
        
        print("Sample data has been loaded successfully.")
        
        # Print summary
        print("\nSummary:")
        print(f"- {len(individuals)} individuals created")
        print(f"- {len(companies)} companies created")
        print(f"- {len(transactions)} transactions created")
        print(f"- {len(business_relationships)} business relationships created")
        
    except Exception as e:
        print(f"Error loading sample data: {e}")
    finally:
        db.close()
        print("Database connection closed.")

def create_individuals():
    """Create sample individual users"""
    print("Creating individual users...")
    
    individuals = [
        User(
            id="user1",
            name="John Smith",
            email="john.smith@example.com",
            phone="+1-555-123-4567",
            address="123 Main St, New York, NY 10001",
            payment_methods=["visa_1234", "paypal_john"],
            entity_type="individual"
        ),
        User(
            id="user2",
            name="Emily Johnson",
            email="emily.johnson@example.com",
            phone="+1-555-234-5678",
            address="456 Park Ave, New York, NY 10022",
            payment_methods=["mastercard_5678", "venmo_emily"],
            entity_type="individual"
        ),
        User(
            id="user3",
            name="Michael Williams",
            email="michael.williams@example.com",
            phone="+1-555-345-6789",
            address="789 Broadway, New York, NY 10003",
            payment_methods=["amex_9012", "paypal_michael"],
            entity_type="individual"
        ),
        User(
            id="user4",
            name="Sarah Brown",
            email="sarah.brown@example.com",
            phone="+1-555-456-7890",
            address="321 5th Ave, New York, NY 10016",
            payment_methods=["visa_3456", "venmo_sarah"],
            entity_type="individual"
        ),
        User(
            id="user5",
            name="David Miller",
            email="david.miller@example.com",
            phone="+1-555-567-8901",
            address="654 Madison Ave, New York, NY 10022",
            payment_methods=["mastercard_7890", "paypal_david"],
            entity_type="individual"
        ),
        User(
            id="user6",
            name="Jennifer Davis",
            email="jennifer.davis@example.com",
            phone="+1-555-678-9012",
            address="987 Lexington Ave, New York, NY 10021",
            payment_methods=["amex_1234", "venmo_jennifer"],
            entity_type="individual"
        ),
        User(
            id="user7",
            name="Robert Wilson",
            email="robert.wilson@example.com",
            phone="+1-555-789-0123",
            address="123 Main St, New York, NY 10001",  # Same address as John Smith
            payment_methods=["visa_5678", "paypal_robert"],
            entity_type="individual"
        ),
        User(
            id="user8",
            name="Lisa Moore",
            email="lisa.moore@example.com",
            phone="+1-555-890-1234",
            address="246 Central Park West, New York, NY 10024",
            payment_methods=["mastercard_9012", "venmo_lisa"],
            entity_type="individual"
        ),
        User(
            id="user9",
            name="James Taylor",
            email="james.taylor@example.com",
            phone="+1-555-901-2345",
            address="369 Wall St, New York, NY 10005",
            payment_methods=["amex_3456", "paypal_james"],
            entity_type="individual"
        ),
        User(
            id="user10",
            name="Patricia Anderson",
            email="patricia.anderson@example.com",
            phone="+1-555-012-3456",
            address="482 Broadway, New York, NY 10013",
            payment_methods=["visa_7890", "venmo_patricia"],
            entity_type="individual"
        )
    ]
    
    for user in individuals:
        GraphOperations.create_user(user)
        print(f"Created individual: {user.name} (ID: {user.id})")
    
    return individuals

def create_companies():
    """Create sample company entities"""
    print("Creating company entities...")
    
    # Calculate dates for incorporation
    ten_years_ago = datetime.now() - timedelta(days=3650)
    five_years_ago = datetime.now() - timedelta(days=1825)
    three_years_ago = datetime.now() - timedelta(days=1095)
    two_years_ago = datetime.now() - timedelta(days=730)
    one_year_ago = datetime.now() - timedelta(days=365)
    
    companies = [
        User(
            id="company1",
            name="Global Enterprises Inc.",
            email="info@globalenterprises.com",
            phone="+1-888-123-4567",
            address="1 Corporate Plaza, New York, NY 10004",
            entity_type="company",
            company_name="Global Enterprises Inc.",
            company_id="GEI-12345",
            tax_id="TAX-GEI-12345",
            incorporation_date=ten_years_ago,
            industry="Finance",
            directors=["user1", "user2"],  # John Smith and Emily Johnson are directors
            shareholders=[
                {"id": "user3", "percentage": 15.0},  # Michael Williams owns 15%
                {"id": "user4", "percentage": 10.0}   # Sarah Brown owns 10%
            ]
        ),
        User(
            id="company2",
            name="Tech Innovations LLC",
            email="info@techinnovations.com",
            phone="+1-888-234-5678",
            address="200 Silicon Ave, San Francisco, CA 94107",
            entity_type="company",
            company_name="Tech Innovations LLC",
            company_id="TIL-67890",
            tax_id="TAX-TIL-67890",
            incorporation_date=five_years_ago,
            industry="Technology",
            directors=["user3"],  # Michael Williams is a director
            shareholders=[
                {"id": "user1", "percentage": 20.0},  # John Smith owns 20%
                {"id": "company1", "percentage": 30.0}  # Global Enterprises owns 30%
            ],
            parent_entity_id="company1"  # Subsidiary of Global Enterprises
        ),
        User(
            id="company3",
            name="Green Energy Solutions",
            email="info@greenenergy.com",
            phone="+1-888-345-6789",
            address="300 Eco Blvd, Portland, OR 97201",
            entity_type="company",
            company_name="Green Energy Solutions",
            company_id="GES-24680",
            tax_id="TAX-GES-24680",
            incorporation_date=three_years_ago,
            industry="Energy",
            directors=["user5", "user6"],  # David Miller and Jennifer Davis are directors
            shareholders=[
                {"id": "user7", "percentage": 25.0},  # Robert Wilson owns 25%
                {"id": "user8", "percentage": 25.0}   # Lisa Moore owns 25%
            ]
        ),
        User(
            id="company4",
            name="Healthcare Partners Ltd",
            email="info@healthcarepartners.com",
            phone="+1-888-456-7890",
            address="400 Medical Center Dr, Boston, MA 02115",
            entity_type="company",
            company_name="Healthcare Partners Ltd",
            company_id="HPL-13579",
            tax_id="TAX-HPL-13579",
            incorporation_date=two_years_ago,
            industry="Healthcare",
            directors=["user9"],  # James Taylor is a director
            shareholders=[
                {"id": "user10", "percentage": 15.0},  # Patricia Anderson owns 15%
                {"id": "company3", "percentage": 40.0}  # Green Energy Solutions owns 40%
            ]
        ),
        User(
            id="company5",
            name="Retail Ventures Group",
            email="info@retailventures.com",
            phone="+1-888-567-8901",
            address="500 Shopping Plaza, Chicago, IL 60611",
            entity_type="company",
            company_name="Retail Ventures Group",
            company_id="RVG-97531",
            tax_id="TAX-RVG-97531",
            incorporation_date=one_year_ago,
            industry="Retail",
            directors=["user2", "user4"],  # Emily Johnson and Sarah Brown are directors
            shareholders=[
                {"id": "user6", "percentage": 30.0},  # Jennifer Davis owns 30%
                {"id": "company1", "percentage": 25.0},  # Global Enterprises owns 25%
                {"id": "company2", "percentage": 15.0}   # Tech Innovations owns 15%
            ]
        )
    ]
    
    for company in companies:
        GraphOperations.create_user(company)
        print(f"Created company: {company.name} (ID: {company.id})")
    
    return companies

def create_transactions(individuals, companies):
    """Create sample transactions between users and companies"""
    print("Creating transactions...")
    
    transactions = [
        # Transactions between individuals
        Transaction(
            id="tx1",
            sender_id="user1",
            receiver_id="user2",
            amount=1500.00,
            currency="USD",
            ip_address="192.168.1.1",
            device_id="device_001",
            metadata={"purpose": "Rent payment"}
        ),
        Transaction(
            id="tx2",
            sender_id="user3",
            receiver_id="user4",
            amount=750.50,
            currency="USD",
            ip_address="192.168.1.2",
            device_id="device_002",
            metadata={"purpose": "Shared expenses"}
        ),
        Transaction(
            id="tx3",
            sender_id="user5",
            receiver_id="user6",
            amount=2000.00,
            currency="USD",
            ip_address="192.168.1.3",
            device_id="device_003",
            metadata={"purpose": "Loan repayment"}
        ),
        Transaction(
            id="tx4",
            sender_id="user7",
            receiver_id="user8",
            amount=350.25,
            currency="USD",
            ip_address="192.168.1.1",  # Same IP as tx1
            device_id="device_004",
            metadata={"purpose": "Dinner split"}
        ),
        Transaction(
            id="tx5",
            sender_id="user9",
            receiver_id="user10",
            amount=5000.00,
            currency="USD",
            ip_address="192.168.1.4",
            device_id="device_005",
            metadata={"purpose": "Car purchase"}
        ),
        
        # Transactions between companies and individuals
        Transaction(
            id="tx6",
            sender_id="company1",
            receiver_id="user1",
            amount=8500.00,
            currency="USD",
            ip_address="10.0.0.1",
            device_id="device_corp_001",
            metadata={"purpose": "Salary payment"}
        ),
        Transaction(
            id="tx7",
            sender_id="company2",
            receiver_id="user3",
            amount=7500.00,
            currency="USD",
            ip_address="10.0.0.2",
            device_id="device_corp_002",
            metadata={"purpose": "Consulting fee"}
        ),
        Transaction(
            id="tx8",
            sender_id="user5",
            receiver_id="company3",
            amount=10000.00,
            currency="USD",
            ip_address="10.0.0.3",
            device_id="device_corp_003",
            metadata={"purpose": "Investment"}
        ),
        Transaction(
            id="tx9",
            sender_id="company4",
            receiver_id="user7",
            amount=12000.00,
            currency="USD",
            ip_address="10.0.0.4",
            device_id="device_corp_004",
            metadata={"purpose": "Contract payment"}
        ),
        Transaction(
            id="tx10",
            sender_id="user9",
            receiver_id="company5",
            amount=3500.00,
            currency="USD",
            ip_address="10.0.0.5",
            device_id="device_corp_005",
            metadata={"purpose": "Product purchase"}
        ),
        
        # Transactions between companies
        Transaction(
            id="tx11",
            sender_id="company1",
            receiver_id="company2",
            amount=50000.00,
            currency="USD",
            ip_address="172.16.0.1",
            device_id="device_corp_006",
            metadata={"purpose": "Investment funding"}
        ),
        Transaction(
            id="tx12",
            sender_id="company2",
            receiver_id="company3",
            amount=35000.00,
            currency="USD",
            ip_address="172.16.0.2",
            device_id="device_corp_007",
            metadata={"purpose": "Partnership agreement"}
        ),
        Transaction(
            id="tx13",
            sender_id="company3",
            receiver_id="company4",
            amount=42000.00,
            currency="USD",
            ip_address="172.16.0.3",
            device_id="device_corp_008",
            metadata={"purpose": "Service contract"}
        ),
        Transaction(
            id="tx14",
            sender_id="company4",
            receiver_id="company5",
            amount=28000.00,
            currency="USD",
            ip_address="172.16.0.4",
            device_id="device_corp_009",
            metadata={"purpose": "Supply agreement"}
        ),
        Transaction(
            id="tx15",
            sender_id="company5",
            receiver_id="company1",
            amount=65000.00,
            currency="USD",
            ip_address="172.16.0.5",
            device_id="device_corp_010",
            metadata={"purpose": "Loan repayment"}
        )
    ]
    
    for transaction in transactions:
        GraphOperations.create_transaction(transaction)
        print(f"Created transaction: {transaction.id} (Amount: {transaction.amount} {transaction.currency})")
    
    return transactions

def create_business_relationships(individuals, companies):
    """Create explicit business relationships"""
    print("Creating business relationships...")
    
    business_relationships = [
        # Legal entity relationships
        BusinessRelationship(
            source_id="user1",
            target_id="company1",
            relationship_type="LEGAL_ENTITY_OF",
            details={"position": "Founder", "established_date": datetime.now().isoformat()}
        ),
        BusinessRelationship(
            source_id="user3",
            target_id="company2",
            relationship_type="LEGAL_ENTITY_OF",
            details={"position": "Co-Founder", "established_date": datetime.now().isoformat()}
        ),
        BusinessRelationship(
            source_id="user5",
            target_id="company3",
            relationship_type="LEGAL_ENTITY_OF",
            details={"position": "Founder", "established_date": datetime.now().isoformat()}
        ),
        
        # Additional director relationships
        BusinessRelationship(
            source_id="user7",
            target_id="company4",
            relationship_type="DIRECTOR_OF",
            details={"position": "Non-Executive Director", "appointed_date": datetime.now().isoformat()}
        ),
        BusinessRelationship(
            source_id="user9",
            target_id="company5",
            relationship_type="DIRECTOR_OF",
            details={"position": "Executive Director", "appointed_date": datetime.now().isoformat()}
        ),
        
        # Additional shareholder relationships
        BusinessRelationship(
            source_id="user2",
            target_id="company3",
            relationship_type="SHAREHOLDER_OF",
            strength=0.15,
            details={"percentage": 15.0, "acquisition_date": datetime.now().isoformat()}
        ),
        BusinessRelationship(
            source_id="user4",
            target_id="company4",
            relationship_type="SHAREHOLDER_OF",
            strength=0.20,
            details={"percentage": 20.0, "acquisition_date": datetime.now().isoformat()}
        ),
        
        # Composite relationships
        BusinessRelationship(
            source_id="user1",
            target_id="company2",
            relationship_type="COMPOSITE",
            strength=0.85,
            details={
                "relationship_types": ["SHAREHOLDER_OF", "DIRECTOR_OF"],
                "description": "Major investor and strategic advisor"
            }
        ),
        BusinessRelationship(
            source_id="user5",
            target_id="company5",
            relationship_type="COMPOSITE",
            strength=0.90,
            details={
                "relationship_types": ["SHAREHOLDER_OF", "LEGAL_ENTITY_OF", "DIRECTOR_OF"],
                "description": "Founder, major shareholder, and key decision maker"
            }
        )
    ]
    
    for relationship in business_relationships:
        try:
            GraphOperations.create_business_relationship(relationship)
            print(f"Created business relationship: {relationship.source_id} -{relationship.relationship_type}-> {relationship.target_id}")
        except Exception as e:
            print(f"Error creating relationship: {e}")
    
    return business_relationships

if __name__ == "__main__":
    load_sample_data()
