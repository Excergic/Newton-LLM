import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from rag.data_pipeline import NewtonDataPipeline
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)

def main():
    load_dotenv()
    
    print("🚀 Building Newton RAG System")
    print("MongoDB → Clean → Chunk → Embed → Qdrant")
    
    pipeline = NewtonDataPipeline()
    pipeline.process_mongodb_to_qdrant()
    
    print("\n✅ Newton RAG system ready!")
    print("   - Vector Store: Qdrant (newton_knowledge)")
    print("   - Ready for queries with reranking & evaluation!")

if __name__ == "__main__":
    main()
