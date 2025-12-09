from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class DocumentType(str, Enum):
    TEXT = "text"
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000, description="Question to search")
    limit: Optional[int] = Field(10, ge=1, le=100, description="Maximum number of results")
    similarity_threshold: Optional[float] = Field(
        0.0, ge=0.0, le=1.0, description="Minimum similarity threshold"
    )


class DocumentResponse(BaseModel):
    id: int
    filename: str
    content: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    file_size: Optional[int] = None
    content_length: Optional[int] = None
    document_type: Optional[str] = None


class SearchResponse(BaseModel):
    query: str
    results: Any
    total_found: int
    processing_time_ms: float
    similarity_threshold_used: Optional[float] = None


class UploadResponse(BaseModel):
    message: str
    filename: str
    document_id: int
    processing_time_ms: float
    content_length: Optional[int] = None
    document_type: str = DocumentType.TEXT
