from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import sys
import os
from dotenv import load_dotenv
import uvicorn

# Load environment variables
load_dotenv()

# Add src to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from rag.newton_rag import EnhancedNewtonRAG

# Initialize FastAPI app
app = FastAPI(
    title="Isaac Newton AI Chatbot API",
    description="Intelligent RAG-powered chatbot about Isaac Newton's life and discoveries",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for web frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG system (cached)
rag_system = None

def get_rag_system():
    global rag_system
    if rag_system is None:
        rag_system = EnhancedNewtonRAG()
    return rag_system

# Request/Response Models
class ChatRequest(BaseModel):
    question: str
    evaluate: bool = True
    
    class Config:
        schema_extra = {
            "example": {
                "question": "What did Isaac Newton contribute to calculus?",
                "evaluate": True
            }
        }

class ChatResponse(BaseModel):
    answer: str
    sources: List[str]
    num_docs_used: int
    evaluation: Optional[Dict] = None

class HealthResponse(BaseModel):
    status: str
    message: str
    system_info: Dict

# API Endpoints
@app.get("/", response_model=Dict)
async def root():
    """Welcome message and API info"""
    return {
        "message": "Welcome to Isaac Newton AI Chatbot API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "chat_endpoint": "/chat"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Test RAG system initialization
        rag = get_rag_system()
        return HealthResponse(
            status="healthy",
            message="Newton AI API is running perfectly",
            system_info={
                "rag_system": "initialized",
                "vector_store": "qdrant_cloud",
                "knowledge_chunks": "515",
                "embedding_model": "text-embedding-3-small",
                "llm_model": "gpt-4o-mini"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"System unhealthy: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat_with_newton(request: ChatRequest):
    """
    Chat with Isaac Newton AI
    
    Send a question about Newton's life, discoveries, or scientific work.
    Get back an intelligent answer with source citations and quality metrics.
    """
    try:
        # Get RAG system
        rag = get_rag_system()
        
        # Process question
        #this will store 1)answer 2)sources 3)num_docs_used 4)rerank_docs
        result = rag.answer_question(request.question, evaluate=request.evaluate)
        
        # Return structured response
        return ChatResponse(
            answer=result['answer'],
            sources=result['sources'],
            num_docs_used=result['num_docs_used'],
            evaluation=result.get('evaluation') if request.evaluate else None
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing question: {str(e)}"
        )

@app.get("/examples")
async def get_example_questions():
    """Get example questions to ask Newton"""
    return {
        "example_questions": [
            "Who was Isaac Newton?",
            "What did Newton contribute to calculus?",
            "Explain Newton's laws of motion",
            "What were Newton's key discoveries in optics?",
            "How did Newton develop the theory of universal gravitation?",
            "What is the Principia Mathematica about?",
            "How did Newton's work influence modern science?"
        ]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
