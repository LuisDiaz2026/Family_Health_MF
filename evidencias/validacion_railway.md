# Validacion real sobre el despliegue de Railway

> Family Health MF - cierre tecnico de la version final

- **URL evaluada:** https://familyhealthmf-production.up.railway.app
- **Fecha/hora (UTC):** 2026-10-20T03:53:13+00:00
- **Casos ejecutados:** 20
- **Aprobados:** 20
- **Fallidos:** 0

Los codigos HTTP son los que el servicio devolvio realmente. No se
almacenan tokens ni contrasenas completos (solo huellas enmascaradas).

| ID | Requisito | Descripcion | Metodo | Ruta | HTTP esperado | HTTP real | Resultado | Observacion |
|---|---|---|---|---|---|---|---|---|
| RW01 | RNF-DIS-01 | Health check publico | GET | `/api/v1/health/` | 200 | 200 | PASS | database=ok version=1.0.0 |
| RW02 | RQF-AUT-01 | Login correcto (cliente1_fh) | POST | `/api/v1/auth/login/` | 200 | 200 | PASS | rol=CLIENT access=eyJhbGciOi...YR0g (551 car.) (0.3487s) |
| RW03 | RQF-AUT-02 | Login con contrasena incorrecta | POST | `/api/v1/auth/login/` | 401 | 401 | PASS |  |
| RW04 | RQF-AUT-03 | Usuario inactivo (registro publico) no puede autenticarse | POST | `/api/v1/auth/login/` | 400 | 400 | PASS | registro HTTP 201; usuario=val_rw_047999e2; detalle={"non_field_errors": ["Tu cuenta está INACTIVA o pendiente de aprobación por el Administrador del Club Family Health. Contáctate con recepción o con el administ |
| RW05 | RQF-AUT-04 | Login administrador y acceso al panel de KPIs | GET | `/api/v1/reports/dashboard/summary/` | 200 | 200 | PASS |  |
| RW06 | RQF-AUT-05 | Login recepcion y listado de reservas | GET | `/api/v1/reservations/reservations/` | 200 | 200 | PASS |  |
| RW07 | RQF-AUT-06 | Login cliente y consulta de su propio perfil | GET | `/api/v1/auth/me/` | 200 | 200 | PASS | usuario=cliente1_fh |
| RW08 | RQF-AUT-07 | Acceso permitido: cliente consulta sus reservas | GET | `/api/v1/reservations/reservations/my-upcoming/` | 200 | 200 | PASS | reservas_proximas=0 |
| RW09 | RQF-AUT-08 | Acceso prohibido: cliente hacia panel administrativo | GET | `/api/v1/reports/dashboard/summary/` | 403 | 403 | PASS |  |
| RW10 | RQF-RES-01 | Consulta del catalogo de espacios | GET | `/api/v1/reservations/spaces/` | 200 | 200 | PASS | 10 espacios |
| RW11 | RQF-RES-02 | Consulta de disponibilidad de un espacio | GET | `/api/v1/reservations/spaces/2/availability/?date=2026-10-28` | 200 | 200 | PASS | espacio=CANCHA-BASKET-01 fecha=2026-10-28 franjas_libres=32 |
| RW12 | RQF-RES-03 | Creacion real de una reserva | POST | `/api/v1/reservations/reservations/` | 201 | 201 | PASS | id=4 estado=CONFIRMED total=40000.00 |
| RW13 | RQF-RES-04 | Consulta posterior de la reserva creada | GET | `/api/v1/reservations/reservations/4/` | 200 | 200 | PASS | estado=CONFIRMED |
| RW14 | RQF-RES-05 | Rechazo de una reserva solapada | POST | `/api/v1/reservations/reservations/` | 400 | 400 | PASS | respuesta={'detail': "['Conflicto: Espacio no disponible en horario solicitado']"} |
| RW15 | RNF-ERR-01 | Error 400 controlado (duracion invalida) | POST | `/api/v1/reservations/reservations/` | 400 | 400 | PASS |  |
| RW16 | RNF-ERR-02 | Error 401 sin credenciales | GET | `/api/v1/reservations/reservations/` | 401 | 401 | PASS |  |
| RW17 | RNF-ERR-03 | Error 404 sobre recurso inexistente | GET | `/api/v1/reservations/spaces/99999999/` | 404 | 404 | PASS |  |
| RW18 | RQF-AUT-09 | Refresco de token de acceso | POST | `/api/v1/auth/token/refresh/` | 200 | 200 | PASS | nuevo access=eyJhbGciOi...I0Dg (551 car.) |
| RW19 | RQF-RES-06 | Cancelacion de la reserva de prueba | POST | `/api/v1/reservations/reservations/4/cancel/` | 200 | 200 | PASS | estado final=CANCELLED |
| RW20 | RQF-BDI-01 | Persistencia verificada en una sesion nueva (nueva autenticacion) | GET | `/api/v1/reservations/reservations/4/` | 200 | 200 | PASS | estado en BD=CANCELLED sesion_nueva_token=eyJhbGciOi...iWOA (562 car.) |

## Comandos de reproduccion

```powershell
cd c:\Family_Health_MF
$env:FH_PASS_ADMIN="<contrasena demo admin>";$env:FH_PASS_RECEPCION="<...>";
$env:FH_PASS_CAFETERIA="<...>";$env:FH_PASS_CLIENTE1="<...>";$env:FH_PASS_CLIENTE2="<...>"
.venv\Scripts\python.exe tests\railway_validation.py
```

## Nota sobre datos de prueba

La reserva creada durante esta validacion se identifica con la nota
`VALIDACION RAILWAY - dato de prueba controlado` y se cancela al final del
propio script (caso RW19), por lo que no queda ocupando disponibilidad real.
