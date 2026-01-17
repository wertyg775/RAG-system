"""LLM generation using Gemini."""
from typing import List, Dict, Any, AsyncIterator
import google.generativeai as genai
from config import settings
from prompts import create_rag_prompt, create_no_context_prompt, SYSTEM_PROMPT


class RAGGenerator:
    """Handles response generation using Gemini."""
    
    def __init__(self):
        genai.configure(api_key=settings.google_api_key)
        self.model = genai.GenerativeModel(
            settings.llm_model,
            system_instruction=SYSTEM_PROMPT
        )
        self.generation_config = {
            'temperature': settings.temperature,
            'max_output_tokens': settings.max_tokens,
        }
    
    async def generate(
        self,
        query: str,
        contexts: List[Dict[str, Any]],
        stream: bool = None
    ):
        """
        Generate a response based on query and retrieved contexts.
        
        Args:
            query: User's question
            contexts: Retrieved document chunks
            stream: Whether to stream the response
        
        Returns:
            Generated response (string or async iterator if streaming)
        """
        stream = stream if stream is not None else settings.stream_responses
        
        # Handle case with no relevant contexts
        if not contexts:
            no_context_msg = create_no_context_prompt(query)
            if stream:
                async def no_context_stream():
                    yield no_context_msg
                return no_context_stream()
            return no_context_msg
        
        # Create prompt
        prompt = create_rag_prompt(query, contexts)
        
        try:
            if stream:
                return self._generate_stream(prompt)
            else:
                response = self.model.generate_content(
                    prompt,
                    generation_config=self.generation_config
                )
                return response.text
        
        except Exception as e:
            error_msg = self._handle_error(e, query, contexts)
            if stream:
                async def error_stream():
                    yield error_msg
                return error_stream()
            return error_msg
    
    async def _generate_stream(self, prompt: str):
        """Generate streaming response."""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config,
                stream=True
            )
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        
        except Exception as e:
            yield f"\n\nError generating response: {str(e)}"
    
    def _handle_error(
        self,
        error: Exception,
        query: str,
        contexts: List[Dict[str, Any]]
    ) -> str:
        """Handle errors during generation."""
        error_msg = str(error)
        
        # Handle specific error types
        if "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
            return """I'm currently experiencing high demand. Please try again in a moment.

Error: Rate limit exceeded."""
        
        elif "context length" in error_msg.lower() or "token" in error_msg.lower():
            # Try again with fewer contexts
            if len(contexts) > 1:
                reduced_contexts = contexts[:len(contexts)//2]
                prompt = create_rag_prompt(query, reduced_contexts)
                try:
                    response = self.model.generate_content(
                        prompt,
                        generation_config=self.generation_config
                    )
                    return response.text + "\n\n(Note: Response generated with reduced context due to length constraints)"
                except:
                    pass
            
            return """The context is too long to process. Try:
1. Being more specific in your question
2. Searching for information in a specific document"""
        
        else:
            return f"""I encountered an error while generating a response:

{error_msg}

Please try rephrasing your question or contact support if the issue persists."""
    
    async def generate_summary(self, text: str, max_words: int = 100) -> str:
        """Generate a summary of text."""
        from prompts import create_summary_prompt
        
        prompt = create_summary_prompt(text, max_words)
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={'temperature': 0.3, 'max_output_tokens': 500}
            )
            return response.text
        except Exception as e:
            return f"Error generating summary: {str(e)}"


# Global generator instance
generator = RAGGenerator()
