from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Environment
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Gemini API
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # Qdrant Configuration
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_GRPC_PORT: int = 6334
    QDRANT_HTTPS: bool = False

    # Application
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB in bytes
    CHUNK_SIZE: int = 1000  # Number of tokens per chunk
    CHUNK_OVERLAP: int = 200  # Number of tokens to overlap between chunks

    # API
    API_V1_STR: str = "/api/v1"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

    def validate_environment(self):
        """Validate that required settings are present based on environment."""
        if self.is_production and not self.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required in production environment")
        return True

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra environment variables


settings = Settings()