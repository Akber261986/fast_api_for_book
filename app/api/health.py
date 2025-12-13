from fastapi import APIRouter
from datetime import datetime
from typing import Dict, Any
import asyncio
import httpx

from app.core.config import settings

router = APIRouter()


@router.get("/detailed_health")
async def detailed_health_check():
    """Detailed health check that verifies external dependencies"""
    checks = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "checks": {}
    }

    # Check if Gemini API key is accessible
    try:
        if settings.GEMINI_API_KEY:
            checks["checks"]["gemini_configured"] = {"status": "ok", "message": "API key present"}
        else:
            checks["checks"]["gemini_configured"] = {"status": "error", "message": "GEMINI_API_KEY not set"}
    except Exception as e:
        checks["checks"]["gemini_configured"] = {"status": "error", "message": f"Gemini config error: {str(e)}"}

    # Check if Qdrant is accessible (basic connectivity check)
    try:
        qdrant_url = f"http://{settings.QDRANT_HOST}:{settings.QDRANT_PORT}/collections"
        timeout = httpx.Timeout(5.0)  # 5 second timeout
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(qdrant_url)
            if response.status_code in [200, 404]:  # 404 means service is reachable
                checks["checks"]["qdrant_connection"] = {"status": "ok", "message": f"Connected to {settings.QDRANT_HOST}"}
            else:
                checks["checks"]["qdrant_connection"] = {"status": "warning", "message": f"Qdrant responded with status {response.status_code}"}
    except Exception as e:
        checks["checks"]["qdrant_connection"] = {"status": "error", "message": f"Cannot connect to Qdrant: {str(e)}"}

    return checks