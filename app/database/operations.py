from app.database.connection import db
from app.models.models import User, Transaction, BusinessRelationship
from app.utils.serializers import serialize_neo4j_object
from typing import List, Dict, Any, Optional
from datetime import datetime

class GraphOperations:
    @staticmethod
    def create_user(user: User) -> Dict[str, Any]:
        """Create a user node in the graph database"""
        query = """
        MERGE (u:User {id: $id})
        SET u += {
            name: $name,
            email: $email,
            phone: $phone,
            address: $address,
            payment_methods: $payment_methods,
            entity_type: $entity_type,
            company_name: $company_name,
            company_id: $company_id,
            tax_id: $tax_id,
            incorporation_date: CASE WHEN $incorporation_date IS NOT NULL THEN datetime($incorporation_date) ELSE null END,
            industry: $industry,
            directors: $directors,
            shareholders: $shareholders,
            parent_entity_id: $parent_entity_id,
            subsidiaries: $subsidiaries,
            created_at: datetime($created_at),
            updated_at: datetime($updated_at)
        }
        RETURN u
        """

        # Convert incorporation_date to ISO format if it exists
        incorporation_date_iso = user.incorporation_date.isoformat() if user.incorporation_date else None

        parameters = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "address": user.address,
            "payment_methods": user.payment_methods,
            "entity_type": user.entity_type,
            "company_name": user.company_name,
            "company_id": user.company_id,
            "tax_id": user.tax_id,
            "incorporation_date": incorporation_date_iso,
            "industry": user.industry,
            "directors": user.directors,
            "shareholders": str(user.shareholders) if user.shareholders else None,
            "parent_entity_id": user.parent_entity_id,
            "subsidiaries": user.subsidiaries,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat()
        }

        result = db.execute_query(query, parameters)
        return result[0]["u"] if result else None

    @staticmethod
    def create_transaction(transaction: Transaction) -> Dict[str, Any]:
        """Create a transaction node in the graph database"""
        query = """
        MATCH (sender:User {id: $sender_id})
        MATCH (receiver:User {id: $receiver_id})
        MERGE (t:Transaction {id: $id})
        SET t += {
            amount: $amount,
            currency: $currency,
            timestamp: datetime($timestamp),
            ip_address: $ip_address,
            device_id: $device_id,
            status: $status,
            metadata: $metadata
        }
        MERGE (sender)-[:SENT]->(t)
        MERGE (t)-[:RECEIVED_BY]->(receiver)
        RETURN t
        """

        parameters = {
            "id": transaction.id,
            "sender_id": transaction.sender_id,
            "receiver_id": transaction.receiver_id,
            "amount": transaction.amount,
            "currency": transaction.currency,
            "timestamp": transaction.timestamp.isoformat(),
            "ip_address": transaction.ip_address,
            "device_id": transaction.device_id,
            "status": transaction.status,
            "metadata": str(transaction.metadata) if transaction.metadata else None
        }

        result = db.execute_query(query, parameters)
        return result[0]["t"] if result else None

    @staticmethod
    def create_transactions_bulk(transactions: List[Transaction]) -> int:
        """Create multiple transaction nodes in the graph database efficiently"""
        if not transactions:
            return 0
            
        query = """
        UNWIND $transactions AS tx
        MATCH (sender:User {id: tx.sender_id})
        MATCH (receiver:User {id: tx.receiver_id})
        MERGE (t:Transaction {id: tx.id})
        SET t += {
            amount: tx.amount,
            currency: tx.currency,
            timestamp: datetime(tx.timestamp),
            ip_address: tx.ip_address,
            device_id: tx.device_id,
            status: tx.status,
            metadata: tx.metadata
        }
        MERGE (sender)-[:SENT]->(t)
        MERGE (t)-[:RECEIVED_BY]->(receiver)
        """
        
        # Prepare list of dictionaries for UNWIND
        tx_data = []
        for tx in transactions:
            tx_data.append({
                "id": tx.id,
                "sender_id": tx.sender_id,
                "receiver_id": tx.receiver_id,
                "amount": tx.amount,
                "currency": tx.currency,
                "timestamp": tx.timestamp.isoformat(),
                "ip_address": tx.ip_address,
                "device_id": tx.device_id,
                "status": tx.status,
                "metadata": str(tx.metadata) if tx.metadata else None
            })
            
        db.execute_query(query, {"transactions": tx_data})
        return len(transactions)

    @staticmethod
    def get_all_users(skip: int = 0, limit: int = 100, search_query: str = None) -> List[Dict[str, Any]]:
        """Get all users from the graph database with pagination and optional search"""
        if search_query:
            query = """
            MATCH (u:User) 
            WHERE toLower(u.name) CONTAINS toLower($search) OR toLower(u.id) CONTAINS toLower($search)
            RETURN u SKIP $skip LIMIT $limit
            """
            parameters = {"skip": skip, "limit": limit, "search": search_query}
        else:
            query = "MATCH (u:User) RETURN u SKIP $skip LIMIT $limit"
            parameters = {"skip": skip, "limit": limit}
            
        result = db.execute_query(query, parameters)
        return [serialize_neo4j_object(record["u"]) for record in result]

    @staticmethod
    def get_all_transactions(skip: int = 0, limit: int = 100, search_query: str = None) -> List[Dict[str, Any]]:
        """Get all transactions from the graph database with pagination and optional search"""
        if search_query:
            query = """
            MATCH (t:Transaction) 
            WHERE toLower(t.id) CONTAINS toLower($search)
            RETURN t SKIP $skip LIMIT $limit
            """
            parameters = {"skip": skip, "limit": limit, "search": search_query}
        else:
            query = "MATCH (t:Transaction) RETURN t SKIP $skip LIMIT $limit"
            parameters = {"skip": skip, "limit": limit}
            
        result = db.execute_query(query, parameters)
        return [serialize_neo4j_object(record["t"]) for record in result]

    @staticmethod
    def get_user_relationships(user_id: str) -> Dict[str, Any]:
        """Get all relationships of a user"""
        query = """
        MATCH (u:User {id: $user_id})
        OPTIONAL MATCH (u)-[r1]->(n)
        OPTIONAL MATCH (n)-[r2]->(u)
        RETURN u,
               collect(DISTINCT {type: type(r1), node: n, direction: 'outgoing'}) AS outgoing,
               collect(DISTINCT {type: type(r2), node: n, direction: 'incoming'}) AS incoming
        """

        parameters = {"user_id": user_id}
        result = db.execute_query(query, parameters)

        if not result:
            return None

        record = result[0]
        return serialize_neo4j_object({
            "user": record["u"],
            "relationships": {
                "outgoing": record["outgoing"],
                "incoming": record["incoming"]
            }
        })

    @staticmethod
    def get_transaction_relationships(transaction_id: str) -> Dict[str, Any]:
        """Get all relationships of a transaction"""
        query = """
        MATCH (t:Transaction {id: $transaction_id})
        OPTIONAL MATCH (u1)-[r1]->(t)
        OPTIONAL MATCH (t)-[r2]->(u2)
        OPTIONAL MATCH (t)-[r3:LINKED_TO]-(t2:Transaction)
        RETURN t,
               collect(DISTINCT {type: type(r1), node: u1, direction: 'incoming'}) AS incoming_users,
               collect(DISTINCT {type: type(r2), node: u2, direction: 'outgoing'}) AS outgoing_users,
               collect(DISTINCT {type: type(r3), node: t2, direction: 'both'}) AS linked_transactions
        """

        parameters = {"transaction_id": transaction_id}
        result = db.execute_query(query, parameters)

        if not result:
            return None

        record = result[0]
        return serialize_neo4j_object({
            "transaction": record["t"],
            "relationships": {
                "incoming_users": record["incoming_users"],
                "outgoing_users": record["outgoing_users"],
                "linked_transactions": record["linked_transactions"]
            }
        })

    @staticmethod
    def detect_and_create_relationships():
        """Detect and create relationships between users and transactions"""
        # Create relationships based on shared email
        GraphOperations._create_shared_email_relationships()

        # Create relationships based on shared phone
        GraphOperations._create_shared_phone_relationships()

        # Create relationships based on shared address
        GraphOperations._create_shared_address_relationships()

        # Create relationships based on shared payment methods
        GraphOperations._create_shared_payment_method_relationships()

        # Create relationships between transactions with shared IP or device ID
        GraphOperations._create_linked_transaction_relationships()

        # Create business relationships
        GraphOperations._create_parent_child_relationships()
        GraphOperations._create_director_relationships()
        GraphOperations._create_shareholder_relationships()
        GraphOperations._create_composite_relationships()

    @staticmethod
    def _create_shared_email_relationships():
        """Create relationships between users with shared email addresses"""
        query = """
        MATCH (u1:User), (u2:User)
        WHERE u1.email IS NOT NULL AND u1.email = u2.email AND u1.id <> u2.id
        MERGE (u1)-[r:SHARED_EMAIL {email: u1.email}]->(u2)
        RETURN count(r) as relationship_count
        """
        result = db.execute_query(query)
        return result[0]["relationship_count"] if result else 0

    @staticmethod
    def _create_shared_phone_relationships():
        """Create relationships between users with shared phone numbers"""
        query = """
        MATCH (u1:User), (u2:User)
        WHERE u1.phone IS NOT NULL AND u1.phone = u2.phone AND u1.id <> u2.id
        MERGE (u1)-[r:SHARED_PHONE {phone: u1.phone}]->(u2)
        RETURN count(r) as relationship_count
        """
        result = db.execute_query(query)
        return result[0]["relationship_count"] if result else 0

    @staticmethod
    def _create_shared_address_relationships():
        """Create relationships between users with shared addresses"""
        query = """
        MATCH (u1:User), (u2:User)
        WHERE u1.address IS NOT NULL AND u1.address = u2.address AND u1.id <> u2.id
        MERGE (u1)-[r:SHARED_ADDRESS {address: u1.address}]->(u2)
        RETURN count(r) as relationship_count
        """
        result = db.execute_query(query)
        return result[0]["relationship_count"] if result else 0

    @staticmethod
    def _create_shared_payment_method_relationships():
        """Create relationships between users with shared payment methods"""
        query = """
        MATCH (u1:User), (u2:User)
        WHERE u1.id <> u2.id
        AND any(pm IN u1.payment_methods WHERE pm IN u2.payment_methods)
        WITH u1, u2, [pm IN u1.payment_methods WHERE pm IN u2.payment_methods] AS shared_methods
        MERGE (u1)-[r:SHARED_PAYMENT_METHOD {methods: shared_methods}]->(u2)
        RETURN count(r) as relationship_count
        """
        result = db.execute_query(query)
        return result[0]["relationship_count"] if result else 0

    @staticmethod
    def _create_linked_transaction_relationships():
        """Create relationships between transactions with shared IP or device ID"""
        # Link by IP address
        ip_query = """
        MATCH (t1:Transaction), (t2:Transaction)
        WHERE t1.ip_address IS NOT NULL
        AND t1.ip_address = t2.ip_address
        AND t1.id <> t2.id
        MERGE (t1)-[r:LINKED_TO {reason: 'shared_ip', ip_address: t1.ip_address}]-(t2)
        RETURN count(r) as relationship_count
        """
        ip_result = db.execute_query(ip_query)

        # Link by device ID
        device_query = """
        MATCH (t1:Transaction), (t2:Transaction)
        WHERE t1.device_id IS NOT NULL
        AND t1.device_id = t2.device_id
        AND t1.id <> t2.id
        MERGE (t1)-[r:LINKED_TO {reason: 'shared_device', device_id: t1.device_id}]-(t2)
        RETURN count(r) as relationship_count
        """
        device_result = db.execute_query(device_query)

        return {
            "ip_relationships": ip_result[0]["relationship_count"] if ip_result else 0,
            "device_relationships": device_result[0]["relationship_count"] if device_result else 0
        }

    @staticmethod
    def create_business_relationship(relationship: BusinessRelationship) -> Dict[str, Any]:
        """Create a business relationship between two users"""
        # Convert details to a string representation if it exists
        details_str = str(relationship.details) if relationship.details else None

        # Use standard Cypher directly without trying APOC first
        query = f"""
        MATCH (source:User {{id: $source_id}})
        MATCH (target:User {{id: $target_id}})
        CREATE (source)-[r:{relationship.relationship_type} {{
            strength: $strength,
            details_str: $details_str,
            created_at: datetime($created_at)
        }}]->(target)
        RETURN r
        """

        parameters = {
            "source_id": relationship.source_id,
            "target_id": relationship.target_id,
            "strength": relationship.strength,
            "details_str": details_str,
            "created_at": relationship.created_at.isoformat()
        }

        result = db.execute_query(query, parameters)
        return serialize_neo4j_object(result[0]["r"]) if result else None

    @staticmethod
    def _create_parent_child_relationships():
        """Create parent-child relationships between users based on parent_entity_id field"""
        query = """
        MATCH (child:User), (parent:User)
        WHERE child.parent_entity_id IS NOT NULL
        AND child.parent_entity_id = parent.id
        AND child.id <> parent.id
        MERGE (parent)-[r:PARENT_OF {created_at: datetime()}]->(child)
        MERGE (child)-[r2:SUBSIDIARY_OF {created_at: datetime()}]->(parent)
        RETURN count(r) as relationship_count
        """
        result = db.execute_query(query)
        return result[0]["relationship_count"] if result else 0

    @staticmethod
    def _create_director_relationships():
        """Create director relationships between users based on directors field"""
        query = """
        MATCH (company:User), (director:User)
        WHERE company.directors IS NOT NULL
        AND director.id IN company.directors
        AND company.id <> director.id
        MERGE (director)-[r:DIRECTOR_OF {
            created_at: datetime()
        }]->(company)
        RETURN count(r) as relationship_count
        """
        result = db.execute_query(query)
        return result[0]["relationship_count"] if result else 0

    @staticmethod
    def _create_shareholder_relationships():
        """Create shareholder relationships between users based on shareholders field"""
        # Since we're storing shareholders as a string, we need to handle it differently
        # First, get all companies with shareholders
        query1 = """
        MATCH (company:User)
        WHERE company.shareholders IS NOT NULL
        RETURN company.id as company_id, company.shareholders as shareholders_str
        """
        companies = db.execute_query(query1)

        relationship_count = 0

        # Process each company manually
        for record in companies:
            company_id = record["company_id"]
            shareholders_str = record["shareholders_str"]

            # Skip if the format is not as expected
            if not shareholders_str.startswith("[{") or not shareholders_str.endswith("}]"):
                continue

            # Extract shareholder IDs from the string - this is a simple approach
            # A more robust approach would use a proper parser
            import re
            shareholder_matches = re.findall(r"'id': '([^']+)'", shareholders_str)
            percentage_matches = re.findall(r"'percentage': ([0-9.]+)", shareholders_str)

            # Create relationships for each shareholder
            for i, shareholder_id in enumerate(shareholder_matches):
                percentage = float(percentage_matches[i]) if i < len(percentage_matches) else 0.0

                query2 = """
                MATCH (company:User {id: $company_id}), (shareholder:User {id: $shareholder_id})
                WHERE company.id <> shareholder.id
                MERGE (shareholder)-[r:SHAREHOLDER_OF {
                    percentage: $percentage,
                    created_at: datetime()
                }]->(company)
                RETURN count(r) as rel_count
                """

                params = {
                    "company_id": company_id,
                    "shareholder_id": shareholder_id,
                    "percentage": percentage
                }

                result = db.execute_query(query2, params)
                if result:
                    relationship_count += result[0]["rel_count"]

        return relationship_count

    @staticmethod
    def _create_composite_relationships():
        """Create composite relationships by combining multiple relationship types"""
        query = """
        // Find users that have multiple types of relationships
        MATCH (u1:User)-[r1]->(u2:User)
        WITH u1, u2, count(distinct type(r1)) as rel_count, collect(distinct type(r1)) as rel_types
        WHERE rel_count >= 2

        // Calculate relationship strength based on number of relationships
        WITH u1, u2, rel_count, rel_types,
             (rel_count * 0.2) +
             CASE WHEN "PARENT_OF" IN rel_types OR "SUBSIDIARY_OF" IN rel_types THEN 0.3 ELSE 0 END +
             CASE WHEN "DIRECTOR_OF" IN rel_types THEN 0.2 ELSE 0 END +
             CASE WHEN "SHAREHOLDER_OF" IN rel_types THEN 0.2 ELSE 0 END +
             CASE WHEN "SHARED_EMAIL" IN rel_types THEN 0.1 ELSE 0 END +
             CASE WHEN "SHARED_PHONE" IN rel_types THEN 0.1 ELSE 0 END +
             CASE WHEN "SHARED_ADDRESS" IN rel_types THEN 0.1 ELSE 0 END +
             CASE WHEN "SHARED_PAYMENT_METHOD" IN rel_types THEN 0.1 ELSE 0 END
             as strength

        // Create composite relationship with calculated strength
        MERGE (u1)-[r:COMPOSITE {
            strength: strength,
            relationship_types: rel_types,
            created_at: datetime()
        }]->(u2)

        RETURN count(r) as relationship_count
        """
        result = db.execute_query(query)
        return result[0]["relationship_count"] if result else 0

    @staticmethod
    def get_business_relationships(user_id: str) -> Dict[str, Any]:
        """Get all business relationships of a user"""
        query = """
        MATCH (u:User {id: $user_id})

        // Get outgoing business relationships
        OPTIONAL MATCH (u)-[r1:PARENT_OF|DIRECTOR_OF|SHAREHOLDER_OF|COMPOSITE]->(target1:User)

        // Get incoming business relationships
        OPTIONAL MATCH (source2:User)-[r2:PARENT_OF|DIRECTOR_OF|SHAREHOLDER_OF|COMPOSITE]->(u)

        // Get subsidiary relationships
        OPTIONAL MATCH (u)-[r3:SUBSIDIARY_OF]->(parent:User)

        RETURN u,
               collect(DISTINCT {type: type(r1), node: target1, properties: properties(r1), direction: 'outgoing'}) AS outgoing_business,
               collect(DISTINCT {type: type(r2), node: source2, properties: properties(r2), direction: 'incoming'}) AS incoming_business,
               collect(DISTINCT {type: type(r3), node: parent, properties: properties(r3), direction: 'outgoing'}) AS parent_entities
        """

        parameters = {"user_id": user_id}
        result = db.execute_query(query, parameters)

        if not result:
            return None

        record = result[0]
        return serialize_neo4j_object({
            "user": record["u"],
            "business_relationships": {
                "outgoing": record["outgoing_business"],
                "incoming": record["incoming_business"],
                "parent_entities": record["parent_entities"]
            }
        })

    @staticmethod
    def get_current_timestamp() -> str:
        """Get the current timestamp in ISO format"""
        return datetime.now().isoformat()