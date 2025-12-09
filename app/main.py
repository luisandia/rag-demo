import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.documents import router as document_router
from app.api.routes.search import router as search_router

from .config.settings import app_config, get_db_service, get_embedding_service

logging.basicConfig(
    level=getattr(logging, app_config.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting RAG API...")

    # Test database connection
    db_service = get_db_service()
    if not db_service.test_connection():
        logger.error("Database connection failed")
        raise Exception("Cannot connect to database")

    # Test OpenAI connection
    embedding_service = get_embedding_service()
    if not await embedding_service.test_connection():
        logger.error("OpenAI connection failed")
        raise Exception("Cannot connect to OpenAI")

    logger.info("RAG API started successfully")

    yield

    # Shutdown
    logger.info("Shutting down RAG API...")


app = FastAPI(
    title=app_config.app_title,
    description=app_config.app_description,
    debug=app_config.debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(document_router, prefix="/documents", tags=["Documents"])
app.include_router(search_router, prefix="/search", tags=["Search"])


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_service = get_db_service()
    embedding_service = get_embedding_service()

    return {
        "status": "healthy",
        "database_connected": db_service.test_connection(),
        "openai_connected": await embedding_service.test_connection(),
        "timestamp": time.time(),
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "RAG Search API", "version": "1.0.0", "status": "running"}
