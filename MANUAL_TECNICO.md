# Manual Técnico - Family Health MF

> Trabajo de Grado - Universidad Antonio Nariño - Autor: Luis Díaz

Documento técnico del aplicativo web Mobile-First de gestión de reservas del **Club Family Health** (Maicao, La Guajira). Este manual describe exclusivamente componentes, archivos, comandos y rutas que existen realmente en el repositorio `c:\Family_Health_MF`.

---

## 1. Descripción general del sistema y alcance

**Family Health MF** es un aplicativo web con enfoque *mobile-first* que integra la operación del Club Family Health en un único sistema: autenticación de usuarios con roles, reserva de espacios deportivos y recreativos (con control anti-solapamiento horario), venta de productos de refresquería, programa de fidelización por puntos, rutinas de gimnasio con fines informativos y un panel administrativo con indicadores operativos.

Alcance funcional confirmado por el código:

- **Cliente (rol CLIENT):** registro, inicio de sesión, reserva de espacios con asistente por pasos, consulta de disponibilidad, pedidos de refresquería, puntos y recompensas, consulta de rutinas de gimnasio, perfil y notificaciones.
- **Recepción (rol RECEPCION):** gestión de reservas (listar, aprobar, rechazar, marcar pagada, cancelar), consulta de clientes y espacios.
- **Cafetería (rol CAFETERIA):** gestión de productos, ofertas y pedidos de barra.
- **Administrador (rol ADMIN):** control total, panel de KPIs, reportes, gestión de usuarios, catálogos y configuración.

Fuera de alcance (no implementado, confirmado en el README del proyecto y en el código): aplicaciones nativas iOS/Android, pasarelas de pago en línea (el cobro es presencial), hardware externo (torniquetes, RFID), inteligencia artificial/ML e integraciones con terceros.

El sistema está desplegado en producción en Railway: `https://familyhealthmf-production.up.railway.app/`. Puede ejecutarse también en entorno local de desarrollo con SQLite.

---

## 2. Arquitectura

El sistema sigue una arquitectura de N capas con separación *frontend* / *backend* y una única base de datos relacional.

| Capa | Componentes reales |
|---|---|
| Presentación (SPA) | Vue 3 (Composition API), Vite 5, Pinia, Vue Router 4, Axios, Tailwind CSS 3 |
| Lógica de negocio (API) | Django 5.0.7 + Django REST Framework 3.15.2 (ViewSets, acciones `@action`) |
| Persistencia | SQLite 3 en desarrollo local; PostgreSQL en producción (vía `dj-database-url`) |
| Servidor de aplicación | Gunicorn (producción) / `runserver` (desarrollo) |
| Servidor de estáticos y SPA | WhiteNoise dentro del mismo contenedor Django |

**Flujo de petición:** el navegador carga la SPA; la SPA consume la API REST bajo el prefijo `/api/v1/` usando JWT (Bearer). En producción no hay Nginx ni un servidor de Vite: Django sirve la SPA compilada y los estáticos a través de WhiteNoise.

### Cómo se sirve la SPA dentro del contenedor Django

Verificado en `backend/config/settings.py`:

- `STATIC_URL = "/static/"`.
- `STATIC_ROOT = BASE_DIR / "staticfiles"`.
- `SPA_BUILD_DIR = PROJECT_ROOT / "frontend" / "dist"`.
- `STATICFILES_DIRS = [BASE_DIR / "static"]` y, si `SPA_BUILD_DIR` existe, se añade a `STATICFILES_DIRS`.
- `STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"`.
- El middleware `whitenoise.middleware.WhiteNoiseMiddleware` está registrado justo después de `SecurityMiddleware`.
- Vite compila con `base: '/static/'` y `outDir: ./dist` (`frontend/vite.config.js`), por lo que los recursos del bundle quedan bajo `/static/`.

La ruta raíz de la SPA (`frontend/src/router/index.js`) usa **hash history** (`createWebHashHistory`), por lo que la navegación del cliente no requiere reglas de reescritura del servidor. No obstante, `backend/config/urls.py` define una vista `spa_index` que, como último patrón de URL, entrega `frontend/dist/index.html` (o `staticfiles/index.html`) para cualquier ruta que no empiece por `admin`, `api`, `media`, `static`, `robots.txt` o `favicon.ico`.

---

## 3. Tecnologías y versiones exactas

Tomadas literalmente de `backend/requirements.txt` y `frontend/package.json`. El runtime de Python local es **3.10.11** (entorno `.venv`) y el contenedor de producción usa **Python 3.11-slim-bookworm**.

### Backend (`backend/requirements.txt`)

| Paquete | Versión |
|---|---|
| Django | 5.0.7 |
| django-environ | 0.11.2 |
| djangorestframework | 3.15.2 |
| djangorestframework-simplejwt | 5.3.1 |
| django-cors-headers | 4.4.0 |
| django-ratelimit | 4.1.0 |
| django-axes | 6.3.0 |
| django-allauth | 0.61.1 |
| argon2-cffi | 23.1.0 |
| django-hashid-field | 3.4.1 |
| django-phonenumber-field[phonenumbers] | 7.3.0 |
| Pillow | 10.3.0 |
| psycopg2-binary | 2.9.9 |
| dj-database-url | 2.2.0 |
| openpyxl | 3.1.5 |
| reportlab | 4.1.0 |
| python-dateutil | 2.9.0.post0 |
| pytz | 2024.1 |
| pytest | 8.0.2 |
| pytest-django | 4.8.0 |
| pytest-cov | 5.0.0 |
| factory-boy | 3.3.1 |
| black | 24.3.0 |
| flake8 | 7.0.0 |
| isort | 5.13.2 |
| mypy | 1.9.0 |
| gunicorn | 21.2.0 |
| whitenoise | 6.6.0 |

### Frontend (`frontend/package.json`)

| Paquete | Versión declarada |
|---|---|
| vue | ^3.4.0 |
| vue-router | ^4.2.5 |
| pinia | ^2.1.7 |
| axios | ^1.6.0 |
| lucide-vue-next | ^0.312.0 |
| @vitejs/plugin-vue (dev) | ^5.0.0 |
| vite (dev) | ^5.0.0 |
| tailwindcss (dev) | ^3.4.0 |
| postcss (dev) | ^8.4.32 |
| autoprefixer (dev) | ^10.4.16 |

### Entorno

| Elemento | Valor |
|---|---|
| Python local | 3.10.11 (`.venv` del proyecto) |
| Python producción | `python:3.11-slim-bookworm` (etapa runtime del `Dockerfile`) |
| Node build producción | `node:20-bookworm-slim` (etapa de build del `Dockerfile`) |
| Node local (herramientas) | v24.14.0 / npm 11.9.0 (evidencia en `evidencias/_versions.txt`) |

---

## 4. Estructura del repositorio

