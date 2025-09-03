from .vector_store import NewtonVectorStore
from .reranker import NewtonReranker
from .evaluator import RAGEvaluator
from openai import OpenAI
from typing import Dict, List
import logging
import os

logger = logging.getLogger(__name__)

class EnhancedNewtonRAG:
    def __init__(self):
        self.vector_store = NewtonVectorStore()
        self.reranker = NewtonReranker()
        self.evaluator = RAGEvaluator()
        self.llm = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

        logger.info("✅ Newton RAG initialized with Qdrant Cloud")
    
    def create_embedding(self, text: str) -> List[float]:
        response = self.llm.embeddings.create(
            input=text, model="text-embedding-3-small"
        )
        return response.data[0].embedding
    
    def answer_question(self, question: str, evaluate: bool = True) -> Dict:
        """Complete RAG pipeline with reranking and evaluation"""
        
        # 1. Vector search
        query_embedding = self.create_embedding(question)
        search_results = self.vector_store.search(query_embedding, limit=20)
        
        initial_docs = []
        for result in search_results:
            initial_docs.append({
                'text': result.payload['text'],
                'title': result.payload['title'],
                'url': result.payload['url'],
                'vector_score': result.score
            })
        
        logger.info(f"✓ Retrieved {len(initial_docs)} initial documents")
        
        # 2. Rerank documents
        reranked_docs = self.reranker.rerank_documents(question, initial_docs, top_k=5)
        
        # 3. Evaluate retrieval (optional)
        retrieval_metrics = {}
        if evaluate:
            retrieval_metrics = self.evaluator.evaluate_retrieval_relevance(
                question, reranked_docs
            )
        
        # 4. Generate answer
        context = "\n\n".join([doc['text'] for doc in reranked_docs])
        
        prompt = f"""Based on this information about Isaac Newton, answer the question accurately.

Context: {context}

Question: {question}

Instructions:
- Answer based only on the provided context
- Be specific and cite Newton's actual work when possible
- If the context doesn't contain enough information, say so
- Keep your answer informative but concise

Answer:"""
        
        response = self.llm.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        answer = response.choices[0].message.content
        
        # 5. Evaluate answer quality (optional)
        answer_metrics = {}
        if evaluate:
            answer_metrics = self.evaluator.evaluate_answer_quality(
                question, answer, reranked_docs
            )
        
        # 6. Compile results
        result = {
            'answer': answer,
            'sources': [doc['title'] for doc in reranked_docs],
            'num_docs_used': len(reranked_docs),
            'reranked_docs': reranked_docs
        }
        
        if evaluate:
            result['evaluation'] = {
                'retrieval_metrics': retrieval_metrics,
                'answer_metrics': answer_metrics
            }
        
        return result
