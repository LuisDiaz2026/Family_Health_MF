# CORRECCIONES FINALES — Noviembre 2026

> Resumen punto por punto de las correcciones atendidas tras la **Evaluación 1 del trabajo de grado** (jurados del 18 de noviembre de 2026).
>
> Proyecto: **Club Family Health MF** — implementación de un aplicativo web Mobile-First para la gestión centralizada de reservas.
> Autor: **Luis Fermín Díaz Choles** · Director: **Fabio González**.
> Documento fuente: `Evaluación 1 del trabajo de grado de Luis Fermín D_261118_161058.pdf`.

---

## 0. Datos de la evaluación (contexto)

| Campo | Valor |
|---|---|
| Instancia | Universidad Antonio Nariño — Facultad de Ingeniería de Sistemas — Comité Nacional de Trabajos de Grado |
| Fecha / lugar | 18 de noviembre de 2026 · Sede Bogotá Sur |
| Estudiante | Luis Fermín Díaz Choles |
| Título | *Implementación de un aplicativo web Mobile-First para la gestión centralizada de reservas en el Club Family Health, Maicao, La Guajira* |
| Modalidad | Desarrollo de software |
| Director | Fabio González |
| Concepto | El paso a sustentar queda **condicionado** a la realización de las correcciones solicitadas por los jurados |
| Participantes | Jorge Camargo (Decano), Juan Camilo Ramírez (Director UDCI), Carlos Henry López (Coordinador Académico), Ómar Torres (Profesor) |

El jurado reconoce el trabajo como **pertinente, técnicamente sólido y con aplicación práctica claramente identificada**. Las correcciones se concentran en tres frentes: *validación con usuarios*, *pruebas de concurrencia* y *correspondencia entre las pruebas ejecutadas y la versión final entregada*.

---

## Parte A — Observaciones del Jurado 1 (6 puntos)

### A.1 · Incorporar una validación práctica con usuarios reales

- **Qué solicitó el jurado:** el documento no demuestra todavía la experiencia de uso de administradores, recepción y clientes.
- **Qué se hizo:** la validación con **personas reales no estaba disponible dentro del alcance del trabajo**, por lo que NO se ejecutó con sujetos humanos. En su lugar se:
  1. documentó esta actividad como **fase complementaria** explícita (no como resultado obtenido);
  2. dejó **listo el instrumento** de evaluación de usuarios (escala 1-5) y el protocolo (Anexo J) para su aplicación futura;
  3. separó con total claridad la *aceptación del prototipo* (técnica) de la *validación por usuarios* (perceptual).
- **Evidencia:** `evidencias/aceptacion_institucional.md` (sección B), `evidencias/instrumento_evaluacion_usuarios.md`, `evidencias/instrumento_evaluacion_usuarios.csv`.
- **Estado:** **Pendiente / fase complementaria** — declarado de forma honesta. No se atribuyen puntuaciones de usabilidad a personas.

### A.2 · Fortalecer las pruebas de concurrencia

- **Qué solicitó el jurado:** los rechazos de reservas superpuestas no demuestran del todo el comportamiento ante **solicitudes simultáneas independientes**.
- **Qué se hizo:** se implementó y ejecutó el script reproducible `tests/concurrencia_reservas.py`, que lanza **N peticiones simultáneas reales** (barrera `threading.Barrier(n)`) contra el despliegue sobre **PostgreSQL en Railway**, cada una reservando el mismo espacio y la misma franja horaria.
- **Resultado (ejecución real):** 10 hilos → **1 aceptada / 9 rechazadas / 0 otras** · **PASS**.
- **Mecanismo verificado:** anti-solapamiento en tres niveles — `Space.is_available_at()` + `Reservation.save()` dentro de `transaction.atomic()` + `select_for_update()` sobre el `Space`.
- **Evidencia:** `tests/concurrencia_reservas.py`, `evidencias/concurrencia_reservas.json`, `evidencias/concurrencia_reservas.md`.
- **Estado:** **Ejecutado y verificado (PASS).**

### A.3 · Ejecutar y documentar las pruebas sobre la versión final