```
c:\Family_Health_MF\
├── backend/
│   ├── config/            Settings (settings.py), URLs raíz (urls.py), WSGI/ASGI
│   ├── apps/
│   │   ├── authentication/  Usuarios RBAC, perfil, auditoría Ley 1581
│   │   ├── reservations/    Espacios, horarios, festivos y reservas
│   │   ├── refreshments/    Productos, categorías, ofertas y pedidos
│   │   ├── rewards/         Reglas, niveles, transacciones, catálogo de premios
│   │   ├── gym/             Músculos, equipo, ejercicios, rutinas y registros
│   │   └── reports/         Notificaciones, KPIs y salud (health check)
│   ├── manage.py            Punto de entrada Django
│   ├── requirements.txt     Dependencias backend
│   ├── bootstrap_data.py    Semilla (usuarios demo, espacios, productos, rutinas)
│   ├── smoke_test.py        Pruebas humo de la API (14 casos)
│   ├── fix_tiers.py         Script auxiliar de mantenimiento de niveles
│   ├── fixtures/  media/  static/     Directorios de apoyo (.gitkeep)
│   └── EVIDENCIA_SMOKE_TEST_20261005.txt
├── frontend/
│   ├── src/
│   │   ├── api/client.js          Axios + JWT con cola de refresh
│   │   ├── stores/                7 stores Pinia (auth, gym, refreshments, reports, reservations, rewards, users)
│   │   ├── router/index.js        Rutas + guards RBAC (hash history)
│   │   ├── layouts/MobileLayout.vue
│   │   ├── components/            GlobalToast, ProductCard, ReservationCard, RoutineCard, EmptyState, SkeletonLoader
│   │   ├── utils/toast.js
│   │   ├── views/auth/            Login, Registro
│   │   ├── views/client/          12 vistas de cliente
│   │   ├── views/staff/           9 vistas de staff
│   │   └── NotFoundView.vue
│   ├── index.html
│   ├── package.json  package-lock.json
│   ├── tailwind.config.js  postcss.config.js  vite.config.js
├── scripts/
│   ├── railway_build.sh  railway_start.sh          (Linux / Railway)
│   ├── railway_build_local.bat  railway_start_local.bat  (Windows, simulación local)
├── tests/
│   ├── unit/         32 pruebas unitarias (test_auth, test_users, test_spaces, test_reservations)
│   ├── integration/  12 pruebas de integración (test_flujos)
│   ├── e2e/          paquete Node para pruebas de navegador
│   ├── base.py  harness.py  runner.py  run_suite.py  credenciales.py
│   ├── railway_validation.py   (20 casos HTTP contra producción)
│   └── metricas_operacion.py   (indicadores operativos reales)
├── evidencias/        Salidas de las suites (txt/json/csv/md)
├── Dockerfile          Multietapa: build Vite + runtime Django/Gunicorn
├── railway.json        Configuración de build/deploy en Railway
├── arrancar.bat        Levanta local (Django 8000 + Vite 5173)
├── .env.example  .env.evidencias.example  .gitignore  .dockerignore
├── README.md  MANUAL_USUARIO.md  EVIDENCIA_VERSION_FINAL.md
```

---

## 5. Dependencias

- **Backend:** `backend/requirements.txt` (versiones exactas en la sección 3).
- **Frontend:** `frontend/package.json` (dependencias `vue`, `vue-router`, `pinia`, `axios`, `lucide-vue-next`; dev dependencies `@vitejs/plugin-vue`, `vite`, `tailwindcss`, `postcss`, `autoprefixer`).

Scripts npm disponibles (`frontend/package.json`): `dev` (Vite en `0.0.0.0:5173`), `build` (Vite build), `preview` (Vite preview en `0.0.0.0:4173`) y `lint` (marcador sin linter configurado).

---

## 6. Instalación local paso a paso (Windows PowerShell)

Prerrequisitos: Python 3.10.x, Node.js 18+ y Git. Los comandos siguientes son los documentados en `README.md` y en `arrancar.bat`.

```powershell
# 1) Entorno virtual
cd c:\Family_Health_MF
py -3.10 -m venv --clear .venv
.\.venv\Scripts\activate

# 2) Dependencias backend
.\.venv\Scripts\pip install -r backend\requirements.txt

# 3) Verificación del backend
cd backend
..\.venv\Scripts\python.exe manage.py check
..\.venv\Scripts\python.exe smoke_test.py

# 4) Dependencias frontend
cd ..\frontend
npm.cmd install --no-audit --no-fund
```

Migraciones y datos de semilla (necesarios para tener catálogos y usuarios demo):

```powershell
cd c:\Family_Health_MF\backend
..\.venv\Scripts\python.exe manage.py migrate
..\.venv\Scripts\python.exe bootstrap_data.py
```

Levantar ambos servidores:

- **Opción A (un clic):** desde `c:\Family_Health_MF`, ejecutar `.\arrancar.bat` (abre dos ventanas: backend en `0.0.0.0:8000` y frontend en `0.0.0.0:5173`).
- **Opción B (dos terminales):**

```powershell
# Terminal 1 - Backend
cd c:\Family_Health_MF\backend
..\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000

# Terminal 2 - Frontend
cd c:\Family_Health_MF\frontend
npm.cmd run dev
```

Build local de simulación del build de Railway (Windows): `scripts\railway_build_local.bat` y arranque `scripts\railway_start_local.bat` (usa `waitress-serve` si está instalado; en su defecto `runserver`). No forman parte del despliegue real.

---

## 7. Variables de entorno

Todas las variables siguientes existen en `.env.example` y/o son consumidas por `backend/config/settings.py` o el `Dockerfile`. No se reproducen valores secretos reales; los de `.env.example` son marcadores de relleno.

