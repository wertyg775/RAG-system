"""Simple test script to verify the RAG system setup."""
import sys
import asyncio
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from embeddings import embedding_service
from vector_store import vector_store
from chunking import get_chunker
from retrieval import retriever
from generator import generator


async def test_setup():
    """Test basic functionality of the RAG system."""
    print("=" * 60)
    print("RAG System Setup Test")
    print("=" * 60)
    
    # Test 1: Configuration
    print("\n1. Testing Configuration...")
    print(f"   ✓ LLM Model: {settings.llm_model}")
    print(f"   ✓ Embedding Model: {settings.embedding_model}")
    print(f"   ✓ Chunk Size: {settings.chunk_size}")
    print(f"   ✓ Top-K Results: {settings.top_k_results}")
    
    # Test 2: Embeddings
    print("\n2. Testing Embeddings...")
    try:
        embedding = await embedding_service.embed_text("Hello, world!")
        print(f"   ✓ Embedding generated (dimension: {len(embedding)})")
    except Exception as e:
        print(f"   ✗ Embedding failed: {e}")
        return
    
    # Test 3: Chunking
    print("\n3. Testing Chunking...")
    chunker = get_chunker("recursive")
    test_text = "This is a test document. " * 100
    chunks = chunker.chunk(test_text, {"filename": "test.txt"})
    print(f"   ✓ Created {len(chunks)} chunks from test text")
    
    # Test 4: Vector Store
    print("\n4. Testing Vector Store...")
    try:
        # Clear any existing test data
        test_docs = ["The cat sat on the mat.", "The dog played in the park."]
        test_meta = [{"filename": "test1.txt"}, {"filename": "test2.txt"}]
        
        ids = await vector_store.add_documents(test_docs, test_meta)
        print(f"   ✓ Added {len(ids)} test documents to vector store")
        
        # Test retrieval
        results = await vector_store.similarity_search("cat", k=1)
        print(f"   ✓ Retrieved {len(results)} results for test query")
        
        # Clean up
        for doc_id in ids:
            vector_store.delete_document(doc_id)
        print(f"   ✓ Cleaned up test documents")
        
    except Exception as e:
        print(f"   ✗ Vector store test failed: {e}")
        return
    
    # Test 5: Generation
    print("\n5. Testing Generation...")
    try:
        test_contexts = [{
            'text': "Python is a programming language.",
            'metadata': {'filename': 'test.txt', 'page': 1, 'chunk_index': 0}
        }]
        
        response = await generator.generate(
            "What is Python?",
            test_contexts,
            stream=False
        )
        print(f"   ✓ Generated response ({len(response)} chars)")
        
    except Exception as e:
        print(f"   ✗ Generation test failed: {e}")
        print(f"      Make sure your GOOGLE_API_KEY is set correctly in .env")
        return
    
    print("\n" + "=" * 60)
    print("✓ All tests passed! The RAG system is ready to use.")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Start the backend: python -m uvicorn api.main:app --reload")
    print("2. Start the frontend: cd frontend && npm run dev")
    print("3. Open http://localhost:3000 in your browser")


if __name__ == "__main__":
    asyncio.run(test_setup())
