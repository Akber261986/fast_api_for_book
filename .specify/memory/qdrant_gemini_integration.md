# Qdrant Integration with Gemini Embeddings Specification

## Overview
This document outlines the integration between Qdrant vector database and Google's Gemini embedding model for semantic search of book content.

## Architecture
- **Content Source**: Markdown files from GitHub Pages Docusaurus deployment
- **Embedding Model**: Google's Gemini Flash-2.5 for generating text embeddings
- **Vector Database**: Qdrant for storing and searching vector embeddings
- **Processing Pipeline**: Markdown → Text extraction → Gemini embedding → Qdrant storage

## Qdrant Collection Design
- **Collection Name**: `book_content`
- **Vector Size**: 768 dimensions (standard for Gemini embeddings)
- **Distance Metric**: Cosine similarity
- **Payload Schema**:
  - `title`: String - Document/chapter title
  - `content`: String - Original text content
  - `source_file`: String - Original markdown filename
  - `section`: String - Section identifier if applicable
  - `created_at`: DateTime - Timestamp of embedding creation

## Processing Pipeline
1. **Content Extraction**: Parse markdown files to extract text content while preserving document structure
2. **Chunking Strategy**: Split long documents into smaller chunks (max 1000 tokens) to fit Gemini context
3. **Embedding Generation**: Use Gemini Flash-2.5 to convert text chunks to vector embeddings
4. **Storage**: Store embeddings in Qdrant with relevant metadata
5. **Indexing**: Create efficient indexes for fast similarity search

## API Endpoints for Embedding Operations
- `POST /embeddings/process`: Process markdown files and store embeddings in Qdrant
- `POST /embeddings/search`: Perform semantic search using query embedding and Qdrant
- `DELETE /embeddings/collection`: Clear and rebuild the collection

## Search Parameters
- **Top K**: Number of similar results to return (default: 5)
- **Similarity Threshold**: Minimum similarity score (default: 0.7)
- **Filter**: Optional metadata filters (by source file, section, etc.)

## Error Handling
- Handle Gemini API rate limits and errors gracefully
- Implement retry logic for failed embedding operations
- Validate embedding dimensions before storing in Qdrant
- Log failed operations for debugging

## Performance Considerations
- Batch embedding operations to optimize API usage
- Implement caching for frequently accessed embeddings
- Use Qdrant's sparse indexing for faster retrieval
- Monitor and optimize embedding generation time

## Security
- Secure API keys for Gemini and Qdrant access
- Validate input content before processing
- Implement rate limiting for embedding operations