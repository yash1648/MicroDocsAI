# Usage Guide

## Prerequisites
- Python 3.11, `pip`.
- Google API key with access to Gemini.

## Local Run
1. `pip install -r requirements.txt`
2. Set `GOOGLE_API_KEY` in your environment or `.env`.
3. Run orchestrator: `python main.py`
4. Run RAG engine: `python rag_system.py`
5. Run evaluator: `python evaluation.py`

Outputs are written to `documentation_output.json` and logs into `logs/` (if configured).

## Docker
- See `DockerGuide.md` for full container setup.
- Quick start: `docker-compose up -d`

## Common Commands
- `python main.py` – generate documentation.
- `python rag_system.py` – query documentation semantically.
- `python evaluation.py` – assess documentation quality.