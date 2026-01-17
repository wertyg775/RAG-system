"""FastAPI application for RAG system."""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import asyncio
from datetime import datetime
from typing import List, Dict, Any
import json

from api.models import (
    QueryRequest, QueryResponse, UploadResponse,
    DocumentListResponse, DeleteResponse, HealthResponse
)
from document_processor import DocumentProcessor
from chunking import get_chunker
from vector_store import vector_store
from retrieval import retriever
from generator import generator
from config import settings


# Create FastAPI app
app = FastAPI(
    title="RAG System API",
    description="API for document ingestion and question answering",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Frontend development server
        "http://127.0.0.1:3000",  # Alternative localhost
        # Add production domain here when deploying
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        # Check if vector store is accessible
        vector_store.collection.count()
        vector_db_connected = True
    except:
        vector_db_connected = False
    
    return HealthResponse(
        status="healthy",
        vector_db_connected=vector_db_connected,
        model_loaded=True  # If we got this far, imports worked
    )


@app.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process a document.
    
    Supports: PDF, DOCX, Markdown, TXT
    """
    try:
        # Read file content
        content = await file.read()
        filename = file.filename
        
        # Check file type
        if not any(filename.lower().endswith(ext) for ext in DocumentProcessor.supported_extensions()):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Supported: {DocumentProcessor.supported_extensions()}"
            )
        
        # Parse document
        parsed_doc = DocumentProcessor.parse(content, filename)
        
        # Chunk the document
        chunker = get_chunker("recursive")
        metadata_dict = parsed_doc.metadata.to_dict()
        metadata_dict['upload_time'] = datetime.now().isoformat()
        
        chunks = chunker.chunk(parsed_doc.text, metadata_dict)
        
        # Prepare data for vector store
        texts = [chunk.text for chunk in chunks]
        metadatas = []
        
        for i, chunk in enumerate(chunks):
            chunk_meta = chunk.metadata.copy()
            # Add page information if available
            if parsed_doc.page_texts and len(parsed_doc.page_texts) > 1:
                # Estimate which page this chunk belongs to
                chunk_meta['page'] = min(i // (len(chunks) // len(parsed_doc.page_texts)) + 1, len(parsed_doc.page_texts))
            else:
                chunk_meta['page'] = 1
            metadatas.append(chunk_meta)
        
        # Add to vector store
        doc_ids = await vector_store.add_documents(texts, metadatas)
        
        return UploadResponse(
            success=True,
            message=f"Successfully processed {filename}",
            document_id=doc_ids[0] if doc_ids else "",
            filename=filename,
            chunks_created=len(chunks)
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")


@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Query the RAG system (non-streaming).
    
    For streaming, use the /query/stream endpoint or WebSocket.
    """
    try:
        # Retrieve relevant chunks
        contexts = await retriever.retrieve(
            request.query,
            k=request.top_k,
            filter_dict={'filename': request.filename} if request.filename else None
        )
        
        # Generate answer
        answer = await generator.generate(request.query, contexts, stream=False)
        
        # Format sources
        sources = []
        for ctx in contexts:
            sources.append({
                'text': ctx['text'][:200] + '...' if len(ctx['text']) > 200 else ctx['text'],
                'metadata': ctx.get('metadata', {}),
                'score': ctx.get('score', 0)
            })
        
        return QueryResponse(
            answer=answer,
            sources=sources,
            query=request.query
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@app.post("/query/stream")
async def query_documents_stream(request: QueryRequest):
    """
    Query the RAG system with streaming response.
    """
    async def generate_stream():
        try:
            # Retrieve relevant chunks
            contexts = await retriever.retrieve(
                request.query,
                k=request.top_k,
                filter_dict={'filename': request.filename} if request.filename else None
            )
            
            # Send sources first
            sources_data = {
                'type': 'sources',
                'sources': [
                    {
                        'text': ctx['text'][:200] + '...' if len(ctx['text']) > 200 else ctx['text'],
                        'metadata': ctx.get('metadata', {}),
                        'score': ctx.get('score', 0)
                    }
                    for ctx in contexts
                ]
            }
            yield f"data: {json.dumps(sources_data)}\n\n"
            
            # Stream answer
            stream_gen = await generator.generate(request.query, contexts, stream=True)
            async for chunk in stream_gen:
                chunk_data = {
                    'type': 'chunk',
                    'content': chunk
                }
                yield f"data: {json.dumps(chunk_data)}\n\n"
            
            # Send completion signal
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        
        except Exception as e:
            error_data = {
                'type': 'error',
                'message': str(e)
            }
            yield f"data: {json.dumps(error_data)}\n\n"
    
    return StreamingResponse(generate_stream(), media_type="text/event-stream")


@app.websocket("/ws/query")
async def websocket_query(websocket: WebSocket):
    """
    WebSocket endpoint for real-time query streaming.
    """
    await websocket.accept()
    
    try:
        while True:
            # Receive query
            data = await websocket.receive_json()
            query = data.get('query', '')
            top_k = data.get('top_k', 5)
            filename = data.get('filename')
            
            if not query:
                await websocket.send_json({
                    'type': 'error',
                    'message': 'Query is required'
                })
                continue
            
            # Retrieve contexts
            contexts = await retriever.retrieve(
                query,
                k=top_k,
                filter_dict={'filename': filename} if filename else None
            )
            
            # Send sources
            await websocket.send_json({
                'type': 'sources',
                'sources': [
                    {
                        'text': ctx['text'][:200] + '...',
                        'metadata': ctx.get('metadata', {}),
                        'score': ctx.get('score', 0)
                    }
                    for ctx in contexts
                ]
            })
            
            # Stream answer
            stream_gen = await generator.generate(query, contexts, stream=True)
            async for chunk in stream_gen:
                await websocket.send_json({
                    'type': 'chunk',
                    'content': chunk
                })
            
            # Send completion
            await websocket.send_json({'type': 'done'})
    
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        await websocket.send_json({
            'type': 'error',
            'message': str(e)
        })


@app.get("/documents", response_model=DocumentListResponse)
async def list_documents():
    """List all uploaded documents."""
    try:
        all_docs = vector_store.list_documents()
        
        # Group by filename
        doc_groups = {}
        for doc in all_docs:
            metadata = doc.get('metadata', {})
            filename = metadata.get('filename', 'Unknown')
            
            if filename not in doc_groups:
                doc_groups[filename] = {
                    'filename': filename,
                    'metadata': metadata,
                    'chunk_ids': [],
                    'chunk_count': 0
                }
            
            doc_groups[filename]['chunk_ids'].append(doc['id'])
            doc_groups[filename]['chunk_count'] += 1
        
        documents = list(doc_groups.values())
        
        return DocumentListResponse(
            documents=documents,
            total_count=len(documents)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")


@app.delete("/documents/{filename}", response_model=DeleteResponse)
async def delete_document(filename: str):
    """Delete all chunks of a document by filename."""
    try:
        all_docs = vector_store.list_documents()
        
        # Find all chunk IDs for this filename
        ids_to_delete = []
        for doc in all_docs:
            metadata = doc.get('metadata', {})
            if metadata.get('filename') == filename:
                ids_to_delete.append(doc['id'])
        
        if not ids_to_delete:
            raise HTTPException(status_code=404, detail=f"Document '{filename}' not found")
        
        # Delete each chunk
        for doc_id in ids_to_delete:
            vector_store.delete_document(doc_id)
        
        return DeleteResponse(
            success=True,
            message=f"Deleted {len(ids_to_delete)} chunks from '{filename}'",
            deleted_id=filename
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")


@app.delete("/documents/clear/all")
async def clear_all_documents():
    """Clear all documents from the vector store."""
    try:
        vector_store.clear()
        return {
            "success": True,
            "message": "All documents cleared"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing documents: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
