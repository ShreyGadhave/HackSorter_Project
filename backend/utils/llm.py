import os
from langchain_groq import ChatGroq


def initialize_llm():
    """
    Initialize ChatGroq LLM with Llama 3.1 70B model.
    
    Configuration:
    - Model: llama3-70b-8192 (Free tier, fast)
    - Temperature: 0 (Deterministic output for consistent JSON)
    - API Key: From environment variable GROQ_API_KEY
    
    Returns:
        ChatGroq: Configured LLM instance
    """
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set")
    
    llm = ChatGroq(
        model="llama3-70b-8192",
        temperature=0,
        groq_api_key=api_key
    )
    
    return llm