| Variable | Propósito | Origen | ¿Obligatoria? |
|---|---|---|---|
| `DJANGO_SECRET_KEY` | Firma de sesiones y de los JWT (`SIGNING_KEY`) | settings.py / .env | Sí en producción (DEBUG=False). En desarrollo, si falta, se autogenera con advertencia |
| `DJANGO_DEBUG` | Modo depuración (True/False) | settings.py / .env | No (default `False`) |
| `DJANGO_ALLOWED_HOSTS` | Lista de hosts permitidos | settings.py / .env | No (default vacío; en DEBUG se añaden hosts LAN) |
| `DJANGO_PUBLIC_DOMAIN` | Dominio público (fallback si Railway no inyecta el suyo) | settings.py (os.getenv) | No |
| `RAILWAY_PUBLIC_DOMAIN` | Dominio inyectado por Railway | settings.py (os.getenv) | No (automática en Railway) |
| `DATABASE_URL` | Cadena de conexión PostgreSQL (selecciona el motor en producción) | settings.py / .env | No en local (SQLite); la provee el plugin de Railway en producción |
| `DB_ENGINE` | Motor de base de datos (default `django.db.backends.sqlite3`) | settings.py / .env | No |
| `DB_NAME` | Nombre de la base (default `db.sqlite3`) | settings.py / .env | No |
| `DB_USER` / `DB_PASSWORD` / `DB_HOST` / `DB_PORT` | Credenciales/host/puerto de base de datos | settings.py / .env | No (vacías por defecto; para SQLite no se usan) |
| `RAILWAY_VOLUME_MOUNT_PATH` | Ruta del volumen; si existe, la base SQLite y los `media` se ubican allí | settings.py / .env | No |
| `HASHID_FIELD_SALT` | Sal para los campos hashid | settings.py / .env | No (default de relleno; debe cambiarse) |
| `ACCESS_TOKEN_LIFETIME_MINUTES` | Vida del token de acceso JWT en minutos | settings.py | No (default 60) |
| `REFRESH_TOKEN_LIFETIME_DAYS` | Vida del token de refresco JWT en días | settings.py | No (default 7) |
| `LOGIN_MAX_ATTEMPTS` | Intentos fallidos de login antes del bloqueo (django-axes) | settings.py | No (default 5) |
| `LOGIN_COOLDOWN_MINUTES` | Minutos de bloqueo tras superar los intentos | settings.py | No (default 15) |
| `CORS_ALLOWED_ORIGINS` | Orígenes permitidos por CORS | settings.py / .env | No |
| `CSRF_TRUSTED_ORIGINS` | Orígenes de confianza para CSRF | settings.py / .env | No |
| `RAILWAY_SEED_BOOTSTRAP` | `1` ejecuta `bootstrap_data.py` en el arranque | railway.json / .env | No |
| `WEB_CONCURRENCY` | Número de workers de Gunicorn | railway.json / .env | No (default 2 en scripts) |
| `GUNICORN_THREADS` | Hilos por worker de Gunicorn | railway.json / .env | No (default 4) |
| `GUNICORN_TIMEOUT` | Timeout de Gunicorn (segundos) | railway.json / .env | No (default 120) |
| `GUNICORN_LOGLEVEL` | Nivel de log de Gunicorn | Dockerfile/scripts | No (default info) |
| `PORT` | Puerto que expone el contenedor (inyectado por Railway) | Dockerfile | No |
| `DEMO_PASS_ADMIN`, `DEMO_PASS_EMP`, `DEMO_PASS_C1`, `DEMO_PASS_C2`, `DEMO_PASS_C3` | Contraseñas fijas opcionales para la semilla demo | .env / `bootstrap_data.py` | No |
| `DEMO_PASS_CAF` | Contraseña opcional de la cuenta de cafetería en la semilla | `bootstrap_data.py` | No |
| `ADMIN_USERNAME`, `ADMIN_EMAIL`, `ADMIN_PASSWORD` | Datos del administrador inicial (semilla) | .env | No |
| `BACKEND_PORT`, `FRONTEND_PORT` | Puertos locales sugeridos | .env | No |
| `CLUB_NAME`, `CLUB_NIT`, `CLUB_CITY` | Datos del club usados por la API (health, etc.) | settings.py / .env | No |

Además, el archivo `.env.evidencias.example` documenta variables para los scripts de evidencia (no secretas en el repo): `FH_BASE`, `FH_USER_ADMIN`, `FH_PASS_ADMIN`, `FH_USER_RECEPCION`, `FH_PASS_RECEPCION`, `FH_USER_CAFETERIA`, `FH_PASS_CAFETERIA`, `FH_USER_CLIENTE1`, `FH_PASS_CLIENTE1`, `FH_USER_CLIENTE2`, `FH_PASS_CLIENTE2`. Las contraseñas se leen del entorno o de `.env.evidencias` (ignorado por Git) y nunca se escriben en el código.

---

## 8. Ejecución local

| Recurso | URL |
|---|---|
| Frontend Mobile-First (Vite) | `http://127.0.0.1:5173/` |
| Panel Admin Django | `http://127.0.0.1:8000/admin/` |
| Base de la API REST | `http://127.0.0.1:8000/api/v1/` |
| Health Check | `http://127.0.0.1:8000/api/v1/health/` |

El **Health Check** (`GET /api/v1/health/`) es público (permiso `AllowAny`) y responde HTTP 200 con:

```json
{
  "status": "ok",
  "timestamp": "...",
  "version": "1.0.0",
  "app": "Club Family Health MF API",
  "club_name": "Club Family Health",
  "club": { "name": "Club Family Health", "nit": "32739028-5", "city": "Maicao, La Guajira" },
  "database": "ok"
}
```

En desarrollo, el servidor de Vite publica en `0.0.0.0` y define un proxy hacia el backend para `/api`, `/admin`, `/media` y `/static` (`frontend/vite.config.js`). Esto permite acceder desde un dispositivo móvil en la misma red LAN usando la IP privada del equipo.

---

## 9. Base de datos

| Entorno | Motor | Detalle |
|---|---|---|
| Desarrollo local | SQLite 3 | Archivo `backend/db.sqlite3` (derivado de `DB_NAME` relativo a `BASE_DIR`) |
| Suite de pruebas | SQLite aislada | Creada por el runner de Django; `tests/run_suite.py` neutraliza cualquier `DATABASE_URL` externo |
| Producción (Railway) | PostgreSQL | Seleccionado automáticamente al existir `DATABASE_URL` con esquema `postgres*` |

**Aislamiento de `DATABASE_URL` en DEBUG (`_read_dotenv_value`).** En `backend/config/settings.py` existe la función `_read_dotenv_value(name)`, que lee un valor **exclusivamente** desde el archivo `.env` del proyecto, ignorando `os.environ`. Cuando `DEBUG=True`, el valor de `DATABASE_URL` se obtiene solo con esa función; así, una variable global del sistema perteneciente a otro proyecto instalado en el mismo equipo no desvía la ejecución local hacia una base ajena. Cuando `DEBUG=False` (producción), sí se permite leer `DATABASE_URL` desde el entorno (Railway). Si el valor empieza por `postgres`, se parsea con `dj-database-url`; en caso contrario se usa SQLite. En ambos casos la conexión se crea con `ATOMIC_REQUESTS = True`.

---

## 10. Despliegue en Railway

### Dockerfile multietapa

`Dockerfile` define dos etapas:

1. **Etapa `frontend-build`** (`node:20-bookworm-slim`): copia `frontend/package*.json`, ejecuta `npm ci` (con fallback a `npm install`) y `npm run build -- --logLevel warn`, generando `frontend/dist/`.
2. **Etapa `runtime`** (`python:3.11-slim-bookworm`): instala dependencias del sistema mínimas (`libpq5`, `curl`, `ca-certificates`), instala `backend/requirements.txt`, copia el backend y el `dist/` de la etapa 1, define `DJANGO_SETTINGS_MODULE=config.settings` y `PROJECT_ROOT=/app`, expone el puerto 8000 y ejecuta como CMD:

   1. `python manage.py migrate --noinput`
   2. `python manage.py collectstatic --noinput --clear`
   3. `python bootstrap_data.py` (semilla demo)
   4. `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT` con workers, hilos, timeout y `max-requests` parametrizados por variables de entorno.

El bundle de la SPA (`frontend/dist/`) se sirve desde Django con WhiteNoise; no se usa Nginx ni Vite en producción.

### railway.json

- `build.builder = "DOCKERFILE"`, `dockerfilePath = "Dockerfile"` y `watchPatterns` sobre `backend/**`, `frontend/src/**`, `frontend/package*.json`, `frontend/vite.config.js`, `frontend/index.html`, `frontend/tailwind.config.js`, `frontend/postcss.config.js`, `Dockerfile` y `.dockerignore`.
- `deploy.restartPolicyType = "ON_FAILURE"`, `restartPolicyMaxRetries = 5`.
- `deploy.healthcheckPath = "/api/v1/health/"`, `healthcheckTimeout = 15`, `healthcheckInterval = 60`, `healthcheckRetries = 6`.
- `deploy.configVariables` define: `DJANGO_DEBUG=False`, `DJANGO_ALLOWED_HOSTS=*`, `LOGIN_MAX_ATTEMPTS=5`, `LOGIN_COOLDOWN_MINUTES=15`, `ACCESS_TOKEN_LIFETIME_MINUTES=60`, `REFRESH_TOKEN_LIFETIME_DAYS=7`, `WEB_CONCURRENCY=2`, `GUNICORN_THREADS=4`, `GUNICORN_TIMEOUT=120`, `RAILWAY_SEED_BOOTSTRAP=1`.

### Scripts de Railway

- `scripts/railway_build.sh`: script histórico/alternativo (Nixpacks). Detecta Node y Python en el PATH, instala dependencias npm, compila Vite, instala `requirements.txt`, ejecuta `collectstatic`, `migrate` y la semilla si `RAILWAY_SEED_BOOTSTRAP=1`. Está reemplazado por el `Dockerfile`.
- `scripts/railway_start.sh`: al arrancar asegura `migrate`, `collectstatic`, semilla opcional y lanza Gunicorn (`config.wsgi:application`) en `0.0.0.0:$PORT` con las variables de workers/hilos/timeout.

### Variables esperadas en Railway

`DJANGO_DEBUG=False`, `DJANGO_ALLOWED_HOSTS=*`, `DJANGO_SECRET_KEY` (secreta, definida en el panel), `DATABASE_URL` (secreta, provista por el plugin de PostgreSQL), `RAILWAY_SEED_BOOTSTRAP=1`, `WEB_CONCURRENCY=2`, `GUNICORN_THREADS=4`, `GUNICORN_TIMEOUT=120`, `ACCESS_TOKEN_LIFETIME_MINUTES=60`, `REFRESH_TOKEN_LIFETIME_DAYS=7`, `LOGIN_MAX_ATTEMPTS=5`, `LOGIN_COOLDOWN_MINUTES=15`. Las variables secretas (`DJANGO_SECRET_KEY`, `DATABASE_URL`) nunca se versionan.

---

## 11. Endpoints

Todas las rutas están fundamentadas en los archivos `urls.py` y `views.py` reales. La base de la API es `/api/v1/`. Salvo indicación contraria, se requiere autenticación JWT (`IsAuthenticated`). Las acciones personalizadas se listan con su `url_path` exacto.

### Autenticación (`/api/v1/auth/`)

| Método | Ruta | Permiso |
|---|---|---|
| POST | `/auth/login/` | Público (throttle `login` 10/min) |
| POST | `/auth/token/refresh/` | Público |
| POST | `/auth/logout/` | Público (invalida refresh por blacklist) |
| POST | `/auth/register/` | Público (throttle `register` 5/h) |
| GET, POST | `/auth/admin/users/` | `IsAuthenticated & IsAdminOrReception` |
| GET, PUT, PATCH, DELETE | `/auth/admin/users/{id}/` | `IsAuthenticated & IsAdminOrReception` |
| POST | `/auth/admin/users/{id}/toggle-active/` | `IsAuthenticated & IsAdminOrReception` |
| POST | `/auth/admin/users/{id}/set-password/` | `IsAuthenticated & IsAdminOrReception` |
| GET | `/auth/clients/` y `/auth/clients/{id}/` | `IsAuthenticated & IsAdminOrReception` (solo lectura) |
| GET | `/auth/me/` | `IsAuthenticated` |
| PATCH, PUT | `/auth/me/` | `IsAuthenticated` |
| POST | `/auth/me/change-password/` | `IsAuthenticated` |
| GET | `/auth/me/audit-logs/` | `IsAuthenticated` (últimas 50 propias) |
| GET | `/auth/me/loyalty/` | `IsAuthenticated` |

### Reservas (`/api/v1/reservations/`)

| Método | Ruta | Permiso |
|---|---|---|
| GET | `/reservations/space-types/` | `IsAuthenticated` |
| POST, PUT, PATCH, DELETE | `/reservations/space-types/` | `IsAuthenticated & IsAdmin` |
| GET | `/reservations/spaces/` y `/reservations/spaces/{id}/` | `IsAuthenticated` |
| POST, PUT, PATCH, DELETE | `/reservations/spaces/` | `IsAuthenticated & IsAdmin` |
| GET | `/reservations/spaces/{id}/availability/` | `IsAuthenticated` |
| GET, POST, PUT, PATCH, DELETE | `/reservations/operating-hours/` | `IsAuthenticated & IsAdmin` |
| GET, POST, PUT, PATCH, DELETE | `/reservations/holidays/` | `IsAuthenticated & IsAdmin` |
| GET | `/reservations/reservations/` | `IsAuthenticated & IsAdminOrReception` |
| POST | `/reservations/reservations/` | `IsAuthenticated & (IsClient \| IsAdminOrReception)` |
| GET | `/reservations/reservations/{id}/` | `IsAuthenticated` |
| PUT, PATCH | `/reservations/reservations/{id}/` | `IsAuthenticated & IsAdminOrReception` |
| DELETE | `/reservations/reservations/{id}/` | `IsAuthenticated & IsAdmin` |
| POST | `/reservations/reservations/{id}/cancel/` | `IsAuthenticated & (IsClient \| IsAdminOrReception)` |
| POST | `/reservations/reservations/{id}/approve/` | `IsAuthenticated & IsAdminOrReception` |
| POST | `/reservations/reservations/{id}/reject/` | `IsAuthenticated & IsAdminOrReception` |
| POST | `/reservations/reservations/{id}/mark-paid/` | `IsAuthenticated & IsAdminOrReception` |
| GET | `/reservations/reservations/my-upcoming/` | `IsAuthenticated & IsClient` |

Filtros del listado de reservas (`get_queryset`): `status`, `space_id`, `user_id`, `date_from`, `date_to`. Un usuario CLIENT solo ve sus propias reservas. La acción `availability` acepta el parámetro `date` (formato `YYYY-MM-DD`) y devuelve franjas de 30 minutos, horario operativo, festivos y franjas ocupadas.

### Refresquería (`/api/v1/refreshments/`)

| Método | Ruta | Permiso |
|---|---|---|
| GET | `/refreshments/categories/` | `IsAuthenticated` |
| POST, PUT, PATCH, DELETE | `/refreshments/categories/` | `IsAuthenticated & IsAdmin` |
| GET, POST, PUT, PATCH, DELETE | `/refreshments/products/` | `IsAuthenticated & IsAdminOrCafeteria` |
| GET | `/refreshments/products/available-catalog/` | `IsAuthenticated` |
| GET, POST, PUT, PATCH, DELETE | `/refreshments/offers/` | `IsAuthenticated & IsAdminOrCafeteria` |
| GET | `/refreshments/offers/active-offers/` | `IsAuthenticated` |
| GET | `/refreshments/orders/` | `IsAuthenticated & IsAdminOrCafeteria` |
| POST | `/refreshments/orders/` | `IsAuthenticated & (IsClient \| IsAdminOrCafeteria)` |
| GET | `/refreshments/orders/{id}/` | `IsAuthenticated` |
| PUT, PATCH | `/refreshments/orders/{id}/` | `IsAuthenticated & IsAdminOrCafeteria` |
| DELETE | `/refreshments/orders/{id}/` | `IsAuthenticated & IsAdmin` |
| POST | `/refreshments/orders/{id}/next-status/` | `IsAuthenticated & IsAdminOrCafeteria` |
| POST | `/refreshments/orders/{id}/mark-paid/` | `IsAuthenticated & IsAdminOrCafeteria` |
| POST | `/refreshments/orders/{id}/cancel/` | `IsAuthenticated & (IsClient \| IsAdminOrCafeteria)` |
| GET | `/refreshments/orders/my-orders/` | `IsAuthenticated & IsClient` |

