import logging
import time
from typing import List, Optional

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(self, client: AsyncOpenAI):
        self.client = client
        self.model = "text-embedding-ada-002"

    async def get_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for a single text"""
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return None

        try:
            start_time = time.time()
            response = await self.client.embeddings.create(model=self.model, input=text.strip())
            embedding = response.data[0].embedding
            processing_time = (time.time() - start_time) * 1000

            logger.info(
                f"Generated embedding in {processing_time:.2f}ms for text length: {len(text)}"
            )
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def validate_embedding(self, embedding: List[float]) -> bool:
        """Validate embedding format and dimensions"""
        if not isinstance(embedding, list):
            return False
        if len(embedding) != 1536:  # OpenAI embedding dimension
            return False
        if not all(isinstance(x, (int, float)) for x in embedding):
            return False
        return True

    async def test_connection(self) -> bool:
        """Test OpenAI API connection"""
        try:
            await self.get_embedding("test")
            return True
        except Exception as e:
            logger.error(f"OpenAI connection test failed: {e}")
            return False
