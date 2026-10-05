#!/usr/bin/env bash
# ============================================================
# Script Start - Railway (Gunicorn WSGI)
# Proyecto: Club Family Health MF - Trabajo Grado UAN
# ============================================================
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
cd "$BACKEND_DIR"

# === [DOBLE SEGURIDAD MIGRACIONES / STATIC] ===
# Build time puede no tener acceso a DB o fallar collectstatic.
# Nos aseguramos justo ANTES de arrancar Gunicorn:
echo "[RAILWAY START 1/3] Asegurando migraciones Django..."
python manage.py migrate --noinput -v 0

echo "[RAILWAY START 2/3] Asegurando staticfiles (collectstatic)..."
python manage.py collectstatic --noinput --clear -v 0 2>&1 | tail -3 || true

# Bootstrap seed (solo si RAILWAY_SEED_BOOTSTRAP=1 y no hay Admin creado):
if [[ "${RAILWAY_SEED_BOOTSTRAP:-0}" == "1" ]]; then
    echo "[RAILWAY START EXTRA] Poblando datos demo (bootstrap_data.py)..."
    python bootstrap_data.py || echo "WARN: bootstrap no aplicó (probablemente ya corrió)."
fi

PORT="${PORT:-8000}"
WORKERS="${WEB_CONCURRENCY:-2}"
THREADS="${GUNICORN_THREADS:-4}"
TIMEOUT="${GUNICORN_TIMEOUT:-120}"

echo "[RAILWAY START 3/3] Starting Gunicorn (workers=$WORKERS, threads=$THREADS, port=$PORT, timeout=$TIMEOUT)"

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
