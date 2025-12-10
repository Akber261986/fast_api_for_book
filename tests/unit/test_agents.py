import pytest
from unittest.mock import AsyncMock, MagicMock

from app.models.agents import ChatRequest, AgentQueryRequest
from app.services.agent_service import AgentService


@pytest.mark.asyncio
async def test_agent_query_request_validation():
    """Test validation of agent query request parameters"""
    # Test valid request
    request = AgentQueryRequest(
        query="test query",
        context_window=5,
        max_tokens=500,
        temperature=0.3
    )

    assert request.query == "test query"
    assert request.context_window == 5
    assert request.max_tokens == 500
    assert request.temperature == 0.3

    # Test invalid query
    with pytest.raises(ValueError):
        AgentQueryRequest(
            query="",
            context_window=5,
            max_tokens=500,
            temperature=0.3
        )

    # Test too long query
    with pytest.raises(ValueError):
        AgentQueryRequest(
            query="a" * 1001,  # More than 1000 characters
            context_window=5,
            max_tokens=500,
            temperature=0.3
        )

    # Test invalid context window
    with pytest.raises(ValueError):
        AgentQueryRequest(
            query="test",
            context_window=0,  # Below range
            max_tokens=500,
            temperature=0.3
        )

    with pytest.raises(ValueError):
        AgentQueryRequest(
            query="test",
            context_window=21,  # Above range
            max_tokens=500,
            temperature=0.3
        )


@pytest.mark.asyncio
async def test_chat_request_validation():
    """Test validation of chat request parameters"""
    # Test valid request
    request = ChatRequest(
        message="Hello, how are you?",
        session_id="test_session_id",
        context={"context_window": 5}
    )

    assert request.message == "Hello, how are you?"
    assert request.session_id == "test_session_id"

    # Test invalid message
    with pytest.raises(ValueError):
        ChatRequest(
            message="",
            session_id="test_session_id"
        )

    # Test too long message
    with pytest.raises(ValueError):
        ChatRequest(
            message="a" * 2001,  # More than 2000 characters
            session_id="test_session_id"
        )


@pytest.mark.asyncio
async def test_agent_service_create_session():
    """Test creating a chat session"""
    # Mock dependencies
    mock_client = MagicMock()
    agent_service = AgentService.__new__(AgentService)
    agent_service.client = mock_client
    agent_service.model = "gpt-4-turbo"
    agent_service.sessions = {}
    agent_service.content_service = MagicMock()

    # Create a session
    session = await agent_service.create_session(context={"topic": "book"})

    # Verify the session was created
    assert session.session_id is not None
    assert len(session.messages) == 0
    assert session.context == {"topic": "book"}
    assert session.created_at is not None
    assert session.updated_at is not None

    # Verify the session is stored
    assert session.session_id in agent_service.sessions


@pytest.mark.asyncio
async def test_agent_service_get_session():
    """Test getting a chat session"""
    # Mock dependencies
    mock_client = MagicMock()
    agent_service = AgentService.__new__(AgentService)
    agent_service.client = mock_client
    agent_service.model = "gpt-4-turbo"
    agent_service.sessions = {}
    agent_service.content_service = MagicMock()

    # Create a session first
    created_session = await agent_service.create_session()

    # Get the session
    retrieved_session = await agent_service.get_session(created_session.session_id)

    # Verify the session was retrieved
    assert retrieved_session is not None
    assert retrieved_session.session_id == created_session.session_id


@pytest.mark.asyncio
async def test_agent_service_add_message_to_session():
    """Test adding a message to a chat session"""
    from datetime import datetime
    from app.models.agents import Message

    # Mock dependencies
    mock_client = MagicMock()
    agent_service = AgentService.__new__(AgentService)
    agent_service.client = mock_client
    agent_service.model = "gpt-4-turbo"
    agent_service.sessions = {}
    agent_service.content_service = MagicMock()

    # Create a session
    session = await agent_service.create_session()

    # Create a message
    message = Message(
        message_id="test_message_id",
        role="user",
        content="Hello, world!",
        timestamp=datetime.now(),
        sources=[]
    )

    # Add the message to the session
    updated_session = await agent_service.add_message_to_session(session.session_id, message)

    # Verify the message was added
    assert len(updated_session.messages) == 1
    assert updated_session.messages[0].content == "Hello, world!"
    assert updated_session.messages[0].role == "user"


