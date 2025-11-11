FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first so we can leverage Docker layer caching
COPY requirements.txt /app/requirements.txt

# Install system dependencies, create non-root user and install Python deps
# Keep this in one RUN to reduce layers
RUN DEBIAN_FRONTEND=noninteractive apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc libffi-dev libpq-dev libssl-dev \
    && useradd -m appuser \
    && pip install --no-cache-dir -r /app/requirements.txt \
    && rm -rf /var/lib/apt/lists/*

# Copy application code with ownership set to the non-root user to avoid permission issues
COPY --chown=appuser:appuser ./auth /app/auth
COPY --chown=appuser:appuser ./config /app/config
COPY --chown=appuser:appuser ./database /app/database
COPY --chown=appuser:appuser ./routers /app/routers
COPY --chown=appuser:appuser ./schemas /app/schemas
COPY --chown=appuser:appuser ./services /app/services
COPY --chown=appuser:appuser ./main.py /app/main.py

# Switch to non-root user
USER appuser


# Expose port
EXPOSE 8000

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Run uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]