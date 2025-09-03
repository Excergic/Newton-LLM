from dotenv import load_dotenv
from qdrant_client import QdrantClient
import os

load_dotenv()

def test_qdrant_connection():
    try:
        client = QdrantClient(
            url=os.getenv('QDRANT_CLOUD_URL'),
            api_key=os.getenv('QDRANT_APIKEY')
        )
        
        # Test connection
        collections = client.get_collections()
        print(f"✅ Connected to Qdrant Cloud successfully!")
        print(f"📊 Available collections: {len(collections.collections)}")
        
        # Test if newton collection exists
        collection_name = "newton_knowledge"
        if client.collection_exists(collection_name):
            info = client.get_collection(collection_name)
            print(f"✅ Newton collection exists with {info.vectors_count} vectors")
        else:
            print("ℹ️  Newton collection not found - will be created during pipeline")
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    test_qdrant_connection()
