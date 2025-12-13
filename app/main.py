import json
import logging
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.endpoints import query, ingest


class EventFilter(logging.Filter):
    """Custom filter to exclude certain log events."""

    def filter(self, record):
        # Filter out noisy events
        if "GET /health" in record.getMessage():
            return False
        return True


def setup_structured_logging():
    """Set up structured logging with JSON output."""
    # Configure standard logging
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format="%(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )

    # Add custom filter
    logging.getLogger().addFilter(EventFilter())

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle application startup and shutdown events.
    """
    # Startup
    setup_structured_logging()
    logger = structlog.get_logger()
    logger.info("Starting RAG System for Markdown Files API", version="1.0.0")

    yield

    # Shutdown
    logger = structlog.get_logger()
    logger.info("Shutting down RAG System for Markdown Files API")


app = FastAPI(
    title="RAG System for Markdown Files API",
    description="API for querying Markdown files using Retrieval-Augmented Generation",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, configure specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# Include API routes
app.include_router(query.router, prefix="/query", tags=["query"])
app.include_router(ingest.router, prefix="/ingest", tags=["ingest"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.ENVIRONMENT == "development" else False
    )