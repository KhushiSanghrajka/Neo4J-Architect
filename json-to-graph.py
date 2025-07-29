"""
JSON to Neo4j Graph Database Uploader

This script provides functionality to upload JSON data to Neo4j graph database,
creating nodes and relationships based on the JSON structure.
"""

import asyncio
import os
import logging
from typing import Dict, Any, List
from neo4j import AsyncGraphDatabase
import json
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)

class JsonToNeo4jUploader:
    """Handles uploading JSON data to Neo4j graph database"""
    
    def __init__(self, neo4j_uri: str, neo4j_user: str, neo4j_password: str):
        """Initialize the uploader with Neo4j connection details"""
        self.neo4j_uri = os.getenv("NEO4J_URI")
        self.neo4j_user = os.getenv("NEO4J_USER")
        self.neo4j_password = os.getenv("NEO4J_PASSWORD")
        self.driver = None

    async def initialize(self):
        """Initialize Neo4j connection"""
        logger.info("Initializing Neo4j connection...")
        self.driver = AsyncGraphDatabase.driver(
            self.neo4j_uri, 
            auth=(self.neo4j_user, self.neo4j_password)
        )
        logger.info("Neo4j connection initialized successfully")

    async def close(self):
        """Close Neo4j connection"""
        if self.driver:
            await self.driver.close()
            logger.info("Neo4j connection closed")

    async def create_constraints(self, label: str, property_name: str):
        """Create constraints for uniqueness"""
        async with self.driver.session() as session:
            try:
                await session.run(
                    f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{label}) REQUIRE n.{property_name} IS UNIQUE"
                )
                logger.info(f"Created constraint for {label} on {property_name}")
            except Exception as e:
                logger.warning(f"Could not create constraint: {e}")

    async def upload_json_data(self, json_data: Dict[str, Any], node_mappings: Dict[str, str]):
        """
        Upload JSON data to Neo4j
        
        Args:
            json_data: The JSON data to upload
            node_mappings: Dictionary mapping JSON keys to Neo4j node labels
                         Example: {"users": "User", "products": "Product"}
        """
        try:
            async with self.driver.session() as session:
                # Create nodes first
                created_nodes = {}
                for key, data_list in json_data.items():
                    if key in node_mappings:
                        label = node_mappings[key]
                        logger.info(f"Creating {label} nodes...")
                        
                        for item in data_list:
                            # Create node with all properties from JSON
                            properties = {
                                k: v for k, v in item.items() 
                                if not isinstance(v, (dict, list))
                            }
                            
                            # Create unique identifier for node
                            node_id = item.get('id', item.get('uuid', item.get('identifier')))
                            if not node_id:
                                continue
                                
                            query = f"""
                            MERGE (n:{label} {{id: $node_id}})
                            SET n += $properties
                            RETURN n
                            """
                            
                            result = await session.run(
                                query,
                                node_id=str(node_id),
                                properties=properties
                            )
                            
                            # Store reference to created node
                            if key not in created_nodes:
                                created_nodes[key] = {}
                            created_nodes[key][node_id] = dict(properties)
                            
                            logger.debug(f"Created {label} node with id {node_id}")
                
                # Create relationships
                logger.info("Creating relationships...")
                for key, data_list in json_data.items():
                    if key in node_mappings:
                        source_label = node_mappings[key]
                        
                        for item in data_list:
                            source_id = item.get('id', item.get('uuid', item.get('identifier')))
                            if not source_id:
                                continue
                                
                            # Look for relationship fields (lists or objects)
                            for field, value in item.items():
                                if isinstance(value, (list, dict)):
                                    # Determine target label and relationship type
                                    target_key = field.rstrip('s')  # Simple pluralization handling
                                    if target_key in node_mappings:
                                        target_label = node_mappings[target_key]
                                        rel_type = f"HAS_{target_key.upper()}"
                                        
                                        # Handle both list and single object relationships
                                        target_ids = []
                                        if isinstance(value, list):
                                            target_ids = [
                                                str(v.get('id', v.get('uuid', v.get('identifier'))))
                                                for v in value if isinstance(v, dict)
                                            ]
                                        elif isinstance(value, dict):
                                            target_id = value.get('id', value.get('uuid', value.get('identifier')))
                                            if target_id:
                                                target_ids = [str(target_id)]
                                        
                                        # Create relationships
                                        for target_id in target_ids:
                                            query = f"""
                                            MATCH (source:{source_label} {{id: $source_id}})
                                            MATCH (target:{target_label} {{id: $target_id}})
                                            MERGE (source)-[r:{rel_type}]->(target)
                                            RETURN r
                                            """
                                            
                                            await session.run(
                                                query,
                                                source_id=str(source_id),
                                                target_id=target_id
                                            )
                                            
                                            logger.debug(
                                                f"Created {rel_type} relationship: "
                                                f"{source_label}({source_id}) -> {target_label}({target_id})"
                                            )
                
                logger.info("Successfully uploaded JSON data to Neo4j")
                return created_nodes
                
        except Exception as e:
            logger.error(f"Error uploading JSON data: {e}")
            raise

async def main():
    """Example usage"""
    # Sample JSON data
    sample_data = {
        "users": [
            {
                "id": "1",
                "name": "John Doe",
                "email": "john@example.com",
                "orders": [
                    {"id": "101", "product": "Laptop"},
                    {"id": "102", "product": "Mouse"}
                ]
            },
            {
                "id": "2",
                "name": "Jane Smith",
                "email": "jane@example.com",
                "orders": [
                    {"id": "103", "product": "Keyboard"}
                ]
            }
        ],
        "orders": [
            {
                "id": "101",
                "product": "Laptop",
                "price": 999.99
            },
            {
                "id": "102",
                "product": "Mouse",
                "price": 29.99
            },
            {
                "id": "103",
                "product": "Keyboard",
                "price": 59.99
            }
        ]
    }

    # Define node mappings
    node_mappings = {
        "users": "User",
        "orders": "Order"
    }

    # Initialize uploader
    uploader = JsonToNeo4jUploader(
        neo4j_uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        neo4j_user=os.getenv("NEO4J_USER", "neo4j"),
        neo4j_password=os.getenv("NEO4J_PASSWORD")
    )

    try:
        # Initialize connection
        await uploader.initialize()

        # Create constraints
        await uploader.create_constraints("User", "id")
        await uploader.create_constraints("Order", "id")

        # Upload data
        created_nodes = await uploader.upload_json_data(sample_data, node_mappings)
        
        # Print summary
        print("\n=== Upload Summary ===")
        for node_type, nodes in created_nodes.items():
            print(f"{node_type}: {len(nodes)} nodes created")

    finally:
        await uploader.close()

if __name__ == "__main__":
    asyncio.run(main()) 