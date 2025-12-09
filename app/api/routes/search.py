import logging
import time

from fastapi import APIRouter, Depends, HTTPException

from app.config.settings import get_db_service, get_embedding_service
from app.models.schemas import QueryRequest, SearchResponse
from app.services.database_service import DatabaseService
from app.services.embedding_service import EmbeddingService
from app.services.rag_service import RAGService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/semantic-search")
async def rag_query(
    query: QueryRequest,
    db_service: DatabaseService = Depends(get_db_service),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
):
    """RAG query endpoint"""
    start_time = time.time()

    try:
        # Validate input
        if not query.question or not query.question.strip():
            raise HTTPException(status_code=400, detail="La pregunta no puede estar vacía")

        # Create RAG service
        rag_service = RAGService(embedding_service, db_service)

        # Process RAG query
        result = await rag_service.rag_query(
            question=query.question, limit=query.limit, similarity_threshold=0.0
        )

        total_time = (time.time() - start_time) * 1000

        return SearchResponse(
            query=query.question,
            results=result,
            total_found=len(result.get("sources", [])),
            processing_time_ms=total_time,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in RAG query: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error interno del servidor en consulta RAG: {str(e)}"
        )
