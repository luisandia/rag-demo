import logging
from contextlib import asynccontextmanager, contextmanager
from typing import Any, AsyncGenerator, Dict, Generator, List

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.config.settings import DatabaseConfig
from app.models.document import LatamDoc
from app.repositories.document_repository import DocumentRepository

logger = logging.getLogger(__name__)


class DatabaseService:
    def __init__(self, db_config: DatabaseConfig):
        self.db_config = db_config

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Async context manager for database sessions"""
        async with self.db_config.SessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise e

    async def create_document(
        self, filename: str, content: str, embedding: list[float]
    ) -> LatamDoc:
        """Create a new document asynchronously"""
        async with self.get_session() as session:  # <- async with
            repo = DocumentRepository(session)
            doc = await repo.create_document(
                filename, content, embedding
            )  # await the async repo method
            return doc

    async def search_documents(
        self, query_embedding: List[float], limit: int = 10, similarity_threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """Search documents and return formatted results"""
        async with self.get_session() as session:
            repo = DocumentRepository(session)
            results = await repo.semantic_search(query_embedding, limit)
            return results
            # return [
            #     {
            #         "id": doc.id,
            #         "filename": doc.filename,
            #         "content": doc.content,
            #         "similarity": similarity,
            #         "created_at": doc.created_at.isoformat() if doc.created_at else None,
            #     }
            #     for doc, similarity in results
            # ]

    async def test_connection(self) -> bool:
        try:
            async for session in self.get_session():
                await session.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"=====Database connection test failed: {e}")
            return False
