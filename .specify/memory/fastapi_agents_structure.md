# FastAPI Structure with OpenAI Agents SDK Specification

## Overview
This document outlines the FastAPI application structure that integrates OpenAI Agents SDK for intelligent query processing over book content stored in Qdrant.

## Application Structure
```
app/
├── main.py                 # FastAPI application entry point
├── config/                 # Configuration settings
│   ├── __init__.py
│   └── settings.py
├── api/                    # API routes
│   ├── __init__.py
│   ├── v1/
│   │   ├── __init__.py
│   │   ├── search.py       # Search endpoints
│   │   ├── embeddings.py   # Embedding operations
│   │   └── agents.py       # Agent endpoints
├── services/               # Business logic
│   ├── __init__.py
│   ├── qdrant_service.py   # Qdrant operations
│   ├── gemini_service.py   # Gemini embedding operations
│   ├── agent_service.py    # OpenAI Agents operations
│   └── content_service.py  # Content processing
├── models/                 # Data models
│   ├── __init__.py
│   ├── search.py           # Search request/response models
│   ├── embeddings.py       # Embedding models
│   └── agents.py           # Agent models
├── utils/                  # Utility functions
│   ├── __init__.py
│   └── validators.py       # Validation utilities
└── core/                   # Core configurations
    ├── __init__.py
    ├── dependencies.py     # FastAPI dependencies
    └── middleware.py       # Application middleware
```

## Core Dependencies
- `fastapi`: Web framework
- `uvicorn`: ASGI server
- `openai`: OpenAI Agents SDK
- `qdrant-client`: Qdrant database client
- `google-generativeai`: Google's Gemini API client
- `pydantic`: Data validation
- `python-multipart`: File upload handling

## API Endpoints

### Search Endpoints (`/api/v1/search/`)
- `POST /query` - Semantic search with query processing
  - Request: Query text, top_k, similarity_threshold
  - Response: List of relevant content chunks with similarity scores

### Embedding Endpoints (`/api/v1/embeddings/`)
- `POST /process` - Process and store markdown files
  - Request: Markdown content or file upload
  - Response: Processing status and statistics
- `GET /status` - Get embedding collection status
  - Response: Collection info, vector count, etc.

### Agent Endpoints (`/api/v1/agents/`)
- `POST /query` - Process query using OpenAI Agent
  - Request: User query, context options
  - Response: Agent response with source citations
- `POST /chat` - Interactive chat with book content
  - Request: Chat messages history
  - Response: Agent response and follow-up suggestions

## OpenAI Agent Integration
- **Agent Type**: Retrieval Augmented Generation (RAG) agent
- **Tools**: Custom tools for Qdrant search and content retrieval
- **Memory**: Conversation history management
- **Response Format**: JSON with answer, sources, and confidence scores

## Middleware and Dependencies
- **Authentication**: Optional API key validation
- **Rate Limiting**: Per-endpoint rate limiting
- **Logging**: Structured logging for all requests
- **Error Handling**: Global exception handlers

## Configuration
- Environment-based settings for different deployment stages
- API key management for Gemini, OpenAI, and Qdrant
- Database connection settings
- Performance tuning parameters

## Health Checks
- `/health` - Overall application health
- `/health/qdrant` - Qdrant connection status
- `/health/gemini` - Gemini API connectivity
- `/health/openai` - OpenAI API connectivity

## Security Considerations
- Input validation for all endpoints
- Rate limiting to prevent abuse
- Secure handling of API keys
- CORS configuration for web frontend access