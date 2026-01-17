"""Retrieval system for RAG."""
from typing import List, Dict, Any
from vector_store import vector_store
from config import settings


class Retriever:
    """Handles document retrieval for RAG."""
    
    def __init__(self, use_hybrid: bool = None):
        self.use_hybrid = use_hybrid if use_hybrid is not None else settings.use_hybrid_search
    
    async def retrieve(
        self,
        query: str,
        k: int = None,
        filter_dict: Dict[str, Any] = None,
        threshold: float = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks for a query.
        
        Args:
            query: User query
            k: Number of results to retrieve
            filter_dict: Optional metadata filters
            threshold: Minimum similarity score threshold
        
        Returns:
            List of retrieved chunks with metadata and scores
        """
        k = k or settings.top_k_results
        threshold = threshold or settings.similarity_threshold
        
        # Choose search method
        if self.use_hybrid:
            results = await vector_store.hybrid_search(query, k=k * 2)  # Get more for filtering
        else:
            results = await vector_store.similarity_search(query, k=k * 2, filter_dict=filter_dict)
        
        # Filter by threshold
        filtered_results = [r for r in results if r['score'] >= threshold]
        
        # Re-rank if needed (placeholder for future enhancement)
        # ranked_results = self._rerank(query, filtered_results)
        
        # Return top k
        return filtered_results[:k]
    
    def _rerank(self, query: str, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Re-rank results (placeholder for future implementation).
        
        Could use:
        - Cohere rerank API
        - Cross-encoder models
        - Custom scoring logic
        """
        # For now, just return as-is
        return results
    
    async def retrieve_with_metadata(
        self,
        query: str,
        filename: str = None,
        k: int = None
    ) -> List[Dict[str, Any]]:
        """Retrieve chunks filtered by specific metadata."""
        filter_dict = {}
        if filename:
            filter_dict['filename'] = filename
        
        return await self.retrieve(query, k=k, filter_dict=filter_dict)


# Global retriever instance
retriever = Retriever()
