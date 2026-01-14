FROM python:3.11-slim as base

WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Install Python dependencies directly
RUN pip install --no-cache-dir \
    fastapi>=0.104.0 \
    uvicorn[standard]>=0.24.0 \
    pydantic>=2.4.0 \
    pydantic-settings>=2.0.0

# Copy application code
COPY apps/ ./apps/
COPY packages/ ./packages/

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run the application
# Use environment variables for host and port configuration
CMD uvicorn apps.api.main:app --host ${APP_HOST:-0.0.0.0} --port ${APP_PORT:-8000}
