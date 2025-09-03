import os
import re
import uuid
from typing import List, Dict
from pymongo import MongoClient
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from openai import OpenAI
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class NewtonDataPipeline:
    def __init__(self):
        self.mongo_client = MongoClient(os.getenv('MONGO_URI'))

        self.qdrant_client = QdrantClient(
            url=os.getenv("QDRANT_CLOUD_URL"),
            api_key=os.getenv("QDRANT_APIKEY")
        )

        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        self.mongo_db = self.mongo_client[os.getenv('MONGO_DB_NAME')]
        self.collection = self.mongo_db['newton_content']
        self.qdrant_collection = "newton_knowledge"
    
    def clean_text(self, content: str) -> str:
        """Clean text from MongoDB content"""
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r'[^\w\s.,;:!?()-]', '', content)
        content = re.sub(r'([.!?])\s*', r'\1 ', content)
        return content.strip()
    
    def chunk_text(self, text: str, title: str, url: str, chunk_size: int = 800) -> List[Dict]:
        """Smart chunking with sentence boundaries"""
        sentences = text.split('. ')
        chunks = []
        current_chunk = ""
        chunk_index = 0
        
        for sentence in sentences:
            if len(current_chunk + sentence) <= chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk.strip():
                    chunks.append({
                        'text': current_chunk.strip(),
                        'title': title,
                        'url': url,
                        'chunk_index': chunk_index,
                        'source_type': 'wikipedia'
                    })
                    chunk_index += 1
                current_chunk = sentence + ". "
        
        if current_chunk.strip():
            chunks.append({
                'text': current_chunk.strip(),
                'title': title,
                'url': url,
                'chunk_index': chunk_index,
                'source_type': 'wikipedia'
            })
        
        return chunks
    
    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for text chunks"""
        response = self.openai_client.embeddings.create(
            input=texts,
            model="text-embedding-3-small"
        )
        return [data.embedding for data in response.data]
    
    def setup_qdrant_collection(self):
        """Initialize Qdrant collection on cloud"""
        if not self.qdrant_client.collection_exists(self.qdrant_collection):
            self.qdrant_client.create_collection(
                collection_name=self.qdrant_collection,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
            )
            logger.info(f"✓ Created Qdrant collection: {self.qdrant_collection}")
        else:
            logger.info(f"✓ Connected to existing Qdrant collection: {self.qdrant_collection}")
    
    def store_in_qdrant(self, chunks: List[Dict], embeddings: List[List[float]]):
        """Store chunks with embeddings in Qdrant"""
        points = []
        for chunk, embedding in zip(chunks, embeddings):
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    'text': chunk['text'],
                    'title': chunk['title'],
                    'url': chunk['url'],
                    'chunk_index': chunk['chunk_index'],
                    'source_type': chunk['source_type']
                }
            )
            points.append(point)
        
        self.qdrant_client.upsert(
            collection_name=self.qdrant_collection,
            points=points
        )
        logger.info(f"✓ Stored {len(points)} chunks in Qdrant")
    
    def process_mongodb_to_qdrant(self):
        """Complete pipeline: MongoDB → Clean → Chunk → Embed → Qdrant"""
        self.setup_qdrant_collection()
        
        total_chunks = 0
        for doc in self.collection.find({}):
            logger.info(f"Processing: {doc['title']}")
            
            # Clean text
            cleaned_text = self.clean_text(doc['content'])
            
            # Chunk text
            chunks = self.chunk_text(cleaned_text, doc['title'], doc['url'])
            
            # Create embeddings
            embeddings = self.create_embeddings([chunk['text'] for chunk in chunks])
            
            # Store in Qdrant
            self.store_in_qdrant(chunks, embeddings)
            total_chunks += len(chunks)
        
        logger.info(f"✅ Pipeline complete - {total_chunks} chunks ready in Qdrant!")