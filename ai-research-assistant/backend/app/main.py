"""
FastAPI Main Application Entrypoint.
Includes routers for papers, chat, and research agent.
Initializes PostgreSQL pgvector database on startup.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.connection import init_db
from app.api import papers, chat, research

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing database and pgvector extension...")
    try:
        init_db()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.warning(f"Database initialization deferred/failed: {e}")
    yield
    # Shutdown
    logger.info("Shutting down application...")


app = FastAPI(
    title="AI Research Assistant API",
    description="End-to-end AI Research Assistant supporting paper search, AI summarization, PDF RAG chat, and automated research synthesis.",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health Check Endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring uptime.
    Returns 200 OK if the service is running.
    """
    return {
        "status": "healthy",
        "service": "AI Research Assistant API",
        "version": "1.0.0"
    }

# Include API Routers
app.include_router(papers.router)
app.include_router(chat.router)
app.include_router(research.router)


@app.get("/")
def home():
    return {
        "status": "online",
        "message": "AI Research Assistant API is running!",
        "docs": "/docs"
    }