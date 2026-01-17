# 🚀 Quick Start Guide - RAG System

## Prerequisites Check
- [x] Python 3.9+ installed
- [x] Node.js 18+ installed
- [x] Virtual environment created
- [ ] Google API key obtained

## Step 1: Get Your Google API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the key

## Step 2: Configure Environment

Add your API key to the `.env` file:

```bash
# File: rag-system/.env
GOOGLE_API_KEY=your_actual_api_key_here
```

## Step 3: Test the Backend

```bash
cd rag-system
.\venv\Scripts\activate
cd backend
python test_setup.py
```

You should see:
```
✓ All tests passed! The RAG system is ready to use.
```

## Step 4: Start the Backend Server

```bash
# From the backend directory
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will run at: `http://localhost:8000`

## Step 5: Start the Frontend

Open a **NEW terminal window**:

```bash
cd rag-system/frontend
npm run dev
```

Frontend will run at: `http://localhost:3000`

## Step 6: Use the Application

1. **Open browser**: Go to `http://localhost:3000`
2. **Upload document**: Click "+ Upload Document" and drag-drop `sample_documents/ai_introduction.md`
3. **Wait for processing**: You'll see "Successfully uploaded" message
4. **Ask a question**: Type "What types of AI exist?" in the chat
5. **View results**: See the AI-generated answer with source citations!

## Sample Questions to Try

With `ai_introduction.md`:
- "What is the difference between narrow AI and general AI?"
- "What are some applications of AI in healthcare?"
- "What ethical concerns are associated with AI?"

With `python_basics.md`:
- "What are the key features of Python?"
- "What is Python used for?"
- "Why is Python good for beginners?"

## Troubleshooting

### "Error: API key not found"
→ Make sure you added `GOOGLE_API_KEY` to the `.env` file in the rag-system directory

### "Connection refused" on frontend
→ Make sure the backend is running on port 8000

### "Module not found" errors
→ Make sure you activated the virtual environment: `.\venv\Scripts\activate`

### Uploads failing
→ Check that the file type is supported (PDF, DOCX, MD, TXT)

## What's Included

✅ **Backend Features**:
- Document processing (PDF, DOCX, MD, TXT)
- Smart text chunking
- Google embeddings with caching
- Hybrid search (vector + keyword)
- Gemini 1.5 Pro generation
- Streaming responses

✅ **Frontend Features**:
- Modern, beautiful UI
- Drag-and-drop upload
- Real-time chat
- Source citations
- Document management
- Dark mode support

## Next Steps

1. Upload your own documents
2. Experiment with different question types
3. Try filtering by specific documents
4. Check out the README.md for advanced configuration

## Need Help?

- Check [README.md](file:///c:/Users/User/Documents/test/rag-system/README.md) for detailed documentation
- Review [walkthrough.md](file:///c:/Users/User/.gemini/antigravity/brain/f1c3c828-161c-490e-9758-946be1ef1b59/walkthrough.md) for technical details
- Look at backend code comments for implementation details

Enjoy your RAG system! 🎉
