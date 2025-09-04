import streamlit as st
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from rag.newton_rag import EnhancedNewtonRAG

@st.cache_resource
def load_rag_system():
    return EnhancedNewtonRAG()

def main():
    st.set_page_config(page_title="Isaac Newton AI Chatbot", page_icon="🍎", layout="wide")
    
    st.title("🍎 Isaac Newton AI Chatbot")
    st.write("Ask me anything about Isaac Newton's life, discoveries, and scientific work!")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Greetings! I am Isaac Newton, your AI assistant. Ask me anything about my work!"
        })
    
    # Display chat messages
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show metrics for assistant messages (except welcome)
            if message["role"] == "assistant" and i > 0 and "metrics" in message:
                with st.expander("📊 View Quality Metrics & Sources"):
                    metrics = message.get("metrics", {}).get("evaluation")
                    if metrics:
                        retrieval = metrics.get('retrieval_metrics', {})
                        answer = metrics.get('answer_metrics', {})
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("🎯 Retrieval Quality", f"{retrieval.get('avg_retrieval_similarity', 0):.3f}")
                        with col2:
                            st.metric("🔍 Answer Grounding", f"{answer.get('grounding_score', 0):.3f}")
                        with col3:
                            st.metric("📝 Answer Relevance", f"{answer.get('answer_relevance', 0):.3f}")
                    
                    # Show sources
                    sources = message.get("sources", [])
                    if sources:
                        st.subheader("📚 Sources")
                        for j, source in enumerate(sources, 1):
                            st.markdown(f"**{j}.** {source}")
    
    # Chat input
    if prompt := st.chat_input("Ask Newton about his discoveries..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Newton is thinking..."):
                try:
                    rag = load_rag_system()
                    result = rag.answer_question(prompt, evaluate=True)
                    
                    # Display answer
                    st.markdown(result['answer'])
                    
                    # Display metrics and sources
                    with st.expander("📊 View Quality Metrics & Sources"):
                        eval_data = result.get('evaluation', {})
                        retrieval = eval_data.get('retrieval_metrics', {})
                        answer = eval_data.get('answer_metrics', {})
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("🎯 Retrieval Quality", f"{retrieval.get('avg_retrieval_similarity', 0):.3f}")
                        with col2:
                            st.metric("🔍 Answer Grounding", f"{answer.get('grounding_score', 0):.3f}")
                        with col3:
                            st.metric("📝 Answer Relevance", f"{answer.get('answer_relevance', 0):.3f}")
                        
                        # Show sources
                        sources = result.get('sources', [])
                        if sources:
                            st.subheader("📚 Sources")
                            for j, source in enumerate(sources, 1):
                                st.markdown(f"**{j}.** {source}")
                    
                    # Add to chat history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": result['answer'],
                        "metrics": result,
                        "sources": sources
                    })
                    
                except Exception as e:
                    error_msg = f"I apologize, but I encountered an error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    # Sidebar with clear button
    with st.sidebar:
        st.markdown("### 🍎 About Newton AI")
        st.markdown("Powered by 515 knowledge chunks from Newton's work!")
        

if __name__ == "__main__":
    main()
