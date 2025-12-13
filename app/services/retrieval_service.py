from typing import List, Dict, Any, Optional
import logging
from uuid import uuid4

from qdrant_client.http import models
from app.core.database import get_qdrant_client, COLLECTION_NAME
from app.core.gemini_client import gemini_client
from app.core.config import settings

logger = logging.getLogger(__name__)


class RetrievalService:
    """Service for handling document retrieval from Qdrant vector database."""

    def __init__(self):
        self._client = None

    @property
    def client(self):
        """Lazy load the Qdrant client when first accessed."""
        if self._client is None:
            self._client = get_qdrant_client()
        return self._client

    def search_documents(self, query_text: str, top_k: int = 5, similarity_threshold: float = 0.5) -> List[Dict[str, Any]]:
        """
        Search for documents similar to the query text.

        Args:
            query_text: The query text to search for
            top_k: Number of top results to return
            similarity_threshold: Minimum similarity threshold for results

        Returns:
            List of dictionaries containing document information and similarity scores
        """
        try:
            # Validate inputs
            if not query_text.strip():
                raise ValueError("Query text cannot be empty")

            if top_k <= 0 or top_k > 50:
                raise ValueError("top_k must be between 1 and 50")

            if similarity_threshold < 0.0 or similarity_threshold > 1.0:
                raise ValueError("similarity_threshold must be between 0.0 and 1.0")

            # Generate embedding for the query
            query_embedding = gemini_client.embed_text(query_text)

            # Search in Qdrant collection
            search_results = self.client.search(
                collection_name=COLLECTION_NAME,
                query_vector=query_embedding,
                limit=top_k,
                score_threshold=similarity_threshold,
                with_payload=True,
                with_vectors=False
            )

            results = []
            for hit in search_results:
                results.append({
                    'chunk_id': hit.id,
                    'document_id': hit.payload.get('document_id', ''),
                    'content': hit.payload.get('content', ''),
                    'score': hit.score,
                    'metadata': hit.payload.get('metadata', {})
                })

            logger.info(f"Found {len(results)} relevant chunks for query: {query_text[:50]}...")
            return results

        except ValueError as ve:
            logger.error(f"Invalid input for document search: {ve}")
            raise
        except Exception as e:
            logger.error(f"Error during document search: {e}")
            raise

    def search_documents_with_context(self, query_text: str, top_k: int = 5, similarity_threshold: float = 0.5) -> str:
        """
        Search for documents and return them as a formatted context string.

        Args:
            query_text: The query text to search for
            top_k: Number of top results to return
            similarity_threshold: Minimum similarity threshold for results

        Returns:
            Formatted context string containing relevant document chunks
        """
        try:
            results = self.search_documents(query_text, top_k, similarity_threshold)

            if not results:
                return ""

            # Format results as a context string
            context_parts = []
            for result in results:
                context_parts.append(f"Document ID: {result['document_id']}")
                context_parts.append(f"Content: {result['content']}")
                context_parts.append(f"Relevance Score: {result['score']:.3f}")
                context_parts.append("---")

            return "\n".join(context_parts)

        except ValueError as ve:
            logger.error(f"Invalid input for context search: {ve}")
            raise
        except Exception as e:
            logger.error(f"Error during context search: {e}")
            raise

    def get_document_by_id(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific document by its ID.

        Args:
            document_id: The ID of the document to retrieve

        Returns:
            Document information if found, None otherwise
        """
        try:
            # Find points in Qdrant with the specific document_id in payload
            records = self.client.scroll(
                collection_name=COLLECTION_NAME,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="document_id",
                            match=models.MatchValue(value=document_id)
                        )
                    ]
                ),
                limit=1000  # Adjust as needed
            )

            if records:
                result = []
                for record in records[0]:  # First element is the records, second is offset
                    result.append({
                        'chunk_id': record.id,
                        'content': record.payload.get('content', ''),
                        'metadata': record.payload.get('metadata', {}),
                        'vector': record.vector
                    })
                return result

            return None
        except Exception as e:
            logger.error(f"Error retrieving document by ID {document_id}: {e}")
            raise

    def verify_connection(self) -> bool:
        """Verify that we can connect to Qdrant and access the collection."""
        try:
            # Try to get collection info
            collection_info = self.client.get_collection(COLLECTION_NAME)
            logger.info(f"Successfully connected to collection: {COLLECTION_NAME}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to collection {COLLECTION_NAME}: {e}")
            return False


# Global instance
retrieval_service = RetrievalService()