# CLEO Tech Help Chatbot Backend

A RAG-powered chatbot API to help seniors with technology questions.

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Frontend      │────▶│   FastAPI        │────▶│   RAG Pipeline  │
│   (Vercel)      │◀────│   (Railway)      │◀────│                 │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                          │
                                                          ▼
                                                 ┌─────────────────┐
                                                 │   LanceDB       │
                                                 │   Vector Store  │
                                                 └─────────────────┘
                                                          │
                                                          ▼
                                                 ┌─────────────────┐
                                                 │   OpenAI        │
                                                 │   (GPT-4o-mini) │
                                                 └─────────────────┘
```

## Features

- **RAG-powered responses** - Answers grounded in curated tech help content
- **Senior-friendly prompts** - Warm, patient, step-by-step explanations
- **Streaming support** - Real-time response streaming
- **Reranking + MMR** - High-quality retrieval with diversity
- **Incremental indexing** - Only re-indexes changed files

## Local Development

### Prerequisites

- Python 3.11+
- OpenAI API key

### Setup

1. **Create a virtual environment:**
   ```bash
   cd rag
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables:**
   ```bash
   export OPENAI_API_KEY=sk-your-key-here
   ```

4. **Ingest the tech help corpus:**
   ```bash
   python ingest.py
   ```

5. **Start the API server:**
   ```bash
   uvicorn api.main:app --reload --port 8000
   ```

6. **Test the API:**
   ```bash
   curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "How do I make a video call?"}'
   ```

## API Endpoints

### `GET /`
Health check - returns service status.

### `GET /health`
Detailed health check with document count.

### `POST /chat`
Send a chat message.

**Request:**
```json
{
  "message": "How do I send a text message?",
  "stream": false
}
```

**Response:**
```json
{
  "response": "I'd be happy to help you send a text message! Here's how...",
  "sources": ["smartphones.md"]
}
```

### `POST /chat/stream`
Streaming chat endpoint - returns Server-Sent Events.

## Deployment to Railway

### Quick Deploy

1. **Connect your GitHub repo to Railway**

2. **Set environment variables in Railway:**
   - `OPENAI_API_KEY` - Your OpenAI API key
   - `FRONTEND_URL` - Your Vercel frontend URL (for CORS)

3. **Deploy!** Railway will use `railway.toml` for configuration.

### Manual Setup

1. Create a new Railway project
2. Connect to your GitHub repo
3. Set the root directory to `rag/`
4. Add environment variables
5. Deploy

### Ingesting Documents

After deployment, you'll need to ingest the corpus:

```bash
# SSH into your Railway service or run locally with the same DB
python ingest.py
```

For persistent storage, configure a Railway volume for the `./rag_db` directory.

## Adding New Content

1. Add markdown/text files to the `corpus/` directory
2. Run `python ingest.py` to index them
3. The chatbot will now use the new content

### Corpus Topics

Current topics covered:
- `smartphones.md` - Basic smartphone usage
- `video-calling.md` - FaceTime, Zoom, Google Meet
- `email-basics.md` - Email setup and usage
- `social-media.md` - Facebook, Instagram, YouTube
- `internet-safety.md` - Scams, passwords, safe browsing
- `computers.md` - Computer basics

## Configuration

See `api/main.py` for pipeline configuration options:

- `embedding_model` - Sentence transformer model
- `llm_model` - OpenAI model for generation
- `use_reranking` - Enable cross-encoder reranking
- `use_mmr` - Enable diversity in results

## Frontend Integration

The frontend chatbot component connects to this API:

```typescript
const API_URL = import.meta.env.VITE_CHATBOT_API_URL || 'http://localhost:8000';

const response = await fetch(`${API_URL}/chat`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: userQuestion }),
});
```

Set `VITE_CHATBOT_API_URL` in Vercel to your Railway backend URL.
