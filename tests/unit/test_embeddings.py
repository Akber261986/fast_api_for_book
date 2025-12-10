import pytest
from unittest.mock import AsyncMock, MagicMock

from app.models.embeddings import BatchEmbeddingRequest, EmbeddingRequest
from app.services.gemini_service import GeminiService
from app.services.content_service import ContentService


@pytest.mark.asyncio
async def test_batch_embedding_request_validation():
    """Test validation of batch embedding request parameters"""
    # Test valid request
    request = BatchEmbeddingRequest(
        texts=[
            EmbeddingRequest(text="Test text 1", source_file="test1.txt"),
            EmbeddingRequest(text="Test text 2", source_file="test2.txt")
        ],
        rebuild_collection=False
    )

    assert len(request.texts) == 2
    assert request.rebuild_collection is False

    # Test empty texts list
    with pytest.raises(ValueError):
        BatchEmbeddingRequest(
            texts=[],
            rebuild_collection=False
        )


@pytest.mark.asyncio
async def test_gemini_service_generate_embedding_validation():
    """Test validation in generate_embedding method"""
    # Mock dependencies
    gemini_service = GeminiService.__new__(GeminiService)
    gemini_service.model = "text-embedding-004"

    # Test with empty text - should raise ValueError
    with pytest.raises(ValueError, match="Text cannot be empty"):
        await gemini_service.generate_embedding("")

    # Test with too long text - should raise ValueError
    with pytest.raises(ValueError, match="Text too long"):
        await gemini_service.generate_embedding("a" * 10001)  # More than 10000 characters


@pytest.mark.asyncio
async def test_gemini_service_batch_generate_embeddings_validation():
    """Test validation in batch_generate_embeddings method"""
    # Mock dependencies
    gemini_service = GeminiService.__new__(GeminiService)
    gemini_service.model = "text-embedding-004"

    # Test with empty list - should raise ValueError
    with pytest.raises(ValueError, match="Texts list cannot be empty"):
        await gemini_service.batch_generate_embeddings([])

    # Test with too large batch - should raise ValueError
    large_batch = ["test"] * 101  # More than 100 items
    with pytest.raises(ValueError, match="Batch size too large"):
        await gemini_service.batch_generate_embeddings(large_batch)


@pytest.mark.asyncio
async def test_content_service_process_content_chunk_validation():
    """Test validation in process_content_chunk method"""
    # Mock dependencies
    mock_qdrant_service = MagicMock()
    mock_gemini_service = MagicMock()

    content_service = ContentService(mock_qdrant_service, mock_gemini_service)

    # Test with empty text - should raise ValueError
    with pytest.raises(ValueError, match="Text cannot be empty"):
        await content_service.process_content_chunk(text="", source_file="test.txt")

    # Test with too long text - should raise ValueError
    with pytest.raises(ValueError, match="Text too long"):
        await content_service.process_content_chunk(text="a" * 10001, source_file="test.txt")

    # Test with empty source file - should raise ValueError
    with pytest.raises(ValueError, match="Source file must be provided"):
        await content_service.process_content_chunk(text="test", source_file="")


@pytest.mark.asyncio
async def test_content_service_validate_content():
    """Test content validation functionality"""
    # Mock dependencies
    mock_qdrant_service = MagicMock()
    mock_gemini_service = MagicMock()

    content_service = ContentService(mock_qdrant_service, mock_gemini_service)

    # Test valid content
    result = content_service.validate_content("This is a valid content text.", "test.md")
    assert result["valid"] is True
    assert len(result["errors"]) == 0

    # Test short content
    result = content_service.validate_content("Hi", "test.md")
    assert result["valid"] is False
    assert any("too short" in error for error in result["errors"])

    # Test content with too few unique characters
    result = content_service.validate_content("aaaaaaa", "test.md")
    assert result["valid"] is False
    assert any("low information density" in error for error in result["errors"])

    # Test invalid filename
    result = content_service.validate_content("Valid content", "test.invalid_ext")
    assert result["valid"] is False
    assert any("Invalid source file name format" in error for error in result["errors"])

    # Test valid filename
    result = content_service.validate_content("Valid content", "test.md")
    assert result["valid"] is True