- **Qué solicitó el jurado:** el documento reconocía cambios funcionales posteriores a algunas suites de pruebas; había que garantizar la correspondencia entre las pruebas y la versión entregada.
- **Qué se hizo:** se **re-ejecutaron todas las suites críticas el 2026-11-19** contra el código de la versión final.
- **Ajuste adicional:** se detectó que la acción `POST /reservations/{id}/complete/` (finalización añadida en octubre) **no tenía un caso específico** en las suites. Se agregó el **caso de regresión U33 (RQF-RES-17)**, que verifica: (a) la transición CONFIRMED → COMPLETED con registro de `completed_at`; (b) la persistencia tras una nueva consulta; (c) el rechazo (HTTP 400) al intentar completar una reserva en estado no permitido; y (d) que un CLIENT no pueda invocar la acción administrativa (HTTP 403).
- **Resultados (reales, re-ejecutados):**
  - Pruebas **unitarias:** 33 / 33 PASS (incluye el nuevo U33).
  - Pruebas de **integración:** 12 / 12 PASS.
  - Pruebas de **humo:** 14 OK / 0 fallidos.
  - **HTTP contra Railway:** 20 / 20 PASS.
- **Evidencia:** `tests/unit/test_reservations.py` (caso U33), `evidencias/pruebas_unitarias.{csv,json,txt}`, `evidencias/pruebas_integracion.{csv,json,txt}`, `evidencias/smoke_tests_raw.txt`, `evidencias/validacion_railway.{json,md}`.
- **Estado:** **Ejecutado y documentado sobre la versión final.**

### A.4 · Completar la verificación de seguridad SEC-10

- **Qué solicitó el jurado:** uno de los doce controles de seguridad había quedado inconcluso.
- **Qué se hizo:** se cerró SEC-10 con **doble evidencia complementaria**:
  1. **Externa (borde de Railway):** un `Host` desconocido **no se enruta** (HTTP 404 "Application not found"); y las inyecciones por `X-Forwarded-Host` (casos E2–E4) producen la **misma respuesta** que el caso de control con host válido → quedan **neutralizadas**.
  2. **Local (aplicación Django):** con la `ALLOWED_HOSTS` de producción, la aplicación **rechaza** un host no autorizado (`DisallowedHost` → **HTTP 400**) y **acepta** el host válido.
- **Resultado:** **12 de 12 controles CUMPLE** (SEC-01 … SEC-12).
- **Evidencia:** `tests/verificacion_hosts.py`, `evidencias/verificacion_hosts.{json,md}`, `evidencias/checklist_seguridad.md` (tabla SEC-01…SEC-12 + sección "Cierre de SEC-10").
- **Estado:** **Ejecutado y cerrado (CUMPLE).**

### A.5 · Fortalecer las evidencias de aceptación institucional

- **Qué solicitó el jurado:** adjuntar el **acta firmada** y **distinguir la aceptación del prototipo** de la **validación por usuarios**.
- **Qué se hizo:** se elaboró un documento que:
  1. **separa los dos conceptos** (A. Aceptación del prototipo = técnica, objetiva y reproducible, **Ejecutada**; B. Validación por usuarios = perceptual, subjetiva, **Pendiente**);
  2. consolida la evidencia técnica R1–R12 ligada al commit de trazabilidad `d0be182`;
  3. define **criterios de aceptación C1–C6** (6 / 6 CUMPLE);
  4. incluye el **acta de constancia lista para firma** institucional.
- **Evidencia:** `evidencias/aceptacion_institucional.md`.
- **Estado:** **Documento elaborado**; el acta queda lista para firma del club.

### A.6 · Revisar la presentación final de tablas, figuras y anexos

- **Qué solicitó el jurado:** mejorar la legibilidad de algunos diagramas y **uniformar los soportes documentales**.
- **Qué se hizo:** se uniformaron los tres documentos (monografía, manual técnico y manual de usuario): **normas APA**, anuncio y descripción de cada **Figura y Tabla**, pie de imagen estandarizado **"Fuente: Elaboración propia, 2026"** y figuras ajustadas al ancho de página.
- **Evidencia:** monografía, manual técnico y manual de usuario de la entrega final.
- **Estado:** **Atendido.**

---

## Parte B — Sugerencias del Jurado 1 (3 puntos)

### B.1 · Realizar una prueba piloto con usuarios del Club Family Health

- **Sugerencia:** involucrar representantes de los tres perfiles (administrador, recepción, cliente) ejecutando tareas reales de consulta, creación y cancelación de reservas, registrando tiempos, errores y facilidad de uso (Anexo J como punto de partida).
- **Qué se hizo:** instrumento y protocolo **preparados** (los mismos de A.1), pero **no aplicados a personas reales** por limitación del alcance.
- **Estado:** **Pendiente / fase complementaria.**

### B.2 · Fortalecer la confiabilidad y la seguridad del aplicativo

