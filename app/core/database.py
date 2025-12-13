from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import Optional, List
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize Qdrant client
qdrant_client = QdrantClient(
    host=settings.QDRANT_HOST,
    port=settings.QDRANT_PORT,
    api_key=settings.QDRANT_API_KEY,
    grpc_port=settings.QDRANT_GRPC_PORT,
    prefer_grpc=True
)

# Collection name for document embeddings
COLLECTION_NAME = "document_embeddings"

def get_qdrant_client() -> QdrantClient:
    """Return the Qdrant client instance."""
    return qdrant_client

def ensure_collection_exists():
    """Ensure the document embeddings collection exists with proper configuration."""
    try:
        # Check if collection already exists
        collections = qdrant_client.get_collections()
        collection_names = [collection.name for collection in collections.collections]

        if COLLECTION_NAME not in collection_names:
            # Create collection with cosine distance for semantic similarity
            qdrant_client.create_collection(
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
        # Test connection
        qdrant_client.get_collections()
        logger.info("Successfully connected to Qdrant")

        # Ensure collection exists
        ensure_collection_exists()
        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise