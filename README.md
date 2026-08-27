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

### Usuarios DEMO precargados (seed data)

| Usuario | Contraseña | Rol |
|---|---|---|
| `admin_fh` | `AdminFH2026*!` | ADMIN + Superusuario |
| `recepcion_fh` | `RecepcionFH2026*!` | EMPLOYEE (recepción/barra) |
| `cliente1_fh` | `Cliente1FH*!` | CLIENT (Juan Carlos Gómez) |
| `cliente2_fh` | `Cliente2FH*!` | CLIENT (Valeria Martínez) |
| `cliente3_fh` | `Cliente3FH*!` | CLIENT (Andrés Pinto) |

Los accesos DEMO también son visibles en la pantalla de login del frontend.

---

## 4. Módulos implementados

### 4.1 Autenticación + Perfiles RBAC 3 roles
- Registro CLIENTE con políticas Ley 1581 (doble checkbox).
- Login JWT SimpleJWT: access 60 min + refresh 7 días, rotación + blacklist.
- Axios interceptor `client.js` con **queue refresh token** (evita race conditions).
- Perfil personal: datos, membresía, tarjeta fidelidad, seguridad.

### 4.2 Reservas Dinámicas (anti-solape transaccional)
- 10 espacios precargados: 3 canchas fútbol 5, piscina, 3 salones multiusos, tennis, gimnasio, squash.
- Disponibilidad horaria calculada desde `OperatingHours` + `Holiday`.
- Wizard 3 pasos (selecciona espacio → fecha → slot horario).
- Precio final: `minutos / 60 * hourly_rate`.
- `select_for_update()` + restricción única DB → **nunca hay dos reservas solapadas**.

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

| Controles | Estado |
|---|---|
| Hash contraseñas **Argon2** (no MD5/SHA) | ✅ `PASSWORD_HASHERS` primera opción Argon2 |
| **JWT HS512** rotate + blacklist logout | ✅ SimpleJWT + TokenBlacklistView |
| Rate limit login **django-axes** (5 fallos → 15 min bloqueo) | ✅ 403 bloqueado IP + user-agent |
| Throttle login: 10/min · registro: 5/h | ✅ REST_FRAMEWORK DEFAULT_THROTTLE_RATES |
| `CORS_ALLOWED_ORIGINS` explícitos | ✅ localhost:5173, 127.0.0.1:5173 |
| `CSRF_TRUSTED_ORIGINS` explícitos | ✅ Equivalente a CORS |
| Política **Ley 1581/2012** (protección datos Habeas Data) | ✅ Registro cliente con 2 checkboxes + fecha aceptación `privacy_policy_accepted_at` |
| Auditoría acciones (login, registro, ops) | ✅ `AuditLog.objects.create(...)` |
| Anti-solape reservas transaccional | ✅ `select_for_update` + constraint única |
| Stock atómico `F()` | ✅ `Product.objects.filter(pk=...).update(stock=F('stock')-qty)` |

---

## 6. Validación (Smoke Tests)

```powershell
cd backend
..\.venv\Scripts\python.exe smoke_test.py
```

Resultados: **14 OK · 0 FALLIDOS** (Health, Login cliente, Login admin, 10 espacios, disponibilidad, 23 productos, perfil+loyalty, 5 rutinas, Dashboard, Top3 clientes, 401 sin token, Refresh token, Registro rechazado sin política, reserva OK + anti-solape).

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
