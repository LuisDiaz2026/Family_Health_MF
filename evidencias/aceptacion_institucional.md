# Aceptación institucional y validación del prototipo - Club Family Health MF

> Cierre técnico de la versión final · respuesta a la recomendación del jurado:
> «Fortalecer las evidencias de aceptación institucional. Conviene adjuntar el acta
> firmada y distinguir la aceptación del prototipo de la validación por usuarios.»

- **Proyecto:** Club Family Health MF (trabajo de grado, Universidad Antonio Nariño).
- **Autor:** Luis Fermín Díaz Choles.
- **Versión evaluada:** despliegue de Railway `https://familyhealthmf-production.up.railway.app`.
- **Commit de referencia (trazabilidad del software):** `d0be182`
  (corrección funcional previa registrada en `0e46926`).
- **Fecha de elaboración de este documento:** 2026-11-19.

## 1. Dos conceptos que NO deben confundirse

Este documento separa de forma explícita dos cosas distintas que el jurado pidió
diferenciar:

| | **A. Aceptación del prototipo** | **B. Validación por usuarios** |
|---|---|---|
| **Qué es** | El sistema cumple los requisitos funcionales y técnicos verificados | Personas reales usan el sistema y valoran usabilidad y satisfacción |
| **Naturaleza de la evidencia** | Técnica, objetiva y **reproducible** | Perceptual, subjetiva y **dependiente de participantes** |
| **Cómo se obtiene** | Pruebas automatizadas, peticiones HTTP y mediciones contra el despliegue | Instrumento aplicado a personas (escala 1-5) |
| **Estado en esta entrega** | **Ejecutado** (12 verificaciones técnicas) | **Pendiente / fase complementaria** |
| **Qué certifica** | Que el prototipo funciona y cumple lo especificado | Que las personas lo perciben fácil, claro y satisfactorio |

La **aceptación del prototipo** es lo que se certifica en este documento. La
**validación por usuarios** se documenta como **fase complementaria** (sección 7),
porque requiere participantes reales y no puede simularse sin perder validez.

## 2. Estado actual de la aceptación

- **Aceptación del prototipo (A):** sustentada por **12 verificaciones técnicas**
  ejecutadas contra la versión desplegada (sección 3). Resultado global: **CUMPLE**.
- **Validación por usuarios (B):** **no realizada con personas**. Existe un
  instrumento listo para aplicarse (`evidencias/instrumento_evaluacion_usuarios.md`)
  y una simulación de recorrido con perfiles sintéticos
  (`evidencias/simulacion_aceptacion.md`) que **NO** sustituye la medición con personas.
- **Acta de constancia institucional:** modelo listo para firma (sección 6). Estado:
  **pendiente de firma real** por parte del representante del club.

## 3. Evidencia consolidada de la aceptación del prototipo (R1-R12)

Cada verificación es **reproducible** y se apoya en una evidencia archivada en
`evidencias/` y en el script que la genera en `tests/`. Todas corresponden al commit
`d0be182`.

| # | Verificación técnica | Evidencia | Resultado |
|---|---|---|---|
| R1 | Pruebas unitarias del backend (32 casos) | `evidencias/pruebas_unitarias.*` · `tests/unit/*` | 32/32 aprobadas |
| R2 | Pruebas de integración de flujos (12 casos) | `evidencias/pruebas_integracion.*` · `tests/integration/*` | 12/12 aprobadas |
| R3 | Pruebas de humo contra el despliegue | `evidencias/smoke_tests_raw.txt` | Aprobadas |
| R4 | Métricas de operación (M01-M42) | `evidencias/metricas_operacion_real.*` · `tests/metricas_operacion.py` | 42 indicadores medidos |
| R5 | Validación funcional en Railway (casos RW) | `evidencias/validacion_railway.*` · `tests/railway_validation.py` | Aprobadas |
| R6 | Benchmark controlado de escenarios operativos (S1-S4) | `evidencias/benchmark_aplicativo.*` · `tests/benchmark_aplicativo.py` | 30 iteraciones por escenario |
| R7 | Verificación de seguridad (SEC-01 a SEC-12) | `evidencias/verificacion_seguridad.*` · `tests/verificacion_seguridad.py` | 12/12 controles CUMPLE |
| R8 | Cierre del control SEC-10 (dobles evidencia, borde + aplicación) | `evidencias/verificacion_hosts.*` · `tests/verificacion_hosts.py` | CUMPLE |
| R9 | Concurrencia del anti-solapamiento de reservas | `evidencias/concurrencia_reservas.*` · `tests/concurrencia_reservas.py` | 1 aceptada / 9 rechazadas · PASS |
| R10 | Indicadores de impacto del sistema (I-01 a I-04) | `evidencias/indicadores_impacto.*` · `tests/indicadores_impacto.py` | Calculados (I-04 pendiente) |
| R11 | Comprobación mobile-first | `evidencias/mobile_first.*` | Sin incidencias técnicas |
| R12 | Simulación de recorrido de tareas (6 perfiles sintéticos, 68 tareas) | `evidencias/simulacion_aceptacion.*` · `tests/simulacion_aceptacion.py` | 68/68 tareas completadas (evidencia funcional) |