@pytest.mark.asyncio
async def test_agent_service_process_chat_query():
    """Test processing a chat query"""
    from datetime import datetime
    from app.models.agents import Message

    # Mock dependencies
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "This is a test response"
    mock_client.chat.completions.create = MagicMock(return_value=mock_response)

    agent_service = AgentService.__new__(AgentService)
    agent_service.client = mock_client
    agent_service.model = "gpt-4-turbo"
    agent_service.sessions = {}
    agent_service.content_service = MagicMock()

    # Mock content service search
    agent_service.content_service.search_content = AsyncMock(return_value=[
        {
            "id": "test_id",
            "text": "Test content for response",
            "source_file": "test.md",
            "section": "section1",
            "similarity_score": 0.85
        }
    ])

    # Process a chat query
    result = await agent_service.process_chat_query(
        query="What is this book about?",
        max_tokens=200
    )

    # Verify the result
    assert "response" in result
    assert "sources" in result
    assert "session_id" in result
    assert result["response"] == "This is a test response"
    assert len(result["sources"]) == 1
    assert result["sources"][0]["content_id"] == "test_id"

    # Verify that the OpenAI API was called
    mock_client.chat.completions.create.assert_called_once()


@pytest.mark.asyncio
async def test_agent_service_process_chat_query_validation():
    """Test validation in process_chat_query"""
    # Mock dependencies
    mock_client = MagicMock()
    agent_service = AgentService.__new__(AgentService)
    agent_service.client = mock_client
    agent_service.model = "gpt-4-turbo"
    agent_service.sessions = {}
    agent_service.content_service = MagicMock()

    # Test with empty query - should raise ValueError
    with pytest.raises(ValueError, match="Query cannot be empty"):
        await agent_service.process_chat_query(query="")

    # Test with too long query - should raise ValueError
    with pytest.raises(ValueError, match="Query too long"):
        await agent_service.process_chat_query(query="a" * 1001)

    # Test with invalid context window - should raise ValueError
    with pytest.raises(ValueError, match="context_window must be between 1 and 20"):
        await agent_service.process_chat_query(
            query="test query",
            context_window=0
        )

    # Test with invalid max_tokens - should raise ValueError
    with pytest.raises(ValueError, match="max_tokens must be between 1 and 2000"):
        await agent_service.process_chat_query(
            query="test query",
            max_tokens=0
        )


@pytest.mark.asyncio
async def test_agent_service_get_conversation_context():
    """Test getting conversation context"""
    from datetime import datetime
    from app.models.agents import Message

    # Mock dependencies
    mock_client = MagicMock()
    agent_service = AgentService.__new__(AgentService)
    agent_service.client = mock_client
    agent_service.model = "gpt-4-turbo"
    agent_service.sessions = {}
    agent_service.content_service = MagicMock()

    # Create a session
    session = await agent_service.create_session()

    # Add some messages to the session
    msg1 = Message(
        message_id="msg1",
        role="user",
        content="Hello",
        timestamp=datetime.now(),
        sources=[]
    )
    msg2 = Message(
        message_id="msg2",
        role="assistant",
        content="Hi there!",
        timestamp=datetime.now(),
        sources=[]
    )
    await agent_service.add_message_to_session(session.session_id, msg1)
    await agent_service.add_message_to_session(session.session_id, msg2)

    # Get conversation context with window of 5 (should return both messages)
    context = await agent_service.get_conversation_context(session.session_id, context_window=5)

    # Verify the context
    assert len(context) == 2
    assert context[0]["content"] == "Hello"
    assert context[1]["content"] == "Hi there!"


@pytest.mark.asyncio
async def test_agent_service_clear_session():
    """Test clearing a session"""
    from datetime import datetime
    from app.models.agents import Message

    # Mock dependencies
    mock_client = MagicMock()
    agent_service = AgentService.__new__(AgentService)
    agent_service.client = mock_client
    agent_service.model = "gpt-4-turbo"
    agent_service.sessions = {}
    agent_service.content_service = MagicMock()

    # Create a session
    session = await agent_service.create_session()

    # Add a message to the session
    msg = Message(
        message_id="msg1",
        role="user",
        content="Hello",
        timestamp=datetime.now(),
        sources=[]
    )
    await agent_service.add_message_to_session(session.session_id, msg)

    # Verify the message was added
    session_with_msg = await agent_service.get_session(session.session_id)
    assert len(session_with_msg.messages) == 1

    # Clear the session
    success = await agent_service.clear_session(session.session_id)

    # Verify the session was cleared
    assert success is True
    cleared_session = await agent_service.get_session(session.session_id)
    assert len(cleared_session.messages) == 0