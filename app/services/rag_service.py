import logging
import time
from typing import Any, Dict, List

from openai import AsyncOpenAI

from app.models.document import LatamDoc
from app.services.database_service import DatabaseService
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class RAGService:
    def __init__(self, embedding_service: EmbeddingService, database_service: DatabaseService):
        self.embedding_service = embedding_service
        self.database_service = database_service
        self.openai_client = embedding_service.client

    async def search_similar_documents(
        self, query: str, limit: int = 10, similarity_threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """Search for similar documents based on query"""
        try:
            start_time = time.time()

            # Generate query embedding
            query_embedding = await self.embedding_service.get_embedding(query)
            if not query_embedding:
                return []

            # Search database
            results = await self.database_service.search_documents(
                query_embedding, limit, similarity_threshold
            )

            search_time = (time.time() - start_time) * 1000
            logger.info(
                f"RAG search completed in {search_time:.2f}ms, found {len(results)} results"
            )

            return results
        except Exception as e:
            logger.error(f"Error in RAG search: {e}")
            raise

    async def generate_response(self, context: List[str], question: str) -> str:
        """Generate response using OpenAI with context"""
        try:
            start_time = time.time()

            # Format context
            full_context = "\n---\n".join(context)

            # System prompt for LATAM Airlines
            system_prompt = (
                "Eres un asistente de servicio al cliente de LATAM Airlines. "
                "Responde a la pregunta del usuario de forma concisa usando ÚNICAMENTE el contexto proporcionado. "
                "Si la respuesta no está en el contexto, di: 'Lo siento, no tengo esa información en las políticas internas.'"
            )

            # Generate response
            completion = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": f"Contexto:\n{full_context}\n\nPregunta: {question}",
                    },
                ],
                max_tokens=500,
                temperature=0.3,
            )

            response = completion.choices[0].message.content
            generation_time = (time.time() - start_time) * 1000

            logger.info(f"Generated response in {generation_time:.2f}ms")
            return response
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise

    async def rag_query(
        self, question: str, limit: int = 10, similarity_threshold: float = 0.0
    ) -> Dict[str, Any]:
        """Complete RAG query process"""
        try:
            start_time = time.time()

            # Search for similar documents
            search_results = await self.search_similar_documents(
                question, limit, similarity_threshold
            )

            if not search_results:
                return {
                    "answer": "No se encontró información relevante en los documentos de política.",
                    "context_used": [],
                    "sources": [],
                }

            # Extract context
            context_chunks = [result["content"] for result in search_results]
            sources = [
                {"filename": result["filename"], "similarity": result["similarity"]}
                for result in search_results
            ]
            # Generate response
            answer = await self.generate_response(context_chunks, question)
            total_time = (time.time() - start_time) * 1000

            return {
                "answer": answer,
                "context_used": context_chunks,
                "sources": sources,
                "processing_time_ms": total_time,
            }
        except Exception as e:
            logger.error(f"Error in RAG query: {e}")
            raise
