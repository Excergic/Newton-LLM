from sentence_transformers import CrossEncoder
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class NewtonReranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.reranker = CrossEncoder(model_name)
        logger.info(f"✓ Loaded reranker model: {model_name}")
    
    def rerank_documents(self, query: str, documents: List[Dict], top_k: int = 5) -> List[Dict]:
        """Rerank documents by query-document relevance"""
        if not documents:
            return []
        
        # Create query-document pairs
        pairs = [(query, doc['text'][:512]) for doc in documents]
        
        # Get relevance scores
        scores = self.reranker.predict(pairs)
        
        # Sort by relevance score
        scored_docs = [(doc, score) for doc, score in zip(documents, scores)]
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        
        reranked_docs = [doc for doc, _ in scored_docs[:top_k]]
        logger.info(f"✓ Reranked {len(documents)} docs to top {top_k}")
        return reranked_docs