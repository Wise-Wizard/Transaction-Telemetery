from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    payment_methods: Optional[List[str]] = None
    # Business-related fields
    entity_type: Optional[str] = None  # "individual", "company", "organization"
    company_name: Optional[str] = None
    company_id: Optional[str] = None
    tax_id: Optional[str] = None
    incorporation_date: Optional[datetime] = None
    industry: Optional[str] = None
    directors: Optional[List[str]] = None  # List of director IDs
    shareholders: Optional[List[Dict[str, Any]]] = None  # List of shareholder details with ownership percentage
    parent_entity_id: Optional[str] = None  # ID of parent company/entity
    subsidiaries: Optional[List[str]] = None  # List of subsidiary entity IDs
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "+1234567890",
                "address": "123 Main St, City, Country",
                "payment_methods": ["credit_card_1", "bank_account_1"],
                "entity_type": "individual",
                "company_name": "Acme Corp",
                "company_id": "ACM123456",
                "tax_id": "TAX123456",
                "industry": "Technology",
                "directors": ["user_id_2", "user_id_3"],
                "shareholders": [
                    {"id": "user_id_4", "percentage": 25.5},
                    {"id": "user_id_5", "percentage": 30.0}
                ],
                "parent_entity_id": "user_id_6",
                "subsidiaries": ["user_id_7", "user_id_8"]
            }
        }

class Transaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    sender_id: str
    receiver_id: str
    amount: float
    currency: str = "USD"
    timestamp: datetime = Field(default_factory=datetime.now)
    ip_address: Optional[str] = None
    device_id: Optional[str] = None
    status: str = "completed"
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "sender_id": "user_id_1",
                "receiver_id": "user_id_2",
                "amount": 100.50,
                "currency": "USD",
                "ip_address": "192.168.1.1",
                "device_id": "device_123",
                "status": "completed",
                "metadata": {"purpose": "payment for services"}
            }
        }

class UserRelationship(BaseModel):
    source_id: str
    target_id: str
    relationship_type: str
    attributes: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "source_id": "user_id_1",
                "target_id": "user_id_2",
                "relationship_type": "SHARED_EMAIL",
                "attributes": {"email": "shared@example.com"}
            }
        }

class BusinessRelationship(BaseModel):
    source_id: str
    target_id: str
    relationship_type: str  # PARENT_OF, SUBSIDIARY_OF, DIRECTOR_OF, SHAREHOLDER_OF, LEGAL_ENTITY_OF, COMPOSITE
    strength: Optional[float] = None  # For composite relationships, indicates the strength of the connection
    details: Optional[Dict[str, Any]] = None  # Additional details about the relationship
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_schema_extra = {
            "example": {
                "source_id": "user_id_1",
                "target_id": "user_id_2",
                "relationship_type": "DIRECTOR_OF",
                "details": {"position": "CEO", "appointed_date": "2022-01-01"}
            }
        }
