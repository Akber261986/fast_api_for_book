from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List

from app.models.search import SearchQuery, SearchResponse, SemanticSearchRequest
from app.services.content_service import ContentService, get_content_service
from app.core.rate_limiter import limiter, SEARCH_RATE_LIMIT, HEALTH_RATE_LIMIT

router = APIRouter()


@router.post("/search/query", response_model=Dict)
@limiter.limit(SEARCH_RATE_LIMIT)
async def semantic_search(
    request,
    search_query: SearchQuery,
    content_service: ContentService = Depends(get_content_service)
):
    """Perform semantic search on book content using natural language queries"""
    try:
        # Additional validation beyond Pydantic
        if len(search_query.query_text.strip()) < 2:
            raise HTTPException(
                status_code=400,
                detail="Query text must be at least 2 characters long"
            )

        if search_query.top_k > 20:
            raise HTTPException(
                status_code=400,
                detail="top_k cannot exceed 20"
            )

        # Perform the search
        results = await content_service.search_content(
            query=search_query.query_text,
            top_k=search_query.top_k,
            similarity_threshold=search_query.similarity_threshold,
            filters=search_query.filters
        )

        # Format the response
        formatted_results = []
        for result in results:
            formatted_results.append({
                "content": {
                    "id": result["id"],
                    "text": result["text"],
                    "source_file": result["source_file"],
                    "section": result["section"],
                    "title": result["title"]
                },
                "similarity_score": result["similarity_score"],
                "rank": result["rank"]
            })

        response = {
            "query": search_query.query_text,
            "results": formatted_results,
            "total_results": len(formatted_results)
        }

        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


@router.post("/search/advanced", response_model=Dict)
@limiter.limit(SEARCH_RATE_LIMIT)
async def advanced_search(
    request,
    search_request: SemanticSearchRequest,
    content_service: ContentService = Depends(get_content_service)
):
    """Perform advanced semantic search with additional options"""
    try:
        # Additional validation beyond Pydantic
        if len(search_request.query_text.strip()) < 2:
            raise HTTPException(
                status_code=400,
                detail="Query text must be at least 2 characters long"
            )

        if search_request.top_k > 20:
            raise HTTPException(
                status_code=400,
                detail="top_k cannot exceed 20"
            )

        # Perform the search
        results = await content_service.search_content(
            query=search_request.query_text,
            top_k=search_request.top_k,
            similarity_threshold=search_request.similarity_threshold,
            filters=search_request.filters
        )

        # Format the response based on request options
        formatted_results = []
        for result in results:
            result_dict = {
                "content": {
                    "id": result["id"],
                    "text": result["text"],
                    "source_file": result["source_file"],
                    "section": result["section"],
                    "title": result["title"]
                },
                "similarity_score": result["similarity_score"],
                "rank": result["rank"]
            }

            # Add explanations if requested
            if search_request.return_explanations:
                result_dict["explanation"] = f"Content matches query with similarity score {result['similarity_score']}"

            formatted_results.append(result_dict)

        response = {
            "query": search_request.query_text,
            "results": formatted_results,
            "total_results": len(formatted_results)
        }

        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Advanced search failed: {str(e)}"
        )


@router.get("/search/status")
@limiter.limit(HEALTH_RATE_LIMIT)
async def search_status(
    request,
    content_service: ContentService = Depends(get_content_service)
):
    """Get the status of the search service"""
    try:
        # Check if services are available
        # This is a basic check - in a real implementation you might check more detailed status
        return {
            "status": "ok",
            "service": "semantic-search",
            "capabilities": ["semantic-search", "filtering", "similarity-thresholding"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Status check failed: {str(e)}"
        )


@router.post("/search/validate")
@limiter.limit(SEARCH_RATE_LIMIT)
async def validate_search_query(
    request,
    search_query: SearchQuery
):
    """Validate a search query without executing it"""
    try:
        # Basic validation is handled by Pydantic, but we can add additional checks
        errors = []

        if len(search_query.query_text.strip()) < 3:
            errors.append("Query text should be at least 3 characters long")

        if search_query.top_k > 50:
            errors.append("top_k should not exceed 50 for performance reasons")

        if errors:
            return {
                "valid": False,
                "errors": errors
            }

        return {
            "valid": True,
            "message": "Query is valid"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Validation failed: {str(e)}"
        )


@router.get("/search/collections")
@limiter.limit(HEALTH_RATE_LIMIT)
async def get_search_collections(
    request,
    content_service: ContentService = Depends(get_content_service)
):
    """Get information about available search collections"""
    try:
        # In a real implementation, this would return information about collections
        # For now, we'll return basic information
        from app.services.qdrant_service import get_qdrant_service
        qdrant_service = get_qdrant_service()
        collection_status = await qdrant_service.get_collection_status()

        return {
            "collections": [collection_status],
            "total_collections": 1
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get collections: {str(e)}"
        )