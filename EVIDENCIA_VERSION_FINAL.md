# EVIDENCIA DE VERSIÓN FINAL ENTREGADA

**Proyecto:** Family Health MF — Aplicativo web Mobile-First para la gestión centralizada de reservas del Club Family Health
**Trabajo de grado:** Ingeniería de Sistemas y Computación — Universidad Antonio Nariño (UAN), sede Maicao, La Guajira
**Autor:** Luis Fermín Díaz Choles
**Fecha de actualización de este documento:** 2026-10-23 (America/Bogota)

> Este documento identifica de forma inequívoca la **versión de software entregada** al director del trabajo de grado. No contiene secretos, tokens ni credenciales.

---

## 1. Identificación del software entregado

| Elemento | Valor |
|---|---|
| Repositorio | `https://github.com/LuisDiaz2026/Family_Health_MF.git` |
| Rama | `main` |
| Commit del software final (código) | `d46cd89fc9d955ca5cc548fa4c5d1a4bbfd18af4` |
| Commit corto | `d46cd89` |
| Mensaje del commit | `entrega: retirar script de depuracion con credenciales y volcados temporales de evidencia` |
| Fecha del commit | 2026-10-21 20:27:08 -0500 |
| Commit funcional de referencia (validación) | `51cffda5147b239231917d9ab781fdbb16b1012f` |
| Etiqueta de cierre documental | `v1.0.0` → `2a0124a` |
| URL de producción | `https://familyhealthmf-production.up.railway.app/` |
| Endpoint de salud | `/api/v1/health/` |

El commit `d46cd89` corresponde al código final del aplicativo. Cualquier commit posterior en `main` es **exclusivamente documental** (esta misma evidencia y las guías de entrega) y no modifica el código del backend ni del frontend.

### Cómo verificar la versión

```powershell
git clone https://github.com/LuisDiaz2026/Family_Health_MF.git
cd Family_Health_MF
git checkout d46cd89
git show -s --format="%H | %ad | %s" --date=iso HEAD
```

La verificación del despliegue se realiza consultando `GET /api/v1/health/`, que debe responder HTTP 200 con `"database":"ok"`.

---

## 2. Estructura del paquete de software

| Carpeta / archivo | Contenido |
|---|---|
| `backend/` | Proyecto Django 5.0.7 + DRF 3.15.2 (autenticación, reservas, refresquería, recompensas, gimnasio, reportes) |
| `frontend/` | SPA Vue 3.4 + Pinia + Vite 5 (vistas de cliente, recepción, cafetería y administración) |
| `tests/` | Suites unitarias, de integración, smoke, benchmark, métricas, validación Railway y evaluación por perfiles |
| `evidencias/` | Salidas reales de las verificaciones (CSV, JSON, TXT, Markdown y capturas Mobile-First) |
| `docs/` | Manual técnico y manual de usuario en formato Word |
| `Dockerfile`, `railway.json` | Configuración de despliegue en Railway (Dockerfile multietapa) |
| `README.md` | Instrucciones de instalación y ejecución |
| `EVIDENCIA_VERSION_FINAL.md` | Este documento |
| `MATRIZ_CORRESPONDENCIA_FINAL.xlsx`, `INFORME_RESULTADOS_FINALES.md` | Trazabilidad y consolidación de resultados |

---

## 3. Tecnologías y versiones (verificadas)

| Componente | Versión |
|---|---|
| Python (local) | 3.10.11 |
| Python (contenedor producción) | 3.11-slim-bookworm |
| Django | 5.0.7 |
| Django REST Framework | 3.15.2 |
| Node.js (build producción) | 20-bookworm-slim |
| Vue | 3.4 |
| Vite | 5.0 |
| Base de datos local | SQLite 3 |
| Base de datos producción | PostgreSQL (Railway) |

---

## 4. Resultados de verificación de la versión final

| Verificación | Resultado | Evidencia |
|---|---|---|
| Pruebas unitarias | 32/32 aprobadas | `evidencias/pruebas_unitarias.*` |
| Pruebas de integración | 12/12 aprobadas | `evidencias/pruebas_integracion.*` |
| Smoke tests | 14/14 aprobados | `evidencias/smoke_tests_raw.txt` |
| Validación HTTP en Railway | 20/20 aprobados | `evidencias/validacion_railway.*` |
| Anti-solapamiento | 32 intentos, 0 aceptados indebidamente | `evidencias/benchmark_*`, `evidencias/validacion_railway.md` |
| Benchmark de rendimiento | 120/120 iteraciones, 100 % éxito | `evidencias/benchmark_iteraciones.csv` |
| Mobile-First | 36/36 PASS, 0 px de desbordamiento | `evidencias/mobile_first.*` |
| Indicadores de estado en PostgreSQL | 42 indicadores | `evidencias/metricas_operacion_real.*` |
| Evaluación programática por perfiles | 68/68 tareas, 25 requisitos (identidades sintéticas) | `evidencias/simulacion_aceptacion.*` |

**Nota.** Las 68 comprobaciones con identidades sintéticas corresponden a **validación técnica del software**, no a pruebas de usabilidad con participantes humanos. El sistema no mide tiempos de atención humana ni satisfacción de usuarios.

---

## 5. Verificación de ausencia de secretos

- `DJANGO_SECRET_KEY` y `DATABASE_URL` se gestionan por variables de entorno; en producción el arranque falla si la clave no está definida.
- El archivo `.env` está excluido del repositorio (`.gitignore`); solo se versiona `.env.example` con valores de relleno.
- No se incluyen tokens JWT, contraseñas ni cadenas de conexión en el repositorio ni en las evidencias.
- El script `backend/debug_login.py` fue retirado del repositorio; `backend/smoke_test.py` lee las credenciales del entorno.

---

## 6. Punto de restauración

- **Punto de restauración funcional:** commit `d46cd89` (rama `main`).
- **Rama histórica de cierre:** `release/tg-final` (conservada como referencia reversible).
- **Artefacto de evidencias:** carpeta `evidencias/`.

La correspondencia entre requerimientos, historias de usuario, módulos, código, endpoints y pruebas se documenta en `MATRIZ_CORRESPONDENCIA_FINAL.xlsx`. Los resultados consolidados se presentan en `INFORME_RESULTADOS_FINALES.md`.
