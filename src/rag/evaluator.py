from openai import OpenAI
import numpy as np
from typing import Dict, List
from rouge_score import rouge_scorer
import logging
import os

logger = logging.getLogger(__name__)

class RAGEvaluator:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.rouge_scorer = rouge_scorer.RougeScorer(['rouge1', 'rougeL'], use_stemmer=True)
    
    def get_embedding(self, text: str) -> List[float]:
        response = self.openai_client.embeddings.create(
            input=text, model="text-embedding-3-small"
        )
        return response.data[0].embedding
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        vec1, vec2 = np.array(vec1), np.array(vec2)
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    
    def evaluate_retrieval_relevance(self, query: str, retrieved_docs: List[Dict]) -> Dict:
        """Evaluate how well retrieved documents match the query"""
        query_emb = self.get_embedding(query)
        similarities = [
            self.cosine_similarity(query_emb, self.get_embedding(doc['text'])) 
            for doc in retrieved_docs
        ]
        
        return {
            'avg_retrieval_similarity': np.mean(similarities) if similarities else 0.0,
            'max_retrieval_similarity': max(similarities) if similarities else 0.0,
            'num_retrieved_docs': len(retrieved_docs)
        }
    
    def check_factual_grounding(self, answer: str, retrieved_docs: List[Dict]) -> float:
        """Check if answer is grounded in retrieved documents"""
        context = "\n".join([doc['text'] for doc in retrieved_docs])[:2000]
        
        prompt = f"""
        Evaluate if the answer is factually grounded in the context.
        
        Context: {context}
        Answer: {answer}
        
        Rate from 0.0 to 1.0 how well supported the answer is:
        - 1.0: Fully supported
        - 0.5: Partially supported  
        - 0.0: Not supported
        
        Return only the numeric score:
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=10
            )
            return float(response.choices[0].message.content.strip())
        except Exception as e:
            logger.error(f"Grounding evaluation failed: {e}")
            return 0.5
    
    def evaluate_answer_quality(self, query: str, answer: str, retrieved_docs: List[Dict]) -> Dict:
        """Evaluate overall answer quality"""
        grounding_score = self.check_factual_grounding(answer, retrieved_docs)
        
        # Answer relevance
        query_emb = self.get_embedding(query)
        answer_emb = self.get_embedding(answer)
        relevance_score = self.cosine_similarity(query_emb, answer_emb)
        
        return {
            'grounding_score': grounding_score,
            'answer_relevance': relevance_score
        }
