from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
from uuid import uuid4

from app.models.document import DocumentIngestionRequest, DocumentIngestionResponse, DocumentStatus, DocumentChunk
from app.core.database import get_qdrant_client, COLLECTION_NAME
from app.core.gemini_client import gemini_client
from app.utils.chunking import chunk_text_by_tokens as chunk_text
from app.utils.markdown_parser import extract_text_from_markdown as parse_markdown
from app.services.embedding_service import embedding_service

logger = logging.getLogger(__name__)


class IngestionService:
    """Service for ingesting documents into the RAG system."""

    def __init__(self):
        self._client = None

    @property
    def client(self):
        """Lazy load the Qdrant client when first accessed."""
        if self._client is None:
            self._client = get_qdrant_client()
        return self._client

    def ingest_document(self, request: DocumentIngestionRequest) -> DocumentIngestionResponse:
        """
        Ingest a document into the system.

        Args:
            request: Document ingestion request containing content and metadata

        Returns:
            DocumentIngestionResponse with ingestion status
        """
        try:
            # Generate document ID if not provided
            document_id = request.document_id or str(uuid4())
            logger.info(f"Starting ingestion for document: {document_id}")

            # Parse content if it's Markdown
            if request.metadata and request.metadata.file_type == "text/markdown":
                content = parse_markdown(request.content)
            else:
                content = request.content

            # Chunk the document content
            chunks = chunk_text(
                content,
                chunk_size=request.chunk_size,
                overlap_size=request.chunk_overlap
            )

            logger.info(f"Document {document_id} chunked into {len(chunks)} pieces")

            # Process and store each chunk
            processed_chunks = []
            for i, chunk_text in enumerate(chunks):
                chunk_id = f"{document_id}_chunk_{i}"

                # Generate embedding for the chunk
                embedding = embedding_service.generate_embedding(chunk_text)

                # Prepare payload for Qdrant
                payload = {
                    "document_id": document_id,
                    "content": chunk_text,
                    "chunk_id": chunk_id,
                    "metadata": request.metadata.dict() if request.metadata else {}
                }

                # Store in Qdrant
                self.client.upsert(
                    collection_name=COLLECTION_NAME,
                    points=[{
                        "id": chunk_id,
                        "vector": embedding,
                        "payload": payload
                    }]
                )

                processed_chunks.append(chunk_id)
                logger.debug(f"Stored chunk {chunk_id} for document {document_id}")

            # Create response
            response = DocumentIngestionResponse(
                document_id=document_id,
                status=DocumentStatus.INDEXED,
                chunks_processed=len(processed_chunks),
                message=f"Successfully ingested document with {len(processed_chunks)} chunks"
            )

            logger.info(f"Completed ingestion for document: {document_id}")
            return response

        except Exception as e:
            logger.error(f"Error during document ingestion: {e}")
            raise

    def validate_document_content(self, content: str, max_size: int = 10 * 1024 * 1024) -> bool:
        """
        Validate document content before ingestion.

        Args:
            content: Document content as text
            max_size: Maximum allowed size in bytes

        Returns:
            True if content is valid, False otherwise
        """
        try:
            content_size = len(content.encode('utf-8'))
            if content_size > max_size:
                logger.warning(f"Document size {content_size} exceeds maximum allowed size {max_size}")
                return False

            if not content.strip():
                logger.warning("Document content is empty")
                return False

            return True
        except Exception as e:
            logger.error(f"Error validating document content: {e}")
            return False

    def check_document_exists(self, document_id: str) -> bool:
        """
        Check if a document already exists in the system.

        Args:
            document_id: ID of the document to check

        Returns:
            True if document exists, False otherwise
        """
        try:
            # Try to retrieve the first chunk of the document
            records = self.client.scroll(
                collection_name=COLLECTION_NAME,
                scroll_filter={
                    "must": [
                        {
                            "key": "document_id",
                            "match": {
                                "value": document_id
                            }
                        }
                    ]
                },
                limit=1
            )

            # If any records were returned, the document exists
            return len(records[0]) > 0 if records else False
        except Exception as e:
            logger.error(f"Error checking if document exists: {e}")
            return False

    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document from the system.

        Args:
            document_id: ID of the document to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            # Find all chunks belonging to the document
            records = self.client.scroll(
                collection_name=COLLECTION_NAME,
                scroll_filter={
                    "must": [
                        {
                            "key": "document_id",
                            "match": {
                                "value": document_id
                            }
                        }
                    ]
                }
            )

            if records and records[0]:
                # Extract IDs of all chunks
                chunk_ids = [record.id for record in records[0]]

                # Delete all chunks
                self.client.delete(
                    collection_name=COLLECTION_NAME,
                    points_selector=chunk_ids
                )

                logger.info(f"Deleted {len(chunk_ids)} chunks for document {document_id}")
                return True
            else:
                logger.warning(f"No chunks found for document {document_id}")
                return False

        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            return False

    def get_document_status(self, document_id: str) -> DocumentStatus:
        """
        Get the processing status of a document.

        Args:
            document_id: ID of the document to check

        Returns:
            DocumentStatus indicating the current status
        """
        try:
            exists = self.check_document_exists(document_id)
            if exists:
                return DocumentStatus.INDEXED
            else:
                return DocumentStatus.PENDING
        except Exception as e:
            logger.error(f"Error getting document status: {e}")
            return DocumentStatus.FAILED


# Global instance
ingestion_service = IngestionService()