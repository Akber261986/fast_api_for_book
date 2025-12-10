from fastapi import APIRouter, Depends
from qdrant_client import QdrantClient

from app.config.settings import settings
from app.core.dependencies import get_qdrant_client
from app.services.gemini_service import GeminiService, get_gemini_service
from app.services.agent_service import AgentService, get_agent_service

router = APIRouter()


@router.get("/health/qdrant")
async def check_qdrant_health(qdrant_client: QdrantClient = Depends(get_qdrant_client)):
    """Check Qdrant connection status"""
    try:
        # Test connection by getting collections
        collections = qdrant_client.get_collections()
        return {
            "status": "ok",
            "connected": True,
            "collections_count": len(collections.collections)
        }
    except Exception as e:
        return {
            "status": "error",
            "connected": False,
            "error": str(e)
        }


@router.get("/health/gemini")
async def check_gemini_health(gemini_service: GeminiService = Depends(get_gemini_service)):
    """Check Gemini API connectivity"""
    try:
        is_valid = await gemini_service.validate_api_key()
        return {
            "status": "ok" if is_valid else "invalid_api_key",
            "connected": is_valid
        }
    except Exception as e:
        return {
            "status": "error",
            "connected": False,
            "error": str(e)
        }


@router.get("/health/openai")
async def check_openai_health(agent_service: AgentService = Depends(get_agent_service)):
    """Check OpenAI API connectivity"""
    try:
        is_valid = await agent_service.validate_api_key()
        return {
            "status": "ok" if is_valid else "invalid_api_key",
            "connected": is_valid
        }
    except Exception as e:
        return {
            "status": "error",
            "connected": False,
            "error": str(e)
        }


@router.get("/health/app")
async def check_app_health():
    """Check overall application health"""
    return {
        "status": "ok",
        "service": "book-search-api",
        "environment": settings.environment,
        "debug": settings.debug
    }


@router.get("/health/full")
async def check_full_health(
    qdrant_client: QdrantClient = Depends(get_qdrant_client),
    gemini_service: GeminiService = Depends(get_gemini_service),
    agent_service: AgentService = Depends(get_agent_service)
):
    """Check full system health including all services"""
    # Check Qdrant
    try:
        collections = qdrant_client.get_collections()
        qdrant_status = {
            "status": "ok",
            "connected": True,
            "collections_count": len(collections.collections)
        }
    except Exception as e:
        qdrant_status = {
            "status": "error",
            "connected": False,
            "error": str(e)
        }

    # Check Gemini
    try:
        gemini_valid = await gemini_service.validate_api_key()
        gemini_status = {
            "status": "ok" if gemini_valid else "invalid_api_key",
            "connected": gemini_valid
        }
    except Exception as e:
        gemini_status = {
            "status": "error",
            "connected": False,
            "error": str(e)
        }

    # Check OpenAI
    try:
        openai_valid = await agent_service.validate_api_key()
        openai_status = {
            "status": "ok" if openai_valid else "invalid_api_key",
            "connected": openai_valid
        }
    except Exception as e:
        openai_status = {
            "status": "error",
            "connected": False,
            "error": str(e)
        }

    overall_status = all([
        qdrant_status["connected"],
        gemini_status["connected"],
        openai_status["connected"]
    ])

    return {
        "status": "ok" if overall_status else "degraded",
        "timestamp": __import__('datetime').datetime.now().isoformat(),
        "services": {
            "qdrant": qdrant_status,
            "gemini": gemini_status,
            "openai": openai_status
        },
        "overall_health": overall_status
    }