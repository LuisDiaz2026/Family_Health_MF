# CLUB FAMILY HEALTH MF - Aplicativo Web Integral

> **Ingeniería de Sistemas**
> Universidad Antonio Nariño (UAN) - Maicao, La Guajira
> Autor: **Luis Fermín Díaz Choles**
> NIT Club: 32739028-5

**Proyecto:** Sistema integral de gestión y reservas mobile-first para **Club Family Health**, una organización deportiva y recreativa en Maicao.

---

## 1. Stack Tecnológico

| Capa | Tecnologías (versiones pinneadas) |
|---|---|
| **Backend** | Python 3.10.x, Django 5.0.7, Django REST Framework 3.15, SimpleJWT (HS512) |
| **Frontend** | Vue 3.4 (Composition API + script setup), Vite 5, Pinia 2.1, Vue Router 4.2, Axios 1.6, Tailwind 3.4, Lucide Vue |
| **Base de datos** | SQLite 3 (desarrollo) · PostgreSQL psycopg2-binary (producción lista) |
| **Seguridad** | Argon2-Cffi password hashing · django-axes rate limit (5 fallos/login) · JWT rotate + blacklist · CORS CSRF whitelist · Ley 1581/2012 protección datos |
| **Linting/tests** | black 24.3 · flake8 7 · mypy 1.9 · pytest + pytest-django + pytest-cov · 14 smoke tests |

> ⚠️ **Importante:** Todo el proyecto **funciona EXCLUSIVAMENTE con Python 3.10.x** (no Python 3.11, 3.12, 3.14). El entorno virtual `.venv` se creó con Python 3.10.11.

---

## 2. Estructura de carpetas

```
c:\Family_Health_MF\
├── .venv/                 <- Entorno virtual Python 3.10.x (NO VERSIONAR)
├── backend/
│   ├── config/            <- Settings, URLs, WSGI/ASGI
│   ├── apps/
│   │   ├── authentication/ <- 3 roles RBAC (ADMIN/EMPLOYEE/CLIENT), perfil, Leyes 1581
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
│   │   ├── stores/ (6 stores Pinia)
│   │   ├── router/index.js        <- Hash mode + guards RBAC
│   │   ├── layouts/MobileLayout    <- Sticky header + bottom nav safe-area
│   │   ├── components/            <- GlobalToast Teleport, Cards, Empty, Skeleton
│   │   ├── utils/toast.js         <- Estado global toasts
│   │   └── views/
│   │       ├── auth/              <- Login + Registro (2 vistas)
│   │       ├── client/            <- 12 vistas: Home, Reservas, ReservaCreate, Refrescos, Carrito, Pedidos, Puntos, Fidelidad, Gimnasio, RutinaDetalle, Perfil, Notificaciones
│   │       ├── staff/             <- 8 vistas: Dashboard, Reservas, Pedidos, Clientes, Productos, Espacios, Reportes, Perfil
│   │       └── NotFoundView.vue
│   ├── package.json    <- Deps pinneadas Node 18+
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── vite.config.js  <- Proxy /api -> :8000
├── .env.example
├── .env                <- Variables de entorno (cargadas por django-environ)
├── .gitignore
├── arrancar.bat        <- Doble clic: levanta Django 8000 + Vite 5173
└── README.md           <- Este archivo
```

---

## 3. Instalación y puesta en marcha (PASO A PASO)

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
| Recurso | URL |
|---|---|
| **Frontend Mobile-First** | http://127.0.0.1:5173/ |
| **Panel Admin Django** | http://127.0.0.1:8000/admin/ |
| **Base URL API REST** | http://127.0.0.1:8000/api/v1/ |
| **Health Check API** | http://127.0.0.1:8000/api/v1/health/ (200 sin auth) |

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

### 4.1 Autenticación + Perfiles RBAC 3 roles
- Registro CLIENTE con políticas Ley 1581 (doble checkbox).
- Login JWT SimpleJWT: access 60 min + refresh 7 días, rotación + blacklist.
- Axios interceptor `client.js` con **queue refresh token** (evita race conditions).
- Perfil personal: datos, membresía, tarjeta fidelidad, seguridad.

