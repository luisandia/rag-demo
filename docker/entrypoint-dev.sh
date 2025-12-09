#!/bin/bash
set -e

# -------------------------------
# Wait for Postgres to be ready
# -------------------------------
echo "Waiting for database..."
while ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" > /dev/null 2>&1; do
  sleep 1
done
echo "Database is up!"

# -------------------------------
# Optional: Run migrations here
# -------------------------------
# echo "Running migrations..."
# alembic upgrade head

# -------------------------------
# Start FastAPI with reload
# -------------------------------
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload
