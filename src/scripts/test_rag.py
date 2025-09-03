import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from rag.newton_rag import EnhancedNewtonRAG
from dotenv import load_dotenv

def test_newton_rag():
    """Test the complete Newton RAG system"""
    load_dotenv()
    
    print("🧪 Testing Newton RAG System")
    print("=" * 50)
    
    # Initialize RAG system
    try:
        rag = EnhancedNewtonRAG()
        print("✅ RAG system initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize RAG: {e}")
        return
    
    # Test questions about Newton
    test_questions = [
        "Who was Isaac Newton?",
        "What did Newton contribute to calculus?", 
        "Explain Newton's laws of motion",
        "What were Newton's key discoveries in optics?",
        "How did Newton develop the theory of universal gravitation?"
    ]
    
    print(f"\n🔍 Testing {len(test_questions)} questions...\n")
    
    for i, question in enumerate(test_questions, 1):
        print(f"Question {i}: {question}")
        
        try:
            # Get answer with evaluation
            result = rag.answer_question(question, evaluate=True)
            
            # Print answer
            print(f"Answer: {result['answer'][:200]}...")
            print(f"Sources: {', '.join(result['sources'])}")
            print(f"Documents used: {result['num_docs_used']}")
            
            # Print evaluation metrics
            if 'evaluation' in result:
                eval_data = result['evaluation']
                retrieval = eval_data['retrieval_metrics']
                answer = eval_data['answer_metrics']
                
                print(f"📊 Metrics:")
                print(f"   Retrieval Quality: {retrieval['avg_retrieval_similarity']:.3f}")
                print(f"   Answer Grounding: {answer['grounding_score']:.3f}")
                print(f"   Answer Relevance: {answer['answer_relevance']:.3f}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 80)
    
    print("✅ RAG testing complete!")

if __name__ == "__main__":
    test_newton_rag()
