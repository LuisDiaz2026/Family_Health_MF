# Instrumento de evaluación con personas reales (una página)

> Family Health MF · cierre técnico de la versión final · punto 10
>
> Formulario diseñado para diligenciarse en aproximadamente **5 minutos**.
> **Este documento está vacío a propósito**: las respuestas deben provenir de
> participantes reales. No se registran respuestas inventadas.

## Instrucciones para quien aplica el instrumento

1. Entregue a la persona el enlace de la versión final y, si corresponde, sus
   credenciales de prueba.
2. Explique que se evaluará la facilidad de uso, no a la persona.
3. Registre una fila por cada tarea realizada. No complete la columna de
   percepción: la responde la persona.
4. Al finalizar, transcriba las filas al archivo
   `evidencias/instrumento_evaluacion_usuarios.csv` (mismas columnas).

## Datos de la sesión (a diligenciar por quien aplica)

| Campo | Valor |
|---|---|
| Fecha | |
| Lugar / modalidad | |
| Enlace evaluado | `https://familyhealthmf-production.up.railway.app/` |
| Nombre de quien aplica | |

## Formulario (una fila por tarea)

| Campo | Respuesta |
|---|---|
| **Código anónimo** (ej. P-01, no use nombres) | |
| **Perfil** (administrador / recepción / cliente) | |
| **Dispositivo** (celular / tablet / computador) | |
| **Tarea realizada** | |
| **¿Completó la tarea?** (sí / no) | |
| **Tiempo empleado (min)** | |
| **Errores cometidos** (número y breve descripción) | |
| **Facilidad percibida (1 = muy difícil, 5 = muy fácil)** | |
| **Claridad de la información (1–5)** | |
| **Satisfacción general (1–5)** | |
| **Observación libre de la persona** | |

## Escala de referencia (mostrar a la persona)

| Valor | Significado |
|---|---|
| 1 | Muy difícil / nada claro / nada satisfecho |
| 2 | Difícil / poco claro / poco satisfecho |
| 3 | Aceptable / regular |
| 4 | Fácil / claro / satisfecho |
| 5 | Muy fácil / muy claro / muy satisfecho |

## Tareas sugeridas por perfil

| Perfil | Tarea sugerida |
|---|---|
| Cliente | Iniciar sesión, consultar disponibilidad de un espacio y crear una reserva. |
| Cliente | Consultar sus reservas y cancelar una reserva que cumpla la política de cancelación. |
| Recepción | Iniciar sesión, consultar el listado de reservas y aprobar o rechazar una reserva pendiente. |
| Administrador | Iniciar sesión, revisar el panel de indicadores y gestionar un producto del inventario. |

## Registro consolidado

Las respuestas se consolidan en `evidencias/instrumento_evaluacion_usuarios.csv`
con estas columnas exactas:

```
código_anónimo, perfil, dispositivo, tarea, completada_si_no, tiempo_min,
errores, facilidad_1_5, claridad_1_5, satisfaccion_1_5, observación
```

> Mientras no existan participantes, el archivo permanece con el encabezado y sin
> filas. La evaluación automatizada del punto 9 (`evidencias/evaluacion_controlada_tareas.csv`)
> **no sustituye** esta validación humana y no debe presentarse como opinión de usuarios.
