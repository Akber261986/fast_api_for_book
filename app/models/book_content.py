from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator


class BookContent(BaseModel):
    """Model for book content chunks with metadata"""
    id: str
    text: str
    embedding: Optional[list] = None  # Optional since it might not always be included
    source_file: str
    section: Optional[str] = None
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    @field_validator('text')
    def validate_text_length(cls, v):
        if len(v) < 10 or len(v) > 2000:
            raise ValueError('text must be between 10 and 2000 characters')
        return v

    @field_validator('source_file')
    def validate_source_file(cls, v):
        if not v or len(v) > 500:
            raise ValueError('source_file must be provided and not exceed 500 characters')
        return v

    @field_validator('id')
    def validate_id(cls, v):
        if not v or len(v) > 100:
            raise ValueError('id must be provided and not exceed 100 characters')
        return v