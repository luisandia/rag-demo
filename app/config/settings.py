import os
from typing import AsyncGenerator, Generator

from alembic.config import Config
from dotenv import load_dotenv
from openai import AsyncOpenAI
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from app.models.base import Base

load_dotenv()
# Constants
VECTOR_DIMENSION = 1536

engine = create_async_engine(
    os.getenv("DATABASE_URL", "postgresql+psycopg://user:password@localhost:5432/rag_db"),
    echo=os.getenv("DB_ECHO", "false").lower() == "true",
    pool_pre_ping=True,
    pool_size=2,
    max_overflow=1,
    pool_recycle=300,
)

SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Database Configuration
class DatabaseConfig:
    def __init__(self):
        self.database_url = os.getenv(
            "DATABASE_URL", "postgresql+psycopg://user:password@localhost:5432/rag_db"
        )
        self.SessionLocal = SessionLocal
        self.engine = engine

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Dependency for FastAPI"""
        async with self.SessionLocal() as session:
            yield session


# OpenAI Configuration
class OpenAIConfig:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

    def get_client(self):
        return AsyncOpenAI(api_key=self.api_key)


# Application Configuration
class AppConfig:
    def __init__(self):
        self.app_title = "LATAM RAG Search"
        self.app_description = "API de búsqueda semántica con FastAPI y pgvector"
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", "DEBUG")


# Global instances
db_config = DatabaseConfig()
openai_config = OpenAIConfig()
app_config = AppConfig()


# Dependency injection
def get_db_service():
    from app.services.database_service import DatabaseService

    return DatabaseService(db_config)


def get_openai_client():
    return openai_config.get_client()


def get_embedding_service():
    from app.services.embedding_service import EmbeddingService

    return EmbeddingService(get_openai_client())
