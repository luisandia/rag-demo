import json
import logging
from typing import List, Optional, Tuple

from pgvector.sqlalchemy import Vector
from sqlalchemy import func, literal, select, text
from sqlalchemy.orm import Session

from app.models.document import LatamDoc

logger = logging.getLogger(__name__)


class DocumentRepository:
    def __init__(self, session: Session):
        self.session = session

    async def create_document(
        self, filename: str, content: str, embedding: List[float]
    ) -> LatamDoc:
        try:
            doc = LatamDoc(filename=filename, content=content, embedding=embedding)
            self.session.add(doc)
            await self.session.commit()
            await self.session.refresh(doc)
            logger.info(f"Created document: {doc.id} - {filename}")
            return doc
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error creating document: {e}")
            raise

    async def semantic_search(self, query_embedding: List[float], limit: int = 3) -> List[dict]:
        try:

            # Convert to JSON
            embedding_json = json.dumps(query_embedding)

            # Use literal with explicit type annotation

            vector_literal = literal(embedding_json).cast(Vector)

            # Build query
            query = (
                select(
                    LatamDoc.id,
                    LatamDoc.filename,
                    LatamDoc.content,
                    LatamDoc.document_type,
                    LatamDoc.created_at,
                )
                .add_columns(
                    func.cosine_distance(LatamDoc.embedding, vector_literal).label("distance"),
                    (1 - func.cosine_distance(LatamDoc.embedding, vector_literal)).label(
                        "similarity"
                    ),
                )
                .order_by("distance")
                .limit(limit)
            )

            # Execute
            result = await self.session.execute(query)

            # Process results
            documents = []
            for row in result:
                doc_data = {
                    "id": row[0],
                    "filename": row[1],
                    "content": row[2],
                    "document_type": row[3],
                    "created_at": row[4].isoformat() if row[4] else None,
                    "distance": float(row[5]),
                    "similarity": float(row[6]),
                }
                documents.append(doc_data)

            return documents

        except Exception as e:
            logger.error(f"Semantic search error: {e}", exc_info=True)
            return []
