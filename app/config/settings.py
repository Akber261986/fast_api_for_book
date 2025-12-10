from pydantic import BaseModel
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # API Keys
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    qdrant_api_key: Optional[str] = None

    # Qdrant Configuration
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_https: bool = False

    # Application Configuration
    environment: str = "development"
    debug: bool = True

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000

    # Qdrant Collection Configuration
    qdrant_collection_name: str = "book_content"

    # Embedding Configuration
    embedding_model: str = "text-embedding-004"  # Gemini model
    embedding_dimensions: int = 768

    # Search Configuration
    default_top_k: int = 5
    default_similarity_threshold: float = 0.7
    max_top_k: int = 20

    # Content Processing Configuration
    chunk_size: int = 1000  # characters
    chunk_overlap: int = 100  # characters

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,  # Changed to False to allow case-insensitive matching
        "extra": "ignore"  # This allows extra fields from the environment
    }


class QdrantConfig(BaseModel):
    host: str
    port: int
    api_key: Optional[str] = None
    https: bool = False
    collection_name: str = "book_content"


class GeminiConfig(BaseModel):
    api_key: Optional[str] = None
    model: str = "text-embedding-004"
    dimensions: int = 768


class SearchConfig(BaseModel):
    default_top_k: int = 5
    default_similarity_threshold: float = 0.7
    max_top_k: int = 20


# Global settings instance
settings = Settings()