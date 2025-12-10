from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, field_validator

from app.models.book_content import BookContent


class SearchQuery(BaseModel):
    """Model for search queries"""
    query_text: str
    top_k: int = 5
    similarity_threshold: float = 0.7
    filters: Optional[Dict[str, str]] = {}
    user_context: Optional[str] = None

    @field_validator('query_text')
    def validate_query_text(cls, v):
        if len(v) < 1 or len(v) > 500:
            raise ValueError('query_text must be between 1 and 500 characters')
        return v

    @field_validator('top_k')
    def validate_top_k(cls, v):
        if v < 1 or v > 20:
            raise ValueError('top_k must be between 1 and 20')
        return v

    @field_validator('similarity_threshold')
    def validate_similarity_threshold(cls, v):
        if v < 0.0 or v > 1.0:
            raise ValueError('similarity_threshold must be between 0.0 and 1.0')
        return v


class SearchResult(BaseModel):
    """Model for search results"""
    content: BookContent
    similarity_score: float
    rank: int
    explanation: Optional[str] = None

    @field_validator('similarity_score')
    def validate_similarity_score(cls, v):
        if v < 0.0 or v > 1.0:
            raise ValueError('similarity_score must be between 0.0 and 1.0')
        return v

    @field_validator('rank')
    def validate_rank(cls, v):
        if v < 1:
            raise ValueError('rank must be a positive integer')
        return v


class SearchResponse(BaseModel):
    """Model for search responses"""
    query: str
    results: List[SearchResult]
    total_results: int


class SearchQueryWithEmbedding(SearchQuery):
    """Model for search queries that include pre-generated embeddings"""
    query_embedding: Optional[List[float]] = None


class SemanticSearchRequest(SearchQuery):
    """Enhanced search request model with additional options"""
    include_metadata: bool = True
    return_explanations: bool = False