### 4.2 Reservas Dinámicas (anti-solape a nivel aplicación + transacciones)
- 10 espacios precargados: 3 canchas fútbol 5, piscina, 3 salones multiusos, tennis, gimnasio, squash.
- Disponibilidad horaria calculada desde `OperatingHours` + `Holiday`.
- Wizard 3 pasos (selecciona espacio → fecha → slot horario).
- Precio final: `minutos / 60 * hourly_rate`.
- **Protección anti-solape actual (capa aplicación + transacción atómica):**
  1. `Space.is_available_at(start, end)` en [models.py:L163-L180](file:///c:/Family_Health_MF/backend/apps/reservations/models.py#L163-L180) — consulta `start_time < fin AND end_time > inicio` detecta solape PARCIAL (p. ej. 10:00-11:00 vs 10:30-11:30).
  2. `Reservation.save()` en [models.py:L447-L460](file:///c:/Family_Health_MF/backend/apps/reservations/models.py#L447-L460) invoca la validación anterior dentro de un bloque `with transaction.atomic()`.
- **Limitaciones conocidas y acciones pendientes (revisión profesor):**
  1. **SQLite (dev):** no implementa bloqueo de filas `SELECT FOR UPDATE` ni exclusion constraints. En escenarios de concurrencia extrema la validación en capa de aplicación es suficiente para uso habitual del club, pero no ofrece garantía matemática 100%.
  2. **PostgreSQL (producción):** para garantía 100.00% en producción se **RECOMIENDA AÑADIR una Exclusion Constraint** con extensión `btree_gist`: `ALTER TABLE reservations ADD CONSTRAINT no_overlap_reservations EXCLUDE USING gist (space_id WITH =, tstzrange(start_time, end_time) WITH &&)`. Esta mejora está documentada pero aún no implementada en el esquema actual.
  3. Actualmente el modelo NO invoca explícitamente `select_for_update()`; la concurrencia depende del bloque `transaction.atomic()` + validación `is_available_at`. Para fortalecerlo en PostgreSQL, añadir antes de la consulta `Space.objects.select_for_update().get(pk=...)` en la vista create reserva.
- **Pruebas:** Smoke test [14] ejecuta el flujo "crear reserva + intento solapado → 2ª reserva rechazada" correctamente → ver archivo `SCRUM_DOCS\EVIDENCIA_SMOKE_TEST_14_OK.txt`.

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
| Anti-solape reservas (capa aplicación) | ⚠️ Validación `is_available_at()` + `transaction.atomic()` (funcional). No hay Exclusion Constraint PostgreSQL ni `select_for_update()` aún. Pendiente para producción. Ver sección 4.2. |
| Stock atómico `F()` | ✅ `Product.objects.filter(pk=...).update(stock=F('stock')-qty)` · código refreshments views |

---

## 6. Validación (Smoke Tests - evidencia real verificable)

```powershell
cd backend
..\.venv\Scripts\python.exe smoke_test.py
```

**Resultado ejecución real:** `14 OK · 0 FALLIDOS` ✅
- **Fecha y hora de ejecución:** 2026-09-20 18:57:55 (formato ISO).
- **Entorno de pruebas:** backend/db.sqlite3 (seed data 10 espacios / 23 productos / 5 rutinas / 5 usuarios demo).
- **Evidencia archivo original guardada en:** [`SCRUM_DOCS\EVIDENCIA_SMOKE_TEST_14_OK.txt`](file:///c:/Users/gusta/OneDrive%20-%20UNIR/TRABAJOS%20DE%20GRADO/TRABAJOS%20DE%20GRADO/UAN/LUIS/SCRUM_DOCS/EVIDENCIA_SMOKE_TEST_14_OK.txt)
- **Escenarios probados en la suite 14 humos:** [01] Health → [02] Login Cliente → [03] Login Admin → [04] Listar 10 Espacios → [05] Consulta disponibilidad → [06] 23 Productos → [07] Perfil + Fidelidad → [08] 5 Rutinas Gym → [09] Dashboard KPI → [10] Top3 Clientes → [11] Bloqueo 401 sin Token → [12] Refresh Token → [13] Registro sin Política (rechazo 400) → [14] Reserva + Anti-solapamiento.

> **Pruebas unitarias / integración / aceptación (restante para validación formal):** Las pruebas complementarias (31 UT + 12 IT + 30 AT usuarios reales club) están planificadas, pero **aún no cuentan con registro de ejecución ni firma de acta de validación formal por el Product Owner Club Family Health**. Una vez disponibles, se incorporarán los certificados y actas al anexo de la monografía.

---

## 6.1 Acceso Mobile-First Real desde dispositivos en RED WI-FI local

Por defecto arrancar.bat publica el frontend en `127.0.0.1` (solo el propio PC). **Para probar el diseño Mobile-First en celulares reales:**

1. **En el PC servidor**: averigua tu IP LAN → PowerShell: `ipconfig` → "Dirección IPv4" (p. ej. `192.168.1.42`)
2. **Edita `frontend\vite.config.js`** sección `server`:
   ```js
   server: {
     port: 5173,
     host: "0.0.0.0",       // <- permite conexiones desde cualquier IP de la LAN
     strictPort: true
   }
   ```
3. **Edita `backend\config\settings.py`** ALLOWED_HOSTS:
   ```py
   ALLOWED_HOSTS = ["127.0.0.1", "localhost", "192.168.1.42"]  # <- reemplaza por tu IP
   ```
4. Reinicia `arrancar.bat`. **En Windows Defender, marca "Permitir redes privadas"** si aparece la ventana emergente.
5. **En el celular** (Chrome / Safari): `http://192.168.1.42:5173/` (usa TU IP real).

Resultado esperado: todas las pantallas con sticky header + bottom nav safe-area renderizan correctamente en 320-430 px y tiempos de agenda <3s.

---

## 7. Build para producción (Frontend)

```powershell
cd frontend
npm.cmd run build
# → salida en frontend/dist/ (index.html + /assets/*.js/*.css)
npm.cmd run preview   # Prueba local del build final
```

---

## 8. Repositorio Git

```powershell
cd c:\Family_Health_MF
git config user.name "Luis Fermín Díaz Choles"
git config user.email "diazcholesl@gmail.com"
git init
git add -A
git commit -m "Release 1.0: Sistema Integral Club Family Health MF.
Backend Django 5 + DRF 6 apps + 14 smoke tests OK.
Frontend Vue 3 Mobile-First 20+ vistas RBAC cliente/staff.
Stack: Python 3.10 + Node 18 + SQLite + JWT HS512 + Argon2 + Axes."
```

---

## 9. Soporte y Fuera de Alcance (explicítamente NO implementado)

- ❌ Aplicaciones nativas iOS/Android.
- ❌ Pasarelas de pago online (cobro 100% presencial).
- ❌ Hardware externo (torniquetes, tarjetas RFID).
- ❌ IA/ML.
- ❌ Despliegue 24/7 con SLA.
- ❌ Integraciones terceros (Wompi, PlaceToPay, WhatsApp, etc.).

El prototipo desplegable se sirve en local ejecutando `.\arrancar.bat` como se explicó arriba.
