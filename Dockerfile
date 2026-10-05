# ============================================================
# FAMILY HEALTH MF - DOCKERFILE OFICIAL RAILWAY (SOLUCION FINAL)
# Arquitectura: 2 etapas (multistage) para build frontend y luego runtime
# - Stage 1 = Node 20 (build Vite frontend dist/)
# - Stage 2 = Python 3.11 (Django + psycopg2 + gunicorn + whitenoise)
# NO requiere Nixpacks, NO hay providers que detectar, NO falla.
# ============================================================

# ------------- ETAPA 1: BUILD FRONTEND (Vue 3 + Vite) -------------
FROM node:20-bookworm-slim AS frontend-build
WORKDIR /src/frontend
COPY frontend/package*.json ./
RUN npm ci --no-audit --no-fund --loglevel=error || npm install --no-audit --no-fund --loglevel=error
COPY frontend/ ./
RUN npm run build -- --logLevel warn

# ------------- ETAPA 2: RUNTIME BACKEND (Django 5.0.7) -------------
FROM python:3.11-slim-bookworm AS runtime

# Seguridad / No interactividad
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Dependencias SISTEMA MINIMAS para psycopg2-binary y Numpy (NO hay que compilar nada)
RUN apt-get update -qq && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# -------- Backend requirements --------
COPY backend/requirements.txt /tmp/requirements.txt
RUN python -m pip install --upgrade pip --quiet && \
    python -m pip install -r /tmp/requirements.txt --quiet

# -------- Backend code --------
COPY backend /app/backend

# -------- Frontend build (Vite dist/) copiado desde etapa 1 --------
COPY --from=frontend-build /src/frontend/dist /app/frontend/dist

# -------- Variables --------
ENV DJANGO_SETTINGS_MODULE=config.settings
ENV PROJECT_ROOT=/app
WORKDIR /app/backend

EXPOSE 8000

# START: migrate + collectstatic + opcional seed + gunicorn
CMD ["bash", "-c", "\
set -euo pipefail; \
echo '[BOOT 1/3] Django migrate...'; \
python manage.py migrate --noinput -v 0; \
echo '[BOOT 2/3] Django collectstatic...'; \
python manage.py collectstatic --noinput --clear -v 0 2>&1 | tail -3 || true; \
if [ \"${RAILWAY_SEED_BOOTSTRAP:-0}\" = \"1\" ]; then \
  echo '[BOOT EXTRA] Seed bootstrap_data.py'; \
  python bootstrap_data.py || true; \
fi; \
echo '[BOOT 3/3] Gunicorn on 0.0.0.0:'\"${PORT:-8000}\"' workers='\"${WEB_CONCURRENCY:-2}\"; \
exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:${PORT:-8000} \
  --workers ${WEB_CONCURRENCY:-2} \
  --threads ${GUNICORN_THREADS:-4} \
  --timeout ${GUNICORN_TIMEOUT:-120} \
  --graceful-timeout 30 \
  --keep-alive 5 \
  --max-requests 1500 \
  --max-requests-jitter 100 \
  --access-logfile - \
  --error-logfile - \
  --log-level ${GUNICORN_LOGLEVEL:-info} \
"]