- **Sugerencia:** ejecutar pruebas de **reservas simultáneas sobre PostgreSQL**, **completar SEC-10** y **repetir las pruebas críticas** sobre la versión definitiva.
- **Qué se hizo:** los tres puntos quedaron cubiertos → **A.2** (concurrencia PASS sobre PostgreSQL/Railway), **A.4** (SEC-10 CUMPLE, 12/12) y **A.3** (suites re-ejecutadas sobre la versión final).
- **Estado:** **Ejecutado y verificado.**

### B.3 · Establecer indicadores para medir el impacto del sistema

- **Sugerencia:** implementar seguimiento de indicadores: tiempo de confirmación de reservas, número de conflictos de programación, cancelaciones y satisfacción de los usuarios.
- **Qué se hizo:** se implementó el script `tests/indicadores_impacto.py`, que calcula **I-01 … I-04** a partir de los datos del sistema, distinguiendo el conjunto de reservas **operativas** del conjunto total (excluyendo las marcadas como dato de prueba controlado).
  - **I-01** Tiempo de confirmación · **I-02** Conflictos de programación · **I-03** Cancelaciones → **calculables** con los registros actuales.
  - **I-04** Satisfacción de los usuarios → **NO CALCULABLE** sin usuarios reales (se declara explícitamente).
- **Evidencia:** `tests/indicadores_impacto.py`, `evidencias/indicadores_impacto.{json,md}`.
- **Estado:** **Ejecutado** (I-04 pendiente por depender de personas).

---

## Parte C — Observaciones del Jurado 2 (por entregable)

> Nota del jurado: *todos los entregables deben ajustarse según estas anotaciones.*

### C.1 · Monografía

| Aspecto | Observación / recomendación | Atención |
|---|---|---|
| Resumen | Muy bien delimitado; valora la frase *"La evidencia respalda el funcionamiento técnico…, no equivale a pruebas perceptivas con personas…"*. Contiene **demasiadas métricas** (32 unitarias, 12 integración, 14 humo, 20 HTTP, 120 iteraciones, 36 Mobile-First, 68 casos) → **reducir** y concentrarse en objetivo, metodología, solución y resultados. | Ajustado: se aligeró la carga de métricas en el resumen. |
| Objetivo general | Bien redactado y alineado con problema, metodología y resultados. | Sin cambios requeridos. |
| Pregunta de investigación | Correctamente formulada: claridad, pertinencia, viabilidad y relación con el objeto de estudio. | Sin cambios requeridos. |
| Alcances y limitaciones | Delimitación excelente (qué se incluye / qué no). | Sin cambios requeridos. |
| Cap. 2 — Marco Teórico | Conceptos correctos: reservas, Mobile-First, Scrum, permisos, tratamiento de datos. | Sin cambios requeridos. |
| Cap. 3 — Metodología | Excelente claridad (qué hizo, qué midió, qué no midió). **Recomendación:** anunciar **todas las Figuras y Tablas** y describir qué muestra cada una **en los 3 documentos**. | Ajustado: anuncio y descripción de Figuras/Tablas. |
| Cap. 4 — Desarrollo | Product Backlog bien documentado: 34 historias, 255 Story Points, 4 Sprints; 70 RF + 30 RNF = **100 requerimientos** (cantidad alta para proyecto individual, pero el estudiante no afirma haberlos validado todos individualmente). | Se mantiene la redacción honesta de "subconjunto crítico". |
| Cap. 5 — Resultados | Relación explícita objetivos ↔ requerimientos ↔ pruebas; resultados verificables. | Sin cambios requeridos. |
| Cap. 6 — Conclusiones | Demuestran cumplimiento de objetivos; recomendaciones acordes al producto. | Sin cambios requeridos. |

### C.2 · Manual Técnico

- Documenta instrucciones de **instalación, ejecución, reinicio y desinstalación**.
- Documenta la **gestión de usuarios**, los **requisitos de hardware y software** y los **procedimientos de solución de problemas**.
- Concepto del jurado: *"La documentación del manual técnico es suficiente, clara y completa."*
- **Estado:** **Aprobado por el jurado** (se unificó el estilo de Figuras/Tablas conforme a C.1).

### C.3 · Manual de Usuario

- Documenta el **proceso de ingreso** del usuario y le informa de sus **permisos y nivel de acceso**.
- Documenta el **proceso de operación**: totalidad de menús, pantallas y reportes, con ejemplos de entrada/salida.
- Concepto del jurado: *"La documentación del manual de usuario es suficiente, clara y completa."*
- **Estado:** **Aprobado por el jurado** (se unificó el anuncio de Figuras/Tablas conforme a C.1).

### C.4 · Software