> **Advertencia metodológica (R12):** los recorridos con **identidades sintéticas**
> son **evidencia funcional** (demuestran que las tareas pueden completarse en el
> sistema), **no** pruebas de usabilidad con personas. Las puntuaciones subjetivas de
> `simulacion_aceptacion.*` están etiquetadas como **SIMULADAS** y no se presentan
> como medición de usuarios reales.

## 4. Indicadores de impacto (línea base)

En respuesta a la recomendación de «establecer indicadores para medir el impacto»,
la versión final mide cuatro familias (`evidencias/indicadores_impacto.md`):

| ID | Indicador | Estado |
|---|---|---|
| I-01 | Tiempo de confirmación de reservas | Aproximado (cota superior; falta `approved_at`) |
| I-02 | Conflictos de programación (solapamientos) | Calculable |
| I-03 | Cancelaciones (número y tasa) | Calculable |
| I-04 | Satisfacción de los usuarios | Pendiente (requiere usuarios reales) |

Estos valores son una **línea base**, no un estudio longitudinal. **No** se atribuye
ningún porcentaje de mejora frente a métodos manuales (WhatsApp, planillas): esa
conclusión exigiría un diseño de medición con volumen y periodo comparables.

## 5. Criterios de aceptación verificables (C1-C6)

El prototipo se considera **aceptado** si se cumplen todos los criterios siguientes;
cada uno es verificable con las evidencias de la sección 3.

| # | Criterio de aceptación | Verificación | Estado |
|---|---|---|---|
| C1 | El sistema está desplegado y disponible (health check HTTP 200) | SEC-01 / R5 | Cumple |
| C2 | La reserva de espacios funciona con anti-solapamiento (incluso en concurrencia) | R6 / R9 | Cumple |
| C3 | El control de acceso por roles es efectivo (401/403 y permisos) | SEC-08, SEC-09, RBAC / R7 | Cumple |
| C4 | Los controles de seguridad (SEC-01 a SEC-12) se cumplen | R7 / R8 | Cumple |
| C5 | Los indicadores de operación son medibles sobre datos reales | R4 / R10 | Cumple |
| C6 | La interfaz mobile-first opera sin incidencias técnicas | R11 | Cumple |

**Resultado global de aceptación del prototipo: CUMPLE (6/6 criterios).**

## 6. Modelo de acta de constancia (lista para firma)

> El texto siguiente reproduce el modelo `05_MODELO_CONSTANCIA_ACEPTACION_FAMILY_HEALTH`.
> Los campos entre corchetes deben completarse antes de la firma.

**ACTA DE CONSTANCIA DE ACEPTACIÓN DEL PROTOTIPO**

En [ciudad], a los [día] días del mes de [mes] de [año], el/la suscrito(a)
[NOMBRE DEL REPRESENTANTE], identificado(a) con documento [N° DE DOCUMENTO], en
calidad de [CARGO] del [NOMBRE DEL CLUB], hace constar que:

1. Recibió y probó el sistema **Club Family Health MF** desplegado en
   `https://familyhealthmf-production.up.railway.app`, correspondiente al trabajo de
   grado de **Luis Fermín Díaz Choles**.
2. Verificó que el sistema permite gestionar usuarios, espacios y reservas, con
   control de acceso por roles y anti-solapamiento de horarios.
3. La comprobación se apoyó en la evidencia técnica `evidencias/` (12 verificaciones,
   sección 3 de este documento) y en la ejecución directa del prototipo.
4. Esta constancia certifica la **aceptación del prototipo** (cumplimiento funcional
   y técnico). **No** constituye una medición de usabilidad con usuarios finales.

Para constancia, se firma:

_____________________________
[NOMBRE DEL REPRESENTANTE] · [CARGO] · [CLUB]

## 7. Fase complementaria de validación por usuarios (B - pendiente)

Para completar la validación por usuarios se propone:

1. Aplicar el instrumento de una página (`evidencias/instrumento_evaluacion_usuarios.md`)
   a una muestra de usuarios reales del club (al menos un usuario por rol).
2. Registrar las respuestas en el CSV `evidencias/instrumento_evaluacion_usuarios.csv`.
3. Reportar los resultados como **medición real** (facilidad, claridad y satisfacción
   en escala 1-5), diferenciándolos de las puntuaciones **simuladas** de R12.

Mientras esta fase no se ejecute, el indicador **I-04** permanece **Pendiente** y no
se presentan valores de satisfacción como si fueran reales.

## 8. Qué NO certifica este documento

- **No** certifica pruebas de usabilidad con personas (R12 usa perfiles sintéticos).
- **No** certifica mejoras porcentuales frente a WhatsApp o planillas.
- **No** certifica una medición longitudinal de impacto (sólo una línea base).
- **No** sustituye el acta firmada: la sección 6 es un **modelo pendiente de firma**.

## 9. Trazabilidad

| Elemento | Referencia |
|---|---|
| Software evaluado | commit `d0be182` (corrección funcional `0e46926`) |
| Evidencia técnica | carpeta `evidencias/` (scripts reproducibles en `tests/`) |
| Observación del jurado atendida | J1-05 (adjuntar acta firmada y distinguir aceptación de validación por usuarios) |
| Paquete de software | `08_SOFTWARE_FAMILY_HEALTH_MF_FINAL.zip` (generado con `git archive` del commit final) |
