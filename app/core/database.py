from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import Optional, List
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Qdrant client will be initialized lazily when first accessed
_qdrant_client = None

def get_qdrant_client() -> QdrantClient:
    """Return the Qdrant client instance, creating it if it doesn't exist."""
    global _qdrant_client
    if _qdrant_client is None:
        # Check if QDRANT_HOST is a full URL (for cloud instances)
        if settings.QDRANT_HOST.startswith(('http://', 'https://')):
            # For cloud instances, use URL with api_key
            _qdrant_client = QdrantClient(
                url=settings.QDRANT_HOST,
                api_key=settings.QDRANT_API_KEY,
                grpc_port=settings.QDRANT_GRPC_PORT,
                prefer_grpc=True
            )
        else:
            # For local instances, use host/port
            _qdrant_client = QdrantClient(
                host=settings.QDRANT_HOST,
                port=settings.QDRANT_PORT,
                api_key=settings.QDRANT_API_KEY,
                grpc_port=settings.QDRANT_GRPC_PORT,
                prefer_grpc=True
            )
    return _qdrant_client

# Collection name for document embeddings
COLLECTION_NAME = "document_embeddings"

def ensure_collection_exists():
    """Ensure the document embeddings collection exists with proper configuration."""
    try:
        client = get_qdrant_client()
        # Check if collection already exists
        collections = client.get_collections()
        collection_names = [collection.name for collection in collections.collections]

        if COLLECTION_NAME not in collection_names:
            # Create collection with cosine distance for semantic similarity
            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=models.VectorParams(
                    size=768,  # Gemini embedding dimension
                    distance=models.Distance.COSINE
                )
            )
            logger.info(f"Created Qdrant collection: {COLLECTION_NAME}")
        else:
            logger.info(f"Qdrant collection {COLLECTION_NAME} already exists")
    except Exception as e:
        logger.error(f"Error ensuring collection exists: {e}")
        raise

def initialize_database():
    """Initialize the database connection and ensure required collections exist."""
    try:
        client = get_qdrant_client()
        # Test connection
        client.get_collections()
        logger.info("Successfully connected to Qdrant")

        # Ensure collection exists
        ensure_collection_exists()
        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise