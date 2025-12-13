# FastAPI Book Search with Qdrant and Gemini Constitution

## Core Principles

### I. Semantic Search First
Leverage vector embeddings and Qdrant database for intelligent book content search; All search functionality must be powered by semantic understanding rather than keyword matching; Accuracy and relevance of search results are paramount.

### II. AI Integration
Integrate both OpenAI Agents SDK and Google's Gemini models for enhanced query processing and response generation; Maintain clear separation between embedding generation and query processing components; Support both synchronous and asynchronous AI operations.

### III. Test-First (NON-NEGOTIABLE)
TDD mandatory: Tests written → User approved → Tests fail → Then implement; Red-Green-Refactor cycle strictly enforced; All API endpoints must have comprehensive unit and integration tests.

### IV. Scalable Architecture
Design for horizontal scaling using Railway deployment platform; All components must be stateless where possible; Support for increasing document volumes and concurrent users without performance degradation.

### V. Security and Observability
Secure handling of API keys and credentials using environment variables; Implement structured logging for all operations; Include health checks and monitoring endpoints; All external API calls must have proper error handling and timeouts.

### VI. Efficient Vector Operations
Optimize Qdrant vector database operations for fast similarity search; Implement proper collection management and cleanup procedures; Support configurable similarity thresholds and search parameters.

## Architecture and Technology Stack
FastAPI backend with Pydantic models for data validation; Qdrant vector database for storing and searching book content embeddings; Google's Gemini Flash-2.5 for generating text embeddings from markdown content; OpenAI Agents SDK for intelligent query processing; Railway for containerized deployment; GitHub Pages Docusaurus as content source for book markdown files.

## Development Workflow
All features must follow the Spec-Driven Development lifecycle (specify → plan → tasks → implement); Code reviews must verify compliance with architectural principles; Automated testing required before merge; Clear documentation for all API endpoints and components.

## Governance
This constitution supersedes all other practices; Amendments require documentation, approval, and migration plan; All PRs/reviews must verify compliance with these principles; Complexity must be justified with clear benefits.

**Version**: 1.0.0 | **Ratified**: 2025-12-09 | **Last Amended**: 2025-12-09
