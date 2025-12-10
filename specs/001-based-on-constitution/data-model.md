# Data Model: FastAPI Book Search with Qdrant and Gemini

## Overview
This document defines the data models for the FastAPI book search application, including entities, their attributes, relationships, and validation rules.

## Core Entities

### BookContent
Represents processed book content chunks with metadata, including original text, embedding vector, source file, and section information.

**Attributes**:
- `id` (str): Unique identifier for the content chunk
- `text` (str): Original text content of the chunk
- `embedding` (List[float]): Vector embedding representation of the text
- `source_file` (str): Original markdown filename
- `section` (str): Section identifier if applicable
- `title` (str): Title or heading associated with this content
- `created_at` (datetime): Timestamp of when the content was indexed
- `updated_at` (datetime): Timestamp of last update

**Validation Rules**:
- Text must be between 10 and 2000 characters
- Embedding vector must have correct dimensions (768 for Gemini)
- Source file must be a valid path reference

### SearchQuery
Represents user search requests with query text, parameters, and context.

**Attributes**:
- `query_text` (str): The natural language query from the user
- `top_k` (int): Number of results to return (default: 5, max: 20)
- `similarity_threshold` (float): Minimum similarity score (default: 0.7, range: 0.0-1.0)
- `filters` (Dict[str, Any]): Optional metadata filters
- `user_context` (str): Optional user context for personalized search

**Validation Rules**:
- Query text must be between 1 and 500 characters
- Top_k must be between 1 and 20
- Similarity_threshold must be between 0.0 and 1.0

### SearchResult
Represents semantically relevant content returned to users with similarity scores and source citations.

**Attributes**:
- `content` (BookContent): The matching content chunk
- `similarity_score` (float): Similarity score between 0.0 and 1.0
- `rank` (int): Position in the result list
- `explanation` (str): Optional explanation of why this result matches

**Validation Rules**:
- Similarity score must be between 0.0 and 1.0
- Rank must be positive integer

### ChatSession
Represents conversational state between user and AI agent with message history.

**Attributes**:
- `session_id` (str): Unique identifier for the chat session
- `messages` (List[Message]): History of messages in the conversation
- `created_at` (datetime): Timestamp of session creation
- `updated_at` (datetime): Timestamp of last interaction
- `context` (Dict[str, Any]): Context information for the conversation

**Validation Rules**:
- Session ID must be unique
- Messages list must not exceed 100 items

### Message
Represents a single message in a chat conversation.

**Attributes**:
- `message_id` (str): Unique identifier for the message
- `role` (str): Role of the message sender (user, assistant, system)
- `content` (str): The message content
- `timestamp` (datetime): When the message was created
- `sources` (List[BookContent]): Source citations for assistant responses

**Validation Rules**:
- Role must be one of: 'user', 'assistant', 'system'
- Content must not be empty

### EmbeddingJob
Represents a content processing job for converting markdown files to embeddings.

**Attributes**:
- `job_id` (str): Unique identifier for the job
- `status` (str): Current status (pending, processing, completed, failed)
- `source_files` (List[str]): List of markdown files to process
- `progress` (int): Number of files processed
- `total` (int): Total number of files to process
- `created_at` (datetime): Timestamp of job creation
- `completed_at` (datetime): Timestamp of job completion (if completed)

**Validation Rules**:
- Status must be one of: 'pending', 'processing', 'completed', 'failed'
- Progress must not exceed total

## Relationships
- One ChatSession contains many Messages
- One SearchResult references one BookContent
- One EmbeddingJob processes many BookContent items

## State Transitions

### EmbeddingJob Status Transitions
- `pending` → `processing`: When job starts processing
- `processing` → `completed`: When all files are successfully processed
- `processing` → `failed`: When processing encounters an unrecoverable error

### ChatSession Lifecycle
- Created when user starts a new conversation
- Updated with each message exchange
- Expires after inactivity period (configurable)

## Indexes and Performance Considerations
- Qdrant collection for BookContent with vector index on embedding field
- Metadata indexes on source_file and section for filtering
- Time-based indexes on created_at for content management