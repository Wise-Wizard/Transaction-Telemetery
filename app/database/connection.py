import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Neo4jConnection:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI")
        self.user = os.getenv("NEO4J_USER")
        self.password = os.getenv("NEO4J_PASSWORD")
        self.driver = None

    def connect(self):
        """Connect to the Neo4j database"""
        try:
            self.driver = GraphDatabase.driver(
                self.uri, 
                auth=(self.user, self.password),
                max_connection_lifetime=200,  # Refresh connections every 200s
                keep_alive=True  # Enable TCP keep-alive
            )
            print("Connected to Neo4j database")
            return self.driver
        except Exception as e:
            print(f"Failed to connect to Neo4j database: {e}")
            raise

    def close(self):
        """Close the connection to the Neo4j database"""
        if self.driver:
            self.driver.close()
            print("Connection to Neo4j database closed")

    def execute_query(self, query, parameters=None):
        """Execute a Cypher query"""
        if not self.driver:
            self.connect()
        
        from neo4j.exceptions import ServiceUnavailable, SessionExpired, TransientError
        import time
        
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                with self.driver.session() as session:
                    result = session.run(query, parameters or {})
                    return [record for record in result]
            except (ServiceUnavailable, SessionExpired, TransientError) as e:
                if attempt < max_retries - 1:
                    print(f"Query failed (attempt {attempt+1}/{max_retries}): {e}. Retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    print(f"Query failed after {max_retries} attempts: {e}")
                    raise
            except Exception as e:
                print(f"Query execution error: {e}")
                raise

# Create a singleton instance
db = Neo4jConnection()
