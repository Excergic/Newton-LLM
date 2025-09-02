from airflow import DAG
from airflow.decorators import task
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from extractors.wikipedia_extractor import SimpleWikipediaExtractor
from storage.mongodb_manager import SimpleStorage

# Newton pages for chatbot
NEWTON_PAGES = [
    "Isaac Newton",
    "Newton's laws of motion", 
    "Calculus",
    "Opticks",
    "Philosophiæ Naturalis Principia Mathematica"
]

dag = DAG(
    'simple_newton_chatbot_etl',
    description='Simple ETL for Newton chatbot content',
    schedule=timedelta(days=7),  # Weekly
    start_date=datetime(2025, 9, 2),
    catchup=False
)

@task(dag=dag)
def extract_and_store_newton_content():
    """Extract Newton content and store for RAG/chatbot"""
    
    extractor = SimpleWikipediaExtractor()
    storage = SimpleStorage()
    
    content_list = []
    for page in NEWTON_PAGES:
        try:
            print(f"Extracting: {page}")
            content = extractor.extract_page(page)
            content_list.append(content)
            print(f"✓ Got {len(content.content)} characters from {page}")
        except Exception as e:
            print(f"✗ Failed {page}: {e}")
    
    # Store all content
    storage.store_content(content_list)
    
    return f"Successfully processed {len(content_list)} Newton pages for chatbot"

# Single task - extract and store
process_newton_content = extract_and_store_newton_content()