@pytest.mark.asyncio
async def test_content_service_process_markdown_file_validation():
    """Test validation in process_markdown_file method"""
    # Mock dependencies
    mock_qdrant_service = MagicMock()
    mock_gemini_service = MagicMock()

    content_service = ContentService(mock_qdrant_service, mock_gemini_service)

    # Test with empty file path - should raise ValueError
    with pytest.raises(ValueError, match="File path cannot be empty"):
        await content_service.process_markdown_file("", "test.md")

    # Test with empty source file - should raise ValueError
    with pytest.raises(ValueError, match="Source file cannot be empty"):
        await content_service.process_markdown_file("test.md", "")


@pytest.mark.asyncio
async def test_content_service_update_content_validation():
    """Test validation in update_content method"""
    # Mock dependencies
    mock_qdrant_service = MagicMock()
    mock_gemini_service = MagicMock()

    content_service = ContentService(mock_qdrant_service, mock_gemini_service)

    # Mock the delete and store methods
    content_service.delete_content = AsyncMock(return_value=True)
    mock_gemini_service.generate_embedding = AsyncMock(return_value=[0.1, 0.2, 0.3])
    mock_qdrant_service.store_embedding = AsyncMock(return_value="test_id")

    # Test with empty text - should raise ValueError
    with pytest.raises(ValueError, match="Content validation failed"):
        await content_service.update_content(content_id="test_id", text="")


@pytest.mark.asyncio
async def test_content_service_process_raw_text():
    """Test processing raw text functionality"""
    # Mock dependencies
    mock_qdrant_service = MagicMock()
    mock_gemini_service = MagicMock()

    content_service = ContentService(mock_qdrant_service, mock_gemini_service)

    # Mock the process_content_chunk method
    content_service.process_content_chunk = AsyncMock(return_value="test_content_id")

    # Test processing raw text
    result = await content_service.process_raw_text(
        text="This is a test text for processing.",
        source_file="test_source.txt",
        title="Test Title"
    )

    # Verify the result
    assert len(result) == 1
    assert result[0] == "test_content_id"

    # Verify that process_content_chunk was called
    content_service.process_content_chunk.assert_called_once()


@pytest.mark.asyncio
async def test_content_service_validate_and_process_markdown_file():
    """Test validate_and_process_markdown_file method"""
    # Mock dependencies
    mock_qdrant_service = MagicMock()
    mock_gemini_service = MagicMock()

    content_service = ContentService(mock_qdrant_service, mock_gemini_service)

    # Mock the process_markdown_file method
    content_service.process_markdown_file = AsyncMock(return_value=["content_id_1", "content_id_2"])

    # Test with a mock file path
    result = await content_service.validate_and_process_markdown_file(
        file_path="tests/unit/test_data/sample.md",
        source_file="sample.md"
    )

    # The file doesn't exist, so it should return an error
    assert result["valid"] is False
    assert len(result["errors"]) > 0
    assert any("File does not exist" in error for error in result["errors"])


def test_content_service_filename_validation():
    """Test filename validation functionality"""
    # Mock dependencies
    mock_qdrant_service = MagicMock()
    mock_gemini_service = MagicMock()

    content_service = ContentService(mock_qdrant_service, mock_gemini_service)

    # Test valid filenames
    assert content_service._is_valid_filename("test.md") is True
    assert content_service._is_valid_filename("my-file_123.txt") is True
    assert content_service._is_valid_filename("document.pdf") is True

    # Test invalid filenames
    assert content_service._is_valid_filename("test.invalid") is False
    assert content_service._is_valid_filename("") is False
    assert content_service._is_valid_filename("test<>file.md") is False


@pytest.mark.asyncio
async def test_gemini_service_generate_embeddings_with_retry():
    """Test generate_embeddings_with_retry functionality"""
    # Mock dependencies
    gemini_service = GeminiService.__new__(GeminiService)
    gemini_service.model = "text-embedding-004"

    # Mock the batch_generate_embeddings method to fail initially then succeed
    call_count = 0
    async def mock_batch_generate_embeddings(texts):
        nonlocal call_count
        call_count += 1
        if call_count < 2:  # Fail on first call, succeed on second
            raise Exception("API rate limit exceeded")
        return [[0.1, 0.2, 0.3]] * len(texts)

    gemini_service.batch_generate_embeddings = mock_batch_generate_embeddings

    # Test retry functionality (should succeed on second attempt)
    result = await gemini_service.generate_embeddings_with_retry(["test"], max_retries=3)
    assert len(result) == 1
    assert len(result[0]) == 3  # Should have 3 embedding values
    assert call_count == 2  # Should have been called twice (first failed, second succeeded)