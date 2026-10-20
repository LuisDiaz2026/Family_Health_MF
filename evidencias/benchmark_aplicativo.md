# Benchmark controlado del aplicativo

> Family Health MF · cierre tecnico de la version final · punto 7

- **Version evaluada:** despliegue de Railway `https://familyhealthmf-production.up.railway.app`
- **Fecha/hora (UTC):** 2026-10-20T04:25:17+00:00
- **Escenarios ejecutados:** 4
- **Iteraciones por escenario:** 30
- **Espacio utilizado:** `CANCHA-BASKET-01` (id=2)
- **Franja aislada de prueba:** 2027-02-16 03:00 en adelante (America/Bogota)
- **Reservas de prueba creadas y eliminadas:** 30 (fallos de limpieza: 0)

Todos los tiempos son mediciones reales obtenidas con el reloj monotono
(`time.perf_counter`) sobre peticiones HTTP reales contra la API desplegada.
No se declara ningun resultado que no provenga de una ejecucion efectiva.

## Resumen

| Escenario | n | Media (ms) | Mediana (ms) | Min (ms) | Max (ms) | Desv. (ms) | Exito % | Conflictos persistidos % | Resolucion 1er intento % | Reprocesos tecnicos | Linea base manual |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S1_consultar_disponibilidad | 30 | 328.47 | 320.18 | 303.7 | 559.14 | 44.23 | 100.0 | 0.0 | 100.0 | 0 | (no proporcionada) |
| S2_registrar_reserva | 30 | 331.75 | 331.16 | 314.33 | 355.3 | 9.4 | 100.0 | 0.0 | 100.0 | 0 | (no proporcionada) |
| S3_detectar_solapamiento | 30 | 320.77 | 319.68 | 304.42 | 349.72 | 11.3 | 100.0 | 0.0 | 100.0 | 0 | (no proporcionada) |
| S4_cancelar_reserva | 30 | 327.49 | 323.75 | 310.57 | 352.4 | 10.96 | 100.0 | 0.0 | 100.0 | 0 | (no proporcionada) |

## Correspondencia con los indicadores solicitados

| Indicador solicitado | Escenario que lo mide |
|---|---|
| Tiempo para consultar disponibilidad | `S1_consultar_disponibilidad` |
| Tiempo para registrar una reserva | `S2_registrar_reserva` |
| Tiempo hasta confirmacion/rechazo | `S2_registrar_reserva` (lectura posterior del estado) |
| Numero de verificaciones necesarias | 1 lectura de verificacion por reserva |
| Conflictos persistidos | `S3_detectar_solapamiento` |
| Reprocesos tecnicos | columna `reprocesos_tecnicos` (0 = ningun reintento) |
| Resolucion en primer intento | `resolucion_primer_intento_pct` |

## Notas metodologicas

- Los tiempos incluyen la latencia de red real entre el equipo de medicion y
  el despliegue de Railway, por lo que representan el tiempo percibido por el
  usuario final.
- La franja `03:00` sobre una fecha a 120 dias se eligio para aislar los datos
  de prueba de la operacion real; todas las reservas creadas se eliminan al
  terminar (`DELETE` con rol administrador) y se verifica que no queden restos.
- La columna `linea_base_manual` queda vacia a proposito: no se inventan
  valores de la linea base manual.

## Comandos de reproduccion

```powershell
cd c:\Family_Health_MF
$env:BENCH_ITERS="30"
.venv\Scripts\python.exe tests\benchmark_aplicativo.py
```

- Detalle por iteracion: `evidencias/benchmark_iteraciones.csv`