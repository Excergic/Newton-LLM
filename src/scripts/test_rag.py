import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from rag.newton_rag import EnhancedNewtonRAG
from dotenv import load_dotenv
import json

def main():
    load_dotenv()
    
    # Initialize RAG system
    rag = EnhancedNewtonRAG()
    
    # Test questions
    test_questions = [
        "What did Isaac Newton contribute to mathematics?",
        "How did Newton's laws of motion work?",
        "What was Newton's role in developing calculus?",
        "What experiments did Newton do with light and optics?"
    ]
    
    print("🧪 Testing Newton RAG System\n")
    
    for i, question in enumerate(test_questions, 1):
        print(f"Question {i}: {question}")
        
        result = rag.answer_question(question, evaluate=True)
        
        print(f"Answer: {result['answer']}")
        print(f"Sources: {', '.join(result['sources'])}")
        
        if 'evaluation' in result:
            eval_data = result['evaluation']
            retrieval = eval_data['retrieval_metrics']
            answer = eval_data['answer_metrics']
            
            print(f"Retrieval Quality: {retrieval['avg_retrieval_similarity']:.3f}")
            print(f"Answer Grounding: {answer['grounding_score']:.3f}")
            print(f"Answer Relevance: {answer['answer_relevance']:.3f}")
        
        print("-" * 80)

if __name__ == "__main__":
    main()
