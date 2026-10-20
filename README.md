# CLUB FAMILY HEALTH MF - Aplicativo Web Integral

> **Ingeniería de Sistemas**
> Universidad Antonio Nariño (UAN) - Maicao, La Guajira
> Autor: **Luis Fermín Díaz Choles**
> NIT Club: 32739028-5

**Proyecto:** Sistema integral de gestión y reservas mobile-first para **Club Family Health**, una organización deportiva y recreativa en Maicao.

**🚀 Despliegue en producción (Railway):** <https://familyhealthmf-production.up.railway.app/>
**Repositorio GitHub:** <https://github.com/LuisDiaz2026/Family_Health_MF>
**Health Check API:** <https://familyhealthmf-production.up.railway.app/api/v1/health/>

**Versión funcional validada en producción:** rama `main`, commit `51cffda` (despliegue Railway con PostgreSQL y health check HTTP 200). La etiqueta **`v1.0.0`** marca el commit de cierre `2a0124a`, que añade exclusivamente documentación y evidencias (sin cambios funcionales).

---

## 1. Stack Tecnológico

| Capa | Tecnologías (versiones pinneadas) |
|---|---|
| **Backend** | Python 3.10.x (local) · Python 3.11-slim (Railway) · Django 5.0.7, Django REST Framework 3.15, SimpleJWT (HS512) |
| **Frontend** | Vue 3.4 (Composition API + script setup), Vite 5, Pinia 2.1, Vue Router 4.2, Axios 1.6, Tailwind 3.4, Lucide Vue |
| **Base de datos** | SQLite 3 (desarrollo local) · **PostgreSQL (Railway, producción activa)** · psycopg2-binary |
| **Servidor app** | Gunicorn (Railway) · WhiteNoise (static files) · Docker multistage |
| **Seguridad** | Argon2-Cffi password hashing · django-axes rate limit (5 fallos/login) · JWT rotate + blacklist · CORS CSRF whitelist · Ley 1581/2012 protección datos |
| **Linting/tests** | black 24.3 · flake8 7 · mypy 1.9 · pytest + pytest-django + pytest-cov · 14 smoke tests |

> ⚠️ **Versión de Python:** El entorno local (`.venv`) se creó con **Python 3.10.11**. La imagen de producción en Railway usa **python:3.11-slim-bookworm**. `requirements.txt` es compatible con ambas.

---

## 2. Estructura de carpetas