### Recompensas (`/api/v1/rewards/`)

| Método | Ruta | Permiso |
|---|---|---|
| GET, POST, PUT, PATCH, DELETE | `/rewards/rules/` | `IsAuthenticated & IsAdmin` |
| GET, POST, PUT, PATCH, DELETE | `/rewards/tiers/` | `IsAuthenticated & IsAdmin` |
| GET | `/rewards/profiles/` y `/rewards/profiles/{id}/` | `IsAuthenticated & (IsAdmin \| IsAdminOrEmployee)` |
| POST, PUT, PATCH, DELETE | `/rewards/profiles/` | `IsAuthenticated & IsAdmin` |
| GET | `/rewards/profiles/me/` | `IsAuthenticated & IsClient` |
| POST | `/rewards/profiles/{id}/adjust-points/` | `IsAuthenticated & IsAdmin` |
| GET | `/rewards/transactions/` y `/rewards/transactions/{id}/` | `IsAuthenticated` (solo lectura) |
| GET | `/rewards/catalog/` y `/rewards/catalog/{id}/` | `IsAuthenticated` |
| POST, PUT, PATCH, DELETE | `/rewards/catalog/` | `IsAuthenticated & IsAdmin` |
| POST | `/rewards/catalog/redeem/` | `IsAuthenticated & IsClient` |

### Gimnasio (`/api/v1/gym/`)

| Método | Ruta | Permiso |
|---|---|---|
| GET | `/gym/muscle-groups/`, `/gym/equipment/`, `/gym/exercises/`, `/gym/routines/`, `/gym/logs/` | `IsAuthenticated` |
| POST, PUT, PATCH, DELETE | `/gym/muscle-groups/`, `/gym/equipment/`, `/gym/exercises/`, `/gym/routines/` | `IsAuthenticated & IsAdminOrEmployee` |
| DELETE | `/gym/logs/{id}/` | `IsAuthenticated & IsAdminOrEmployee` |
| GET | `/gym/routines/my-routines/` | `IsAuthenticated & IsClient` |

### Reportes y notificaciones (`/api/v1/reports/`)

| Método | Ruta | Permiso |
|---|---|---|
| GET, POST, PUT, PATCH, DELETE | `/reports/notifications/` | `IsAuthenticated` (cada usuario solo ve las propias) |
| POST | `/reports/notifications/mark-all-read/` | `IsAuthenticated` |
| GET | `/reports/notifications/unread/` | `IsAuthenticated` |
| GET | `/reports/dashboard/summary/` | `IsAuthenticated & (IsAdmin \| IsAdminOrEmployee)` |
| GET | `/reports/dashboard/reservations-by-date/` | `IsAuthenticated & (IsAdmin \| IsAdminOrEmployee)` |
| GET | `/reports/dashboard/revenue-by-month/` | `IsAuthenticated & (IsAdmin \| IsAdminOrEmployee)` |
| GET | `/reports/dashboard/top-clients/` | `IsAuthenticated & (IsAdmin \| IsAdminOrEmployee)` |
| GET | `/reports/top-clients/` | `IsAuthenticated & (IsAdmin \| IsAdminOrEmployee)` (alias corto) |

### Salud y administración

| Método | Ruta | Permiso |
|---|---|---|
| GET | `/api/v1/health/` | Público (`AllowAny`) |
| Cualquiera | `/admin/` | Panel administrativo Django |

---

## 12. Autenticación JWT

Configuración real en el diccionario `SIMPLE_JWT` de `backend/config/settings.py`:

| Parámetro | Valor |
|---|---|
| Algoritmo | `HS512` |
| Clave de firma | `SECRET_KEY` |
| Vida del token de acceso | `ACCESS_TOKEN_LIFETIME_MINUTES` (default 60 minutos) |
| Vida del token de refresco | `REFRESH_TOKEN_LIFETIME_DAYS` (default 7 días) |
| Rotación de refresh | `ROTATE_REFRESH_TOKENS = True` |
| Blacklist tras rotación | `BLACKLIST_AFTER_ROTATION = True` |
| Actualizar último login | `UPDATE_LAST_LOGIN = True` |
| Audiencia (`AUDIENCE`) | `family-health-mf` |
| Emisor (`ISSUER`) | `club-family-health` |
| Margen (`LEEWAY`) | 10 segundos |
| Cabecera | `Bearer` en `Authorization` |
| Campo/claim de usuario | `id` / `user_id` |
| Token deslizante | 120 minutos (refresco 7 días) |
| Serializer de obtención | `apps.authentication.serializers.CustomTokenObtainPairSerializer` |

El backend carga `rest_framework_simplejwt.token_blacklist` en `INSTALLED_APPS`. El endpoint de login usa un serializer propio que además devuelve `role` y, para clientes, `points` y `tier`. El endpoint `logout/` usa `TokenBlacklistView`, de modo que un refresh usado se invalida. En el frontend, `frontend/src/api/client.js` implementa un interceptor de Axios con **cola de refresco**: al recibir un 401, refresca el token una sola vez y reintenta las peticiones encoladas.

---

## 13. RBAC (control de acceso basado en roles)

Roles definidos en `User.ROLE_CHOICES` (`backend/apps/authentication/models.py`):

| Rol | Descripción |
|---|---|
| `ADMIN` | Administrador. Acceso total; `create_superuser` lo asigna por defecto |
| `RECEPCION` | Recepción. Reservas, espacios, clientes |
| `CAFETERIA` | Cafetería. Productos, ofertas, pedidos |
| `CLIENT` | Cliente. Rol por defecto en el registro |
| `EMPLOYEE` | Empleado (compatibilidad con datos existentes). Se comporta como recepción/cafetería combinadas en los permisos |

Permisos DRF (`backend/apps/authentication/permissions.py`):

- `IsAdmin`: solo ADMIN (o `is_superuser`).
- `IsReception`: RECEPCION o EMPLOYEE.
- `IsCafeteria`: CAFETERIA o EMPLOYEE.
- `IsClient`: solo CLIENT.
- `IsEmployee`: solo EMPLOYEE (compatibilidad).
- `IsAdminOrEmployee`: ADMIN, RECEPCION, CAFETERIA o EMPLOYEE (o `is_staff`/`is_superuser`). Usado en gimnasio y reportes.
- `IsAdminOrReception`: ADMIN, RECEPCION o EMPLOYEE (o `is_superuser`). Usado en reservas, espacios y clientes.
- `IsAdminOrCafeteria`: ADMIN, CAFETERIA o EMPLOYEE (o `is_superuser`). Usado en productos y pedidos.
- `IsAdminOrOwner`: objeto propio o ADMIN.
- `IsStaffOrReadOnly`: lectura para autenticados, escritura para el personal.

El control de acceso también se refuerza con `get_queryset`: los CLIENT solo ven sus propios recursos (reservas, pedidos, transacciones de puntos, rutinas, notificaciones); el rol RECEPCION, en el ViewSet de usuarios, solo puede ver/gestionar cuentas con rol CLIENT.

En el frontend (`frontend/src/router/index.js`) los guards redirigen según rol: el panel `/panel` es para staff, la zona `/cliente` es para clientes, y la cafetería/recepción tienen listas de vistas permitidas.

---

## 14. Módulos del sistema

### authentication
Responsable de usuarios, roles, perfil, fidelidad de lectura y auditoría. Modelos: `User` (AbstractBaseUser con `email`, `username`, `role`, datos personales, membresía, campos de auditoría de acceso y banderas de aceptación de política de privacidad y términos) y `AuditLog` (registro de acciones: login, login fallido, logout, vista/edición de perfil, exportación y eliminación de datos). Un `UserManager` personalizado gestiona la creación de usuarios y superusuarios.

### reservations
Responsable de espacios y reservas con control anti-solapamiento. Modelos: `SpaceType`, `Space` (con `hourly_rate`, límites de duración mínimo/máximo, `requires_employee_approval`, `cancellation_penalty_hours`, estado), `OperatingHours` (horario semanal por espacio), `Holiday` (festivos y cierres), `Reservation` (con estados PENDING/CONFIRMED/CANCELLED/COMPLETED/REJECTED/NO_SHOW y estados de pago PENDING/PAID/EXEMPT). El método `Space.is_available_at()` y `Reservation.save()` aplican la validación de disponibilidad dentro de `transaction.atomic()` con `Space.objects.select_for_update()`.

### refreshments
Responsable del inventario y los pedidos de la refresquería. Modelos: `ProductCategory`, `Product` (SKU, precio, costo, stock, `min_stock`, alérgenos, calorías), `Offer` (promociones con vigencia y precio de oferta), `Order` (estados PENDING/PREPARING/READY/DELIVERED/PAID/CANCELLED; métodos de pago presenciales) y `OrderItem`. El control de stock usa `F('stock') - cantidad` dentro de una transacción al guardar la línea.

### rewards
Responsable de la fidelización. Modelos: `RewardRule` (puntos por tipo de acción), `LoyaltyTier` (niveles con `min_points`, color y `discount_percent`), `PointsTransaction` (EARN/REDEEM/EXPIRE/ADJUST), `LoyaltyProfile` (puntos actuales/históricos, nivel, referidos) y `RewardCatalogItem` (catálogo de premios canjeables). El perfil actualiza el nivel automáticamente según los puntos.

### gym
Responsable de la información de entrenamiento. Modelos: `MuscleGroup`, `Equipment`, `Exercise` (instrucciones, series/reps recomendadas, descanso, calorías, video), `Routine` (genérica o asignada a un cliente, con calentamiento, enfriamiento y tips nutricionales), `RoutineExercise` (parámetros por rutina) y `WorkoutLog` (registro de sesiones).

### reports
Responsable de notificaciones y de los indicadores del panel. Modelo persistente: `Notification` (tipos INFO/SUCCESS/WARNING/DANGER/RESERVATION/ORDER/REWARD). Las vistas de reporte (`dashboard_summary`, `reservations_by_date`, `revenue_by_month`, `top_clients`) calculan agregados en tiempo de ejecución y no tienen tablas propias. El módulo también expone `health_check`.

---

## 15. Migraciones

Ubicación: `backend/apps/<app>/migrations/`. Migraciones existentes:

| App | Migraciones |
|---|---|
| authentication | `0001_initial.py`, `0002_alter_user_role.py` |
| reservations | `0001_initial.py` |
| refreshments | `0001_initial.py`, `0002_offer.py` |
| rewards | `0001_initial.py` |
| gym | `0001_initial.py` |
| reports | `0001_initial.py` |

Aplicación local:

```powershell
cd c:\Family_Health_MF\backend
..\.venv\Scripts\python.exe manage.py migrate
```

En producción, tanto el `Dockerfile` como `scripts/railway_start.sh` ejecutan `python manage.py migrate --noinput` antes de recolectar estáticos y arrancar Gunicorn.

---

## 16. Pruebas

La suite real y sus comandos (PowerShell, desde la raíz del repositorio):

### 16.1 Pruebas unitarias (32 casos: U01-U32)

Archivos: `tests/unit/test_auth.py` (U01-U06), `tests/unit/test_users.py` (U07-U11), `tests/unit/test_spaces.py` (U12-U16), `tests/unit/test_reservations.py` (U17-U32).

```powershell
cd c:\Family_Health_MF
.\.venv\Scripts\python.exe tests\run_suite.py unit
```

Genera evidencias en `evidencias/`: `pruebas_unitarias.txt`, `pruebas_unitarias.json`, `pruebas_unitarias.csv`.

La ejecución final conservada en el repositorio registra **32/32 casos aprobados**, incluyendo el caso `U32`, que valida el endpoint `mis-reservas/` para que el cliente consulte todas sus reservas propias sin exponer el listado global administrativo.

### 16.2 Pruebas de integración (12 casos: I01-I12)

Archivo: `tests/integration/test_flujos.py`.

```powershell
cd c:\Family_Health_MF
.\.venv\Scripts\python.exe tests\run_suite.py integration
```

Genera evidencias en `evidencias/`: `pruebas_integracion.txt`, `pruebas_integracion.json`, `pruebas_integracion.csv`.

### 16.3 Smoke test (14 casos)

Archivo: `backend/smoke_test.py`. Usa el cliente de pruebas de Django; imprime el resultado de los 14 casos.

```powershell
cd c:\Family_Health_MF\backend
..\.venv\Scripts\python.exe smoke_test.py
```

### 16.4 Validación contra Railway (20 casos HTTP: RW01-RW20)

Archivo: `tests/railway_validation.py`. Requiere las contraseñas demo en el entorno (o en `.env.evidencias`).

```powershell
cd c:\Family_Health_MF
$env:FH_PASS_ADMIN="<contraseña demo admin>"
$env:FH_PASS_RECEPCION="<contraseña demo recepción>"
$env:FH_PASS_CAFETERIA="<contraseña demo cafetería>"
$env:FH_PASS_CLIENTE1="<contraseña demo cliente 1>"
$env:FH_PASS_CLIENTE2="<contraseña demo cliente 2>"
..\.venv\Scripts\python.exe tests\railway_validation.py
```

Alternativamente, las contraseñas pueden dejarse en el archivo local `.env.evidencias` (ignorado por Git; ver `.env.evidencias.example`), que `tests/credenciales.py` carga automáticamente en el entorno.

Los 20 casos RW01-RW20 cubren: health check público, login correcto e incorrecto, usuario inactivo, acceso por rol (admin/recepción/cliente), permisos permitidos y prohibidos (403), catálogo de espacios, consulta de disponibilidad, creación/consulta/cancelación de reserva, rechazo de solape, errores controlados (400/401/404), refresco de token y persistencia verificada en una sesión nueva.

Salidas (carpeta `evidencias/`): `validacion_railway.json` y `validacion_railway.md`. En la evidencia almacenada el resultado es 20/20 aprobados (consulta del 2026-10-20T03:53:13 UTC contra `https://familyhealthmf-production.up.railway.app`). Los tokens se registran enmascarados en el formato `eyJhbGciOi...XXXX (N car.)`.

### 16.5 Métricas operativas (indicadores M01-M42)

