# ============================================================
# Family Health MF - Railway Dockerfile (Despliegue GARANTIZADO)
# NO USA NIXPACKS. Usa image oficial Python 3.11 + instala Node 20.
# Build: Vite build frontend, pip install requirements, collectstatic, migrate
# Run:   Gunicorn config.wsgi application
# ============================================================

# Etapa 1: Python 3.11 (Django / Backend)
FROM python:3.11-slim-bookworm AS base

# Evitar preguntas interactivas de apt-get
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Instalar dependencias SO: curl (nvm/node), git, libpq-dev (psycopg2 build), gcc, pkg-config
RUN apt-get update -qq && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    git \
    gcc \
    g++ \
    make \
    libpq-dev \
    pkg-config \
    procps \
    bash && \
    rm -rf /var/lib/apt/lists/*

# Instalar NODE v20 LTS + npm (directo, no nvm - es más rápido)
# Usamos nodesource en Debian Bookworm
ARG NODE_MAJOR=20
RUN mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_${NODE_MAJOR}.x nodistro main" > /etc/apt/sources.list.d/nodesource.list && \
    apt-get update -qq && apt-get install -y --no-install-recommends nodejs && \
    npm install -g npm@latest --silent && \
    node --version && npm --version

# Copiar TODO el repo al WORKDIR /app
COPY . /app/

# -------- Backend Python (Django 5.0.7 + psycopg2-binary) --------
WORKDIR /app/backend
RUN python -m pip install --upgrade pip --quiet && \
    python -m pip install -r requirements.txt --quiet && \
    python -m pip install gunicorn whitenoise --quiet

# -------- Frontend Node.js / Vite build --------
WORKDIR /app/frontend
RUN npm ci --no-audit --no-fund --loglevel=error || npm install --no-audit --no-fund --loglevel=error; \
    npm run build -- --logLevel warn

# -------- CollectStatic + Migrate en START (no en build - Railway build no tiene DB) --------
WORKDIR /app/backend

# Puerto Railway variable PORT por defecto 8000
EXPOSE 8000

# Start Command: siempre hacemos migrate + collectstatic antes de gunicorn.
ENV DJANGO_SETTINGS_MODULE=config.settings
CMD ["bash", "-c", "set -euo pipefail; cd /app/backend; python manage.py migrate --noinput -v 0; python manage.py collectstatic --noinput --clear -v 0 2>&1 | tail -3 || true; if [ \"${RAILWAY_SEED_BOOTSTRAP:-0}\" = \"1\" ]; then python bootstrap_data.py || true; fi; exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers ${WEB_CONCURRENCY:-2} --threads ${GUNICORN_THREADS:-4} --timeout ${GUNICORN_TIMEOUT:-120} --graceful-timeout 30 --keep-alive 5 --max-requests 1500 --max-requests-jitter 100 --access-logfile - --error-logfile - --log-level ${GUNICORN_LOGLEVEL:-info}"]
