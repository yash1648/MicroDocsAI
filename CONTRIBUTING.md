# Contributing to MicroDocs AI

Thank you for your interest in contributing! This project automates documentation for Spring Boot microservices using a multi-agent architecture and a RAG engine.

## Getting Started
- Clone the repo and create a Python 3.11 virtual environment.
- Install dependencies: `pip install -r requirements.txt`.
- Set `GOOGLE_API_KEY` in `.env` or your shell.
- Run locally: `python main.py` (or see `DockerGuide.md`).

## Development Workflow
- Open a feature/bugfix branch from `main`.
- Keep changes small and focused; include tests where relevant.
- Update docs if behavior or configuration changes.
- Ensure code passes linting and runs without errors.

## Coding Standards
- Use type hints and clear function names.
- Prefer straightforward logic; avoid unnecessary complexity.
- Log meaningful events; avoid noisy logs.

## Pull Requests
- Describe the change, rationale, and impact.
- Include screenshots or sample output if applicable.
- Reference related issues.
- Update `CHANGELOG.md` for user-facing changes.

## Areas to Contribute
- Agent improvements (orchestrator, evaluator, RAG).
- Documentation (guides, examples, FAQs).
- Docker and deployment workflows.
- Sample Spring Boot project enhancements.

## Reporting Issues
- Provide reproduction steps and environment details.
- Attach logs from `logs/` if available.

## License
- By contributing, you agree your contributions are licensed under the repository’s license.