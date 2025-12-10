# Quickstart Guide: FastAPI Book Search with Qdrant and Gemini

## Overview
This guide provides a quick setup and usage guide for the FastAPI book search application with Qdrant and Gemini integration.

## Prerequisites
- Python 3.11+
- Docker (for local Qdrant setup)
- Google Gemini API key
- OpenAI API key
- Qdrant database (local or cloud)

## Installation

### 1. Clone and Setup
```bash
# Clone the repository
git clone <repository-url>
cd fastapi-book-search

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration
Create a `.env` file with the following variables:
```env
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key
QDRANT_HOST=your_qdrant_host
QDRANT_API_KEY=your_qdrant_api_key  # if authentication enabled
QDRANT_PORT=6333
ENVIRONMENT=development
```

### 3. Qdrant Setup
For local development:
```bash
# Run Qdrant using Docker
docker run -p 6333:6333 -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage:z \
  qdrant/qdrant
```

## Usage

### 1. Start the Application
```bash
# Run the FastAPI application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Process Book Content
Upload and process your markdown files to create embeddings:
```bash
curl -X POST http://localhost:8000/api/v1/embeddings/process \
  -H "Content-Type: application/json" \
  -d '{
    "source_files": ["path/to/your/book.md"],
    "rebuild_collection": true
  }'
```

### 3. Perform Semantic Search
Search through your book content using natural language:
```bash
curl -X POST http://localhost:8000/api/v1/search/query \
  -H "Content-Type: application/json" \
  -d '{
    "query_text": "What are the main concepts discussed in the book?",
    "top_k": 5,
    "similarity_threshold": 0.7
  }'
```

### 4. Use AI Agent for Conversations
Have conversations with your book content:
```bash
curl -X POST http://localhost:8000/api/v1/agents/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explain the key principles mentioned in the book",
    "context_window": 5
  }'
```

## API Endpoints

### Search Endpoints
- `POST /api/v1/search/query` - Semantic search with natural language queries
- `GET /api/v1/search/status` - Get search service status

### Embedding Endpoints
- `POST /api/v1/embeddings/process` - Process and store markdown files
- `GET /api/v1/embeddings/status` - Get embedding collection status

### Agent Endpoints
- `POST /api/v1/agents/query` - Process query using AI agent
- `POST /api/v1/agents/chat` - Interactive chat with book content

### Health Check Endpoints
- `GET /health` - Overall application health
- `GET /health/qdrant` - Qdrant connection status
- `GET /health/gemini` - Gemini API connectivity
- `GET /health/openai` - OpenAI API connectivity

## Development

### Running Tests
```bash
# Run all tests
pytest

# Run unit tests
pytest tests/unit/

# Run integration tests
pytest tests/integration/
```

### Local Development
The application is structured with:
- `app/` - Main application code
- `app/api/` - API route definitions
- `app/services/` - Business logic implementations
- `app/models/` - Pydantic models
- `tests/` - Test files

## Deployment to Railway
1. Connect your GitHub repository to Railway
2. Set the environment variables in Railway dashboard
3. Add the Dockerfile to your repository
4. Deploy using Railway's deployment interface

The application will be automatically built and deployed with the specified configuration.