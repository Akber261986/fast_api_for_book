from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, field_validator


class Message(BaseModel):
    """Model for chat messages"""
    message_id: str
    role: str  # user, assistant, system
    content: str
    timestamp: datetime
    sources: Optional[List[Dict]] = []

    @field_validator('role')
    def validate_role(cls, v):
        if v not in ['user', 'assistant', 'system']:
            raise ValueError('role must be one of: user, assistant, system')
        return v

    @field_validator('content')
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError('content cannot be empty')
        return v


class ChatSession(BaseModel):
    """Model for chat sessions"""
    session_id: str
    messages: List[Message] = []
    created_at: datetime
    updated_at: datetime
    context: Optional[Dict[str, str]] = {}

    @field_validator('messages')
    def validate_messages_length(cls, v):
        if len(v) > 100:
            raise ValueError('messages list cannot exceed 100 items')
        return v


class AgentQueryRequest(BaseModel):
    """Model for agent query requests"""
    query: str
    context_window: int = 5
    max_tokens: int = 500
    temperature: float = 0.3

    @field_validator('query')
    def validate_query(cls, v):
        if not v.strip():
            raise ValueError('query cannot be empty')
        if len(v) > 1000:
            raise ValueError('query must be less than 1000 characters')
        return v

    @field_validator('context_window')
    def validate_context_window(cls, v):
        if v < 1 or v > 20:
            raise ValueError('context_window must be between 1 and 20')
        return v


class AgentQueryResponse(BaseModel):
    """Model for agent query responses"""
    response: str
    sources: List[Dict]
    query: str
    timestamp: datetime


class ChatRequest(BaseModel):
    """Model for chat requests"""
    message: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, str]] = {}

    @field_validator('message')
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError('message cannot be empty')
        if len(v) > 2000:
            raise ValueError('message must be less than 2000 characters')
        return v


class ChatResponse(BaseModel):
    """Model for chat responses"""
    response: str
    sources: List[Dict]
    session_id: str
    timestamp: datetime


class AgentStatusResponse(BaseModel):
    """Model for agent status responses"""
    status: str
    model: str
    capabilities: List[str]
    timestamp: datetime