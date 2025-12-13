# Data Model: RAG System for Markdown Files

## Document Entity
**Fields:**
- `id`: str - Unique identifier for the document
- `filename`: str - Original filename
- `content`: str - Raw content of the document
- `metadata`: dict - Additional metadata (creation date, source, etc.)
- `chunks`: List[DocumentChunk] - List of semantic chunks from the document

**Validation rules:**
- `id` must be unique across all documents
- `filename` must have .md extension
- `content` must not exceed 10MB
- `chunks` must contain at least one chunk

**State transitions:**
- `pending_ingestion` → `processed` → `indexed_in_qdrant`

## DocumentChunk Entity
**Fields:**
- `chunk_id`: str - Unique identifier for the chunk
- `document_id`: str - Reference to parent document
- `content`: str - Chunked content
- `embedding`: List[float] - Vector embedding of the content
- `metadata`: dict - Chunk-specific metadata (position in document, etc.)

**Validation rules:**
- `chunk_id` must be unique across all chunks
- `document_id` must reference an existing document
- `embedding` must match expected dimension from Gemini model
- `content` must not be empty

**State transitions:**
- `created` → `embedded` → `stored_in_qdrant`

## Query Entity
**Fields:**
- `query_id`: str - Unique identifier for the query
- `text`: str - User's natural language query
- `top_k`: int - Number of results to retrieve (default: 5)
- `similarity_threshold`: float - Minimum similarity threshold (default: 0.5)

**Validation rules:**
- `text` must not be empty
- `top_k` must be between 1 and 20
- `similarity_threshold` must be between 0.0 and 1.0

## RetrievedContext Entity
**Fields:**
- `query_id`: str - Reference to the original query
- `chunks`: List[DocumentChunk] - Retrieved relevant chunks
- `scores`: List[float] - Similarity scores for each chunk
- `retrieval_metadata`: dict - Information about retrieval process

**Validation rules:**
- `chunks` and `scores` must have the same length
- All scores must be between 0.0 and 1.0
- `chunks` must not be empty

## Response Entity
**Fields:**
- `response_id`: str - Unique identifier for the response
- `query_id`: str - Reference to the original query
- `content`: str - Generated response content
- `source_chunks`: List[DocumentChunk] - Chunks that informed the response
- `confidence`: float - Confidence score for the response (0.0-1.0)

**Validation rules:**
- `content` must not be empty
- `confidence` must be between 0.0 and 1.0
- `source_chunks` must not be empty