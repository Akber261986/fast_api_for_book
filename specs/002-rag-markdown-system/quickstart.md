# Quickstart: RAG System for Markdown Files

## Prerequisites
- Python 3.11+
- Poetry or uv for dependency management
- Qdrant vector database (local or cloud)
- Google Gemini API key

## Setup

1. **Clone and install dependencies:**
```bash
# Install dependencies with uv
uv sync
# Or with poetry
poetry install
```

2. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your Gemini API key and Qdrant configuration
```

3. **Start Qdrant:**
```bash
# Option 1: Docker
docker run -p 6333:6333 -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage:z \
  qdrant/qdrant

# Option 2: Cloud Qdrant (update .env accordingly)
```

## Basic Usage

1. **Start the API server:**
```bash
uv run python -m app.main
# Or with poetry
poetry run python -m app.main
```

2. **Ingest Markdown files:**
```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: multipart/form-data" \
  -F "file=@docs/sample_document.md"
```

3. **Query the system:**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What does the document say about machine learning?",
    "top_k": 3,
    "similarity_threshold": 0.7
  }'
```

## API Endpoints

- `POST /ingest` - Upload and process Markdown files
- `POST /query` - Query the RAG system
- `GET /health` - Health check endpoint
- `GET /docs` - Interactive API documentation

## Testing

```bash
# Run all tests
pytest

# Run specific test suites
pytest tests/unit/
pytest tests/integration/
pytest tests/contract/
```