```
c:\Family_Health_MF\
├── .venv/                 <- Entorno virtual Python 3.10.x (NO VERSIONAR)
├── backend/
│   ├── config/            <- Settings, URLs, WSGI/ASGI
│   ├── apps/
│   │   ├── authentication/ <- 4 roles RBAC (ADMIN/RECEPCION/CAFETERIA/CLIENT; EMPLOYEE de compatibilidad), perfil, Leyes 1581
│   │   ├── reservations/   <- Espacios + disponibilidad + anti-solape transaccional
│   │   ├── refreshments/   <- Inventario productos + pedidos + stock atómico F()
│   │   ├── rewards/        <- 4 tiers (Bronce Plata Oro Diamante) + puntos + canje
│   │   ├── gym/            <- Rutinas preestablecidas + ejercicios + músculos
│   │   └── reports/        <- Dashboard KPI, ranking clientes, notificaciones
│   ├── manage.py
│   ├── requirements.txt    <- Dependencias pinneadas EXCLUSIVO Py3.10
│   ├── db.sqlite3          <- BD desarrollo (seed data ya cargada)
│   ├── bootstrap_data.py   <- Script seed 10 espacios / 23 productos / 5 rutinas
│   ├── smoke_test.py       <- 14 pruebas humo API (14 OK)
│   └── fixtures, media, static
├── frontend/
│   ├── src/
│   │   ├── api/client.js          <- Axios + JWT refresh queue
│   │   ├── stores/ (7 stores Pinia)
│   │   ├── router/index.js        <- Hash mode + guards RBAC
│   │   ├── layouts/MobileLayout    <- Sticky header + bottom nav safe-area
│   │   ├── components/            <- GlobalToast Teleport, Cards, Empty, Skeleton
│   │   ├── utils/toast.js         <- Estado global toasts
│   │   └── views/
│   │       ├── auth/              <- Login + Registro (2 vistas)
│   │       ├── client/            <- 12 vistas: Home, Reservas, ReservaCreate, Refrescos, Carrito, Pedidos, Puntos, Fidelidad, Gimnasio, RutinaDetalle, Perfil, Notificaciones
│   │       ├── staff/             <- 9 vistas: Dashboard, Reservas, Pedidos, Clientes, Productos, Espacios, Ofertas, Reportes, Perfil
│   │       └── NotFoundView.vue
│   ├── package.json    <- Deps pinneadas Node 18+
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── vite.config.js  <- Proxy /api -> :8000
├── .env.example
├── .env                <- Variables de entorno (cargadas por django-environ)
├── .gitignore
├── Dockerfile          <- Multistage: build Vite + runtime Django/Gunicorn (Railway)
├── railway.json        <- Config Railway: builder DOCKERFILE + healthcheck
├── arrancar.bat        <- Doble clic: levanta Django 8000 + Vite 5173 (SOLO LOCAL)
├── scripts/
│   ├── railway_build.sh <- Build script (legacy, reemplazado por Dockerfile)
│   ├── railway_start.sh <- Start: migrate + collectstatic + bootstrap + gunicorn
│   └── railway_build_local.bat / railway_start_local.bat <- Simulación local (Windows)
├── tests/
│   ├── unit/           <- 32 pruebas unitarias (U01-U32)
│   ├── integration/    <- 12 pruebas de integración (I01-I12)
│   ├── e2e/            <- Pruebas de navegador (mobile-first, evaluación de tareas)
│   ├── run_suite.py    <- Ejecutor de la suite que genera evidencias
│   ├── railway_validation.py <- 20 casos HTTP contra producción (RW01-RW20)
│   └── metricas_operacion.py <- 42 indicadores operativos reales (M01-M42)
├── evidencias/         <- Salidas reales de las suites (txt/json/csv/md) y capturas Mobile-First
├── EVIDENCIA_VERSION_FINAL.md        <- Punto de restauración y versión congelada
├── INFORME_RESULTADOS_FINALES.md     <- Consolidado de resultados (secciones A-K)
├── MATRIZ_CORRESPONDENCIA_FINAL.xlsx <- Trazabilidad requerimiento-prueba
├── MANUAL_TECNICO.md   <- Fuente del manual técnico (documento FIS-UDCII-G05)
├── MANUAL_USUARIO.md   <- Fuente del manual de usuario (documento FIS-UDCII-G06)
└── README.md           <- Este archivo
```

---

## 3. Instalación y puesta en marcha (PASO A PASO)

> 🔒 **Esta sección es solo para entorno de desarrollo local.** El sistema ya está desplegado en producción en Railway: <https://familyhealthmf-production.up.railway.app/>. Para ver el aplicativo en funcionamiento no necesitas instalar nada; abre la URL de producción en tu navegador.

### Prerrequisitos instalados en tu equipo
1. **Python 3.10.x** (3.10.11 recomendado): descarga desde <https://www.python.org/downloads/release/python-31011/>.
   - Instálalo en **C:\Users\TU_USUARIO\AppData\Local\Programs\Python\Python310\** (ubicación por defecto).
   - Verifica: `py -0p` → lista las versiones con rutas.
2. **Node.js 18+** (recomendado LTS): <https://nodejs.org/es/> (ya instalado en este equipo).
3. **Git 2.40+** para versionamiento.

### Paso 1 - Instalar entorno virtual (Python 3.10)
```powershell
cd c:\Family_Health_MF
py -3.10 -m venv --clear .venv
.\.venv\Scripts\activate
```
Listo — en este repo el entorno ya está creado y las dependencias ya instaladas.

