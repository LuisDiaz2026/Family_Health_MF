# INFORME DE RESULTADOS FINALES

## A. Versión evaluada

La versión evaluada corresponde al cierre funcional del aplicativo **Family Health MF**, desplegado en Railway en la URL `https://familyhealthmf-production.up.railway.app`. La validación productiva, el benchmark, las métricas operativas y las pruebas Mobile-First se ejecutaron sobre ese despliegue, mientras que las suites unitarias, de integración y de humo se ejecutaron en entorno local controlado usando el repositorio `C:\Family_Health_MF`.

- **Repositorio:** `https://github.com/LuisDiaz2026/Family_Health_MF.git`
- **Rama de publicación:** `main`
- **Commit funcional publicado en producción:** `51cffda`
- **Entorno local de prueba:** Windows + Django test runner + SQLite en memoria
- **Entorno productivo:** Railway + PostgreSQL
- **Health check productivo:** `GET /api/v1/health/` con HTTP 200 y `database=ok`

## B. Pruebas unitarias

La evidencia final de pruebas unitarias registra **32 casos ejecutados**, **32 aprobados**, **0 fallidos** y **0 errores**, con una duración total de **4.5981 s**. La suite cubre autenticación, JWT, usuarios, espacios, disponibilidad, validaciones de fecha y duración, creación de reserva, estados, pagos, anti-solapamiento y permisos por rol.

- **Total ejecutado:** 32
- **Aprobadas:** 32
- **Fallidas:** 0
- **Errores:** 0
- **Duración total:** 4.5981 s
- **Evidencias:** `evidencias/pruebas_unitarias.txt`, `evidencias/pruebas_unitarias.json`, `evidencias/pruebas_unitarias.csv`

Se destaca el caso `U32`, incorporado al cierre final, para validar el acceso del cliente a `mis-reservas/` sin romper la restricción del listado global administrativo.

## C. Pruebas de integración

La suite de integración registró **12 flujos ejecutados**, **12 aprobados**, **0 fallidos** y una duración total de **2.626 s**. Los escenarios cubren registro y activación, ciclo de reservas entre cliente y recepción, anti-solapamiento entre usuarios, persistencia de cálculos, control de acceso transversal, ciclo completo de JWT, actualización de disponibilidad, cancelación con liberación de franja, integración con reportes y aplicación de la política de privacidad.

- **Total ejecutado:** 12
- **Aprobadas:** 12
- **Fallidas:** 0
- **Duración total:** 2.626 s
- **Evidencias:** `evidencias/pruebas_integracion.txt`, `evidencias/pruebas_integracion.json`, `evidencias/pruebas_integracion.csv`

## D. Smoke tests

La ejecución de humo reportó **14 casos correctos** y **0 fallidos**. Los casos validados incluyen el health check, autenticación por roles, consulta de espacios, disponibilidad, catálogo de refresquería, fidelización, rutinas de gimnasio, panel administrativo, control de acceso sin token, refresco de JWT, política de privacidad y creación de reserva con rechazo de solapamiento.

- **Casos ejecutados:** 14
- **Aprobados:** 14
- **Fallidos:** 0
- **Evidencia bruta:** `evidencias/smoke_tests_raw.txt`

Durante esta ejecución se observaron advertencias del entorno relacionadas con longitud recomendada de clave HMAC para HS512 y marcas de tiempo ingenuas en algunos datos de prueba. No obstante, dichas advertencias no impidieron la aprobación de la suite.

## E. Railway y PostgreSQL

La validación directa contra el despliegue de Railway registró **20 casos ejecutados**, **20 aprobados** y **0 fallidos**. Los resultados reales cubren health check, login correcto e incorrecto, usuario inactivo, acceso permitido y prohibido por rol, consulta de espacios, disponibilidad, creación de reserva, consulta posterior, rechazo de solapamiento, errores controlados 400/401/404, refresco de token, cancelación y persistencia en nueva sesión.

- **Casos Railway:** 20
- **Aprobados:** 20
- **Fallidos:** 0
- **Motor validado por health check:** PostgreSQL
- **Evidencias:** `evidencias/validacion_railway.md`, `evidencias/validacion_railway.json`

La validación sobre Railway confirmó que el sistema respondió correctamente bajo operación real, sin exponer secretos ni datos sensibles en los errores controlados.

## F. Anti-solapamiento

La prevención de solapamiento fue verificada por múltiples mecanismos de prueba. En la validación sobre Railway se ejecutó **1 intento real de reserva solapada** y fue **rechazado** con HTTP 400. En el smoke test se ejecutó **1 intento adicional de solapamiento**, también rechazado, manteniéndose **1 sola reserva persistida**. En el benchmark controlado del escenario `S3_detectar_solapamiento` se ejecutaron **30 intentos**, con **30 rechazos**, **0 aceptaciones indebidas** y **0 conflictos persistidos**.

Resumen cuantitativo mínimo consolidado:

- **Intentos controlados de solapamiento observados:** 32
- **Aceptados indebidamente:** 0
- **Rechazados correctamente:** 32
- **Conflictos persistidos:** 0
- **Estado final en producción del dato de prueba Railway:** `CANCELLED`

Las evidencias correspondientes están en `evidencias/validacion_railway.md`, `evidencias/smoke_tests_raw.txt`, `evidencias/benchmark_aplicativo.md` y `evidencias/benchmark_iteraciones.csv`.

