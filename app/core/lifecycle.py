import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from typing import AsyncGenerator

from app.services.qdrant_service import initialize_qdrant_service, get_qdrant_service
from app.services.gemini_service import initialize_gemini_service, get_gemini_service
from app.services.agent_service import initialize_agent_service, get_agent_service
from app.services.content_service import initialize_content_service, get_content_service


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager for startup and shutdown events
    """
    logger.info("Starting up application...")

    # Startup: Initialize all services
    try:
        # Initialize Qdrant service first
        qdrant_service = initialize_qdrant_service()
        logger.info("Qdrant service initialized")

        # Initialize Gemini service second
        gemini_service = initialize_gemini_service()
        logger.info("Gemini service initialized")

        # Initialize Content service third (depends on Qdrant and Gemini)
        content_service = initialize_content_service()
        logger.info("Content service initialized")

        # Initialize Agent service last (depends on Content service)
        agent_service = initialize_agent_service()
        logger.info("Agent service initialized")

        # Initialize the Qdrant collection if needed
        try:
            is_initialized = await qdrant_service.initialize_collection()
            if is_initialized:
                logger.info("Qdrant collection initialized successfully")
            else:
                logger.warning("Failed to initialize Qdrant collection")
        except Exception as e:
            logger.error(f"Error initializing Qdrant collection: {str(e)}")

        logger.info("All services initialized successfully")

    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise

    # Yield control to the application
    yield

    # Shutdown: Clean up resources
    logger.info("Shutting down application...")
    try:
        # Close Qdrant client if it exists
        try:
            qdrant_service = get_qdrant_service()
            if hasattr(qdrant_service, 'client') and qdrant_service.client:
                qdrant_service.client.close()
                logger.info("Qdrant client closed")
        except Exception as e:
            logger.error(f"Error closing Qdrant client: {str(e)}")

        # Any other cleanup tasks can go here
        logger.info("Application shutdown completed")

    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")
        raise


def setup_lifespan(app: FastAPI):
    """
    Set up the lifespan for the FastAPI application
    """
    # The lifespan is already set in the app initialization, so we don't need this function
    pass