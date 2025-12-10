from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse


class ContentProcessingError(Exception):
    """Raised when content processing fails"""
    pass


class EmbeddingGenerationError(Exception):
    """Raised when embedding generation fails"""
    pass


class QdrantConnectionError(Exception):
    """Raised when connection to Qdrant fails"""
    pass


class InvalidContentError(Exception):
    """Raised when content validation fails"""
    pass


class FileProcessingError(Exception):
    """Raised when file processing fails"""
    pass


async def content_processing_error_handler(request: Request, exc: ContentProcessingError):
    """Handle content processing errors"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Content processing error",
            "message": str(exc),
            "type": "content_processing_error"
        }
    )


async def embedding_generation_error_handler(request: Request, exc: EmbeddingGenerationError):
    """Handle embedding generation errors"""
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content={
            "error": "Embedding generation error",
            "message": str(exc),
            "type": "embedding_generation_error"
        }
    )


async def qdrant_connection_error_handler(request: Request, exc: QdrantConnectionError):
    """Handle Qdrant connection errors"""
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "error": "Qdrant connection error",
            "message": str(exc),
            "type": "qdrant_connection_error"
        }
    )


async def invalid_content_error_handler(request: Request, exc: InvalidContentError):
    """Handle invalid content errors"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Invalid content",
            "message": str(exc),
            "type": "invalid_content_error"
        }
    )


async def file_processing_error_handler(request: Request, exc: FileProcessingError):
    """Handle file processing errors"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "File processing error",
            "message": str(exc),
            "type": "file_processing_error"
        }
    )


def register_exception_handlers(app):
    """Register all custom exception handlers with the FastAPI app"""
    app.add_exception_handler(ContentProcessingError, content_processing_error_handler)
    app.add_exception_handler(EmbeddingGenerationError, embedding_generation_error_handler)
    app.add_exception_handler(QdrantConnectionError, qdrant_connection_error_handler)
    app.add_exception_handler(InvalidContentError, invalid_content_error_handler)
    app.add_exception_handler(FileProcessingError, file_processing_error_handler)