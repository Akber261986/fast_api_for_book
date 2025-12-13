# ADR-001: RAG System Architecture

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-13
- **Feature:** 002-rag-markdown-system
- **Context:** Need to implement a Retrieval-Augmented Generation system that allows users to query Markdown files using natural language, with semantic search capabilities and response generation while adhering to constitutional constraints (no OpenAI services).

## Decision

- **Architecture Pattern**: Retrieval-Augmented Generation (RAG) with semantic search
- **Vector Database**: Qdrant for storing document embeddings
- **AI Model**: Google's Gemini (gemini-2.5-flash) for both embeddings and response generation
- **API Framework**: FastAPI for high-performance async API
- **Document Processing**: Markdown parsing with semantic chunking strategy
- **Search Method**: Cosine similarity for semantic matching

## Consequences

### Positive

- Enables semantic search capabilities that go beyond keyword matching
- Leverages state-of-the-art AI for both understanding and generating responses
- FastAPI provides excellent performance and automatic OpenAPI documentation
- Qdrant offers optimized vector search operations
- Architecture allows for horizontal scaling and concurrent queries

### Negative

- Increased complexity compared to simple keyword search
- Dependency on external AI services (Google Gemini API)
- Higher latency than simple database queries due to AI processing
- Potential cost implications from AI API usage
- Requires careful handling of token limits and context windows

## Alternatives Considered

Alternative A: Traditional keyword search with PostgreSQL full-text search
- Simpler implementation with lower latency
- Rejected: Would not meet semantic search requirements in constitution

Alternative B: Elasticsearch with semantic search plugins
- Good search capabilities with familiar SQL-like query syntax
- Rejected: Constitution specifically mandates Qdrant as vector database

Alternative C: Pinecone or other vector databases with OpenAI embeddings
- Popular and well-documented vector solutions
- Rejected: Constitution prohibits OpenAI services; requires Google Gemini exclusively

## References

- Feature Spec: specs/002-rag-markdown-system/spec.md
- Implementation Plan: specs/002-rag-markdown-system/plan.md
- Related ADRs: none
- Evaluator Evidence: specs/002-rag-markdown-system/research.md