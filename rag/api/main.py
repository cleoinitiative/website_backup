"""FastAPI backend for CLEO Tech Help Chatbot."""

import os
import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.pipeline import RAGPipeline, PipelineConfig
from src.generation.prompts import PromptTemplate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global pipeline instance
pipeline: Optional[RAGPipeline] = None


# Senior-friendly prompt template for tech help
SENIOR_TECH_HELP_PROMPT = PromptTemplate(
    name="senior_tech_help",
    description="Friendly, patient prompt for helping seniors with technology questions",
    system_template="""You are a friendly and patient technology helper for the CLEO Initiative. 
You're helping seniors learn about and use technology. 

Your communication style should be:
- WARM and ENCOURAGING - celebrate their curiosity about technology
- CLEAR and SIMPLE - avoid jargon, use everyday language
- STEP-BY-STEP - break down instructions into small, numbered steps
- PATIENT - never make them feel rushed or silly for asking
- SPECIFIC - give concrete examples they can relate to

Guidelines:
- Answer based on the provided context when available
- If you don't have specific information, give helpful general guidance
- Use analogies to everyday objects when explaining tech concepts
- Suggest they ask a CLEO volunteer for hands-on help if the task is complex
- Always end with an encouraging note

IMPORTANT: These are seniors who may be new to technology. Be supportive and kind.""",
    
    user_template="""Information that may be helpful:
$context

---

Question from a senior: $query

Please provide a helpful, friendly response. Use simple language and numbered steps when giving instructions.""",
)


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str
    stream: bool = False


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str
    sources: list[str] = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize RAG pipeline on startup."""
    global pipeline
    
    logger.info("Initializing RAG pipeline...")
    
    # Configure pipeline for production
    config = PipelineConfig(
        # Database path - use environment variable or default
        db_path=os.getenv("RAG_DB_PATH", "./rag_db"),
        table_name="tech_help",
        
        # Embedding settings
        embedding_model="BAAI/bge-base-en-v1.5",
        embedding_device=os.getenv("EMBEDDING_DEVICE", "cpu"),
        
        # Generation settings
        llm_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        llm_temperature=0.3,  # Slightly higher for warmth
        llm_max_tokens=1024,
        
        # Retrieval settings
        use_reranking=True,
        use_mmr=True,
        mmr_lambda=0.7,
        initial_k=15,
    )
    
    pipeline = RAGPipeline(config)
    
    # Check if we have documents indexed
    try:
        doc_count = pipeline.vector_store.count()
        logger.info(f"RAG pipeline ready with {doc_count} chunks indexed")
    except Exception as e:
        logger.warning(f"Vector store not yet initialized: {e}")
        logger.info("Run the ingestion script to populate the knowledge base")
    
    yield
    
    logger.info("Shutting down RAG pipeline...")
    if pipeline:
        pipeline.shutdown()


app = FastAPI(
    title="CLEO Tech Help Chatbot API",
    description="RAG-powered chatbot to help seniors with technology questions",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev
        "http://localhost:3000",  # Alternative dev
        "https://cleoinitiative.org",  # Production
        "https://www.cleoinitiative.org",  # Production www
        os.getenv("FRONTEND_URL", ""),  # Custom frontend URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "CLEO Tech Help Chatbot"}


@app.get("/health")
async def health():
    """Detailed health check."""
    global pipeline
    
    health_status = {
        "status": "healthy",
        "pipeline_ready": pipeline is not None,
        "documents_indexed": 0,
    }
    
    if pipeline:
        try:
            health_status["documents_indexed"] = pipeline.vector_store.count()
        except Exception:
            pass
    
    return health_status


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint for technology help questions.
    
    Retrieves relevant context from the knowledge base and generates
    a friendly, senior-appropriate response.
    """
    global pipeline
    
    if not pipeline:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    try:
        # Use streaming if requested
        if request.stream:
            return StreamingResponse(
                stream_response(request.message),
                media_type="text/event-stream",
            )
        
        # Non-streaming response
        response = await pipeline.ask_async(
            query=request.message,
            limit=5,
            prompt_template=SENIOR_TECH_HELP_PROMPT,
        )
        
        return ChatResponse(
            response=response.content,
            sources=response.sources,
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(
            status_code=500,
            detail="I'm having trouble right now. Please try again in a moment.",
        )


async def stream_response(message: str):
    """Stream chat response chunks."""
    global pipeline
    
    try:
        async for chunk in pipeline.ask_stream_async(
            query=message,
            limit=5,
            prompt_template=SENIOR_TECH_HELP_PROMPT,
        ):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"
    except Exception as e:
        logger.error(f"Stream error: {e}")
        yield f"data: I'm having trouble right now. Please try again.\n\n"
        yield "data: [DONE]\n\n"


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Streaming chat endpoint."""
    global pipeline
    
    if not pipeline:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    return StreamingResponse(
        stream_response(request.message),
        media_type="text/event-stream",
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("ENV", "development") == "development",
    )
