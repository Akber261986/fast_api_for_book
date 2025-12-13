---
id: 1
title: Update Constitution for RAG System
stage: constitution
date: 2025-12-13
surface: agent
model: Claude Sonnet 4.5
feature: none
branch: 001-based-on-constitution
user: akber
command: /sp.constitution
labels: [constitution, rag, architecture, gemini, qdrant]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - none
---

## Prompt

You are Claude operating as a persistent system architect, debugger, and project auditor
for this repository.

PROJECT NAME:
RAG system for embedding Markdown (.md) files into Qdrant and answering queries using
Gemini (gemini-2.5-flash) via an agent-based architecture.

CORE RESPONSIBILITIES:
1. Track every file that the user shares or references.
2. Maintain a mental model of the full repository structure.
3. Detect inconsistencies between files, imports, configs, and runtime behavior.
4. Proactively identify bugs, edge cases, and missing pieces.
5. Log errors conceptually and suggest precise fixes.
6. Enforce all architectural constraints listed below.
7. When unsure, ask clarifying questions instead of guessing.

ARCHITECTURAL CONSTRAINTS (NON-NEGOTIABLE):
- Python project managed using `uv`
- Vector database: Qdrant
- Data source: Markdown (.md) files
- Embeddings: Gemini embeddings (NOT OpenAI)
- LLM: gemini-2.5-flash
- Agent framework: OpenAI Agents SDK (used WITHOUT OpenAI API keys)
- Chat interface: ChatKit
- Deployment target: Railway
- NO OpenAI API keys anywhere in the system
- All secrets must be environment variables

FILE TRACKING RULES:
- Every file shown becomes part of the tracked system state.
- You must remember:
  - File purpose
  - Imports
  - Public functions
  - Cross-file dependencies
- If a file is modified, update your internal understanding of it.
- If a file is missing but referenced, flag it immediately.

ERROR TRACKING & DEBUGGING:
- When the user pastes an error:
  - Identify the root cause
  - Reference the exact file(s) involved
  - Propose the minimal correct fix
- Track recurring error patterns.
- Warn if a fix introduces architectural violations.

RAG-SPECIFIC INTELLIGENCE:
- Ensure document chunking is sane and retrieval-safe.
- Watch for:
  - Embedding dimension mismatches
  - Qdrant collection misconfiguration
  - Incorrect distance metrics
  - Prompt leakage outside retrieved context
- Flag hallucination risks if context handling is weak.

AGENT & PROMPT SAFETY:
- Ensure sy

## Response snapshot

I've updated the project constitution to align with the specified RAG system architecture. Here are the key changes made:

**Version**: 1.0.0 → 1.1.0 (Minor version bump due to principle updates)

**Key Changes**:
1. Updated the project name to reflect the RAG system for Markdown files with Qdrant and Gemini
2. Modified Principle II to emphasize Gemini-centric AI integration and explicitly prohibit OpenAI usage
3. Updated Principle VI to focus on RAG system excellence with proper document processing
4. Revised the Architecture and Technology Stack to clearly specify the required components
5. Added specific governance clause about NO OpenAI API keys anywhere in the system
6. Updated the Development Workflow to include file tracking requirements

The constitution now properly reflects the architectural constraints specified in the user input, particularly emphasizing:
- NO OpenAI API keys anywhere in the system
- Exclusive use of Gemini (gemini-2.5-flash) for embeddings
- Markdown (.md) files as the primary data source
- Qdrant as the vector database
- Railway as the deployment target

## Outcome

- ✅ Impact: Updated constitution to align with RAG system architecture requirements
- 🧪 Tests: none
- 📁 Files: .specify/memory/constitution.md updated
- 🔁 Next prompts: Implementation can now proceed with clear architectural guidance
- 🧠 Reflection: The constitution now properly enforces the non-negotiable architectural constraints

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Begin implementation following the updated constitution