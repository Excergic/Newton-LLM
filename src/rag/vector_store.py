from qdrant_client import QdrantClient
from typing import List
import logging
import os

logger = logging.getLogger(__name__)

class NewtonVectorStore:
    def __init__(self):
        self.client = QdrantClient(url=os.getenv("QDRANT_CLOUD_URL"), 
        api_key=os.getenv("QDRANT_APIKEY")
        )

        self.collection_name = "newton_knowledge"
        logger.info("✓ Connected to Qdrant Cloud for vector search")
    
    def search(self, query_vector: List[float], limit: int = 20):
        """Search for similar vectors in Qdrant"""
        return self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit
        )