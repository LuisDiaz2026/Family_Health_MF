# Evaluacion SIMULADA de aceptacion y usabilidad (usuarios sinteticos)

> Family Health MF - 2 usuarios sinteticos por rol (6 en total).
> NO participaron personas reales: las sesiones las ejecuto un script.

- **URL evaluada:** https://familyhealthmf-production.up.railway.app
- **Fecha/hora (UTC):** 2026-10-21T02:22:26+00:00
- **Sesiones simuladas:** 6
- **Tareas ejecutadas:** 68
- **Tareas completadas:** 68 (100.0 %)
- **Requisitos cubiertos:** 25

## Advertencia de naturaleza de los datos

Los tiempos, codigos HTTP, errores y resultados SON REALES (medidos
contra el despliegue). Las puntuaciones de **facilidad, claridad y
satisfaccion (1-5) son SIMULADAS**: se derivan de un modelo determinista
(base 5 para competencia Intermedia y 4 para Basica, con penalizacion por
errores y tareas no completadas). **No son opiniones de usuarios reales y
no deben presentarse como tal.**

## Resumen por sesion simulada

| Usuario | Rol | Competencia | Tareas | Completadas | Efectividad % | Tiempo real (s) | Tiempo simulado (s) | Facilidad* | Claridad* | Satisfaccion* |
|---|---|---|---|---|---|---|---|---|---|---|
| SIM-CLI-A | CLIENT | Intermedia | 13 | 13 | 100.0 | 4.9 | 49.89 | 5.0 | 4.77 | 4.77 |
| SIM-CLI-B | CLIENT | Basica | 13 | 13 | 100.0 | 5.61 | 95.61 | 4.0 | 3.77 | 4.0 |
| SIM-REC-A | RECEPCION | Intermedia | 10 | 10 | 100.0 | 3.21 | 33.21 | 5.0 | 4.8 | 4.8 |
| SIM-REC-B | RECEPCION | Basica | 10 | 10 | 100.0 | 3.25 | 63.25 | 4.0 | 3.8 | 4.0 |
| SIM-ADM-A | ADMIN | Intermedia | 11 | 11 | 100.0 | 4.27 | 40.26 | 5.0 | 4.91 | 4.91 |
| SIM-ADM-B | ADMIN | Basica | 11 | 11 | 100.0 | 4.18 | 76.18 | 4.0 | 3.91 | 4.0 |

\* Puntuaciones simuladas (ver advertencia).

## Detalle de tareas ejecutadas

