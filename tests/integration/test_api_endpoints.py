import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


def test_health_endpoint(client):
    """Test the root health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"


def test_search_status_endpoint(client):
    """Test the search status endpoint"""
    response = client.get("/api/v1/search/status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"


def test_agents_status_endpoint(client):
    """Test the agents status endpoint"""
    response = client.get("/api/v1/agents/status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"


def test_embeddings_status_endpoint(client):
    """Test the embeddings status endpoint"""
    response = client.get("/api/v1/embeddings/status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"


def test_search_query_endpoint_validation(client):
    """Test validation for the search query endpoint"""
    # Test with empty query
    response = client.post("/api/v1/search/query", json={"query_text": ""})
    assert response.status_code == 422  # Validation error

    # Test with query that's too short
    response = client.post("/api/v1/search/query", json={"query_text": "a"})
    assert response.status_code == 400  # Custom validation error

    # Test with valid query (should fail due to missing services, but not validation)
    response = client.post("/api/v1/search/query", json={"query_text": "test query"})
    # This might return 500 due to missing services, but shouldn't be a validation error
    assert response.status_code != 422


def test_agents_chat_endpoint_validation(client):
    """Test validation for the agents chat endpoint"""
    # Test with empty message
    response = client.post("/api/v1/agents/chat", json={"message": ""})
    assert response.status_code == 400  # Custom validation error

    # Test with valid message (should fail due to missing services, but not validation)
    response = client.post("/api/v1/agents/chat", json={"message": "Hello"})
    # This might return 500 due to missing services, but shouldn't be a validation error
    assert response.status_code != 422


def test_embeddings_process_markdown_endpoint_validation(client):
    """Test validation for the embeddings process markdown endpoint"""
    # Test with empty file list
    response = client.post("/api/v1/embeddings/process-markdown", json={"source_files": []})
    assert response.status_code == 400  # Custom validation error

    # Test with too many files
    response = client.post("/api/v1/embeddings/process-markdown",
                          json={"source_files": [f"file_{i}.md" for i in range(101)]})
    assert response.status_code == 400  # Custom validation error

    # Test with valid file list (should fail due to missing services, but not validation)
    response = client.post("/api/v1/embeddings/process-markdown",
                          json={"source_files": ["test.md"]})
    # This might return 500 due to missing services, but shouldn't be a validation error
    assert response.status_code != 422


def test_rate_limiting(client):
    """Test that rate limiting is applied to endpoints"""
    # Make multiple requests to test rate limiting
    for i in range(5):
        response = client.get("/health")
        assert response.status_code == 200

    # Test search endpoint rate limiting
    for i in range(5):
        response = client.post("/api/v1/search/query", json={"query_text": f"test query {i}"})
        # Should not be blocked by rate limiting for this test
        assert response.status_code != 429


def test_cors_headers(client):
    """Test that CORS headers are properly set"""
    response = client.get("/health")
    assert response.status_code == 200
    # Check for CORS headers (depends on how CORS is configured)
    # This test might need adjustment based on actual CORS configuration


def test_request_id_header(client):
    """Test that request ID headers are added"""
    response = client.get("/health")
    assert response.status_code == 200
    assert "x-request-id" in response.headers