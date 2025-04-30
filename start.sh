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

# === Start Flask backend in background ===
echo "Starting Flask backend on port 5001..."
flask run --port 5001 &
BACKEND_PID=$!

# === Start Vue frontend ===
echo "Starting Vue frontend..."
(cd frontend && npm run serve)

# === Cleanup ===
echo "Shutting down Flask backend..."
kill $BACKEND_PID