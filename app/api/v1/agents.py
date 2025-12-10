from fastapi import APIRouter, Depends, HTTPException
from typing import Dict

from app.models.agents import ChatRequest, ChatResponse, AgentQueryRequest, AgentQueryResponse
from app.services.agent_service import AgentService, get_agent_service
from app.core.rate_limiter import limiter, CHAT_RATE_LIMIT, HEALTH_RATE_LIMIT

router = APIRouter()


@router.post("/agents/query", response_model=Dict)
@limiter.limit(CHAT_RATE_LIMIT)
async def agent_query(
    request,
    query_request: AgentQueryRequest,
    agent_service: AgentService = Depends(get_agent_service)
):
    """Process a query using OpenAI Agent with book content context"""
    try:
        # Process the query with context from book content
        result = await agent_service.generate_response_with_sources(
            query=query_request.query,
            context=[],  # Context will be retrieved internally based on the query
            max_tokens=query_request.max_tokens
        )

        response = AgentQueryResponse(
            response=result["response"],
            sources=result["sources"],
            query=query_request.query,
            timestamp=__import__('datetime').datetime.now()
        )

        return response.dict()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Agent query failed: {str(e)}"
        )


@router.post("/agents/chat", response_model=Dict)
@limiter.limit(CHAT_RATE_LIMIT)
async def chat_with_agent(
    request,
    chat_request: ChatRequest,
    agent_service: AgentService = Depends(get_agent_service)
):
    """Interactive chat with the book content using AI agent"""
    try:
        # Additional validation beyond Pydantic
        if not chat_request.message or len(chat_request.message.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Message cannot be empty"
            )

        if len(chat_request.message) > 2000:
            raise HTTPException(
                status_code=400,
                detail="Message too long, maximum 2000 characters"
            )

        # Process the chat query with conversation context
        result = await agent_service.process_chat_query(
            query=chat_request.message,
            session_id=chat_request.session_id,
            context_window=chat_request.context.get("context_window", 5),
            max_tokens=500
        )

        response = ChatResponse(
            response=result["response"],
            sources=result["sources"],
            session_id=result["session_id"],
            timestamp=__import__('datetime').datetime.now()
        )

        return response.dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chat with agent failed: {str(e)}"
        )


@router.post("/agents/session/create", response_model=Dict)
@limiter.limit(CHAT_RATE_LIMIT)
async def create_chat_session(
    request,
    context: Dict = None,
    agent_service: AgentService = Depends(get_agent_service)
):
    """Create a new chat session"""
    try:
        session = await agent_service.create_session(context=context or {})
        return {
            "session_id": session.session_id,
            "created_at": session.created_at.isoformat(),
            "message": "Session created successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create session: {str(e)}"
        )


@router.get("/agents/session/{session_id}", response_model=Dict)
@limiter.limit(CHAT_RATE_LIMIT)
async def get_chat_session(
    request,
    session_id: str,
    agent_service: AgentService = Depends(get_agent_service)
):
    """Get details of a chat session"""
    try:
        session = await agent_service.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )

        return {
            "session_id": session.session_id,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "message_count": len(session.messages),
            "context": session.context
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get session: {str(e)}"
        )


@router.delete("/agents/session/{session_id}")
@limiter.limit(CHAT_RATE_LIMIT)
async def delete_chat_session(
    request,
    session_id: str,
    agent_service: AgentService = Depends(get_agent_service)
):
    """Delete a chat session"""
    try:
        success = await agent_service.delete_session(session_id)
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )

        return {
            "message": "Session deleted successfully",
            "session_id": session_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete session: {str(e)}"
        )


@router.get("/agents/status")
@limiter.limit(HEALTH_RATE_LIMIT)
async def agent_status(
    request,
    agent_service: AgentService = Depends(get_agent_service)
):
    """Get the status of the agent service"""
    try:
        # Check if the agent service is available
        return {
            "status": "ok",
            "service": "openai-agent",
            "capabilities": [
                "chat",
                "query_with_context",
                "session_management",
                "source_citations"
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Status check failed: {str(e)}"
        )


@router.post("/agents/session/{session_id}/clear")
@limiter.limit(CHAT_RATE_LIMIT)
async def clear_chat_session(
    request,
    session_id: str,
    agent_service: AgentService = Depends(get_agent_service)
):
    """Clear all messages from a chat session"""
    try:
        success = await agent_service.clear_session(session_id)
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )

        return {
            "message": "Session cleared successfully",
            "session_id": session_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear session: {str(e)}"
        )