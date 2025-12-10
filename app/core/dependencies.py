from typing import Generator

from fastapi import Depends, HTTPException, status
from qdrant_client import QdrantClient

from app.config.settings import settings


def get_qdrant_client() -> Generator[QdrantClient, None, None]:
    """
    Dependency to get Qdrant client instance.
    This creates a new client instance for each request.
    """
    try:
        client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
            api_key=settings.qdrant_api_key,
            https=settings.qdrant_https,
        )
        # Test connection
        client.get_collections()
        yield client
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Could not connect to Qdrant: {str(e)}"
        )
    finally:
        # Close the client connection
        if 'client' in locals():
            client.close()


def get_gemini_api_key():
    """
    Dependency to get Gemini API key with validation.
    """
    if not settings.gemini_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GEMINI_API_KEY not configured in environment"
        )
    return settings.gemini_api_key


def get_openai_api_key():
    """
    Dependency to get OpenAI API key with validation.
    """
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OPENAI_API_KEY not configured in environment"
        )
    return settings.openai_api_key