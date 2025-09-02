from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

class SimpleStorage:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGO_URI'))
        self.db = self.client[os.getenv('MONGO_DB_NAME')]
        self.collection = self.db['newton_content']  # Simple collection name
    
    def store_content(self, content_list):
        """Store clean content for RAG"""
        for content in content_list:
            doc = {
                'title': content.title,
                'content': content.content,
                'url': content.url,
                'extracted_at': content.extracted_at
            }
            
            # Update if exists, insert if new
            self.collection.update_one(
                {'title': content.title},
                {'$set': doc},
                upsert=True
            )
        
        print(f"Stored {len(content_list)} documents for Newton chatbot")
