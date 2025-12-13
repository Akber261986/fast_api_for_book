from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class DocumentStatus(str, Enum):
    """Status of document processing."""
    PENDING = "pending_ingestion"
    PROCESSING = "processing"
    PROCESSED = "processed"
    INDEXED = "indexed_in_qdrant"
    FAILED = "failed"


class DocumentMetadata(BaseModel):
    """Metadata for a document."""
    source: Optional[str] = None  # Source of the document (e.g., 'upload', 'url', 'api')
    file_name: Optional[str] = None
    file_size: Optional[int] = None  # Size in bytes
    file_type: Optional[str] = None  # MIME type or extension
    author: Optional[str] = None
    created_date: Optional[datetime] = None
    modified_date: Optional[datetime] = None
    tags: List[str] = []
    custom_metadata: Dict[str, Any] = {}


class DocumentChunk(BaseModel):
    """A chunk of a document."""
    chunk_id: str
    document_id: str
    content: str
    metadata: Dict[str, Any] = {}
    position: int = 0  # Position in the original document
    token_count: int = 0


class DocumentIngestionRequest(BaseModel):
    """Request model for document ingestion."""
    document_id: Optional[str] = None  # If not provided, will be auto-generated
    content: str  # Document content as text
    metadata: Optional[DocumentMetadata] = None
    chunk_size: int = 1000  # Number of tokens per chunk
    chunk_overlap: int = 200  # Number of tokens to overlap between chunks


class DocumentIngestionResponse(BaseModel):
    """Response model for document ingestion."""
    document_id: str
    status: DocumentStatus
    chunks_processed: int
    message: str
    timestamp: datetime = datetime.now()


class DocumentQuery(BaseModel):
    """Query parameters for document operations."""
    document_id: Optional[str] = None
    status: Optional[DocumentStatus] = None
    tags: List[str] = []
    limit: int = 10
    offset: int = 0


class DocumentInfo(BaseModel):
    """Information about a stored document."""
    document_id: str
    status: DocumentStatus
    metadata: DocumentMetadata
    chunk_count: int
    created_at: datetime
    updated_at: datetime