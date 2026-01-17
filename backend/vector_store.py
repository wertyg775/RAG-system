"""Vector store operations using ChromaDB."""
import uuid
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from rank_bm25 import BM25Okapi
from config import settings
from embeddings import embedding_service


class VectorStore:
    """ChromaDB-based vector store for document chunks."""
    
    def __init__(self, persist_directory: str = None, collection_name: str = None):
        self.persist_directory = persist_directory or settings.chroma_persist_directory
        self.collection_name = collection_name or settings.collection_name
        
        # Initialize ChromaDB client with PersistentClient for proper persistence
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )
        
        # BM25 index for hybrid search (lazy loaded)
        self._bm25_index: Optional[BM25Okapi] = None
        self._bm25_docs: List[str] = []
        self._bm25_ids: List[str] = []
    
    async def add_documents(
        self,
        texts: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str] = None
    ) -> List[str]:
        """Add documents to the vector store."""
        # Generate IDs if not provided
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in texts]
        
        # Generate embeddings
        embeddings = await embedding_service.embed_batch(texts)
        
        # Add to ChromaDB
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )
        
        # Update BM25 index
        self._bm25_docs.extend(texts)
        self._bm25_ids.extend(ids)
        self._rebuild_bm25_index()
        
        return ids
    
    async def similarity_search(
        self,
        query: str,
        k: int = None,
        filter_dict: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Perform similarity search using vector embeddings."""
        k = k or settings.top_k_results
        
        # Generate query embedding
        query_embedding = await embedding_service.embed_query(query)
        
        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where=filter_dict
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results['ids'][0])):
            formatted_results.append({
                'id': results['ids'][0][i],
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'score': 1 - results['distances'][0][i],  # Convert distance to similarity
                'source': 'vector'
            })
        
        return formatted_results
    
    def _rebuild_bm25_index(self):
        """Rebuild BM25 index from documents."""
        if self._bm25_docs:
            # Tokenize documents (simple whitespace tokenization)
            tokenized_docs = [doc.lower().split() for doc in self._bm25_docs]
            self._bm25_index = BM25Okapi(tokenized_docs)
    
    def _bm25_search(self, query: str, k: int) -> List[Dict[str, Any]]:
        """Perform BM25 keyword search."""
        if not self._bm25_index or not self._bm25_docs:
            return []
        
        # Tokenize query
        tokenized_query = query.lower().split()
        
        # Get scores
        scores = self._bm25_index.get_scores(tokenized_query)
        
        # Get top k indices
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
        
        # Format results
        results = []
        for idx in top_indices:
            if scores[idx] > 0:  # Only include results with positive scores
                results.append({
                    'id': self._bm25_ids[idx],
                    'text': self._bm25_docs[idx],
                    'score': scores[idx],
                    'source': 'bm25'
                })
        
        return results
    
    async def hybrid_search(
        self,
        query: str,
        k: int = None,
        alpha: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Hybrid search combining vector similarity and BM25 keyword search.
        
        Args:
            query: Search query
            k: Number of results
            alpha: Weight for vector search (1-alpha for BM25). Range [0, 1]
        """
        k = k or settings.top_k_results
        
        # Get results from both methods
        vector_results = await self.similarity_search(query, k * 2)
        bm25_results = self._bm25_search(query, k * 2)
        
        # Normalize scores to [0, 1] range
        if vector_results:
            max_vector_score = max(r['score'] for r in vector_results)
            min_vector_score = min(r['score'] for r in vector_results)
            vector_range = max_vector_score - min_vector_score or 1
            for r in vector_results:
                r['normalized_score'] = (r['score'] - min_vector_score) / vector_range
        
        if bm25_results:
            max_bm25_score = max(r['score'] for r in bm25_results)
            min_bm25_score = min(r['score'] for r in bm25_results)
            bm25_range = max_bm25_score - min_bm25_score or 1
            for r in bm25_results:
                r['normalized_score'] = (r['score'] - min_bm25_score) / bm25_range
        
        # Combine scores
        combined_scores = {}
        
        for result in vector_results:
            doc_id = result['id']
            combined_scores[doc_id] = {
                'text': result['text'],
                'metadata': result.get('metadata', {}),
                'id': doc_id,
                'score': alpha * result.get('normalized_score', 0),
                'vector_score': result['score']
            }
        
        for result in bm25_results:
            doc_id = result['id']
            if doc_id in combined_scores:
                combined_scores[doc_id]['score'] += (1 - alpha) * result.get('normalized_score', 0)
                combined_scores[doc_id]['bm25_score'] = result['score']
            else:
                combined_scores[doc_id] = {
                    'text': result['text'],
                    'metadata': {},
                    'id': doc_id,
                    'score': (1 - alpha) * result.get('normalized_score', 0),
                    'bm25_score': result['score']
                }
        
        # Sort by combined score
        results = sorted(combined_scores.values(), key=lambda x: x['score'], reverse=True)
        
        return results[:k]
    
    def delete_document(self, doc_id: str):
        """Delete a document by ID."""
        self.collection.delete(ids=[doc_id])
        
        # Remove from BM25 index
        if doc_id in self._bm25_ids:
            idx = self._bm25_ids.index(doc_id)
            self._bm25_ids.pop(idx)
            self._bm25_docs.pop(idx)
            self._rebuild_bm25_index()
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """List all documents in the collection."""
        results = self.collection.get()
        
        documents = []
        for i in range(len(results['ids'])):
            documents.append({
                'id': results['ids'][i],
                'text': results['documents'][i] if results['documents'] else '',
                'metadata': results['metadatas'][i] if results['metadatas'] else {}
            })
        
        return documents
    
    def clear(self):
        """Clear all documents from the collection."""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        self._bm25_docs = []
        self._bm25_ids = []
        self._bm25_index = None


# Global vector store instance
vector_store = VectorStore()
