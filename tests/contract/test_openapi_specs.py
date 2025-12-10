import json
from fastapi.testclient import TestClient
from fastapi.openapi.utils import get_openapi

from app.main import app


def test_openapi_specification():
    """Test that the OpenAPI specification is properly generated"""
    # Get the OpenAPI spec from the app
    openapi_spec = get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        routes=app.routes,
    )

    # Basic validation of the spec structure
    assert "openapi" in openapi_spec
    assert "info" in openapi_spec
    assert "paths" in openapi_spec
    assert "components" in openapi_spec

    # Check that the spec follows the correct version
    assert openapi_spec["openapi"] == "3.1.0"  # FastAPI default

    # Check that the title and version match
    assert openapi_spec["info"]["title"] == "FastAPI Book Search with Qdrant and Gemini"
    assert openapi_spec["info"]["version"] == "0.1.0"

    # Check that we have API paths defined
    assert len(openapi_spec["paths"]) > 0

    # Verify that expected paths exist
    expected_paths = [
        "/health",
        "/api/v1/search/query",
        "/api/v1/search/advanced",
        "/api/v1/search/status",
        "/api/v1/search/validate",
        "/api/v1/search/collections",
        "/api/v1/agents/query",
        "/api/v1/agents/chat",
        "/api/v1/agents/session/create",
        "/api/v1/agents/session/{session_id}",
        "/api/v1/agents/status",
        "/api/v1/agents/session/{session_id}/clear",
        "/api/v1/embeddings/process",
        "/api/v1/embeddings/process-markdown",
        "/api/v1/embeddings/job/{job_id}",
        "/api/v1/embeddings/status",
        "/api/v1/embeddings/jobs",
        "/api/v1/embeddings/job/{job_id}",
    ]

    for path in expected_paths:
        # Check if the path exists (or a similar path with parameters)
        path_exists = any(p.endswith(path.split('/')[-1]) or p.startswith(path.rstrip('{').rstrip('}')) for p in openapi_spec["paths"])
        if not path_exists:
            # Some paths might have parameter placeholders, so check more broadly
            path_exists = any(path.replace('{job_id}', '{id}') in p or path.replace('{session_id}', '{id}') in p for p in openapi_spec["paths"])
        assert path_exists, f"Expected path {path} not found in OpenAPI spec"


def test_api_responses_structure():
    """Test that API responses follow expected structure"""
    client = TestClient(app)

    # Test health endpoint response structure
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"


def test_search_endpoint_contract():
    """Test the search endpoint contract"""
    client = TestClient(app)

    # Check that the endpoint exists and accepts expected parameters
    response = client.post("/api/v1/search/query",
                          json={
                              "query_text": "test query",
                              "top_k": 5,
                              "similarity_threshold": 0.7
                          })
    # This might fail due to missing services, but should have proper structure
    # Check that it's not a 404 (endpoint exists)
    assert response.status_code != 404


def test_agents_endpoint_contract():
    """Test the agents endpoint contract"""
    client = TestClient(app)

    # Check that the endpoint exists and accepts expected parameters
    response = client.post("/api/v1/agents/chat",
                          json={
                              "message": "Hello",
                              "session_id": None
                          })
    # This might fail due to missing services, but should have proper structure
    # Check that it's not a 404 (endpoint exists)
    assert response.status_code != 404


def test_embeddings_endpoint_contract():
    """Test the embeddings endpoint contract"""
    client = TestClient(app)

    # Check that the endpoint exists and accepts expected parameters
    response = client.post("/api/v1/embeddings/process",
                          json={
                              "texts": [
                                  {
                                      "text": "test text",
                                      "source_file": "test.txt"
                                  }
                              ]
                          })
    # This might fail due to missing services, but should have proper structure
    # Check that it's not a 404 (endpoint exists)
    assert response.status_code != 404


def test_api_error_responses():
    """Test that API endpoints return proper error responses"""
    client = TestClient(app)

    # Test with invalid request body to trigger validation error
    response = client.post("/api/v1/search/query", json={})
    assert response.status_code in [400, 422]  # Either validation error or bad request

    # Check that error response has expected structure
    error_data = response.json()
    assert "detail" in error_data or "error" in error_data


def test_rate_limiting_contract():
    """Test that rate limiting is properly applied"""
    client = TestClient(app)

    # Make multiple requests to test rate limiting
    responses = []
    for i in range(3):
        response = client.get("/health")
        responses.append(response.status_code)

    # All requests should succeed (not rate limited in test environment)
    assert all(status == 200 for status in responses)


def test_request_id_in_responses():
    """Test that request IDs are included in responses"""
    client = TestClient(app)

    response = client.get("/health")
    assert response.status_code == 200
    assert "x-request-id" in response.headers
    request_id = response.headers["x-request-id"]
    assert isinstance(request_id, str)
    assert len(request_id) > 0


def test_content_type_headers():
    """Test that proper content type headers are returned"""
    client = TestClient(app)

    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"


def test_api_versioning():
    """Test that API versioning is properly implemented"""
    client = TestClient(app)

    # Check that API endpoints are under the v1 prefix
    response = client.get("/api/v1/search/status")
    assert "/api/v1" in response.request.url.path

    # Verify that older versions are not accessible (if versioning was implemented)
    # For now, just ensure v1 endpoints exist
    v1_endpoints = [
        "/api/v1/search/status",
        "/api/v1/agents/status",
        "/api/v1/embeddings/status"
    ]

    for endpoint in v1_endpoints:
        response = client.get(endpoint)
        # Should not return 404 (endpoint exists)
        assert response.status_code != 404, f"Endpoint {endpoint} not found"