<!--
Sync Impact Report:
Version change: 1.0.0 → 1.1.0
Modified principles:
- II. AI Integration (updated to remove OpenAI references and emphasize Gemini)
- VI. Efficient Vector Operations (updated to reflect RAG system focus)
Added sections: None
Removed sections: None
Templates requiring updates:
- .specify/templates/plan-template.md ⚠ pending
- .specify/templates/spec-template.md ⚠ pending
- .specify/templates/tasks-template.md ⚠ pending
- .specify/templates/commands/*.md ⚠ pending
- README.md ⚠ pending
Follow-up TODOs: None
-->

# RAG System for Markdown Files with Qdrant and Gemini Constitution

## Core Principles

### I. Semantic Search First
Leverage vector embeddings and Qdrant database for intelligent document content search; All search functionality must be powered by semantic understanding rather than keyword matching; Accuracy and relevance of search results are paramount.

### II. Gemini-Centric AI Integration
Integrate Google's Gemini models (gemini-2.5-flash) exclusively for embedding generation and query processing; NO OpenAI API keys or services allowed anywhere in the system; Maintain clear separation between embedding generation and query processing components; Support both synchronous and asynchronous AI operations.

### III. Test-First (NON-NEGOTIABLE)
TDD mandatory: Tests written → User approved → Tests fail → Then implement; Red-Green-Refactor cycle strictly enforced; All API endpoints must have comprehensive unit and integration tests.

### IV. Scalable Architecture
Design for horizontal scaling using Railway deployment platform; All components must be stateless where possible; Support for increasing document volumes and concurrent users without performance degradation.

### V. Security and Observability
Secure handling of API keys and credentials using environment variables; Implement structured logging for all operations; Include health checks and monitoring endpoints; All external API calls must have proper error handling and timeouts.

### VI. RAG System Excellence
Optimize Retrieval-Augmented Generation pipeline for Markdown document processing; Ensure document chunking is sane and retrieval-safe with proper context handling; Implement proper Qdrant vector database operations for fast similarity search; Support configurable similarity thresholds and search parameters.

## Architecture and Technology Stack
Python project managed using `uv`; FastAPI backend with Pydantic models for data validation; Qdrant vector database for storing and searching Markdown file embeddings; Google's Gemini (gemini-2.5-flash) for generating text embeddings; Agent framework using OpenAI Agents SDK (used WITHOUT OpenAI API keys) for intelligent query processing; Railway for containerized deployment; Markdown (.md) files as primary data source.

## Development Workflow
All features must follow the Spec-Driven Development lifecycle (specify → plan → tasks → implement); Code reviews must verify compliance with architectural principles; Automated testing required before merge; Clear documentation for all API endpoints and components; Every file shown becomes part of the tracked system state with purpose, imports, and dependencies maintained.

## Governance
This constitution supersedes all other practices; Amendments require documentation, approval, and migration plan; All PRs/reviews must verify compliance with these principles; Complexity must be justified with clear benefits; NO OpenAI API keys anywhere in the system - all secrets must be environment variables.

**Version**: 1.1.0 | **Ratified**: 2025-12-09 | **Last Amended**: 2025-12-13