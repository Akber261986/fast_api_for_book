# ADR-002: Technology Stack

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-13
- **Feature:** 002-rag-markdown-system
- **Context:** Need to select a technology stack that supports the RAG system requirements while meeting performance, scalability, and constitutional constraints (no OpenAI services, must use Qdrant and Gemini).

## Decision

- **Language**: Python 3.11 for optimal performance and ecosystem compatibility
- **API Framework**: FastAPI for high-performance async API with automatic documentation
- **Dependency Management**: uv for package management (as specified in constitution)
- **Data Validation**: Pydantic for request/response validation
- **Vector Database Client**: python-qdrant-client for Qdrant integration
- **Testing Framework**: pytest for comprehensive testing
- **Deployment**: Railway for containerized deployment
- **Configuration**: Pydantic Settings for environment-based configuration

## Consequences

### Positive

- Python 3.11 offers excellent performance and compatibility with AI libraries
- FastAPI provides automatic OpenAPI documentation and excellent async support
- Pydantic ensures type safety and validation at the API boundary
- pytest offers comprehensive testing capabilities with fixtures and parameterization
- uv provides fast dependency resolution and virtual environment management
- Railway deployment aligns with constitutional requirements

### Negative

- Python ecosystem can have dependency conflicts with complex requirements
- FastAPI async model requires careful consideration of blocking operations
- Some AI libraries may have performance limitations compared to compiled languages
- Need to carefully manage memory usage with vector operations

## Alternatives Considered

Alternative A: Node.js with Express + Typesense
- Familiar JavaScript ecosystem with good performance
- Rejected: Would not integrate well with Qdrant Python client and Gemini Python SDK

Alternative B: Go with Gin framework
- Excellent performance and memory efficiency
- Rejected: Would complicate integration with AI libraries which have better Python support

Alternative C: Java with Spring Boot
- Strong enterprise support and performance
- Rejected: Python has superior ecosystem for AI/ML and vector databases

## References

- Feature Spec: specs/002-rag-markdown-system/spec.md
- Implementation Plan: specs/002-rag-markdown-system/plan.md
- Related ADRs: ADR-001
- Evaluator Evidence: specs/002-rag-markdown-system/research.md