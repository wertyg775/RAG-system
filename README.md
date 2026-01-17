# RAG System for Personal Documents

A full-stack AI-powered document question answering system using Retrieval-Augmented Generation (RAG).

## Features

- **Multi-format Support**: PDF, DOCX, Markdown, and TXT files
- **Hybrid Search**: Combines vector similarity and BM25 keyword search
- **AI-Powered**: Uses Google's Gemini 1.5 Pro for generation
- **Streaming Responses**: Real-time answer streaming for better UX
- **Source Citations**: All answers include source references
- **Modern UI**: Beautiful Next.js frontend with dark mode support

## Tech Stack

### Backend
- **Framework**: FastAPI
- **Vector DB**: ChromaDB (local)
- **Embeddings**: Google's embedding-001
- **LLM**: Gemini 3.0 Flash
- **Document Processing**: PyPDF2, pdfplumber, python-docx

### Frontend
- **Framework**: Next.js 15 with TypeScript
- **Styling**: TailwindCSS
- **Font**: Inter (Google Fonts)

## Setup Instructions

### Prerequisites

- Python 3.9+
- Node.js 18+
- Google AI API Key

### 1. Environment Setup

Create a `.env` file in the `rag-system` directory:

```bash
GOOGLE_API_KEY=your_google_api_key_here
```

Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey).

### 2. Backend Setup

```bash
# Navigate to project directory
cd rag-system

# Activate virtual environment
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies (already done)
# pip install -r requirements.txt

# Start the backend server
cd backend
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### 3. Frontend Setup

```bash
# In a new terminal, navigate to frontend
cd rag-system/frontend

# Install dependencies (already done)
# npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Usage

1. **Upload Documents**: Click "+ Upload Document" and drag-drop or select files
2. **Select Document** (Optional): Click on a document in the sidebar to search only in that document
3. **Ask Questions**: Type your question in the chat interface
4. **View Sources**: Answers include clickable source citations showing which document chunks were used

## API Endpoints

- `GET /` - Health check
- `POST /upload` - Upload and process a document
- `POST /query` - Query the system (non-streaming)
- `POST /query/stream` - Query with streaming response
- `WS /ws/query` - WebSocket endpoint for real-time queries
- `GET /documents` - List all uploaded documents
- `DELETE /documents/{filename}` - Delete a document

## Project Structure

```
rag-system/
├── backend/
│   ├── api/
│   │   ├── main.py          # FastAPI application
│   │   └── models.py        # Pydantic models
│   ├── chunking.py          # Text chunking strategies
│   ├── config.py            # Configuration management
│   ├── document_processor.py # Document parsing
│   ├── embeddings.py        # Embedding generation + caching
│   ├── generator.py         # LLM response generation
│   ├── prompts.py           # Prompt templates
│   ├── retrieval.py         # Retrieval logic
│   └── vector_store.py      # ChromaDB operations
├── frontend/
│   ├── app/
│   │   ├── page.tsx         # Main page
│   │   └── layout.tsx       # Root layout
│   ├── components/
│   │   ├── ChatInterface.tsx
│   │   ├── DocumentManager.tsx
│   │   └── DocumentUploader.tsx
│   └── lib/
│       └── api.ts           # API client
├── requirements.txt         # Python dependencies
└── README.md
```

## Configuration

Edit `backend/config.py` to adjust:

- **Chunk size**: Default 1000 tokens
- **Chunk overlap**: Default 200 tokens
- **Top-k results**: Default 5 chunks
- **Similarity threshold**: Default 0.7
- **Hybrid search**: Enabled by default

## Cost Optimization

- **Embedding caching**: SQLite-based cache prevents re-embedding same content
- **Configurable parameters**: Adjust chunk size and retrieval count to balance quality vs cost
- **Token monitoring**: Track API usage (implement in production)

## Error Handling

The system handles:
- Rate limiting with exponential backoff
- Context length overflow (automatically reduces context)
- Unsupported file types
- Missing documents
- Network errors

## Future Enhancements

- [ ] Re-ranking with cross-encoder or Cohere
- [ ] Multi-document synthesis
- [ ] Conversation memory
- [ ] Export chat history
- [ ] Document previews
- [ ] Advanced analytics

## License

MIT

## Support

For issues or questions, please open an issue on GitHub.
