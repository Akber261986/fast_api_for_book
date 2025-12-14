from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import Dict, Any
import asyncio
import httpx

from app.core.config import settings

router = APIRouter()


@router.get("/deep-health")
async def deep_health_check():
    """
    Deep health check that tests connectivity to external services.
    This is for diagnostic purposes and not intended for deployment health checks.
    """
    results = {
        "basic_status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "environment": settings.ENVIRONMENT,
        "checks": {}
    }

    # Check if Gemini API key is set
    results["checks"]["gemini_api_key"] = {
        "status": "configured" if settings.GEMINI_API_KEY else "missing"
    }

    # Check if Qdrant is accessible (with timeout)
    try:
        if settings.QDRANT_HOST:
            qdrant_url = f"http://{settings.QDRANT_HOST}:{settings.QDRANT_PORT}/collections"
            timeout = httpx.Timeout(10.0)  # 10 second timeout for Qdrant
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(qdrant_url)
                if response.status_code in [200, 404]:  # 200 = OK, 404 = service up but no collections
                    results["checks"]["qdrant_connection"] = {
                        "status": "connected",
                        "host": settings.QDRANT_HOST,
                        "response_time_ms": getattr(response, 'elapsed', {}).total_seconds() * 1000 if hasattr(response, 'elapsed') else 'unknown'
                    }
                else:
                    results["checks"]["qdrant_connection"] = {
                        "status": "connection_error",
                        "error": f"Status {response.status_code}",
                        "host": settings.QDRANT_HOST
                    }
        else:
            results["checks"]["qdrant_connection"] = {
                "status": "configuration_missing",
                "error": "QDRANT_HOST not set"
            }
    except Exception as e:
        results["checks"]["qdrant_connection"] = {
            "status": "connection_error",
            "error": str(e),
            "host": settings.QDRANT_HOST
        }

    # Overall assessment
    connection_errors = [k for k, v in results["checks"].items() 
                         if v.get("status") == "connection_error" or v.get("status") == "configuration_missing"]
    
    if connection_errors:
        results["basic_status"] = "degraded"
    
    return results