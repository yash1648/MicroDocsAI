# Frequently Asked Questions

## What does MicroDocs AI do?
It automates documentation generation for Spring Boot microservices and provides semantic search and evaluation.

## What API key is required?
Set `GOOGLE_API_KEY` with access to Google Gemini. See `CONFIGURATION.md`.

## How do I run quickly?
Use Docker: `docker-compose up -d`. For local runs, see `USAGE.md`.

## Where are outputs stored?
Generated docs are saved to `documentation_output.json`. Logs may be in `logs/`.

## I get API quota or auth errors.
Verify `GOOGLE_API_KEY` validity and quotas. Retry after limits reset.