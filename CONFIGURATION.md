# Configuration Reference

MicroDocs AI reads configuration from environment variables and `.env`.

## Core Variables
- `GOOGLE_API_KEY`: Google Gemini API key (required).
- `LOG_LEVEL`: Logging level (e.g., `INFO`, `DEBUG`).
- `PROJECT_PATH`: Path to the Spring Boot project (Docker orchestrator).

## Optional Services (Docker)
- `MYSQL_ROOT_PASSWORD`, `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD`: MySQL credentials.
- `REDIS_PASSWORD`: Redis authentication.

## How to Set
1. Create `.env` (see `.envExample`).
2. Export variables in your shell or use Docker Compose `environment` section.

## Notes
- Ensure your API key scopes allow Gemini access.
- On Windows, use proper path separators in environment values.