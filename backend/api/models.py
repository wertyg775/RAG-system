"""Pydantic models for API request/response validation."""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class QueryRequest(BaseModel):
    """Request model for querying the RAG system."""
    query: str = Field(..., description="User's question")
    top_k: Optional[int] = Field(5, description="Number of results to retrieve")
    filename: Optional[str] = Field(None, description="Filter by specific filename")
    stream: Optional[bool] = Field(True, description="Stream the response")


class QueryResponse(BaseModel):
    """Response model for query endpoint."""
    answer: str = Field(..., description="Generated answer")
    sources: List[Dict[str, Any]] = Field(..., description="Retrieved source chunks")
    query: str = Field(..., description="Original query")


class DocumentMetadata(BaseModel):
    """Document metadata model."""
    filename: str
    file_type: str
    total_pages: int = 1
    author: str = ""
    title: str = ""
    upload_time: Optional[str] = None


class DocumentInfo(BaseModel):
    """Document information model."""
    id: str
    metadata: DocumentMetadata
    chunk_count: int


class UploadResponse(BaseModel):
    """Response model for document upload."""
    success: bool
    message: str
    document_id: str
    filename: str
    chunks_created: int


class DocumentListResponse(BaseModel):
    """Response model for listing documents."""
    documents: List[Dict[str, Any]]
    total_count: int


class DeleteResponse(BaseModel):
    """Response model for document deletion."""
    success: bool
    message: str
    deleted_id: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    vector_db_connected: bool
    model_loaded: bool
