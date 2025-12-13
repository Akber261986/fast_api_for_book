from typing import List
import logging
from datetime import datetime

from app.core.gemini_client import gemini_client
from app.models.embedding import DocumentEmbedding

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating embeddings using Gemini."""

    def __init__(self):
        pass

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate a single embedding for the provided text.

        Args:
            text: Text to generate embedding for

        Returns:
            Embedding vector as a list of floats
        """
        try:
            embedding = gemini_client.embed_text(text)
            logger.info(f"Generated embedding for text of length {len(text)}")
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of texts to generate embeddings for

        Returns:
            List of embedding vectors
        """
        try:
            embeddings = gemini_client.generate_embeddings(texts)
            logger.info(f"Generated {len(embeddings)} embeddings")
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise

    def create_document_embedding(self, document_id: str, chunk_id: str, text: str, metadata: dict = None) -> DocumentEmbedding:
        """
        Create a DocumentEmbedding object with generated embedding.

        Args:
            document_id: ID of the parent document
            chunk_id: ID of this specific chunk
            text: Text content to embed
            metadata: Optional metadata to store with the embedding

        Returns:
            DocumentEmbedding object with generated embedding
        """
        try:
            embedding = self.generate_embedding(text)

            document_embedding = DocumentEmbedding(
                document_id=document_id,
                chunk_id=chunk_id,
                text=text,
                embedding=embedding,
                metadata=metadata or {}
            )

            logger.info(f"Created document embedding for document {document_id}, chunk {chunk_id}")
            return document_embedding
        except Exception as e:
            logger.error(f"Error creating document embedding: {e}")
            raise

    def validate_embedding_dimension(self, embedding: List[float], expected_dimension: int = 768) -> bool:
        """
        Validate that an embedding has the expected dimension.

        Args:
            embedding: Embedding vector to validate
            expected_dimension: Expected dimension (default 768 for Gemini)

        Returns:
            True if dimension matches, False otherwise
        """
        return len(embedding) == expected_dimension

    def normalize_embedding(self, embedding: List[float]) -> List[float]:
        """
        Normalize an embedding vector to unit length.
        This can help with similarity calculations.

        Args:
            embedding: Embedding vector to normalize

        Returns:
            Normalized embedding vector
        """
        import math
        magnitude = math.sqrt(sum(x * x for x in embedding))
        if magnitude == 0:
            return embedding  # Return as is if zero vector
        return [x / magnitude for x in embedding]


# Global instance
embedding_service = EmbeddingService()