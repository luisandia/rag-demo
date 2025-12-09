FROM python:3.11-slim as base

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN apt-get update && apt-get install -y gcc postgresql-client libpq-dev \
    && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash appuser
RUN chown -R appuser:appuser /app
USER appuser
EXPOSE 8000

# ---- Development stage ----
FROM base AS dev
# Make dev entrypoint executable
RUN chmod +x /app/docker/entrypoint-dev.sh
ENTRYPOINT ["/app/docker/entrypoint-dev.sh"]

# ---- Production stage ----
FROM base AS prod
# Use default CMD for production
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