Archivo: `tests/metricas_operacion.py`. Consulta el despliegue de Railway con la cuenta administradora y calcula **42 indicadores** a partir de respuestas HTTP reales (misma fuente que la base PostgreSQL); no inventa valores.

```powershell
cd c:\Family_Health_MF
$env:FH_PASS_ADMIN="<contraseña demo admin>"
..\.venv\Scripts\python.exe tests\metricas_operacion.py
```

Fuentes y rangos de indicadores:

| Origen (consulta real) | Indicadores |
|---|---|
| `GET /api/v1/reports/dashboard/summary/` | M01-M17 |
| Enumeración paginada `GET /api/v1/reservations/reservations/` | M18-M30 |
| `GET /api/v1/reports/dashboard/reservations-by-date/?days=30` | M31-M33 |
| `GET /api/v1/reports/dashboard/top-clients/?n=20` | M34 |
| Enumeración paginada `GET /api/v1/auth/admin/users/` | M35-M42 |

Salidas declaradas por el script (carpeta `evidencias/`):

- `metricas_operacion_real.csv` (tabla de los 42 indicadores)
- `metricas_operacion_real.md` (informe con tabla de indicadores y limitaciones)
- `metricas_operacion_raw.json` (respuestas crudas de la API)

El informe marca explícitamente los indicadores **no calculables** porque el software no los registra: tiempo de atención por reserva, intentos de inicio de sesión/auditoría por rol (la API no expone un endpoint de lectura de auditoría) y tasa de ocupación por espacio individual. También separa las reservas identificadas como dato de prueba controlado (M26/M27).

> Nota de verificación: la carpeta `evidencias/` contiene las salidas reales de las secciones 16.1 a 16.5, incluyendo `pruebas_unitarias.*`, `pruebas_integracion.*`, `smoke_tests_raw.txt`, `validacion_railway.*`, `metricas_operacion_real.*` y `metricas_operacion_raw.json`, además de los metadatos `_*.txt`.

---

## 17. Mantenimiento y actualización

### Actualización de código y redeploy

El despliegue es automático desde GitHub: un `push` a la rama `main` dispara la construcción (Dockerfile multietapa) y el nuevo despliegue en Railway. El flujo documentado en `README.md` es:

```powershell
cd c:\Family_Health_MF
git add <archivos>
git commit -m "manuales: actualizar documentación final del cierre técnico"
git push origin main
```

Tras el push se espera el build en el panel de Railway y se verifica el health check (`GET /api/v1/health/` debe responder 200 con `"database":"ok"`).

### Ciclo de vida en cada arranque

El `CMD` del contenedor (`Dockerfile`) ejecuta, en orden: `manage.py migrate --noinput`, `manage.py collectstatic --noinput --clear`, `bootstrap_data.py` (si `RAILWAY_SEED_BOOTSTRAP=1`) y Gunicorn. Los mismos pasos aparecen en `scripts/railway_start.sh` (script alternativo), con la semilla condicionada a la variable `RAILWAY_SEED_BOOTSTRAP`.

### Política de datos de semilla (no destructiva)

`bootstrap_data.py` no destruye datos existentes (crea/actualiza), de modo que los cambios manuales de inventario se preservan. Puede omitirse por completo definiendo `RAILWAY_SEED_BOOTSTRAP=0`. Las contraseñas de demostración se toman de las variables `DEMO_PASS_*` o de fallbacks fijos conocidos declarados en `_DEMO_PASS_FALLBACK`.

### Recomendaciones de mantenimiento

- Revisar `backend/requirements.txt` y `frontend/package.json` al actualizar dependencias.
- No versionar `.env`; mantener los secretos (`DJANGO_SECRET_KEY`, `DATABASE_URL`) en el panel de Railway.
- Ejecutar la suite de pruebas (sección 16) antes de promover cambios.
- Mantener `railway.json` como JSON puro (sin comentarios).

---

## 18. Seguridad

Controles verificados en `backend/config/settings.py`:

| Control | Configuración real |
|---|---|
| `SECRET_KEY` en producción | Si `DEBUG=False` y falta `DJANGO_SECRET_KEY`, el arranque **falla** con `RuntimeError`. En `DEBUG=True` se autogenera una clave de desarrollo y se emite una advertencia |
| Hash de contraseñas | `PASSWORD_HASHERS` con `Argon2PasswordHasher` como primera opción (luego PBKDF2, PBKDF2-SHA1 y BCrypt-SHA256) |
| Validadores de contraseña | Similitud con atributos, longitud mínima 8, contraseñas comunes y contraseñas solo numéricas |
| JWT | HS512, `ROTATE_REFRESH_TOKENS=True`, `BLACKLIST_AFTER_ROTATION=True`, `UPDATE_LAST_LOGIN=True`, audiencia `family-health-mf`, emisor `club-family-health`, leeway 10 s |
| Bloqueo por intentos (django-axes) | `AXES_FAILURE_LIMIT=5`, `AXES_COOLOFF_TIME=15 min`, `AXES_LOCKOUT_PARAMETERS=["username","ip_address","user_agent"]`, `AXES_RESET_ON_SUCCESS=True` |
| Throttling DRF | `anon 100/hour`, `user 1000/hour`, `login 10/minute`, `register 5/hour` |
| HTTPS y proxy | `SECURE_PROXY_SSL_HEADER=("HTTP_X_FORWARDED_PROTO","https")`, `USE_X_FORWARDED_HOST=True`; en producción `SECURE_SSL_REDIRECT=True` y HSTS (`SECURE_HSTS_SECONDS=31536000`, con subdominios y preload) |
| Cabeceras de seguridad | `SECURE_CONTENT_TYPE_NOSNIFF=True`, `SECURE_BROWSER_XSS_FILTER=True`, `SECURE_REFERRER_POLICY="strict-origin-when-cross-origin"`; `X_FRAME_OPTIONS="DENY"` en producción y `"SAMEORIGIN"` en desarrollo |
| Cookies | `SESSION_COOKIE_SECURE` y `CSRF_COOKIE_SECURE` activadas cuando `DEBUG=False`; `HTTPONLY=True`; `SAMESITE="Lax"`; sesión de 7 días |
| CORS / CSRF | En producción se respetan `CORS_ALLOWED_ORIGINS` y `CSRF_TRUSTED_ORIGINS`; en desarrollo `CORS_ALLOW_ALL_ORIGINS=True`. El dominio de Railway se añade automáticamente a ambos |
| Subida de archivos | `DATA_UPLOAD_MAX_MEMORY_SIZE=5 MB`; permisos de archivo 0644 y de directorio 0755 |
| Registro (Ley 1581) | Handlers `file_security` (`backend/security.log`), `file_audit` (`backend/audit.log`) y consola; loggers `django.security` y `apps.authentication` |
| Auditoría | Modelo `AuditLog` (inicio/fallo de sesión, cierre de sesión, perfil, exportación y eliminación de datos) |
| Protección de datos | Registro de cliente con aceptación de política de privacidad y términos (`accepted_privacy_policy`, `accepted_terms`) |

Además, `bootstrap_data.py` parametriza las credenciales de demostración y la pantalla de login del frontend no expone credenciales públicas.

---

## 19. Respaldo y recuperación

### Base de datos SQLite (desarrollo local)

