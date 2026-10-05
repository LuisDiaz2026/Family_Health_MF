#!/usr/bin/env bash
# ============================================================
# Script Build - Railway (Nixpacks Node + Python)
# Proyecto: Club Family Health MF - Trabajo Grado UAN
# ============================================================
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

# ============================================================
# FIX RAILWAY: asegurar que Node.js (npm/npx) está disponible.
# Nixpacks a veces NO pone node/node_modules/.bin en el PATH
# si el package.json no está en la RAÍZ del repo.
# ============================================================
fix_node_path() {
    local found=0

    # 1) Nixpacks Node provider (ruta estándar)
    if [[ -d "/nix/var/nix/profiles/default/bin" ]] && [[ -x "/nix/var/nix/profiles/default/bin/npm" ]]; then
        export PATH="/nix/var/nix/profiles/default/bin:$PATH"
        found=1
    fi

    # 2) Nix profile user
    if [[ -x "$HOME/.nix-profile/bin/npm" ]]; then
        export PATH="$HOME/.nix-profile/bin:$PATH"
        found=1
    fi

    # 3) NVM fallback
    if [[ -s "$HOME/.nvm/nvm.sh" ]]; then
        # shellcheck disable=SC1091
        source "$HOME/.nvm/nvm.sh" || true
        command -v npm >/dev/null 2>&1 && found=1
    fi

    # 4) /opt/node (Railway legacy)
    for d in /opt/node* /usr/local/node*; do
        if [[ -d "$d/bin" && -x "$d/bin/npm" ]]; then
            export PATH="$d/bin:$PATH"
            found=1
            break
        fi
    done

    # 5) Última medida: si Nixpacks instaló node pero el provider python no
    #    encontró npm, buscamos con which -a en TODAS las rutas
    local n
    n="$(which -a npm node 2>/dev/null | head -1 || true)"
    if [[ -n "$n" ]]; then
        export PATH="$(dirname "$n"):$PATH"
        found=1
    fi

    # Si después de TODO no encontramos npm, salimos con error CLARO.
    if [[ $found -eq 0 ]]; then
        echo ""
        echo "============================================"
        echo "ERROR CRÍTICO RAILWAY: npm (Node.js) NO ENCONTRADO."
        echo "============================================"
        echo "Solución: en el servicio Family_Health_MF → Variables,"
        echo "AGREGA esta variable RAW y haz Redeploy:"
        echo "    NIXPACKS_NODE_VERSION = 20"
        echo "============================================"
        exit 127
    fi

    echo "[PRE-CHECK] Node.js detectado OK:"
    echo "  node: $(command -v node) ($(node -v 2>/dev/null || echo "v??"))"
    echo "  npm:  $(command -v npm) ($(npm -v 2>/dev/null || echo "??"))"
}
fix_node_path
# ============================================================
# FIX RAILWAY: asegurar que python/pip disponibles.
# Railway/Nixpacks a veces solo crea `python3` sin alias `python`.
# ============================================================
fix_python_path() {
    local pybin=""

    # 1) Busca python en rutas Nixpacks estándar
    for d in \
        /nix/var/nix/profiles/default/bin \
        "$HOME/.nix-profile/bin" \
        /opt/nix/*/bin \
        /pkg/nix/*/bin \
        /usr/local/bin \
        /usr/bin \
        /app; do

        if [[ -x "$d/python" ]]; then
            pybin="$d/python"; break
        elif [[ -z "$pybin" && -x "$d/python3" ]]; then
            pybin="$d/python3"
        fi
    done

    # 1b) Busca con `which -a python3 python` por si PATH no contiene las rutas Nix
    if [[ -z "$pybin" ]]; then
        local w
        w="$(which -a python python3 2>/dev/null | head -1 || true)"
        if [[ -n "$w" ]]; then
            pybin="$w"
            export PATH="$(dirname "$w"):$PATH"
        fi
    fi

    # 2) Si solo tenemos python3, crea alias `python` en un temp PATH
    if [[ -n "$pybin" && "$(basename "$pybin")" == "python3" ]]; then
        local tmpdir
        tmpdir="$(mktemp -d 2>/dev/null || mktemp -d -t pybin)"
        ln -sf "$pybin" "$tmpdir/python"
        ln -sf "${pybin}3-config" "$tmpdir/python-config" 2>/dev/null || true
        export PATH="$tmpdir:$PATH"
        # Alias shell por si acaso
        python() { "$pybin" "$@"; }
        export -f python 2>/dev/null || true
    elif [[ -n "$pybin" ]]; then
        export PATH="$(dirname "$pybin"):$PATH"
    fi

    if ! command -v python >/dev/null 2>&1; then
        echo ""
        echo "============================================"
        echo "ERROR CRÍTICO RAILWAY: python NO ENCONTRADO."
        echo "============================================"
        echo "Solución: agrega NIXPACKS_PYTHON_VERSION=3.11 en Variables"
        echo "y haz Redeploy."
        echo "============================================"
        exit 127
    fi

    echo "[PRE-CHECK] Python detectado OK:"
    echo "  python: $(command -v python)"
    echo "  version: $(python -c 'import sys; print(sys.version.split()[0])' 2>/dev/null || echo '??')"
    echo "  pip:    $(python -m pip --version 2>/dev/null | head -1 || echo 'no pip')"
}
fix_python_path

echo "[1/5] Instalando dependencias NPM (frontend)..."
cd "$FRONTEND_DIR"
npm ci --no-audit --no-fund --loglevel=error || npm install --no-audit --no-fund --loglevel=error

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