### Paso 2 - Instalar dependencias Backend
```powershell
.\.venv\Scripts\pip install -r backend\requirements.txt
```

### Paso 3 - Verificar el backend
```powershell
cd backend
..\.venv\Scripts\python.exe manage.py check
# Debe imprimir: "System check identified no issues (0 silenced)."

# Ejecutar los 14 smoke tests
..\.venv\Scripts\python.exe smoke_test.py
# RESULTADO ESPERADO: 14 OK | 0 FALLIDOS
```

### Paso 4 - Instalar dependencias Frontend
```powershell
cd ..\frontend
npm.cmd install --no-audit --no-fund
```

### Paso 5 - LEVANTAR AMBOS SERVIDORES (2 maneras)

#### Opción A: un clic con `arrancar.bat`
```powershell
cd c:\Family_Health_MF
.\arrancar.bat
```

#### Opción B: manualmente en 2 terminales
Terminal 1 (Backend Django, puerto 8000):
```powershell
cd backend
..\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```
Terminal 2 (Frontend Vite, puerto 5173):
```powershell
cd frontend
npm.cmd run dev
```

### Paso 6 - Accesos

**Entorno local (desarrollo):**

| Recurso | URL |
|---|---|
| **Frontend Mobile-First** | http://127.0.0.1:5173/ |
| **Panel Admin Django** | http://127.0.0.1:8000/admin/ |
| **Base URL API REST** | http://127.0.0.1:8000/api/v1/ |
| **Health Check API** | http://127.0.0.1:8000/api/v1/health/ (200 sin auth) |

**Entorno producción (Railway):**

| Recurso | URL |
|---|---|
| **Frontend Mobile-First** | https://familyhealthmf-production.up.railway.app/ |
| **Panel Admin Django** | https://familyhealthmf-production.up.railway.app/admin/ |
| **Base URL API REST** | https://familyhealthmf-production.up.railway.app/api/v1/ |
| **Health Check API** | https://familyhealthmf-production.up.railway.app/api/v1/health/ (200 sin auth) |

### Usuarios DEMO precargados (seed data - SOLO ENTORNO PRUEBAS LOCAL)

> ⚠️ **ADVERTENCIA DE SEGURIDAD:** Los usuarios y contraseñas listados a continuación son **usuarios de semilla (seed data)** creados para pruebas automáticas y demostraciones iniciales en un entorno de desarrollo aislado. **Nunca los utilices en un entorno de producción accesible por la red o por clientes reales.** Antes de desplegar el sistema en el Club Family Health real:
> 1. Cambia **todas** las contraseñas de las cuentas `admin_*` y `recepcion_*`.
> 2. Elimina los usuarios `cliente1/2/3_fh` o desactívalos (`is_active=False`).
> 3. **Nunca publiques credenciales reales de administración** en el repositorio, los anexos de la monografía o el manual.
> 4. La pantalla de login del frontend **NO muestra credenciales públicas**.

| Usuario DEMO | Rol DEMO (pruebas) | Propósito |
|---|---|---|
| `admin_fh` | ADMIN + Superusuario | Pruebas panel Django Admin y dashboard KPIs |
| `recepcion_fh` | EMPLOYEE (recepción/barra) | Pruebas flujo barra y recepción |
| `cliente1_fh` | CLIENT | Smoke test API perfil cliente |
| `cliente2_fh` | CLIENT | Caso manual |
| `cliente3_fh` | CLIENT | Caso manual |

> Las contraseñas exactas de estas cuentas DEMO no se publican en este README por política de seguridad. Para ejecutar las pruebas o reproducir el entorno, consulta el código fuente de `bootstrap_data.py` y `smoke_test.py` (archivos internos del proyecto), o comunícate con el desarrollador.

---

## 4. Módulos implementados

