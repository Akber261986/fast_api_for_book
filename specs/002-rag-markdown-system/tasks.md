# Implementation Tasks: RAG System for Markdown Files

**Feature**: 002-rag-markdown-system
**Generated**: 2025-12-13
**Spec**: specs/002-rag-markdown-system/spec.md
**Plan**: specs/002-rag-markdown-system/plan.md

## Implementation Strategy

MVP scope: User Story 1 (Query Markdown Content) with minimal ingestion capability to test queries. Implement in priority order: P1 → P2 → P3. Each user story is independently testable and delivers value.

## Dependencies

User Story 2 (Ingest Markdown Files) must be completed before User Story 1 (Query Markdown Content) can be fully tested, as queries require ingested content. User Story 3 (Retrieve Relevant Context) is foundational but will be implemented as part of User Story 1.

## Parallel Execution Examples

- T002-T006 can be done in parallel (foundational components)
- T010-T015 can be done in parallel (US1 services)
- T020-T025 can be done in parallel (US2 services)

---

## Phase 1: Setup

### Goal
Initialize project structure and configure dependencies per implementation plan.

### Tasks

- [x] T001 Create project directory structure per plan: app/, app/api/, app/api/v1/, app/api/endpoints/, app/services/, app/models/, app/core/, app/utils/, tests/, tests/unit/, tests/integration/, tests/contract/
- [x] T002 Create requirements.txt with: fastapi, python-multipart, uvicorn, pydantic, python-qdrant-client, google-generativeai, pytest, python-dotenv
- [x] T003 Create pyproject.toml with project metadata and uv configuration
- [x] T004 Create .env.example with: GEMINI_API_KEY, QDRANT_HOST, QDRANT_PORT, QDRANT_API_KEY
- [x] T005 Create Dockerfile following Railway deployment requirements
- [x] T006 Create railway.toml configuration file
- [x] T007 Create basic main.py with FastAPI app initialization

---

## Phase 2: Foundational Components

### Goal
Implement core components required by all user stories: configuration, database connection, and AI client.

### Independent Test Criteria
- Configuration loads from environment variables
- Qdrant connection can be established
- Gemini client can authenticate

### Tasks

- [x] T008 [P] Create app/core/config.py with Pydantic Settings for environment configuration
- [x] T009 [P] Create app/core/database.py with Qdrant client connection and collection setup
- [x] T010 [P] Create app/core/gemini_client.py with Google Gemini API client wrapper
- [x] T011 [P] Create app/utils/chunking.py with semantic chunking logic (1000 tokens + 200 overlap)
- [x] T012 [P] Create app/utils/markdown_parser.py with Markdown parsing utilities
- [x] T013 [P] Add structured logging configuration to main application
- [x] T014 [P] Create health check endpoint at /health

---

## Phase 3: User Story 1 - Query Markdown Content (Priority: P1)

### Goal
Enable users to ask questions about content stored in Markdown files and receive accurate answers based on the content of those files.

### Independent Test Criteria
- Can ingest a single Markdown file
- Can submit a query about the content
- System returns an accurate response based on the document content
- Response includes source chunks and confidence score

### Tasks

- [x] T015 [US1] Create app/models/query.py with Pydantic models for query request/response
- [x] T016 [US1] Create app/models/embedding.py with Pydantic models for embedding data
- [x] T017 [US1] Create app/services/retrieval_service.py for Qdrant retrieval operations
- [x] T018 [US1] Create app/services/generation_service.py for Gemini response generation
- [x] T019 [US1] Create app/services/embedding_service.py for Gemini embedding generation
- [x] T020 [US1] Create app/api/endpoints/query.py with POST /query endpoint
- [x] T021 [US1] Implement semantic search logic in retrieval service
- [x] T022 [US1] Implement response generation with context constraint (only info from retrieved context)
- [x] T023 [US1] Add configurable similarity threshold support
- [x] T024 [US1] Implement proper error handling for query failures
- [x] T025 [US1] Add validation for query parameters (top_k, similarity_threshold)

---

## Phase 4: User Story 2 - Ingest Markdown Files (Priority: P2)

### Goal
Allow users to upload or specify Markdown files that should be made searchable by the system.

### Independent Test Criteria
- Can upload a Markdown file via API
- Content is properly chunked according to semantic strategy
- Embeddings are generated using Gemini
- Content is stored in Qdrant with proper metadata
- Multiple files can be processed and are available for querying

### Tasks

- [x] T026 [US2] Create app/models/document.py with Pydantic models for document data
- [x] T027 [US2] Create app/services/ingestion_service.py for Markdown processing and ingestion
- [x] T028 [US2] Create app/api/endpoints/ingest.py with POST /ingest endpoint
- [x] T029 [US2] Implement file upload handling with size validation (<10MB)
- [x] T030 [US2] Implement document parsing and semantic chunking
- [x] T031 [US2] Implement embedding generation for document chunks
- [x] T032 [US2] Implement Qdrant storage with proper metadata
- [x] T033 [US2] Add document state tracking (pending_ingestion → processed → indexed_in_qdrant)
- [x] T034 [US2] Implement file format validation (.md extension)
- [x] T035 [US2] Add error handling for ingestion failures

---

## Phase 5: User Story 3 - Retrieve Relevant Context (Priority: P3)

### Goal
Match user queries against vector embeddings to find the most semantically relevant content from stored Markdown files.

### Independent Test Criteria
- Query matches against stored embeddings return relevant content segments
- Similarity scores are properly calculated and returned
- Retrieval respects configurable thresholds
- Context includes proper source information for response generation

### Tasks

- [x] T036 [US3] Enhance retrieval service with configurable similarity threshold filtering
- [x] T037 [US3] Implement top-k retrieval with proper scoring
- [x] T038 [US3] Add support for metadata retrieval with chunks
- [x] T039 [US3] Implement query embedding generation using Gemini
- [x] T040 [US3] Add proper context formatting for response generation
- [x] T041 [US3] Implement handling for queries with no relevant content
- [x] T042 [US3] Add performance optimization for retrieval operations
- [x] T043 [US3] Add logging and metrics for retrieval quality

---

## Phase 6: Polish & Cross-Cutting Concerns

### Goal
Complete the implementation with production-ready features, security, and observability.

### Tasks

- [x] T044 Add comprehensive error handling with proper HTTP status codes
- [ ] T045 Implement rate limiting for API endpoints
- [x] T046 Add request/response logging with correlation IDs
- [x] T047 Implement proper API documentation with OpenAPI tags
- [x] T048 Add security headers and CORS configuration
- [ ] T049 Create comprehensive README with setup and usage instructions
- [ ] T050 Add performance monitoring and metrics
- [x] T051 Implement graceful shutdown handling
- [ ] T052 Add comprehensive test coverage (unit, integration, contract)
- [x] T053 Finalize environment configuration and Railway deployment settings