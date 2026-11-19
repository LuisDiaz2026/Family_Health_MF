# Indicadores de impacto del sistema - Club Family Health MF

> Cierre tecnico de la version final · respuesta a la recomendacion del jurado
> ("Establecer indicadores para medir el impacto del sistema").

- **Fuente:** API publica de la version desplegada (https://familyhealthmf-production.up.railway.app) consultada con
  credenciales de administrador; la API lee directamente de PostgreSQL.
- **Fecha/hora de la consulta (UTC):** 2026-11-19T14:16:21+00:00

## Naturaleza de los datos (leer antes de interpretar)

- Reservas registradas en la base productiva a la fecha de consulta: **8**.
- De ellas, **2** no corresponden a datos de prueba controlados y **6** si (identificadas por su nota).
- El **volumen observado es bajo**: estos valores son una **linea base**, no un
  estudio longitudinal. Por si solos NO permiten afirmar mejoras frente al
  procedimiento manual; para ello el club debe acumular registros suficientes.
- Los indicadores se presentan en dos conjuntos: **Todos** (base completa) y
  **Operativas** (excluye datos de prueba controlados).

## Marco de indicadores (lo solicitado por el jurado)

| ID | Indicador | Definicion | Fuente / registro | Estado |
|---|---|---|---|---|
| I-01 | Tiempo de confirmacion de reservas | Tiempo entre la solicitud y la confirmacion | `created_at` y `updated_at` | **Aproximado** |
| I-02 | Conflictos de programacion | Reservas activas que se solapan en el mismo espacio | Enumeracion de reservas (PENDING/CONFIRMED) | **Calculable** |
| I-03 | Cancelaciones | Numero y tasa de reservas canceladas | `status=CANCELLED` | **Calculable** |
| I-04 | Satisfaccion de los usuarios | Facilidad, claridad y satisfaccion (1-5) | Instrumento con personas reales | **Pendiente** |

## Resultados reales a la fecha de consulta

| Conjunto | Reservas | Activas | Canceladas (tasa) | Confirmadas | n tiempo | Mediana tiempo (min) | Conflictos persistidos |
|---|---|---|---|---|---|---|---|
| **Todos** | 8 | 0 | 8 (100.0%) | 0 | 0 | N/D | 0 |
| **Operativas** | 2 | 0 | 2 (100.0%) | 0 | 0 | N/D | 0 |

**Lectura:**
- **I-01:** tiempo de confirmacion observado como **cota superior** (`updated_at - created_at`). Conjunto operativo: n=0.
- **I-02:** conflictos persistidos = **0** (todos) y **0** (operativas).
- **I-03:** tasa de cancelacion = **100.0%** (todos) y **100.0%** (operativas).
- **I-04:** NO CALCULABLE con datos del sistema; requiere participantes reales.

## Detalle por indicador

### I-01 - Tiempo de confirmacion de reservas

- **Definicion:** tiempo entre la creacion de la solicitud y su confirmacion.
- **Como se calcula:** `updated_at - created_at` para reservas confirmadas/completadas.
- **Limitacion declarada:** la version final NO almacena una marca temporal
  explicita de aprobacion (`approved_at`). Para reservas sin aprobacion la
  confirmacion es inmediata (misma transaccion de creacion), de modo que el
  valor es ~0. Para reservas que exigieron aprobacion, `updated_at` es una
  **cota superior** (puede incluir otras modificaciones posteriores).
- **Resultado:** confirmadas/completadas en la base = 0 (con aprobacion registrada: 0); por eso n de tiempo = 0.

### I-02 - Conflictos de programacion

- **Definicion:** numero de reservas activas (PENDING/CONFIRMED) que se solapan
  en el mismo espacio y franja horaria.
- **Como se calcula:** comparacion por pares de las reservas activas enumeradas.
- **Resultado real:** **0** conflictos persistidos.
  La integridad se garantiza por el anti-solapamiento en la transaccion de
  creacion (validacion + `select_for_update` sobre el espacio).
- **Intentos de solapamiento rechazados:** se miden en pruebas controladas
  (no quedan registrados en la base porque la solicitud se rechaza). Evidencia:
  `evidencias/benchmark_aplicativo.md` (30 intentos, 30 rechazos) y
  `evidencias/validacion_railway.md` (1 intento, 1 rechazo).

### I-03 - Cancelaciones

- **Definicion:** numero y proporcion de reservas canceladas respecto al total.
- **Resultado real:** 8 canceladas de 8 (tasa 100.0%). Conjunto operativo: 2 de 2 (tasa 100.0%).
- **Nota:** el motivo de cancelacion se registra cuando el usuario lo informa.

### I-04 - Satisfaccion de los usuarios

- **Definicion:** facilidad percibida, claridad y satisfaccion general (escala 1-5).
- **Estado:** **pendiente**. No se puede derivar del sistema; requiere aplicar el
  instrumento a participantes reales (`evidencias/instrumento_evaluacion_usuarios.md`).
- **Advertencia:** las puntuaciones de `evidencias/simulacion_aceptacion.*` son
  **simuladas** y NO sustituyen esta medicion con personas.

## Ejecutado vs. Planificado

| Indicador | Estado | Comentario |
|---|---|---|
| I-01 Tiempo de confirmacion | Aproximado (Ejecutado) | Medible hoy como cota superior; requeriria `approved_at` para ser exacto. |
| I-02 Conflictos de programacion | Ejecutado | Se verifica que no haya conflictos persistidos. |
| I-03 Cancelaciones | Ejecutado | Calculable a partir del estado de las reservas. |
| I-04 Satisfaccion | Planificado (Pendiente) | Requiere usuarios reales; instrumento ya disenado. |

## Como el club determina mejoras (sin atribuciones sin sustento)

Estos indicadores establecen una **linea base medible**. El club podra comparar
periodos futuros contra esta base cuando existan **registros suficientes**. No se
atribuye ningun porcentaje de mejora frente a WhatsApp o planillas: esa conclusion
requiere un diseno de medicion con volumen y periodo comparables.

## Comandos de reproduccion

```powershell
cd c:\Family_Health_MF
$env:FH_PASS_ADMIN="<contrasena demo admin>"
.venv\Scripts\python.exe tests\indicadores_impacto.py
```
