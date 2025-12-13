from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import uuid4


class QueryRequest(BaseModel):
    """Request model for query endpoint."""
    query: str = Field(..., min_length=1, max_length=1000, description="Natural language query")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of results to retrieve")
    similarity_threshold: float = Field(default=0.5, ge=0.0, le=1.0, description="Minimum similarity threshold")


class QueryResponse(BaseModel):
    """Response model for query endpoint."""
    response_id: str
    query: str
    answer: str
    source_chunks: List[dict]  # Will contain chunk information
    confidence: float = Field(ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=datetime.now)


class QueryChunk(BaseModel):
    """Model for a single chunk in query response."""
    chunk_id: str
    document_id: str
    content: str
    score: float = Field(ge=0.0, le=1.0)