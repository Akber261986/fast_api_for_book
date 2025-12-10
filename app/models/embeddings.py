from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, field_validator


class EmbeddingJob(BaseModel):
    """Model for content processing jobs"""
    job_id: str
    status: str  # pending, processing, completed, failed
    source_files: List[str]
    progress: int = 0
    total: int = 0
    created_at: datetime
    completed_at: Optional[datetime] = None

    @field_validator('status')
    def validate_status(cls, v):
        if v not in ['pending', 'processing', 'completed', 'failed']:
            raise ValueError('status must be one of: pending, processing, completed, failed')
        return v

    @field_validator('progress')
    def validate_progress(cls, v, values):
        if 'total' in values.data and v > values.data['total']:
            raise ValueError('progress cannot exceed total')
        return v


class EmbeddingRequest(BaseModel):
    """Model for embedding generation requests"""
    text: str
    source_file: Optional[str] = None
    metadata: Optional[Dict[str, str]] = {}

    @field_validator('text')
    def validate_text_length(cls, v):
        if len(v) < 1 or len(v) > 10000:  # Reasonable upper limit
            raise ValueError('text must be between 1 and 10000 characters')
        return v


class BatchEmbeddingRequest(BaseModel):
    """Model for batch embedding generation requests"""
    texts: List[EmbeddingRequest]
    rebuild_collection: bool = False


class MarkdownProcessingRequest(BaseModel):
    """Model for markdown file processing requests"""
    source_files: List[str]
    rebuild_collection: bool = False


class EmbeddingResponse(BaseModel):
    """Model for embedding generation responses"""
    id: str
    text: str
    embedding: List[float]
    source_file: Optional[str] = None
    created_at: datetime


class BatchEmbeddingResponse(BaseModel):
    """Model for batch embedding generation responses"""
    embeddings: List[EmbeddingResponse]
    processed_count: int
    total_count: int


class EmbeddingJobStatus(BaseModel):
    """Model for embedding job status responses"""
    job_id: str
    status: str
    progress: int
    total: int
    message: str
    created_at: datetime
    completed_at: Optional[datetime] = None