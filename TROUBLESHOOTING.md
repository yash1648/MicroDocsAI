# Troubleshooting

## Common Issues
- Missing `GOOGLE_API_KEY`: Set it in `.env` or environment.
- Network/Quota errors: Check Gemini service status and limits.
- Windows paths: Use correct separators in configs.

## Debugging Tips
- Run with `LOG_LEVEL=DEBUG` for verbose logs.
- Inspect Docker logs: `docker-compose logs --tail 100`.
- Validate dependencies: `pip install -r requirements.txt`.

## Resetting State
- Stop and remove containers: `docker-compose down -v`.
- Clear caches/logs if necessary.