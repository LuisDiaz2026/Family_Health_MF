# Prueba de concurrencia del anti-solapamiento de reservas

> Family Health MF - cierre tecnico de la version final (bloque 2)

- **URL evaluada:** https://familyhealthmf-production.up.railway.app
- **Fecha/hora (UTC):** 2026-11-19T14:16:22+00:00
- **Solicitudes simultaneas (N):** 10
- **Clientes:** cliente1_fh, cliente2_fh
- **Espacio en disputa:** CANCHA-BASKET-01 (id=2)
- **Franja en disputa:** `2026-11-22T07:00:00-05:00` -> `2026-11-22T08:00:00-05:00`

## Objetivo

Comprobar que, cuando **varias solicitudes piden el MISMO espacio en la
MISMA franja al mismo tiempo**, el sistema acepta **una sola** reserva y
rechaza el resto, sin generar duplicados en la base de datos. A diferencia
del smoke test (que valida el solapamiento de forma secuencial), aqui las
peticiones se lanzan en paralelo mediante hilos y una barrera de
sincronizacion.

## Resultado

- **Aceptadas (HTTP 201):** 1
- **Rechazadas por conflicto (HTTP 400):** 9
- **Otras respuestas:** 0
- **Reservas activas en BD que solapan la franja:** 1
- **Veredicto:** **PASS**

## Peticiones simultaneas

| # | Usuario | HTTP | Segundos | Reserva id | Detalle |
|---|---|---|---|---|---|
| 0 | cliente1_fh | 400 | 0.3585 | - | `{"detail":"['Conflicto: Espacio no disponible en horario solicitado']"}` |
| 1 | cliente2_fh | 400 | 0.3559 | - | `{"detail":"['Conflicto: Espacio no disponible en horario solicitado']"}` |
| 2 | cliente1_fh | 400 | 0.3755 | - | `{"detail":"['Conflicto: Espacio no disponible en horario solicitado']"}` |
| 3 | cliente2_fh | 400 | 0.3728 | - | `{"detail":"['Conflicto: Espacio no disponible en horario solicitado']"}` |
| 4 | cliente1_fh | 201 | 0.3498 | 85 | `{"id":85,"space":{"id":2,"code":"CANCHA-BASKET-01","name":"Cancha de Baloncesto","space_type_name":"Canchas Deportivas",` |
| 5 | cliente2_fh | 400 | 0.3709 | - | `{"detail":"['Conflicto: Espacio no disponible en horario solicitado']"}` |
| 6 | cliente1_fh | 400 | 0.3838 | - | `{"detail":"['Conflicto: Espacio no disponible en horario solicitado']"}` |
| 7 | cliente2_fh | 400 | 0.3775 | - | `{"detail":"['Conflicto: Espacio no disponible en horario solicitado']"}` |
| 8 | cliente1_fh | 400 | 0.3815 | - | `{"detail":"['Conflicto: Espacio no disponible en horario solicitado']"}` |
| 9 | cliente2_fh | 400 | 0.3696 | - | `{"detail":"['Conflicto: Espacio no disponible en horario solicitado']"}` |

## Verificacion en la base de datos

Consultando la disponibilidad del espacio tras la prueba, las reservas
activas (PENDING/CONFIRMED) que solapan la franja son **1**.

| Reserva id | Estado | Inicio | Fin |
|---|---|---|---|
| 85 | CONFIRMED | 2026-11-22T12:00:00Z | 2026-11-22T13:00:00Z |

## Limpieza

La reserva aceptada durante la prueba se cancela al final del script para
no dejar ocupada la franja:

- reserva id=85 -> cancelacion HTTP 200

## Reproduccion

```powershell
cd c:\Family_Health_MF
$env:FH_PASS_ADMIN="<contrasena demo admin>"
$env:FH_PASS_CLIENTE1="<contrasena demo cliente1>"
$env:FH_PASS_CLIENTE2="<contrasena demo cliente2>"
.venv\Scripts\python.exe tests\concurrencia_reservas.py 10
```

## Nota metodologica

Los codigos HTTP son los que el servicio devolvio realmente. La prueba
crea y luego cancela una reserva identificada con la nota
`CONCURRENCIA - dato de prueba controlado (se cancela al final)`. La proteccion se apoya en `SELECT ... FOR UPDATE` sobre
el espacio dentro de una transaccion (`Reservation.save`) mas la validacion
`Space.is_available_at`.
