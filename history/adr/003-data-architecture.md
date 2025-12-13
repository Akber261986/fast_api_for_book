# ADR-003: Data Architecture

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-13
- **Feature:** 002-rag-markdown-system
- **Context**: Need to design a data architecture that supports efficient storage and retrieval of document embeddings while maintaining semantic search capabilities and handling document lifecycle management.

## Decision

- **Primary Storage**: Qdrant vector database for embeddings and semantic search
- **Document Storage**: Local file system for raw Markdown files
- **Chunking Strategy**: Semantic chunking with overlap to preserve context
- **Embedding Model**: Google's Gemini for generating vector representations
- **Collection Design**: Dedicated Qdrant collection per document set with cosine similarity
- **Metadata Storage**: Embedded in Qdrant records alongside embeddings
- **Indexing Strategy**: Vector indexing for similarity search with configurable thresholds

## Consequences

### Positive

- Qdrant provides optimized vector search performance for semantic similarity
- Semantic chunking preserves context better than fixed-size chunks
- Cosine similarity metric works well for text embeddings
- Embedded metadata allows rich filtering and retrieval
- Scalable architecture that can handle growing document collections

### Negative

- Vector storage requires more space than traditional indexing
- Chunking strategy may create redundant information across chunks
- Qdrant dependency introduces additional infrastructure component
- Need to manage embedding consistency across system updates
- Potential for increased latency during ingestion due to embedding generation

## Alternatives Considered

Alternative A: PostgreSQL with pgvector extension
- Familiar SQL interface with vector capabilities
- Rejected: Constitution specifically mandates Qdrant as vector database

Alternative B: Elasticsearch with dense vector fields
- Good integration with existing search infrastructure
- Rejected: Constitution specifically mandates Qdrant as vector database

Alternative C: Simple keyword-based indexing with full-text search
- Simpler implementation with faster queries
- Rejected: Would not meet semantic search requirements in constitution

Alternative D: ChromaDB or Pinecone as vector databases
- Popular vector database solutions
- Rejected: Constitution mandates Qdrant specifically

## References

- Feature Spec: specs/002-rag-markdown-system/spec.md
- Implementation Plan: specs/002-rag-markdown-system/plan.md
- Related ADRs: ADR-001
- Evaluator Evidence: specs/002-rag-markdown-system/data-model.md