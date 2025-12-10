import pytest
from unittest.mock import AsyncMock, MagicMock

from app.models.search import SearchQuery
from app.services.content_service import ContentService


@pytest.mark.asyncio
async def test_search_query_validation():
    """Test validation of search query parameters"""
    # Test valid query
    query = SearchQuery(
        query_text="test query",
        top_k=5,
        similarity_threshold=0.7
    )

    assert query.query_text == "test query"
    assert query.top_k == 5
    assert query.similarity_threshold == 0.7

    # Test invalid query text
    with pytest.raises(ValueError):
        SearchQuery(
            query_text="",
            top_k=5,
            similarity_threshold=0.7
        )

    # Test invalid top_k
    with pytest.raises(ValueError):
        SearchQuery(
            query_text="test",
            top_k=0,
            similarity_threshold=0.7
        )

    with pytest.raises(ValueError):
        SearchQuery(
            query_text="test",
            top_k=25,  # Exceeds max
            similarity_threshold=0.7
        )

    # Test invalid similarity threshold
    with pytest.raises(ValueError):
        SearchQuery(
            query_text="test",
            top_k=5,
            similarity_threshold=-0.1  # Below range
        )

    with pytest.raises(ValueError):
        SearchQuery(
            query_text="test",
            top_k=5,
            similarity_threshold=1.5  # Above range
        )


@pytest.mark.asyncio
async def test_content_service_search_content():
    """Test the search_content method of ContentService"""
    # Mock dependencies
    mock_qdrant_service = MagicMock()
    mock_gemini_service = MagicMock()

    # Create content service instance
    content_service = ContentService(mock_qdrant_service, mock_gemini_service)

    # Mock the embedding generation
    mock_gemini_service.generate_embedding = AsyncMock(return_value=[0.1, 0.2, 0.3])

    # Mock the qdrant search
    mock_qdrant_service.search_similar = AsyncMock(return_value=[
        {
            "id": "test_id_1",
            "text": "test content 1",
            "score": 0.85,
            "metadata": {
                "source_file": "test.md",
                "section": "section1",
                "title": "Test Title"
            }
        },
        {
            "id": "test_id_2",
            "text": "test content 2",
            "score": 0.75,
            "metadata": {
                "source_file": "test2.md",
                "section": "section2",
                "title": "Test Title 2"
            }
        }
    ])

    # Perform the search
    results = await content_service.search_content(
        query="test query",
        top_k=5,
        similarity_threshold=0.7
    )

    # Verify the results
    assert len(results) == 2
    assert results[0]["id"] == "test_id_1"
    assert results[0]["text"] == "test content 1"
    assert results[0]["similarity_score"] == 0.85

    # Verify that the embedding was generated
    mock_gemini_service.generate_embedding.assert_called_once_with("test query")

    # Verify that qdrant search was called with correct parameters
    mock_qdrant_service.search_similar.assert_called_once()


@pytest.mark.asyncio
async def test_content_service_process_content_chunk():
    """Test the process_content_chunk method of ContentService"""
    # Mock dependencies
    mock_qdrant_service = MagicMock()
    mock_gemini_service = MagicMock()

    # Create content service instance
    content_service = ContentService(mock_qdrant_service, mock_gemini_service)

    # Mock the embedding generation
    mock_gemini_service.generate_embedding = AsyncMock(return_value=[0.1, 0.2, 0.3])

    # Mock storing in qdrant
    mock_qdrant_service.store_embedding = AsyncMock(return_value="test_content_id")

    # Process a content chunk
    content_id = await content_service.process_content_chunk(
        text="Test content text",
        source_file="test_source.md",
        section="test_section",
        title="Test Title"
    )

    # Verify the result
    assert content_id == "test_content_id"

    # Verify that embedding was generated
    mock_gemini_service.generate_embedding.assert_called_once_with("Test content text")

    # Verify that content was stored in qdrant
    mock_qdrant_service.store_embedding.assert_called_once()


@pytest.mark.asyncio
async def test_content_service_search_content_with_filters():
    """Test search_content with filters"""
    # Mock dependencies
    mock_qdrant_service = MagicMock()
    mock_gemini_service = MagicMock()

    # Create content service instance
    content_service = ContentService(mock_qdrant_service, mock_gemini_service)

    # Mock the embedding generation
    mock_gemini_service.generate_embedding = AsyncMock(return_value=[0.1, 0.2, 0.3])

    # Mock the qdrant search with filters
    mock_qdrant_service.search_similar = AsyncMock(return_value=[
        {
            "id": "filtered_result",
            "text": "filtered content",
            "score": 0.9,
            "metadata": {
                "source_file": "filtered.md",
                "section": "filtered_section",
                "title": "Filtered Title"
            }
        }
    ])

    # Perform the search with filters
    results = await content_service.search_content(
        query="test query",
        top_k=5,
        similarity_threshold=0.7,
        filters={"source_file": "test.md"}
    )

    # Verify the results
    assert len(results) == 1
    assert results[0]["id"] == "filtered_result"

    # Verify that qdrant search was called with filters
    mock_qdrant_service.search_similar.assert_called_once()


@pytest.mark.asyncio
async def test_content_service_search_content_empty_query():
    """Test search_content with empty query raises error"""
    # Mock dependencies
    mock_qdrant_service = MagicMock()
    mock_gemini_service = MagicMock()

    # Create content service instance
    content_service = ContentService(mock_qdrant_service, mock_gemini_service)

    # Try to search with empty query - should raise ValueError
    with pytest.raises(ValueError, match="Query cannot be empty"):
        await content_service.search_content(query="")


@pytest.mark.asyncio
async def test_content_service_process_content_chunk_validation():
    """Test validation in process_content_chunk"""
    # Mock dependencies
    mock_qdrant_service = MagicMock()
    mock_gemini_service = MagicMock()

    # Create content service instance
    content_service = ContentService(mock_qdrant_service, mock_gemini_service)

    # Try with empty text - should raise ValueError
    with pytest.raises(ValueError, match="Text cannot be empty"):
        await content_service.process_content_chunk(text="", source_file="test.md")

    # Try with empty source file - should raise ValueError
    with pytest.raises(ValueError, match="Source file must be provided"):
        await content_service.process_content_chunk(text="test", source_file="")