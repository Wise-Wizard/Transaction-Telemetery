import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.connection import db
from app.utils.init_db import init_database

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """Set up the database with test data before running tests"""
    db.connect()
    init_database()
    yield
    # Clean up the database after tests
    db.execute_query("MATCH (n) DETACH DELETE n")
    db.close()

def test_root():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the User & Transaction Graph API"}

def test_get_all_users():
    """Test getting all users"""
    response = client.get("/api/users")
    assert response.status_code == 200
    assert len(response.json()) == 5  # We created 5 test users

def test_get_all_transactions():
    """Test getting all transactions"""
    response = client.get("/api/transactions")
    assert response.status_code == 200
    assert len(response.json()) == 5  # We created 5 test transactions

def test_get_user_relationships():
    """Test getting user relationships"""
    response = client.get("/api/relationships/user/user1")
    assert response.status_code == 200
    data = response.json()
    assert "user" in data
    assert "relationships" in data
    assert data["user"]["id"] == "user1"

def test_get_transaction_relationships():
    """Test getting transaction relationships"""
    response = client.get("/api/relationships/transaction/tx1")
    assert response.status_code == 200
    data = response.json()
    assert "transaction" in data
    assert "relationships" in data
    assert data["transaction"]["id"] == "tx1"

def test_create_user():
    """Test creating a new user"""
    new_user = {
        "name": "Test User",
        "email": "test.user@example.com",
        "phone": "+1999999999",
        "address": "999 Test St, City, Country",
        "payment_methods": ["card_test"]
    }
    response = client.post("/api/users", json=new_user)
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "user_id" in data
    assert data["message"] == "User created successfully"

def test_create_transaction():
    """Test creating a new transaction"""
    new_transaction = {
        "sender_id": "user1",
        "receiver_id": "user2",
        "amount": 300.0,
        "currency": "USD",
        "ip_address": "192.168.1.5",
        "device_id": "device_5"
    }
    response = client.post("/api/transactions", json=new_transaction)
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "transaction_id" in data
    assert data["message"] == "Transaction created successfully"
