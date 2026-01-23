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


# Prompt template for tech help AND CLEO information
SENIOR_TECH_HELP_PROMPT = PromptTemplate(
    name="cleo_assistant",
    description="Friendly assistant for tech help and learning about CLEO",
    system_template="""You are a friendly and helpful assistant for the CLEO Initiative (Computer Literacy Education Outreach).

You help with TWO main things:
1. **Technology Help** - Assisting seniors with technology questions (smartphones, computers, video calls, email, internet safety, etc.)
2. **CLEO Information** - Answering questions about CLEO, how to start a chapter, volunteer opportunities, our mission, and how we help seniors

Your communication style:
- WARM and WELCOMING - whether talking to seniors, students, or anyone curious about CLEO
- CLEAR and SIMPLE - avoid jargon, use everyday language
- STEP-BY-STEP - break down instructions into small, numbered steps
- ENCOURAGING - celebrate curiosity and interest in helping others
- HELPFUL - provide specific, actionable information

Guidelines:
- Answer based on the provided context when available
- For tech questions: use analogies, be patient, suggest asking a CLEO volunteer for hands-on help
- For CLEO questions: share our mission, explain how chapters work, encourage getting involved
- If you don't have specific information, give helpful general guidance
- Always end with an encouraging note or next step

About CLEO: We connect high school student volunteers with seniors to help bridge the digital divide. Students form chapters at their schools and partner with senior centers and assisted living facilities to provide technology education.""",
    
    user_template="""Information that may be helpful:
$context

---

Question: $query

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


def get_pipeline_config() -> PipelineConfig:
    """Get pipeline configuration."""
    return PipelineConfig(
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
        
        # Retrieval settings (reranking disabled - requires heavy local models)
        use_reranking=False,
        use_mmr=True,
        mmr_lambda=0.7,
        initial_k=15,
    )


def init_pipeline():
    """Initialize the pipeline (called lazily on first request)."""
    global pipeline
    if pipeline is None:
        logger.info("Loading RAG pipeline (this may take a minute)...")
        pipeline = RAGPipeline(get_pipeline_config())
        try:
            doc_count = pipeline.vector_store.count()
            logger.info(f"RAG pipeline ready with {doc_count} chunks indexed")
        except Exception as e:
            logger.warning(f"Vector store check failed: {e}")
    return pipeline


@asynccontextmanager
async def lifespan(app: FastAPI):
    """App lifespan - pipeline loads lazily on first request."""
    logger.info("CLEO Chatbot API starting...")
    logger.info("Pipeline will load on first request")
    
    yield
    
    logger.info("Shutting down...")
    global pipeline
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
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=False,  # Must be False when using "*"
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
    pipeline = init_pipeline()
    
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
    pipeline = init_pipeline()
    
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
    pipeline = init_pipeline()
    
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
