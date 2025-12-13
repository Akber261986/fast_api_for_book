from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class EmbeddingRequest(BaseModel):
    """Request model for embedding generation."""
    text: str = Field(..., min_length=1, description="Text to generate embedding for")
    model: Optional[str] = Field(default="models/embedding-001", description="Embedding model to use")


class EmbeddingResponse(BaseModel):
    """Response model for embedding generation."""
    embedding: List[float]
    model: str
    text_length: int
    timestamp: datetime = Field(default_factory=datetime.now)


class DocumentEmbedding(BaseModel):
    """Model for a document embedding stored in the database."""
    document_id: str
    chunk_id: str
    text: str
    embedding: List[float]
    metadata: dict = {}
    created_at: datetime = Field(default_factory=datetime.now)