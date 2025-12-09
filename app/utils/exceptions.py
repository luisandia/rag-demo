import logging
from typing import Optional

from fastapi import HTTPException

logger = logging.getLogger(__name__)


class RAGException(Exception):
    """Base exception for RAG application"""

    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(message)


class DatabaseException(RAGException):
    """Database related exceptions"""

    pass


class EmbeddingException(RAGException):
    """Embedding generation exceptions"""

    pass


class ValidationException(RAGException):
    """Input validation exceptions"""

    pass


def handle_exception(exc: Exception) -> HTTPException:
    """Convert custom exceptions to HTTPException"""
    if isinstance(exc, RAGException):
        logger.error(f"RAG Exception: {exc.message}")
        return HTTPException(status_code=400, detail=exc.message)
    elif isinstance(exc, DatabaseException):
        logger.error(f"Database Exception: {exc.message}")
        return HTTPException(status_code=500, detail="Error en la base de datos")
    elif isinstance(exc, EmbeddingException):
        logger.error(f"Embedding Exception: {exc.message}")
        return HTTPException(status_code=500, detail="Error generando embeddings")
    else:
        logger.error(f"Unexpected Exception: {str(exc)}")
        return HTTPException(status_code=500, detail="Error interno del servidor")
