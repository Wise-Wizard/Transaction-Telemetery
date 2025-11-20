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
                auth=(self.user, self.password)
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
        
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record for record in result]

# Create a singleton instance
db = Neo4jConnection()