- La base local es el archivo `backend/db.sqlite3`, excluido del control de versiones por `.gitignore` (`*.sqlite3`, `backend/db.sqlite3`).
- **Respaldo:** detener el servidor y copiar el archivo `backend/db.sqlite3` a una ubicación segura.
- **Restauración:** reemplazar `backend/db.sqlite3` por la copia y reiniciar el servidor.

### Base de datos PostgreSQL (producción en Railway)

- En producción la base es PostgreSQL y se accede mediante la variable `DATABASE_URL` (nunca versionada), provista por el servicio de PostgreSQL de Railway.
- El respaldo se gestiona desde el panel de Railway del proyecto (servicio de PostgreSQL).
- **Exportación/importación portátil:** Django ofrece los comandos estándar `manage.py dumpdata` y `manage.py loaddata` para exportar e importar el contenido de las tablas como JSON.

### Artefactos de evidencia

La carpeta `evidencias/` (salidas de las suites, health check y metadatos de git) permite reproducir el estado validado. `EVIDENCIA_VERSION_FINAL.md` registra el punto de restauración (rama `release/tg-final` y commit de congelamiento).

> Nota: si en Railway se emplea SQLite junto con un Volume (`RAILWAY_VOLUME_MOUNT_PATH`), el archivo de base de datos y los `media` residen en el volumen; el respaldo se realiza copiando ese volumen.

---

## 20. Solución de problemas (troubleshooting)

| Síntoma | Causa real documentada | Solución |
|---|---|---|
| `ERR_TOO_MANY_REDIRECTS` en producción | Django no reconocía que la petición llegaba por HTTPS a través del proxy de Railway | Resuelto en `settings.py` con `SECURE_PROXY_SSL_HEADER=("HTTP_X_FORWARDED_PROTO","https")` y `USE_X_FORWARDED_HOST=True` |
| Página en blanco al servir el bundle compilado | Discrepancia entre la ruta base del bundle de Vite y el `STATIC_URL` de Django | `frontend/vite.config.js` define `base: '/static/'`, alineado con `STATIC_URL="/static/"` |
| Nixpacks no detecta Node/Python con el código en subcarpetas | `package.json` no está en la raíz del repositorio | Se usa `Dockerfile` multietapa (`builder: DOCKERFILE` en `railway.json`); `scripts/railway_build.sh` documenta el fallback histórico y las variables `NIXPACKS_NODE_VERSION` / `NIXPACKS_PYTHON_VERSION` |
| El archivo `railway.json` no es interpretado | Comentarios `#` u otros caracteres no válidos en un archivo JSON | `railway.json` es JSON puro, sin comentarios |
| La semilla recrea datos demo o sobrescribe el inventario | `RAILWAY_SEED_BOOTSTRAP=1` en un entorno que ya tiene datos | Definir `RAILWAY_SEED_BOOTSTRAP=0` en Variables; `bootstrap_data.py` es no destructivo |
| Cuenta bloqueada por intentos fallidos | Se superó `LOGIN_MAX_ATTEMPTS` (5) y django-axes aplicó el bloqueo | Esperar `LOGIN_COOLDOWN_MINUTES` (15 min) o limpiar bloqueos con el comando de django-axes `manage.py axes_reset` |
| El arranque de producción falla al iniciar | Falta `DJANGO_SECRET_KEY` con `DEBUG=False` | Definirla en Variables de Railway; el arranque lanza `RuntimeError` hasta configurarla |
| El usuario administrador no accede al panel en producción | Deben estar activos `is_staff`, `is_superuser` y el rol `ADMIN` | Verificar y activar los tres campos en el usuario administrador |
| Acceso desde el móvil en la red local no funciona | El servidor o CORS no están abiertos para la LAN | En desarrollo Vite publica en `0.0.0.0:5173` y Django en `0.0.0.0:8000` con `CORS_ALLOW_ALL_ORIGINS=True`; permitir el acceso a redes privadas en el cortafuegos |

---

## 21. Indicadores de versión

Estado verificado en el repositorio local (con `git rev-parse HEAD`, `git branch --show-current`, `git tag` y `git log`):

| Elemento | Valor real |
|---|---|
| Rama actual | `main` |
| Commit actual (SHA completo) | `2a0124aa3c9f9c2709f148cfe57130cdbc93f91f` |
| Commit actual (SHA corto) | `2a0124a` |
| Fecha del último commit | 2026-10-20 00:15:24 -0500 |
| Mensaje del último commit | `documentacion: actualizar manuales finales y agregar informe con matriz de correspondencia` |
| Etiquetas (`git tag`) | `v1.0.0` (etiqueta anotada `6f25e4a` → commit `2a0124a`) |
| Versión reportada por la API | El endpoint `/api/v1/health/` responde `"version": "1.0.0"` |

**Coherencia de la versión publicada.** La etiqueta `v1.0.0` (`v1.0.0 - cierre final verificado del aplicativo Family Health MF`) apunta al commit de cierre `2a0124a`, que agrega exclusivamente documentación y evidencias. La **versión funcional validada en producción** corresponde al commit `51cffda5147b239231917d9ab781fdbb16b1012f` (`51cffda`, 2026-10-19 23:45:17), evaluada sobre el despliegue de Railway con PostgreSQL y health check HTTP 200 (`http://…/api/v1/health/` → `database=ok version=1.0.0`). No existen cambios funcionales posteriores al commit validado.

---

## Trazabilidad de este manual

Este manual se elaboró exclusivamente a partir de la lectura directa de los siguientes archivos del repositorio:

- `README.md`, `MANUAL_USUARIO.md`, `EVIDENCIA_VERSION_FINAL.md`
- `Dockerfile`, `railway.json`, `.dockerignore`
- `scripts/railway_build.sh`, `scripts/railway_start.sh`, `scripts/railway_build_local.bat`, `scripts/railway_start_local.bat`
- `.env.example`, `.env.evidencias.example`, `.gitignore`
- `backend/requirements.txt`, `backend/manage.py`, `backend/bootstrap_data.py`, `backend/smoke_test.py`
- `backend/config/settings.py`, `backend/config/urls.py`
- `backend/apps/authentication/` (`models.py`, `permissions.py`, `views.py`, `urls.py`, `serializers.py`)
- `backend/apps/reservations/`, `backend/apps/refreshments/`, `backend/apps/rewards/`, `backend/apps/gym/`, `backend/apps/reports/` (`urls.py`, `views.py`, `models.py`)
- `frontend/package.json`, `frontend/vite.config.js`, `frontend/tailwind.config.js`, `frontend/src/router/index.js`, `frontend/src/api/client.js`
- `tests/run_suite.py`, `tests/runner.py`, `tests/harness.py`, `tests/base.py`, `tests/credenciales.py`, `tests/railway_validation.py`, `tests/metricas_operacion.py`, `tests/unit/`, `tests/integration/`
- `evidencias/` (`validacion_railway.md`, `_gitinfo.txt`, `_versions.txt` y archivos de resultados de pruebas)
- Estado del repositorio verificado con `git rev-parse HEAD`, `git branch --show-current`, `git tag` y `git log`.

No se documentaron funcionalidades que no existen en el repositorio. Los documentos `MATRIZ_CORRESPONDENCIA_FINAL.xlsx` e `INFORME_RESULTADOS_FINALES.md` forman parte del cierre final y complementan la trazabilidad y la consolidación de resultados del proyecto.
