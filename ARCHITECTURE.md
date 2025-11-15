# MicroDocs AI Architecture

This document explains the high-level architecture and data flow.

## Components
- Orchestrator Agent (`main.py`): Coordinates analysis and documentation generation.
- RAG Engine (`rag_system.py`): Provides semantic search over documentation and code.
- Evaluator (`evaluation.py`): LLM-as-Judge to assess documentation quality.
- Utilities (`utils.py`): Helpers for parsing, IO, formatting.
- Sample Project (`sample_project/`): Demo Spring Boot microservices.

## Data Flow
1. Source code from `sample_project/` is parsed and analyzed.
2. Orchestrator triggers agents to generate OpenAPI specs and dependency maps.
3. Outputs are stored in `documentation_output.json` and related files.
4. RAG indexes documentation for semantic queries.
5. Evaluator scores documentation quality and produces reports.

## Dependencies & Config
- Uses Google Gemini via `google-generativeai` (`GOOGLE_API_KEY`).
- Configuration through `.env`, `docker-compose.yml`, and environment variables.

## Diagram
Refer to `images/architecture.png` for a visual overview.