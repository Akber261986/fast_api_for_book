import logging
import time
import uuid
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
)
logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Custom logging middleware for API requests"""

    def __init__(self, app: FastAPI):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        request_id = str(uuid.uuid4())

        # Add request ID to request state
        request.state.request_id = request_id

        # Log incoming request
        logger.info(
            f"Request ID: {request_id} | "
            f"Method: {request.method} | "
            f"Path: {request.url.path} | "
            f"IP: {request.client.host if request.client else 'unknown'} | "
            f"User-Agent: {request.headers.get('user-agent', 'unknown')}"
        )

        response = await call_next(request)

        # Add request ID to response headers
        response.headers["x-request-id"] = request_id

        # Calculate response time
        process_time = time.time() - start_time

        # Log the response
        logger.info(
            f"Request ID: {request_id} | "
            f"Response Status: {response.status_code} | "
            f"Process Time: {process_time:.3f}s"
        )

        return response


def add_logging_middleware(app: FastAPI):
    """Add logging middleware to the FastAPI application"""
    app.middleware("http")(LoggingMiddleware(app))


async def error_handler_middleware(request: Request, call_next: Callable):
    """Middleware to handle errors globally"""
    request_id = str(uuid.uuid4())
    try:
        response = await call_next(request)
        return response
    except Exception as exc:
        logger.error(
            f"Request ID: {request_id} | "
            f"Unhandled exception: {type(exc).__name__}: {str(exc)} | "
            f"Path: {request.url.path} | "
            f"Method: {request.method}",
            exc_info=True
        )

        # Return a consistent error response
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": "An unexpected error occurred",
                "request_id": request_id
            }
        )


def setup_middlewares(app: FastAPI):
    """Setup all middlewares for the application"""
    # Add error handling middleware
    app.middleware("http")(error_handler_middleware)

    # The LoggingMiddleware class already handles logging, so no need to add the function-based middleware
    pass