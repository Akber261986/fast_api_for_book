# RAG System for Markdown Files

This is a Retrieval-Augmented Generation (RAG) system that allows users to query Markdown files and receive AI-powered responses based on the content of those files.

## Features

- **Document Ingestion**: Upload and store Markdown files in a vector database
- **Semantic Search**: Find relevant content using vector similarity
- **AI-Powered Responses**: Generate answers based on retrieved context using Google Gemini
- **API Endpoints**: RESTful API for document ingestion and querying

## Architecture

- **FastAPI**: Web framework for building the API
- **Qdrant**: Vector database for storing document embeddings
- **Google Gemini**: AI model for generating embeddings and responses
- **Structured Logging**: JSON-formatted logs using structlog

## Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```

   Update the `.env` file with your actual API keys and configuration:
   - `GEMINI_API_KEY`: Your Google Gemini API key
   - `QDRANT_HOST`: Qdrant server host (default: localhost)
   - `QDRANT_PORT`: Qdrant server port (default: 6333)
   - `QDRANT_API_KEY`: Qdrant API key (if authentication is enabled)

4. **Start Qdrant**
   If running locally, you can start Qdrant using Docker:
   ```bash
   docker run -p 6333:6333 -p 6334:6334 \
     -v $(pwd)/qdrant_storage:/qdrant/storage:Z \
     qdrant/qdrant
   ```

5. **Start the application**
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

## API Endpoints

### Health Check
- `GET /health` - Check if the service is running

### Query
- `POST /query/` - Query the RAG system
  - Request body: `{"query": "your question", "top_k": 5, "similarity_threshold": 0.5}`
  - Response: AI-generated answer with source chunks and confidence score

### Ingest
- `POST /ingest/` - Ingest a document via form data
  - Form fields: `content`, `document_id` (optional), `file_name`, `file_type`, `chunk_size`, `chunk_overlap`
  - Response: Document ingestion status

- `POST /ingest/upload` - Upload and ingest a document file
  - Form fields: `file` (file upload), `document_id` (optional), `chunk_size`, `chunk_overlap`
  - Response: Document ingestion status

- `GET /ingest/status/{document_id}` - Get document processing status
- `DELETE /ingest/{document_id}` - Delete a document

## How It Works

1. **Ingestion Process**:
   - Document is uploaded/passed to the system
   - Content is parsed and split into semantic chunks
   - Each chunk is converted to an embedding vector using Gemini
   - Embeddings are stored in Qdrant with metadata

2. **Query Process**:
   - User query is converted to an embedding vector
   - Vector similarity search finds relevant document chunks
   - Relevant chunks are provided as context to Gemini
   - Gemini generates a response based on the context
   - Response includes source information and confidence score

## Configuration

The application can be configured via environment variables in the `.env` file:

- `ENVIRONMENT`: Application environment (default: development)
- `LOG_LEVEL`: Logging level (default: INFO)
- `GEMINI_API_KEY`: Google Gemini API key
- `GEMINI_MODEL`: Gemini model to use (default: gemini-2.5-flash)
- `QDRANT_HOST`: Qdrant server host
- `QDRANT_PORT`: Qdrant server port
- `QDRANT_API_KEY`: Qdrant API key (optional)
- `MAX_FILE_SIZE`: Maximum file size in bytes (default: 10MB)
- `CHUNK_SIZE`: Number of tokens per chunk (default: 1000)
- `CHUNK_OVERLAP`: Number of tokens to overlap between chunks (default: 200)

## Testing

To test the system end-to-end, you can use the provided test script:

```bash
python test_rag_system.py
```

## Deployment

The application is configured for deployment to Railway with the `railway.toml` file. To deploy:

1. Install the Railway CLI
2. Run `railway login`
3. Run `railway up`

Make sure to set the required environment variables in the Railway dashboard.

## Error Handling

The system includes comprehensive error handling:
- Input validation for all API endpoints
- Proper HTTP status codes
- Structured logging for debugging
- Graceful handling of external service failures

## Security

- API endpoints are protected against common vulnerabilities
- File upload size is limited
- Input validation is performed on all user inputs
- CORS is configured to allow specific origins in production

## Limitations

- Requires a valid Google Gemini API key
- Requires a running Qdrant instance.
- File size is limited to 10MB per upload
- Rate limiting is not implemented (can be added via middleware)