## G. Rendimiento operativo controlado

El benchmark controlado se ejecutó con **4 escenarios** y **30 iteraciones por escenario** sobre la API desplegada en Railway. Los resultados agregados fueron los siguientes:

| Escenario | n | Media (ms) | Mediana (ms) | Mínimo (ms) | Máximo (ms) |
|---|---:|---:|---:|---:|---:|
| Consultar disponibilidad | 30 | 328.47 | 320.18 | 303.70 | 559.14 |
| Registrar reserva | 30 | 331.75 | 331.16 | 314.33 | 355.30 |
| Detectar solapamiento | 30 | 320.77 | 319.68 | 304.42 | 349.72 |
| Cancelar reserva | 30 | 327.49 | 323.75 | 310.57 | 352.40 |

Los cuatro escenarios alcanzaron **100.0 % de éxito**, **0.0 % de conflictos persistidos**, **100.0 % de resolución en primer intento** y **0 reprocesos técnicos**.

- **Evidencias:** `evidencias/benchmark_aplicativo.md`, `evidencias/benchmark_aplicativo.csv`, `evidencias/benchmark_iteraciones.csv`

## H. Mobile-First

La validación Mobile-First se ejecutó sobre **36 combinaciones** de resolución y pantalla, distribuidas en 4 tamaños de viewport: **360 px**, **390 px**, **768 px** y **1280 px**. El resultado final fue **36/36 PASS**, con **0 px de desbordamiento horizontal injustificado**.

Las pantallas verificadas fueron:

- acceso público;
- dashboard del cliente;
- listado de reservas del cliente;
- formulario de reserva;
- catálogo de refrescos;
- dashboard administrativo;
- listado administrativo de reservas;
- catálogo administrativo de productos;
- catálogo administrativo de espacios.

- **Evidencias:** `evidencias/mobile_first.md`, `evidencias/mobile_first.csv`, carpeta `evidencias/mobile/`

## I. Evidencia de las dos semanas de utilización

Las métricas operativas reales se calcularon a partir de respuestas HTTP reales del despliegue productivo, el cual consulta directamente PostgreSQL. El informe de métricas consolidó **42 indicadores**. Entre los valores observados se destacan:

- **Usuarios activos totales:** 8
- **Clientes activos:** 3
- **Reservas históricas registradas:** 4
- **Reservas canceladas:** 4
- **Pedidos registrados:** 0
- **Ingresos por reservas del mes:** 40000.00 COP
- **Días distintos con creación de reservas:** 2
- **Primera reserva registrada:** `2026-10-12T09:02:28.127829-05:00`
- **Última reserva registrada:** `2026-10-19T22:53:12.198590-05:00`
- **Primer usuario registrado:** `2026-10-05T13:34:14.076688-05:00`
- **Último usuario registrado:** `2026-10-19T22:53:08.638424-05:00`

Estos resultados muestran que el sistema conserva trazabilidad básica suficiente para cuantificar usuarios, reservas, cancelaciones, fechas de creación y algunos indicadores agregados de actividad. También permiten separar datos operativos de datos de prueba controlados.

- **Evidencias:** `evidencias/metricas_operacion_real.md`, `evidencias/metricas_operacion_real.csv`, `evidencias/metricas_operacion_raw.json`

## J. Limitaciones

La evaluación técnica identificó límites de medición que deben declararse explícitamente:

1. El sistema no expone mediante la API de la versión final un endpoint de lectura de auditoría, por lo que no fue posible calcular retrospectivamente intentos de inicio de sesión ni trazas de auditoría por rol.
2. No existen marcas de tiempo suficientes para calcular tiempos de atención presencial por reserva.
3. La ocupación disponible en reportes corresponde a un indicador agregado de 7 días y no a una tasa por espacio individual para todos los espacios.
4. El volumen operativo real observado en PostgreSQL durante el periodo consultado es todavía bajo; por tanto, las conclusiones sobre uso real deben interpretarse como evidencia inicial de funcionamiento productivo y no como un estudio longitudinal de alta escala.

## K. Conclusión técnica

Los resultados obtenidos permiten concluir que la versión final de **Family Health MF** se encuentra implementada y técnicamente verificada para los componentes centrales del trabajo de grado. Las funciones de autenticación, roles, registro, reservas, disponibilidad, prevención de solapamiento, consulta operativa y adaptación Mobile-First muestran comportamiento correcto tanto en pruebas locales controladas como en validaciones reales sobre Railway y PostgreSQL.

El cierre técnico también confirmó que:

- el cliente puede consultar únicamente sus propias reservas;
- la creación de reservas utiliza disponibilidad real por franjas;
- el panel administrativo restringe adecuadamente el acceso por rol;
- la interfaz se comporta correctamente en resoluciones móviles y de escritorio;
- la base productiva conserva datos suficientes para derivar métricas verificables sin inventar resultados.

Desde el punto de vista académico y técnico, el software queda soportado con evidencia reproducible. Lo que permanece pendiente para etapas posteriores no es una verificación técnica básica del aplicativo, sino la ampliación de validación humana con usuarios finales, el aumento del volumen operativo real y, si se desea mayor robustez futura, el fortalecimiento de restricciones a nivel de motor de base de datos para escenarios de concurrencia extrema.
