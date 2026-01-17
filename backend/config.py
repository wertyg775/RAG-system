"""Configuration management for RAG system."""
from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    google_api_key: str
    vertex_project_id: Optional[str] = None
    vertex_location: Optional[str] = "us-central1"
    
    # Model Configuration
    embedding_model: str = "models/embedding-001"  # Google's embedding model
    llm_model: str = "gemini-3-flash-preview"  # Gemini 3 Flash preview model
    
    # Chunking Configuration
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # Retrieval Configuration
    top_k_results: int = 5
    similarity_threshold: float = 0.4  # Lowered from 0.7 for better retrieval
    use_hybrid_search: bool = True
    
    # ChromaDB Configuration
    chroma_persist_directory: str = "./chroma_db"
    collection_name: str = "documents"
    
    # Generation Configuration
    max_tokens: int = 2000
    temperature: float = 0.7
    stream_responses: bool = True
    
    # Cost Tracking
    enable_cost_tracking: bool = True
    
    class Config:
        # Use absolute path to .env file (in rag-system directory)
        env_file = str(Path(__file__).parent.parent / ".env")
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
