from datetime import datetime
from typing import Any, Dict

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, DateTime, Index, Integer, String, Text

from app.models.base import Base


class LatamDoc(Base):
    __tablename__ = "latam_docs"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Document metadata
    filename = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)

    # Vector embedding for semantic search
    embedding = Column(Vector(1536), nullable=False)  # pgvector column

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Optional metadata fields
    file_size = Column(Integer, nullable=True)
    content_length = Column(Integer, nullable=True)
    document_type = Column(String(50), nullable=True, default="text")

    # Indexes for performance
    __table_args__ = (
        Index("idx_filename", "filename"),
        Index("idx_created_at", "created_at"),
        Index("idx_document_type", "document_type"),
    )

    def __repr__(self):
        return f"<LatamDoc(id={self.id}, filename='{self.filename}')>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "filename": self.filename,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "file_size": self.file_size,
            "content_length": self.content_length,
            "document_type": self.document_type,
        }
