"""Quick diagnostic script to test RAG retrieval"""
import sys
import asyncio
sys.path.insert(0, 'backend')

from vector_store import vector_store
from retrieval import retriever
from embeddings import embedding_service

async def test_retrieval():
    print("=== RAG System Diagnostic ===\n")
    
    # 1. Check documents in vector store
    print("1. Documents in vector store:")
    docs = vector_store.list_documents()
    print(f"   Total chunks: {len(docs)}")
    for i, doc in enumerate(docs[:3]):
        print(f"   Chunk {i}: {doc['metadata'].get('filename', 'unknown')}")
        print(f"   Text preview: {doc['text'][:100]}...")
    print()
    
    # 2. Test query with different thresholds
    queries = ["what is this file about", "DSP", "digital signal processing"]
    
    for query in queries:
        print(f"2. Testing query: '{query}'")
        
        # Test with default threshold (0.7)
        results_high = await retriever.retrieve(query, k=5, threshold=0.7)
        print(f"   Results with threshold 0.7: {len(results_high)}")
        
        # Test with lower threshold (0.3)
        results_low = await retriever.retrieve(query, k=5, threshold=0.3)
        print(f"   Results with threshold 0.3: {len(results_low)}")
        
        if results_low:
            print(f"   Top result score: {results_low[0]['score']:.3f}")
            print(f"   Top result text: {results_low[0]['text'][:100]}...")
        print()
    
    # 3. Test direct vector search
    print("3. Testing direct vector similarity search:")
    vector_results = await vector_store.similarity_search("DSP", k=3)
    for i, res in enumerate(vector_results):
        print(f"   Result {i+1}: Score={res['score']:.3f}")
        print(f"   Text: {res['text'][:80]}...")
    print()

if __name__ == "__main__":
    asyncio.run(test_retrieval())