### 4.1 Autenticación + Perfiles RBAC 4 roles
- Registro CLIENTE con políticas Ley 1581 (doble checkbox).
- Login JWT SimpleJWT: access 60 min + refresh 7 días, rotación + blacklist.
- Axios interceptor `client.js` con **queue refresh token** (evita race conditions).
- Perfil personal: datos, membresía, tarjeta fidelidad, seguridad.

### 4.2 Reservas Dinámicas (anti-solape a nivel aplicación + transacciones + bloqueo de filas)
- 10 espacios precargados: 3 canchas fútbol 5, piscina, 3 salones multiusos, tennis, gimnasio, squash.
- Disponibilidad horaria calculada desde `OperatingHours` + `Holiday`.
- Wizard 3 pasos (selecciona espacio → fecha → slot horario).
- Precio final: `minutos / 60 * hourly_rate`.
- **Protección anti-solape actual (3 niveles de defensa):**
  1. `Space.is_available_at(start, end)` en [models.py:L163-L180](file:///c:/Family_Health_MF/backend/apps/reservations/models.py#L163-L180) — consulta `start_time < fin AND end_time > inicio` detecta solape PARCIAL (p. ej. 10:00-11:00 vs 10:30-11:30).
  2. `Reservation.save()` en [models.py:L447-L460](file:///c:/Family_Health_MF/backend/apps/reservations/models.py#L447-L460) invoca la validación anterior **dentro de un bloque `with transaction.atomic()`**.
  3. **Bloqueo explícito `Space.objects.select_for_update().get(pk=self.space_id)`** en [models.py:L455](file:///c:/Family_Health_MF/backend/apps/reservations/models.py#L455) — obtiene bloqueo exclusivo de fila del espacio ANTES de verificar disponibilidad, evitando race conditions TOCTOU (Time-of-Check / Time-of-Use) en PostgreSQL.
- **Limitaciones conocidas y acciones pendientes (revisión profesor):**
  1. **SQLite (dev):** emula `SELECT FOR UPDATE` pero sin garantía a nivel motor (no implementa bloqueo real de filas ni exclusion constraints). Para el uso habitual del club (flujo de trabajo serial) es válido, pero en producción se recomienda PostgreSQL.
  2. **PostgreSQL (producción):** para garantía 100.00% y evitar solapes incluso por fallos de aplicación, se **RECOMIENDA AÑADIR una Exclusion Constraint** con extensión `btree_gist`: `ALTER TABLE reservations ADD CONSTRAINT no_overlap_reservations EXCLUDE USING gist (space_id WITH =, tstzrange(start_time, end_time) WITH &&)`. Esta mejora es responsabilidad del DBA en despliegue final.
- **Pruebas:** Smoke test [14] ejecuta el flujo "crear reserva + intento solapado → 2ª reserva rechazada HTTP400 + BD count=1 SIN duplicados" correctamente → ver archivo [`evidencias/smoke_tests_raw.txt`](file:///c:/Family_Health_MF/evidencias/smoke_tests_raw.txt).

### 4.3 Gestión Pedidos Refresquería
- 23 productos SKU en 5 categorías (Bebidas frías, Calientes, Snacks, Comidas rápidas, Postres).
- **Stock atómico F()**: nunca se vende por encima del inventario.
- Carrito persistente en `localStorage.fh_cart`.
- % descuento fidelidad automático (tier).
- Métodos pago 100% presencial: EFECTIVO, TRANSFERENCIA, TARJETA, PREPAGADA.

### 4.4 Recompensas y Fidelización
- **4 Niveles** Bronce (0+) → Plata (500+) → Oro (1500+) → Diamante (3000+) con colores distintivos.
- 5 Reward Rules ganar puntos (reserva, pedido, invitado, primera reserva, canje).
- Catálogo canje (e.g. Gatorade 80 pts, 1 día piscina 300 pts, 1 mes membresía 2500 pts...).
- Barra progreso próximo nivel, movimientos recientes.

### 4.5 Módulo Gimnasio (rol CLIENTE)
- 22 ejercicios, 12 músculos (incluye Antebrazos, Gemelos, Glúteos).
- 5 rutinas preestablecidas: Full Body Principiante, Hipertrofia Avanzada, Definición, Acondicionamiento Funcional, Glúteos y Piernas.
- Pantalla detalle: calentamiento, sets/reps/descanso/dificultad, enfriamiento, tips nutricionales.

### 4.6 Panel Admin + Reportes
- **6 KPIs**: usuarios activos, clientes, espacios, reservas totales, pedidos, ingresos mes.
- % Ocupación 7 días, ingresos reservas/barra, distribución niveles, **Top 10 clientes ranking** (puesto, nombre, reservas, gasto total).
- Gestionar reservas (aprobar/cancelar/marcar pagada).
- Estados pedidos (PEND → PREP → LISTO → PAGADO/ENTREGADO).
- Inventario productos + inventario espacios.

---

## 5. Seguridad Integral

| Controles | Estado y evidencia |
|---|---|
| Hash contraseñas **Argon2** (no MD5/SHA) | ✅ `PASSWORD_HASHERS` primera opción Argon2 · código settings |
| **JWT HS512** rotate + blacklist logout | ✅ SimpleJWT + TokenBlacklistView · Smoke test [12] |
| Rate limit login **django-axes** (5 fallos → 15 min bloqueo) | ✅ 403 bloqueado IP + user-agent · settings AXES |
| Throttle login: 10/min · registro: 5/h | ✅ REST_FRAMEWORK DEFAULT_THROTTLE_RATES |
| `CORS_ALLOWED_ORIGINS` explícitos | ✅ localhost:5173, 127.0.0.1:5173 |
| `CSRF_TRUSTED_ORIGINS` explícitos | ✅ Equivalente a CORS |
| Política **Ley 1581/2012** (protección datos Habeas Data) | ✅ Registro cliente con 2 checkboxes + fecha aceptación `privacy_policy_accepted_at` · Smoke test [13] |
| Auditoría acciones (login, registro, ops) | ✅ `AuditLog.objects.create(...)` · código autenticación app |
| Anti-solape reservas (3 niveles) | ✅ Validación `is_available_at()` + `transaction.atomic()` + `Space.objects.select_for_update()` bloqueo exclusivo de fila. Smoke test [14] VERIFICA rechazo HTTP400 solape + count=1 BD sin duplicados. Exclusion Constraint PostgreSQL recomendada en despliegue (opcional). |
| Stock atómico `F()` | ✅ `Product.objects.filter(pk=...).update(stock=F('stock')-qty)` · código refreshments views |

---

## 6. Validación (Smoke Tests - evidencia real verificable)

```powershell
cd backend
..\.venv\Scripts\python.exe smoke_test.py
```

**Resultado ejecución real:** `14 OK · 0 FALLIDOS` ✅
- **Fecha y hora de ejecución:** 2026-10-05 09:45 (formato ISO).
- **Entorno de pruebas:** backend/db.sqlite3 (seed data 10 espacios / 23 productos / 5 rutinas / 5 usuarios demo).
- **Evidencia de la ejecución guardada en:** [`evidencias/smoke_tests_raw.txt`](file:///c:/Family_Health_MF/evidencias/smoke_tests_raw.txt)
- **Escenarios probados en la suite 14 humos:** [01] Health → [02] Login Cliente → [03] Login Admin → [04] Listar 10 Espacios → [05] Consulta disponibilidad → [06] 23 Productos → [07] Perfil + Fidelidad → [08] 5 Rutinas Gym → [09] Dashboard KPI → [10] Top3 Clientes → [11] Bloqueo 401 sin Token → [12] Refresh Token → [13] Registro sin Política (rechazo 400) → [14] Reserva + Anti-solapamiento (HTTP201 + HTTP400 + count=1 BD VERIFICADO).

> **Pruebas unitarias / integración / validación en producción (ejecutadas con evidencia registrada):** **32 pruebas unitarias (32/32 PASS)**, **12 pruebas de integración (12/12 PASS)** y **20 casos HTTP contra el despliegue de Railway (20/20 PASS)**. Las salidas quedan en [`evidencias/`](file:///c:/Family_Health_MF/evidencias): `pruebas_unitarias.txt`, `pruebas_integracion.txt` y `validacion_railway.md`. La firma del acta formal de validación por el Product Owner del Club Family Health permanece como trámite administrativo de cierre.

---

## 6.1 Acceso Mobile-First Real desde dispositivos en RED WI-FI local

**✅ CONFIGURACIÓN PREDETERMINADA (arrancar.bat):**
Ahora los servidores publican automáticamente en `0.0.0.0` para acceso LAN sin editar archivos:
- Django Backend: `0.0.0.0:8000` (vía [arrancar.bat](file:///c:/Family_Health_MF/arrancar.bat))
- Vite Frontend: `0.0.0.0:5173` (vía [package.json](file:///c:/Family_Health_MF/frontend/package.json) scripts `dev`)
- CORS: Permite todos los orígenes SÓLO si `DJANGO_DEBUG=True` en el `.env` ([settings.py#L311-L315](file:///c:/Family_Health_MF/backend/config/settings.py#L311-L315))
- ALLOWED_HOSTS: Incluye rangos CIDR LAN 192.168.0.0/16 · 10.0.0.0/8 · 172.16.0.0/12 ([settings.py#L46-L53](file:///c:/Family_Health_MF/backend/config/settings.py#L46-L53))

**Pasos para probar en móvil/celular REAL:**

- **Producción (Railway):** Abre directamente <https://familyhealthmf-production.up.railway.app/> en el navegador del celular. No requiere configuración adicional.
- **Desarrollo local (WiFi LAN):**
  1. **En el PC servidor**: averigua tu IP LAN → PowerShell: `ipconfig` → "Dirección IPv4" (p. ej. `192.168.1.42`)
  2. **Ejecuta** `arrancar.bat`. **En Windows Defender, marca "Permitir redes privadas"** si aparece la ventana emergente.
  3. **En el celular** (misma red WiFi que el PC): entra a `http://192.168.1.42:5173/` (reemplaza `192.168.1.42` por TU IP real).
  4. Para probar el Backend directo: `http://192.168.1.42:8000/api/v1/health/`

Resultado esperado: todas las pantallas con sticky header + bottom nav safe-area renderizan correctamente en 320-430 px y tiempos de agenda <3s.

> ⚠️ **Producción (Railway / DEBUG=False)**: La configuración se cierra automáticamente a CORS/ALLOWED_HOSTS estrictos según dominio Railway. NO se expone 0.0.0.0 ni CORS abierto.

---

## 7. Despliegue en Producción (Railway + Docker)

El sistema está **desplegado en Railway** mediante un **Dockerfile multistage** (2 etapas) y desplegado automáticamente desde el repositorio de GitHub. No se usa `arrancar.bat` en producción.

### 7.1 Arquitectura del despliegue

| Componente | Detalle |
|---|---|
| **Proveedor** | Railway (contenedor Docker) |
| **Origen** | GitHub `LuisDiaz2026/Family_Health_MF` (rama `main`) |
| **URL producción** | https://familyhealthmf-production.up.railway.app/ |
| **Builder** | `DOCKERFILE` (definido en `railway.json`) |
| **Healthcheck** | `GET /api/v1/health/` (HTTP 200 + `database: ok`) |
| **Reinicio** | `ON_FAILURE`, hasta 5 reintentos |

### 7.2 Dockerfile (2 etapas)

1. **Etapa 1 — Build frontend:** `node:20-bookworm-slim` → `npm ci` + `npm run build` → genera `frontend/dist/`.
2. **Etapa 2 — Runtime backend:** `python:3.11-slim-bookworm` → instala `requirements.txt`, copia el código Django y el `dist/` de la etapa 1.
3. **CMD del contenedor** (al arrancar):
   1. `python manage.py migrate --noinput`
   2. `python manage.py collectstatic --noinput --clear`
   3. `python bootstrap_data.py` (seed demo, si `RAILWAY_SEED_BOOTSTRAP=1`)
   4. `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`

> El `frontend/dist/` se sirve directamente por Django + **WhiteNoise** (no hay un servidor Nginx ni Vite en producción).

### 7.3 Variables de entorno configuradas en Railway

Estas variables están definidas en `railway.json` (no son secretas) o en el panel de Railway:

| Variable | Valor | Propósito |
|---|---|---|
| `DJANGO_DEBUG` | `False` | Modo producción |
| `DJANGO_ALLOWED_HOSTS` | `*` | Hosts permitidos (se restringe por dominio Railway) |
| `DJANGO_SECRET_KEY` | *(secreta, panel Railway)* | Firma de sesiones/JWT |
| `DATABASE_URL` | *(secreta, plugin PostgreSQL Railway)* | Conexión a PostgreSQL |
| `RAILWAY_SEED_BOOTSTRAP` | `1` | Ejecuta `bootstrap_data.py` en el primer arranque |
| `WEB_CONCURRENCY` | `2` | Workers Gunicorn |
| `GUNICORN_THREADS` | `4` | Threads por worker |
| `GUNICORN_TIMEOUT` | `120` | Timeout de request |
| `ACCESS_TOKEN_LIFETIME_MINUTES` | `60` | Duración JWT access |
| `REFRESH_TOKEN_LIFETIME_DAYS` | `7` | Duración JWT refresh |
| `LOGIN_MAX_ATTEMPTS` | `5` | Intentos login antes de bloquear |
| `LOGIN_COOLDOWN_MINUTES` | `15` | Tiempo de bloqueo |

> ⚠️ `DJANGO_SECRET_KEY` y `DATABASE_URL` **NUNCA** se versionan. Se configuran en el panel de Railway → Variables.

### 7.4 Cómo desplegar / redeployar

1. **Push a la rama `main`** de GitHub: Railway detecta el cambio y construye + despliega automáticamente.
   ```powershell
   cd c:\Family_Health_MF
   git add -A
   git commit -m "feat: descripción del cambio"
   git push origin main
   ```
2. Esperar a que Railway termine el build (logs en el dashboard de Railway).
3. Verificar el **Health Check**: `GET https://familyhealthmf-production.up.railway.app/api/v1/health/` debe responder `200 OK` con `"database":"ok"`.

### 7.5 Build local del frontend (solo para probar el bundle)

```powershell
cd frontend
npm.cmd run build
# → salida en frontend/dist/ (index.html + /assets/*.js/*.css)
npm.cmd run preview   # Prueba local del build final
```

---

## 8. Repositorio Git y CI/CD

```powershell
cd c:\Family_Health_MF
git config user.name "Luis Fermín Díaz Choles"
git config user.email "diazcholesl@gmail.com"
```

- **Remote:** `https://github.com/LuisDiaz2026/Family_Health_MF.git`
- **Rama principal:** `main`
- **Despliegue automático:** cada `push` a `main` dispara un build+deploy en Railway (vía `railway.json` + `Dockerfile`).

```powershell
git add -A
git commit -m "Release 1.0: Sistema Integral Club Family Health MF"
git push origin main
```

---

## 9. Soporte y Fuera de Alcance (explícitamente NO implementado)

- ❌ Aplicaciones nativas iOS/Android.
- ❌ Pasarelas de pago online (cobro 100% presencial).
- ❌ Hardware externo (torniquetes, tarjetas RFID).
- ❌ IA/ML.
- ❌ Integraciones terceros (Wompi, PlaceToPay, WhatsApp, etc.).

✅ El sistema está **desplegado en producción en Railway**: <https://familyhealthmf-production.up.railway.app/>. Para ejecutarlo en modo local de desarrollo, usa `.\arrancar.bat` (sección 3).
