#!/usr/bin/env bash
# ============================================================
# Script Start - Railway (Gunicorn WSGI)
# Proyecto: Club Family Health MF - Trabajo Grado UAN
# ============================================================
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
cd "$BACKEND_DIR"

PORT="${PORT:-8000}"
WORKERS="${WEB_CONCURRENCY:-2}"
THREADS="${GUNICORN_THREADS:-4}"
TIMEOUT="${GUNICORN_TIMEOUT:-120}"

echo "Starting Gunicorn (workers=$WORKERS, threads=$THREADS, port=$PORT, timeout=$TIMEOUT)"

exec gunicorn config.wsgi:application \
    --name family_health_mf \
    --bind "0.0.0.0:${PORT}" \
    --workers "${WORKERS}" \
    --threads "${THREADS}" \
    --timeout "${TIMEOUT}" \
    --graceful-timeout 30 \
    --keep-alive 5 \
    --max-requests 1500 \
    --max-requests-jitter 100 \
    --access-logfile - \
    --error-logfile - \
    --log-level "${GUNICORN_LOGLEVEL:-info}"
