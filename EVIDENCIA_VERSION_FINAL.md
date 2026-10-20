# EVIDENCIA DE VERSIÓN FINAL (CONGELAMIENTO)

**Proyecto:** Family Health MF — Aplicativo Web Mobile-First para la gestión centralizada de reservas del Club Family Health
**Trabajo de Grado:** Ingeniería de Sistemas y Computación — Universidad Antonio Nariño (UAN), sede Maicao, La Guajira
**Autor:** Luis Fermín Díaz Choles
**Fecha de generación de este documento:** 2026-10-19 (America/Bogota)

> Este documento registra el **punto de restauración** y el **estado congelado** del software antes de iniciar las actividades de cierre técnico. No contiene secretos, tokens ni credenciales.

---

## 1. Punto de restauración (estado congelado)

| Elemento | Valor |
|---|---|
| Repositorio | `https://github.com/LuisDiaz2026/Family_Health_MF.git` |
| Rama congelada | `release/tg-final` |
| Commit (SHA completo) | `fed4f2206d53410ab07346698ee44bf891ca4718` |
| Commit (SHA corto) | `fed4f22` |
| Mensaje del commit | `fix(bootstrap): separar actualizacion de contraseñas en transaccion independiente` |
| Fecha del commit | 2026-10-12 16:19:11 -0500 |
| Rama remota equivalente | `origin/main` (mismo commit: `fed4f22`) |

El commit `fed4f22` es **idéntico** a `origin/main` (verificado con `git rev-list --left-right --count HEAD...origin/main` → `0 0`). La rama `release/tg-final` se creó como rama de cierre a partir de ese punto, garantizando que todo el trabajo posterior es reversible.

### Comandos de verificación

```powershell
git branch --show-current          # release/tg-final
git rev-parse HEAD                 # fed4f2206d53410ab07346698ee44bf891ca4718
git rev-list --left-right --count HEAD...origin/main   # 0	0
git log -1 --format="%H|%ad|%s" --date=iso
```

### Estado del repositorio al congelar

- **Modificados** (defectos corregidos durante el cierre, ver informe final): `backend/apps/reservations/serializers.py`, `backend/bootstrap_data.py`, `backend/config/settings.py`, `backend/smoke_test.py`
- **Nuevos**: `tests/` (suite de 31 unitarias + 12 de integración + automatización de navegador), `evidencias/`, documentos de cierre.

---

## 2. Tecnologías y versiones (verificadas en ejecución)

| Componente | Versión | Fuente de la verificación |
|---|---|---|
| Python (entorno local del proyecto) | **3.10.11** | `python -c "import sys; print(sys.version)"` |
| Python (contenedor de producción) | **3.11-slim-bookworm** | `Dockerfile`, etapa `runtime` |
| Django | **5.0.7** | `django.get_version()` |
| Django REST Framework | **3.15.2** | `rest_framework.VERSION` |
| djangorestframework-simplejwt | 5.3.1 | `backend/requirements.txt` |
| django-axes | 6.3.0 | `backend/requirements.txt` |
| django-cors-headers | 4.4.0 | `backend/requirements.txt` |
| argon2-cffi | 23.1.0 | `backend/requirements.txt` |
| psycopg2-binary | 2.9.9 | `backend/requirements.txt` |
| gunicorn | 21.2.0 | `backend/requirements.txt` |
| whitenoise | 6.6.0 | `backend/requirements.txt` |
| Node.js (local, herramientas) | **v24.14.0** | `node -v` |
| npm | **11.9.0** | `npm -v` |
| Node.js (build de producción) | **20-bookworm-slim** | `Dockerfile`, etapa `frontend-build` |
| Vue | ^3.4.0 | `frontend/package.json` |
| Vue Router | ^4.2.5 | `frontend/package.json` |
| Pinia | ^2.1.7 | `frontend/package.json` |
| Axios | ^1.6.0 | `frontend/package.json` |
| Vite | ^5.0.0 | `frontend/package.json` |
| Tailwind CSS | ^3.4.0 | `frontend/package.json` |

---

## 3. Base de datos

| Entorno | Motor | Detalle |
|---|---|---|
| **Desarrollo local** | **SQLite 3** (`django.db.backends.sqlite3`) | Archivo `backend/db.sqlite3` (`DB_ENGINE`/`DB_NAME` en `.env`). Verificado en ejecución: `ENGINE=django.db.backends.sqlite3`, `NAME=C:\Family_Health_MF\backend\db.sqlite3` |
| **Pruebas automatizadas** | **SQLite en memoria** | Aislada por el runner de Django; `tests/run_suite.py` neutraliza cualquier `DATABASE_URL` externo |
| **Producción (Railway)** | **PostgreSQL** (servicio administrado por Railway) | Seleccionado automáticamente al existir la variable `DATABASE_URL` con esquema `postgres*` (`backend/config/settings.py`, detección vía `dj-database-url`). El endpoint público no expone la versión del motor; no se declara un número de versión no verificado |

### Regla de seguridad aplicada en la configuración

En `backend/config/settings.py` (rama `DEBUG=True`) la variable `DATABASE_URL` se lee **únicamente** desde el archivo `.env` del proyecto, nunca desde la variable de entorno global del sistema operativo. Esto evita que un `DATABASE_URL` perteneciente a **otro** proyecto instalado en el mismo equipo desvíe la ejecución local hacia una base de datos ajena.

---

## 4. Despliegue y disponibilidad

| Elemento | Valor |
|---|---|
| Plataforma | Railway (constructores: `DOCKERFILE` multietapa) |
| URL pública | `https://familyhealthmf-production.up.railway.app` |
| Endpoint de salud | `/api/v1/health/` |
| Health check configurado en `railway.json` | `healthcheckPath: /api/v1/health/`, 15 s de espera, 6 reintentos |
| Servidor de aplicación | Gunicorn (`config.wsgi:application`), 2 workers × 4 hilos |

### Respuesta REAL del health check (2026-10-20T03:54:31 UTC)

```json
{
  "status": "ok",
  "timestamp": "2026-10-20T03:54:31.826180+00:00",
  "version": "1.0.0",
  "app": "Club Family Health MF API",
  "club_name": "Club Family Health",
  "club": {"name": "Club Family Health", "nit": "32739028-5", "city": "Maicao, La Guajira"},
  "database": "ok"
}
```

Código HTTP observado: **200**. El campo `database` confirma conectividad con PostgreSQL en producción.

---

## 5. Verificación de ausencia de secretos

- `DJANGO_SECRET_KEY` se obtiene por variable de entorno. En producción (`DEBUG=False`) el arranque **falla** si no está definida (`RuntimeError` explícito en `settings.py`); nunca se usa una clave autogenerada en producción.
- El archivo `.env` está excluido del repositorio (`.gitignore`); sólo se versiona `.env.example` con valores de relleno.
- Este documento y el resto de evidencias **no** incluyen tokens JWT, contraseñas ni cadenas de conexión. En los reportes de pruebas los tokens se enmascaran en el formato `eyJhbGciOi...XXXX (N car.)`.

---

## 6. Cierre de la versión

- **Rama de cierre:** `release/tg-final`
- **Etiqueta de versión:** `v1.0.0` (creada sobre el commit final de la rama de cierre)
- **Artefacto de evidencias:** carpeta `evidencias/` (comprimible)

La correspondencia entre requerimientos, historias de usuario, módulos, código, endpoints y pruebas se documenta en `MATRIZ_CORRESPONDENCIA_FINAL.xlsx`. Los resultados consolidados, en `INFORME_RESULTADOS_FINALES.md`.
