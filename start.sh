#!/usr/bin/env bash
set -e

# === Activate Python virtual environment ===
if [ -f "./venv/bin/activate" ]; then
  source "./venv/bin/activate"
else
  echo "Virtual environment not found. Run: python3 -m venv venv" >&2
  exit 1
fi

# === Export Flask settings ===
export FLASK_APP="backend.app:create_app"
export FLASK_ENV=development
export FLASK_DEBUG=1

# === Start Redis ===
echo "Starting Redis server..."
redis-server --daemonize yes

# === Start Celery worker ===
echo "Starting Celery worker..."
celery -A backend.celery_app.celery worker --loglevel=info &
CELERY_WORKER_PID=$!

# === Start Celery beat ===
echo "Starting Celery beat..."
celery -A backend.celery_app.celery beat --loglevel=info &
CELERY_BEAT_PID=$!

# === Start Flask backend in background ===
echo "Starting Flask backend on port 5001..."
flask run --port 5001 &
BACKEND_PID=$!

# === Start Vue frontend ===
echo "Starting Vue frontend..."
(cd frontend && npm run serve)

# === Cleanup ===
echo "Shutting down services..."
kill $BACKEND_PID
kill $CELERY_WORKER_PID
kill $CELERY_BEAT_PID
redis-cli shutdown