- **Operación:** confiabilidad, usabilidad, integridad y eficiencia demostradas en pruebas.
- **Funcionalidad:** cumple requerimientos y objetivos.
- Desarrollo **completo** con requerimientos, historias de usuario, diagramas, arquitectura y pruebas bien documentadas.
- **Estado:** **Aprobado por el jurado**; reforzado con las re-ejecuciones de A.2, A.3 y A.4.

---

## Parte D — Trazabilidad y evidencias

### D.1 · Commits de referencia

| Commit | Descripción | Contenido |
|---|---|---|
| `0e46926` | Corrección funcional previa | Base del software corregido |
| `d0be182` | Trazabilidad previa | Versión referenciada en la aceptación institucional |
| `04a6ab1` | Restauración y evidencia de los Bloques 2, 3, 5 y 6 | Scripts `concurrencia_reservas.py`, `verificacion_hosts.py`, `indicadores_impacto.py` + `checklist_seguridad.md` + `aceptacion_institucional.md` + salidas `.json`/`.md` |
| `dadcf23` | Re-ejecución de suites sobre la versión final | Unitarias (32), integración (12), humo (14) y validación Railway (20) el 2026-11-19 |
| `8c2b1cb` | Documento resumen de correcciones finales | `CORRECCIONES_FINALES_NOV.md` |
| `ddec10f` | **Versión final (HEAD)** · caso de regresión U33 | `tests/unit/test_reservations.py` (U33 / RQF-RES-17) + evidencia unitaria actualizada (33 pruebas) |

**HEAD actual publicado en `origin/main`: `ddec10f`.**

### D.2 · Evidencias clave en `evidencias/`

- **Concurrencia:** `concurrencia_reservas.json`, `concurrencia_reservas.md`.
- **Seguridad:** `checklist_seguridad.md`, `verificacion_hosts.json`, `verificacion_hosts.md`, `verificacion_seguridad.json`.
- **Aceptación:** `aceptacion_institucional.md`, `instrumento_evaluacion_usuarios.md|.csv`.
- **Impacto:** `indicadores_impacto.json|.md`.
- **Versión final:** `pruebas_unitarias.*`, `pruebas_integracion.*`, `smoke_tests_raw.txt`, `validacion_railway.json|.md`.
- **Operación / usabilidad técnica:** `metricas_operacion_real.*`, `mobile_first.*`, `benchmark_aplicativo.*`, `simulacion_aceptacion.*`.

### D.3 · Cifras consolidadas del sistema

- Pruebas unitarias: **33** (incluye el caso de regresión U33) · Integración: **12** · Humo: **14** · HTTP Railway: **20**.
- Iteraciones de disponibilidad (Mobile-First): **120** · Casos Mobile-First: **36**.
- Casos programáticos documentados: **68** (evidencia **funcional**, no pruebas de usabilidad con personas).
- Requerimientos: **70 RF + 30 RNF = 100** · Historias de usuario: **34** · Story Points: **255** · Sprints: **4**.

---

## Parte E — Estado final y pendientes honestos

### Atendido y cerrado

| Punto del jurado | Resultado |
|---|---|
| Concurrencia (A.2 / B.2) | PASS · 1 aceptada / 9 rechazadas |
| SEC-10 (A.4 / B.2) | CUMPLE · 12/12 controles |
| Pruebas sobre versión final (A.3 / B.2) | Re-ejecutadas el 2026-11-19; se añadió el caso de regresión U33 para `complete/` |
| Aceptación institucional (A.5) | Documento con criterios C1–C6 (6/6) y acta para firma |
| Indicadores de impacto (B.3) | I-01…I-03 calculables; I-04 declarado no calculable |
| Tablas, figuras y anexos (A.6) | Unificados en los 3 documentos |

### Pendiente (fase complementaria, declarado sin ambigüedad)

- **Validación práctica con usuarios reales (A.1 / B.1)** y el indicador de **satisfacción I-04**: requieren personas reales y **no forman parte del alcance ejecutado**; el instrumento y el protocolo quedan listos para su aplicación.

### Nota de honestidad académica

- Se distingue **Ejecutado** de **Planificado/Pendiente** en todo el documento.
- Las **68 comprobaciones** con identidades sintéticas son **evidencia funcional**, **no** pruebas de usabilidad con personas.
- Las mediciones **técnicas de red** (benchmark HTTP) **no** equivalen a indicadores **operativos humanos**.
- No se atribuyen **porcentajes de mejora** frente al procedimiento manual (WhatsApp / planillas) por falta de sustento estadístico formal.

---

*Documento de cierre de correcciones · 19 de noviembre de 2026 · Club Family Health MF · Luis Fermín Díaz Choles.*
