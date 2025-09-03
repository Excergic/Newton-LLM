import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from qdrant_client import QdrantClient
from dotenv import load_dotenv

load_dotenv()

def check_qdrant_status():
    """Check Qdrant Cloud status and collections"""
    
    client = QdrantClient(
        url=os.getenv('QDRANT_CLOUD_URL'),
        api_key=os.getenv('QDRANT_APIKEY')
    )
    
    print("🔍 Checking Qdrant Cloud status...")
    
    # List all collections
    collections = client.get_collections()
    print(f"📊 Existing collections: {len(collections.collections)}")
    
    for collection in collections.collections:
        info = client.get_collection(collection.name)
        print(f"   - {collection.name}: {info.vectors_count} vectors")
    
    # Check for newton_knowledge specifically
    if client.collection_exists('newton_knowledge'):
        info = client.get_collection('newton_knowledge')
        print(f"✅ newton_knowledge exists with {info.vectors_count} vectors")
    else:
        print("❌ newton_knowledge collection does NOT exist")
        print("   👉 You need to run the data ingestion pipeline")

if __name__ == "__main__":
    check_qdrant_status()
