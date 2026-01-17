"""Embedding generation using Google's embedding models."""
from __future__ import annotations

import asyncio
import hashlib
import json
import sqlite3
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any
import google.generativeai as genai
from config import settings


class EmbeddingCache:
    """SQLite-based cache for embeddings to reduce API costs."""
    
    def __init__(self, db_path: str = "./embedding_cache.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize the cache database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS embeddings (
                    text_hash TEXT PRIMARY KEY,
                    embedding TEXT NOT NULL,
                    model TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    
    def _hash_text(self, text: str, model: str) -> str:
        """Create a hash of text + model for cache key."""
        combined = f"{model}:{text}"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def get(self, text: str, model: str) -> List[float] | None:
        """Retrieve cached embedding if available."""
        text_hash = self._hash_text(text, model)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT embedding FROM embeddings WHERE text_hash = ?",
                (text_hash,)
            )
            row = cursor.fetchone()
            if row:
                return json.loads(row[0])
        return None
    
    def set(self, text: str, model: str, embedding: List[float]):
        """Store embedding in cache."""
        text_hash = self._hash_text(text, model)
        embedding_json = json.dumps(embedding)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO embeddings (text_hash, embedding, model) VALUES (?, ?, ?)",
                (text_hash, embedding_json, model)
            )
            conn.commit()


class EmbeddingService(ABC):
    """Abstract base class for embedding services."""
    
    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        pass
    
    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        pass


class GoogleEmbeddingService(EmbeddingService):
    """Google's embedding service using Generative AI API."""
    
    def __init__(self, use_cache: bool = True):
        genai.configure(api_key=settings.google_api_key)
        self.model_name = settings.embedding_model
        self.cache = EmbeddingCache() if use_cache else None
    
    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text with caching."""
        # Check cache first
        if self.cache:
            cached = self.cache.get(text, self.model_name)
            if cached:
                return cached
        
        # Generate embedding (wrap in asyncio.to_thread to avoid blocking)
        result = await asyncio.to_thread(
            genai.embed_content,
            model=self.model_name,
            content=text,
            task_type="retrieval_document"
        )
        embedding = result['embedding']
        
        # Store in cache
        if self.cache:
            self.cache.set(text, self.model_name, embedding)
        
        return embedding
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts with caching."""
        embeddings = []
        uncached_texts = []
        uncached_indices = []
        
        # Check cache for each text
        for i, text in enumerate(texts):
            if self.cache:
                cached = self.cache.get(text, self.model_name)
                if cached:
                    embeddings.append(cached)
                    continue
            
            uncached_texts.append(text)
            uncached_indices.append(i)
            embeddings.append(None)  # Placeholder
        
        # Generate embeddings for uncached texts
        if uncached_texts:
            # Note: Google's API may have batch limits, so chunk if needed
            batch_size = 100
            for i in range(0, len(uncached_texts), batch_size):
                batch = uncached_texts[i:i + batch_size]
                results = await asyncio.to_thread(
                    genai.embed_content,
                    model=self.model_name,
                    content=batch,
                    task_type="retrieval_document"
                )
                
                # Extract and cache embeddings
                for j, embedding in enumerate(results['embedding']):
                    idx = uncached_indices[i + j]
                    embeddings[idx] = embedding
                    
                    if self.cache:
                        self.cache.set(batch[j], self.model_name, embedding)
        
        return embeddings
    
    async def embed_query(self, query: str) -> List[float]:
        """Generate embedding for a query (uses different task type)."""
        result = await asyncio.to_thread(
            genai.embed_content,
            model=self.model_name,
            content=query,
            task_type="retrieval_query"
        )
        return result['embedding']


# Global embedding service instance
embedding_service = GoogleEmbeddingService()
