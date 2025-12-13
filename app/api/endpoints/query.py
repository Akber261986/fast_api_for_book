from fastapi import APIRouter, HTTPException, Depends
from typing import List
import logging

from app.models.query import QueryRequest, QueryResponse
from app.services.retrieval_service import retrieval_service
from app.services.generation_service import generation_service
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    """
    Query the RAG system to get answers based on ingested documents.

    Args:
        request: Query request with text and parameters

    Returns:
        QueryResponse with answer and source information
    """
    try:
        logger.info(f"Processing query: {request.query[:50]}...")

        # Validate query parameters
        if request.top_k <= 0 or request.top_k > 20:
            raise HTTPException(
                status_code=400,
                detail="top_k must be between 1 and 20"
            )

        if request.similarity_threshold < 0.0 or request.similarity_threshold > 1.0:
            raise HTTPException(
                status_code=400,
                detail="similarity_threshold must be between 0.0 and 1.0"
            )

        # Retrieve relevant documents based on the query
        retrieved_chunks = retrieval_service.search_documents(
            query_text=request.query,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold
        )

        if not retrieved_chunks:
            # If no relevant documents found, generate response without context
            logger.warning(f"No relevant documents found for query: {request.query[:50]}...")
            response = generation_service.generate_response(
                query=request.query,
                context=None,
                source_chunks=[]
            )
            # Set low confidence when no context is available
            response.confidence = 0.2
            return response

        # Build context from retrieved chunks
        context = retrieval_service.search_documents_with_context(
            query_text=request.query,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold
        )

        # Generate response using the context
        response = generation_service.generate_response(
            query=request.query,
            context=context,
            source_chunks=retrieved_chunks
        )

        logger.info(f"Query processed successfully, returned answer with {len(retrieved_chunks)} source chunks")
        return response

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


@router.get("/test")
async def test_query():
    """
    Test endpoint to verify query functionality.
    """
    return {
        "message": "Query endpoint is working",
        "model": settings.GEMINI_MODEL
    }