from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import search, embeddings, agents, health
from app.core.middleware import add_logging_middleware, LoggingMiddleware
from app.core.rate_limiter import setup_rate_limiter
from app.core.exceptions import register_exception_handlers
from app.core.metrics import MetricsMiddleware, get_metrics
from app.core.lifecycle import lifespan

app = FastAPI(
    title="FastAPI Book Search with Qdrant and Gemini",
    description="""
# FastAPI Book Search API

This API provides semantic search capabilities for book content using vector embeddings.

## Features

- **Semantic Search**: Search book content using natural language queries
- **AI-Powered Chat**: Interactive conversations with book content using AI agents
- **Content Ingestion**: Process and index markdown files for search
- **Vector Embeddings**: Powered by Google's Gemini embedding models

## Endpoints

The API is organized into several main categories:

- `/api/v1/search/` - Semantic search functionality
- `/api/v1/agents/` - AI agent and chat functionality
- `/api/v1/embeddings/` - Content ingestion and embedding processing
- `/api/v1/health/` - Health check endpoints

## Authentication

Most endpoints are publicly accessible, but require proper API keys to be configured
in the service backends (Qdrant, Gemini).

## Rate Limits

- Search endpoints: 100 requests per minute
- Chat endpoints: 50 requests per minute
- Ingestion endpoints: 10 requests per hour
- Health check endpoints: 1000 requests per minute
    """,
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom logging middleware - use the new BaseHTTPMiddleware approach
app.add_middleware(LoggingMiddleware)

# Setup rate limiting
setup_rate_limiter(app)

# Register exception handlers
register_exception_handlers(app)

# Add metrics middleware
app.add_middleware(MetricsMiddleware)

# Include API routes
app.include_router(search.router, prefix="/api/v1", tags=["search"])
app.include_router(embeddings.router, prefix="/api/v1", tags=["embeddings"])
app.include_router(agents.router, prefix="/api/v1", tags=["agents"])
app.include_router(health.router, prefix="/api/v1", tags=["health"])

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    """Endpoint to expose Prometheus metrics"""
    data, content_type = get_metrics()
    return data

from pydantic import BaseModel
from typing import Optional

# Pydantic models for request validation
class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5

class ExplainSelectedRequest(BaseModel):
    query: str
    selected_text: str
    top_k: Optional[int] = 5

# Simple endpoints for frontend integration
@app.post("/query")
async def query_endpoint(request: QueryRequest):
    """
    Handle general queries about the book content
    Expected request format: {"query": "user question", "top_k": 5}
    Expected response format: {"answer": "response text"}
    """
    try:
        from app.services.content_service import get_content_service
        from app.services.agent_service import get_agent_service

        content_service = get_content_service()
        agent_service = get_agent_service()

        # Perform the search
        search_results = await content_service.search_content(
            query=request.query,
            top_k=request.top_k,
            similarity_threshold=0.6
        )

        # Format context from search results
        context_text = "\n".join([
            f"Content: {result['text'][:500]}{'...' if len(result['text']) > 500 else ''}\nSource: {result['source_file']}\n"
            for result in search_results
        ])

        # Generate response using agent service
        full_query = f"Based on the following context, answer the question: {request.query}\n\nContext:\n{context_text}"

        response = await agent_service.create_completion(
            prompt=full_query,
            max_tokens=500
        )

        return {"answer": response}
    except Exception as e:
        print(f"Error in query endpoint: {str(e)}")
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

@app.post("/explain-selected")
async def explain_selected_endpoint(request: ExplainSelectedRequest):
    """
    Handle explanations for selected text
    Expected request format: {"query": "Explain this: selected text", "selected_text": "selected text", "top_k": 5}
    Expected response format: {"answer": "explanation"}
    """
    try:
        from app.services.agent_service import get_agent_service

        agent_service = get_agent_service()

        # Generate explanation for the selected text
        explanation_query = f"Please explain the following text in detail: {request.selected_text}"

        response = await agent_service.create_completion(
            prompt=explanation_query,
            max_tokens=500
        )

        return {"answer": response}
    except Exception as e:
        print(f"Error in explain-selected endpoint: {str(e)}")
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Explanation processing failed: {str(e)}")

# Root health check
@app.get("/health")
async def root_health():
    return {"status": "ok", "service": "book-search-api"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)