| Usuario | ID | Requisito | Descripcion | HTTP | Completada | Interacciones | Duracion real (s) | Errores |
|---|---|---|---|---|---|---|---|---|
| SIM-CLI-A | C01 | RQF-AUT-01 | Iniciar sesion como cliente | 200 | SI | 1 | 0.353 | 0 |
| SIM-CLI-A | C02 | RQF-AUT-06 | Consultar su propio perfil | 200 | SI | 1 | 0.301 | 0 |
| SIM-CLI-A | C03 | RQF-ESP-01 | Consultar el catalogo de espacios | 200 | SI | 1 | 0.321 | 0 |
| SIM-CLI-A | C04 | RQF-ESP-03 | Consultar disponibilidad de un espacio | 200 | SI | 1 | 0.321 | 0 |
| SIM-CLI-A | C05 | RQF-RES-01 | Crear una reserva (espacio sin aprobacion) | 201 | SI | 2 | 0.668 | 0 |
| SIM-CLI-A | C06 | RQF-RES-02 | Crear reserva en espacio que requiere aprobacion | 201 | SI | 2 | 0.657 | 0 |
| SIM-CLI-A | C07 | RQF-RES-16 | Consultar todas sus reservas (todos los estados) | 200 | SI | 1 | 0.306 | 0 |
| SIM-CLI-A | C08 | RQF-RES-11 | Consultar sus reservas proximas | 200 | SI | 1 | 0.314 | 0 |
| SIM-CLI-A | C09 | RQF-RES-07 | Intento de solapamiento (debe rechazarse) | 400 | SI | 1 | 0.321 | 0 |
| SIM-CLI-A | C10 | RNF-ERR-01 | Validacion de datos invalidos (400) | 400 | SI | 1 | 0.328 | 0 |
| SIM-CLI-A | C11 | RQF-RES-06 | Cancelar una reserva propia | 200 | SI | 1 | 0.348 | 0 |
| SIM-CLI-A | C12 | RQF-AUT-08 | Verificar bloqueo del panel administrativo | 403 | SI | 1 | 0.336 | 0 |
| SIM-CLI-A | C13 | RQF-AUT-04 | Refrescar el token de acceso | 200 | SI | 1 | 0.32 | 0 |
| SIM-CLI-B | C01 | RQF-AUT-01 | Iniciar sesion como cliente | 200 | SI | 1 | 0.497 | 0 |
| SIM-CLI-B | C02 | RQF-AUT-06 | Consultar su propio perfil | 200 | SI | 1 | 0.325 | 0 |
| SIM-CLI-B | C03 | RQF-ESP-01 | Consultar el catalogo de espacios | 200 | SI | 1 | 0.344 | 0 |
| SIM-CLI-B | C04 | RQF-ESP-03 | Consultar disponibilidad de un espacio | 200 | SI | 1 | 0.31 | 0 |
| SIM-CLI-B | C05 | RQF-RES-01 | Crear una reserva (espacio sin aprobacion) | 201 | SI | 2 | 0.95 | 0 |
| SIM-CLI-B | C06 | RQF-RES-02 | Crear reserva en espacio que requiere aprobacion | 201 | SI | 2 | 0.95 | 0 |
| SIM-CLI-B | C07 | RQF-RES-16 | Consultar todas sus reservas (todos los estados) | 200 | SI | 1 | 0.32 | 0 |
| SIM-CLI-B | C08 | RQF-RES-11 | Consultar sus reservas proximas | 200 | SI | 1 | 0.314 | 0 |
| SIM-CLI-B | C09 | RQF-RES-07 | Intento de solapamiento (debe rechazarse) | 400 | SI | 1 | 0.313 | 0 |
| SIM-CLI-B | C10 | RNF-ERR-01 | Validacion de datos invalidos (400) | 400 | SI | 1 | 0.308 | 0 |
| SIM-CLI-B | C11 | RQF-RES-06 | Cancelar una reserva propia | 200 | SI | 1 | 0.341 | 0 |
| SIM-CLI-B | C12 | RQF-AUT-08 | Verificar bloqueo del panel administrativo | 403 | SI | 1 | 0.319 | 0 |
| SIM-CLI-B | C13 | RQF-AUT-04 | Refrescar el token de acceso | 200 | SI | 1 | 0.315 | 0 |
| SIM-REC-A | R01 | RQF-AUT-01 | Iniciar sesion como recepcion | 200 | SI | 1 | 0.362 | 0 |
| SIM-REC-A | R02 | RQF-RES-12 | Listar las reservas del club | 200 | SI | 1 | 0.332 | 0 |
| SIM-REC-A | R03 | RQF-USR-05 | Listar clientes del club | 200 | SI | 1 | 0.322 | 0 |
| SIM-REC-A | R04 | RQF-RES-13 | Aprobar una reserva pendiente | 200 | SI | 1 | 0.321 | 0 |
| SIM-REC-A | R05 | RQF-RES-15 | Registrar el pago de una reserva | 200 | SI | 1 | 0.337 | 0 |
| SIM-REC-A | R06 | RQF-ESP-03 | Consultar disponibilidad de espacios | 200 | SI | 1 | 0.299 | 0 |
| SIM-REC-A | R07 | RQF-ESP-04 | Validar fecha invalida en disponibilidad | 400 | SI | 1 | 0.315 | 0 |
| SIM-REC-A | R08 | RNF-ERR-03 | Consultar un recurso inexistente (404) | 404 | SI | 1 | 0.309 | 0 |
| SIM-REC-A | R09 | RQF-AUT-04 | Refrescar el token de acceso | 200 | SI | 1 | 0.316 | 0 |
| SIM-REC-A | R10 | RQF-AUT-05 | Cerrar sesion | 200 | SI | 1 | 0.299 | 0 |
| SIM-REC-B | R01 | RQF-AUT-01 | Iniciar sesion como recepcion | 200 | SI | 1 | 0.362 | 0 |
| SIM-REC-B | R02 | RQF-RES-12 | Listar las reservas del club | 200 | SI | 1 | 0.346 | 0 |
| SIM-REC-B | R03 | RQF-USR-05 | Listar clientes del club | 200 | SI | 1 | 0.314 | 0 |
| SIM-REC-B | R04 | RQF-RES-13 | Aprobar una reserva pendiente | 200 | SI | 1 | 0.305 | 0 |
| SIM-REC-B | R05 | RQF-RES-15 | Registrar el pago de una reserva | 200 | SI | 1 | 0.318 | 0 |
| SIM-REC-B | R06 | RQF-ESP-03 | Consultar disponibilidad de espacios | 200 | SI | 1 | 0.325 | 0 |
| SIM-REC-B | R07 | RQF-ESP-04 | Validar fecha invalida en disponibilidad | 400 | SI | 1 | 0.313 | 0 |
| SIM-REC-B | R08 | RNF-ERR-03 | Consultar un recurso inexistente (404) | 404 | SI | 1 | 0.311 | 0 |
| SIM-REC-B | R09 | RQF-AUT-04 | Refrescar el token de acceso | 200 | SI | 1 | 0.324 | 0 |
| SIM-REC-B | R10 | RQF-AUT-05 | Cerrar sesion | 200 | SI | 1 | 0.331 | 0 |
| SIM-ADM-A | A01 | RQF-AUT-01 | Iniciar sesion como administrador | 200 | SI | 1 | 0.354 | 0 |
| SIM-ADM-A | A02 | RQF-AUT-04 | Consultar el panel de indicadores | 200 | SI | 1 | 0.328 | 0 |
| SIM-ADM-A | A03 | RQF-REP-01 | Reservas por fecha (reporte) | 200 | SI | 1 | 0.291 | 0 |
| SIM-ADM-A | A04 | RQF-REP-02 | Ingresos por mes (reporte) | 200 | SI | 1 | 0.312 | 0 |
| SIM-ADM-A | A05 | RQF-REP-03 | Clientes destacados (reporte) | 200 | SI | 1 | 0.331 | 0 |
| SIM-ADM-A | A06 | RQF-USR-03 | Listar y consultar usuarios del sistema | 200 | SI | 1 | 0.34 | 0 |
| SIM-ADM-A | A07 | RQF-RES-12 | Listar todas las reservas del club | 200 | SI | 1 | 0.331 | 0 |
| SIM-ADM-A | A08 | RQF-ESP-01 | Consultar el catalogo de espacios | 200 | SI | 1 | 0.338 | 0 |
| SIM-ADM-A | A09 | RQF-RES-14 | Rechazar una reserva pendiente | 200 | SI | 2 | 1.025 | 0 |
| SIM-ADM-A | A10 | RNF-ERR-03 | Consultar un recurso inexistente (404) | 404 | SI | 1 | 0.297 | 0 |
| SIM-ADM-A | A11 | RQF-AUT-04 | Refrescar el token de acceso | 200 | SI | 1 | 0.317 | 0 |
| SIM-ADM-B | A01 | RQF-AUT-01 | Iniciar sesion como administrador | 200 | SI | 1 | 0.365 | 0 |
| SIM-ADM-B | A02 | RQF-AUT-04 | Consultar el panel de indicadores | 200 | SI | 1 | 0.319 | 0 |
| SIM-ADM-B | A03 | RQF-REP-01 | Reservas por fecha (reporte) | 200 | SI | 1 | 0.32 | 0 |
| SIM-ADM-B | A04 | RQF-REP-02 | Ingresos por mes (reporte) | 200 | SI | 1 | 0.299 | 0 |
| SIM-ADM-B | A05 | RQF-REP-03 | Clientes destacados (reporte) | 200 | SI | 1 | 0.295 | 0 |
| SIM-ADM-B | A06 | RQF-USR-03 | Listar y consultar usuarios del sistema | 200 | SI | 1 | 0.347 | 0 |
| SIM-ADM-B | A07 | RQF-RES-12 | Listar todas las reservas del club | 200 | SI | 1 | 0.33 | 0 |
| SIM-ADM-B | A08 | RQF-ESP-01 | Consultar el catalogo de espacios | 200 | SI | 1 | 0.325 | 0 |
| SIM-ADM-B | A09 | RQF-RES-14 | Rechazar una reserva pendiente | 200 | SI | 2 | 0.961 | 0 |
| SIM-ADM-B | A10 | RNF-ERR-03 | Consultar un recurso inexistente (404) | 404 | SI | 1 | 0.311 | 0 |
| SIM-ADM-B | A11 | RQF-AUT-04 | Refrescar el token de acceso | 200 | SI | 1 | 0.305 | 0 |

## Requisitos cubiertos

RNF-ERR-01, RNF-ERR-03, RQF-AUT-01, RQF-AUT-04, RQF-AUT-05, RQF-AUT-06, RQF-AUT-08, RQF-ESP-01, RQF-ESP-03, RQF-ESP-04, RQF-REP-01, RQF-REP-02, RQF-REP-03, RQF-RES-01, RQF-RES-02, RQF-RES-06, RQF-RES-07, RQF-RES-11, RQF-RES-12, RQF-RES-13, RQF-RES-14, RQF-RES-15, RQF-RES-16, RQF-USR-03, RQF-USR-05

## Limpieza

Las cuentas y reservas creadas se marcan con el texto `SIMULACION ACEPTACION - dato de prueba controlado` y se eliminan en la fase de limpieza del script
(salvo que se ejecute con el argumento `sin-limpiar`).
