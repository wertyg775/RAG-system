"""Prompt templates for RAG system."""
from typing import List, Dict, Any


def create_rag_prompt(query: str, contexts: List[Dict[str, Any]]) -> str:
    """
    Create a prompt for the LLM with retrieved context.
    
    Args:
        query: User's question
        contexts: List of retrieved chunks with text and metadata
    
    Returns:
        Formatted prompt string
    """
    # Build context section
    context_parts = []
    for i, ctx in enumerate(contexts, 1):
        metadata = ctx.get('metadata', {})
        filename = metadata.get('filename', 'Unknown')
        page = metadata.get('page', 'N/A')
        chunk_idx = metadata.get('chunk_index', 'N/A')
        
        context_parts.append(
            f"[Source {i}] (File: {filename}, Page: {page}, Chunk: {chunk_idx})\n{ctx['text']}"
        )
    
    context_text = "\n\n".join(context_parts)
    
    prompt = f"""You are a helpful AI assistant that answers questions based on provided documents.

IMPORTANT INSTRUCTIONS:
1. Answer the question using ONLY the information from the provided context
2. Always cite your sources using [Source N] notation
3. If the context doesn't contain enough information to answer the question, say "I don't have enough information in the provided documents to answer this question."
4. If you find conflicting information, acknowledge it and present both perspectives with their sources
5. Be concise but thorough in your answers

CONTEXT:
{context_text}

QUESTION: {query}

ANSWER:"""
    
    return prompt


def create_no_context_prompt(query: str) -> str:
    """Create a prompt when no relevant context is found."""
    return f"""I searched through the available documents but couldn't find relevant information to answer your question: "{query}"

This could mean:
1. The information isn't in the uploaded documents
2. The question might be phrased in a way that doesn't match the document content
3. You may need to upload additional documents

Please try:
- Rephrasing your question
- Uploading more relevant documents
- Being more specific about what you're looking for"""


def create_summary_prompt(text: str, max_words: int = 100) -> str:
    """Create a prompt for summarizing text."""
    return f"""Summarize the following text in no more than {max_words} words:

{text}

Summary:"""


SYSTEM_PROMPT = """You are an expert AI assistant specializing in document analysis and question answering. 

Your key responsibilities:
- Provide accurate, well-sourced answers based on the given context
- Cite sources clearly using the [Source N] format
- Acknowledge limitations when information is insufficient
- Present multiple perspectives when sources conflict
- Maintain a helpful and professional tone

Remember: Only use information from the provided context. Do not use external knowledge."""
