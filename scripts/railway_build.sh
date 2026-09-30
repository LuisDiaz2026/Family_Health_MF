#!/usr/bin/env bash
# ============================================================
# Script Build - Railway (Nixpacks Node + Python)
# Proyecto: Club Family Health MF - Trabajo Grado UAN
# ============================================================
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

echo "[1/5] Instalando dependencias NPM (frontend)..."
cd "$FRONTEND_DIR"
npm ci --no-audit --no-fund --loglevel=error

echo "[2/5] Compilando SPA Vue 3 (Vite build)..."
npm run build -- --logLevel warn

echo "[3/5] Instalando dependencias Python (backend)..."
cd "$BACKEND_DIR"
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt --quiet

echo "[4/5] Ejecutando collectstatic (Django + WhiteNoise)..."
python manage.py collectstatic --noinput --clear -v 0 2>&1 | tail -5 || true

echo "[5/5] Aplicando migraciones (Django ORM)..."
python manage.py migrate --noinput -v 0

if [[ "${RAILWAY_SEED_BOOTSTRAP:-0}" == "1" ]]; then
    echo "[EXTRA] Poblando datos demo (bootstrap_data.py)..."
    python bootstrap_data.py || echo "WARNING: bootstrap_data.py falló, continuando sin seed."
fi

echo "BUILD COMPLETADO RAILWAY OK."
