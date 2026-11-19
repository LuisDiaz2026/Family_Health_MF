"""
Indicadores de impacto del sistema (respuesta a la recomendacion del jurado).

Calcula, a partir de datos REALES expuestos por la API de produccion (que lee
directamente de PostgreSQL), las cuatro familias de indicadores solicitadas por
el jurado:

    I-01  Tiempo de confirmacion de reservas
    I-02  Conflictos de programacion (solapamientos)
    I-03  Cancelaciones
    I-04  Satisfaccion de los usuarios

Los indicadores I-01..I-03 se presentan en dos conjuntos para no contaminar la
lectura: "todos" (base completa) y "operativas" (excluye los registros
identificados como datos de prueba controlados). Solo se calculan los
indicadores derivables de los datos disponibles; cuando el software no registra
la informacion necesaria el indicador se marca como APROXIMADO o PENDIENTE y se
explica la limitacion. No se inventan valores.

Uso:
    python tests/indicadores_impacto.py

Salidas:
    evidencias/indicadores_impacto.json
    evidencias/indicadores_impacto.md
"""
from __future__ import annotations

import json
import os
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from credenciales import cargar_en_entorno  # noqa: E402

cargar_en_entorno()

RAIZ = Path(__file__).resolve().parent.parent
DIR_EVIDENCIAS = RAIZ / "evidencias"
DIR_EVIDENCIAS.mkdir(exist_ok=True)

BASE = os.getenv("FH_BASE", "https://familyhealthmf-production.up.railway.app").rstrip("/")
API = f"{BASE}/api/v1"
TIMEOUT = 60

USUARIO_ADMIN = os.getenv("FH_USER_ADMIN", "admin_fh")
CLAVE_ADMIN = os.getenv("FH_PASS_ADMIN", "")

ESTADOS_ACTIVOS = ("PENDING", "CONFIRMED")
ESTADOS_CONFIRMADOS = ("CONFIRMED", "COMPLETED")
TEXTOS_DATO_PRUEBA = ("prueba controlado", "validacion railway", "simulacion")


def _parse_dt(valor: str):
    """Convierte una marca de tiempo ISO 8601 (tolerando el sufijo Z)."""
    if not valor:
        return None
    if valor.endswith("Z"):
        valor = valor[:-1] + "+00:00"
    return datetime.fromisoformat(valor)


def _es_dato_prueba(reserva: dict) -> bool:
    notas = (reserva.get("notes") or "").lower()
    return any(t in notas for t in TEXTOS_DATO_PRUEBA)


def cabecera(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"} if token else {}


def login_admin() -> str:
    r = requests.post(f"{API}/auth/login/",
                      json={"username": USUARIO_ADMIN, "password": CLAVE_ADMIN},
                      timeout=TIMEOUT)
    if r.status_code != 200:
        raise SystemExit(f"No fue posible autenticar al administrador (HTTP {r.status_code}).")
    return r.json()["access"]


def obtener_todo(url: str, headers: dict, max_paginas: int = 300) -> list:
    """Recorre la paginacion de DRF y devuelve todos los elementos."""
    elementos: list = []
    pagina = 0
    while url and pagina < max_paginas:
        r = requests.get(url, headers=headers, timeout=TIMEOUT)
        if r.status_code != 200:
            break
        datos = r.json()
        if isinstance(datos, dict) and "results" in datos:
            elementos.extend(datos["results"])
            url = datos.get("next")
        elif isinstance(datos, list):
            elementos.extend(datos)
            url = None
        else:
            break
        pagina += 1
    return elementos


def _overlaps(activas: list[dict]) -> list[dict]:
    """Pares de reservas activas que se solapan en el mismo espacio."""
    conflictos = []
    for i in range(len(activas)):
        for j in range(i + 1, len(activas)):
            a, b = activas[i], activas[j]
            if a["_space_id"] != b["_space_id"]:
                continue
            if a["_start"] < b["_end"] and b["_start"] < a["_end"]:
                conflictos.append({
                    "a": a.get("code") or a.get("id"),
                    "b": b.get("code") or b.get("id"),
                    "space_id": a["_space_id"],
                })
    return conflictos


def _estadisticas(valores: list[float]) -> dict:
    if not valores:
        return {"n": 0}
    return {
        "n": len(valores),
        "min": round(min(valores), 3),
        "mediana": round(statistics.median(valores), 3),
        "media": round(statistics.mean(valores), 3),
        "max": round(max(valores), 3),
    }


def _bloque(reservas: list[dict]) -> dict:
    """Calcula I-01, I-02 e I-03 sobre un subconjunto de reservas."""
    activas = [r for r in reservas if r.get("status") in ESTADOS_ACTIVOS]
    canceladas = [r for r in reservas if r.get("status") == "CANCELLED"]
    confirmadas = [r for r in reservas if r.get("status") in ESTADOS_CONFIRMADOS]
    con_aprobacion = [r for r in confirmadas if r.get("approved_by")]
    deltas = []
    for r in confirmadas:
        c, u = _parse_dt(r.get("created_at")), _parse_dt(r.get("updated_at"))
        if c and u and u >= c:
            deltas.append((u - c).total_seconds() / 60.0)
    conflictos = _overlaps(activas)
    return {
        "reservas": len(reservas),
        "activas": len(activas),
        "canceladas": len(canceladas),
        "tasa_cancelacion_pct": round(len(canceladas) / len(reservas) * 100, 2)
        if reservas else None,
        "canceladas_con_motivo": sum(1 for r in canceladas if r.get("cancellation_reason")),
        "I-01_confirmadas": len(confirmadas),
        "I-01_con_aprobacion": len(con_aprobacion),
        "I-01_tiempo_min": _estadisticas(deltas),
        "I-02_conflictos_persistidos": len(conflictos),
        "I-02_detalle": conflictos,
    }


def calcular(reservas: list[dict]) -> dict:
    for r_ in reservas:
        r_["_space_id"] = (r_.get("space") or {}).get("id")
        r_["_start"] = _parse_dt(r_.get("start_time"))
        r_["_end"] = _parse_dt(r_.get("end_time"))
    operativas = [r_ for r_ in reservas if not _es_dato_prueba(r_)]
    return {
        "total": _bloque(reservas),
        "operativas": _bloque(operativas),
        "I-04": {
            "calculable": False,
            "motivo": "Requiere participantes reales; la version final no captura "
                      "percepcion de usuarios.",
        },
    }


def _fila_indicador(etiqueta: str, bloque: dict) -> list[str]:
    tc = bloque["I-01_tiempo_min"]
    return [
        f"| **{etiqueta}** | {bloque['reservas']} | {bloque['activas']} | "
        f"{bloque['canceladas']} ({bloque['tasa_cancelacion_pct']}%) | "
        f"{bloque['I-01_confirmadas']} | {tc.get('n', 0)} | "
        f"{tc.get('mediana', 'N/D')} | {bloque['I-02_conflictos_persistidos']} |",
    ]


def exportar(sello: str, datos: dict) -> None:
    resumen = {"fecha": sello, "url": BASE, "indicadores": datos}
    (DIR_EVIDENCIAS / "indicadores_impacto.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    tot, ope = datos["total"], datos["operativas"]
    lineas = [
        "# Indicadores de impacto del sistema - Club Family Health MF",
        "",
        "> Cierre tecnico de la version final · respuesta a la recomendacion del jurado",
        '> ("Establecer indicadores para medir el impacto del sistema").',
        "",
        f"- **Fuente:** API publica de la version desplegada ({BASE}) consultada con",
        "  credenciales de administrador; la API lee directamente de PostgreSQL.",
        f"- **Fecha/hora de la consulta (UTC):** {sello}",
        "",
        "## Naturaleza de los datos (leer antes de interpretar)",
        "",
        f"- Reservas registradas en la base productiva a la fecha de consulta: **{tot['reservas']}**.",
        f"- De ellas, **{ope['reservas']}** no corresponden a datos de prueba controlados y "
        f"**{tot['reservas'] - ope['reservas']}** si (identificadas por su nota).",
        "- El **volumen observado es bajo**: estos valores son una **linea base**, no un",
        "  estudio longitudinal. Por si solos NO permiten afirmar mejoras frente al",
        "  procedimiento manual; para ello el club debe acumular registros suficientes.",
        "- Los indicadores se presentan en dos conjuntos: **Todos** (base completa) y",
        "  **Operativas** (excluye datos de prueba controlados).",
        "",
        "## Marco de indicadores (lo solicitado por el jurado)",
        "",
        "| ID | Indicador | Definicion | Fuente / registro | Estado |",
        "|---|---|---|---|---|",
        "| I-01 | Tiempo de confirmacion de reservas | Tiempo entre la solicitud y la confirmacion | `created_at` y `updated_at` | **Aproximado** |",
        "| I-02 | Conflictos de programacion | Reservas activas que se solapan en el mismo espacio | Enumeracion de reservas (PENDING/CONFIRMED) | **Calculable** |",
        "| I-03 | Cancelaciones | Numero y tasa de reservas canceladas | `status=CANCELLED` | **Calculable** |",
        "| I-04 | Satisfaccion de los usuarios | Facilidad, claridad y satisfaccion (1-5) | Instrumento con personas reales | **Pendiente** |",
        "",
        "## Resultados reales a la fecha de consulta",
        "",
        "| Conjunto | Reservas | Activas | Canceladas (tasa) | Confirmadas | n tiempo | Mediana tiempo (min) | Conflictos persistidos |",
        "|---|---|---|---|---|---|---|---|",
    ]
    lineas += _fila_indicador("Todos", tot)
    lineas += _fila_indicador("Operativas", ope)
    lineas += [
        "",
        "**Lectura:**",
        f"- **I-01:** tiempo de confirmacion observado como **cota superior** "
        f"(`updated_at - created_at`). Conjunto operativo: n={ope['I-01_tiempo_min'].get('n', 0)}.",
        f"- **I-02:** conflictos persistidos = **{tot['I-02_conflictos_persistidos']}** "
        f"(todos) y **{ope['I-02_conflictos_persistidos']}** (operativas).",
        f"- **I-03:** tasa de cancelacion = **{tot['tasa_cancelacion_pct']}%** (todos) y "
        f"**{ope['tasa_cancelacion_pct']}%** (operativas).",
        "- **I-04:** NO CALCULABLE con datos del sistema; requiere participantes reales.",
        "",
        "## Detalle por indicador",
        "",
        "### I-01 - Tiempo de confirmacion de reservas",
        "",
        "- **Definicion:** tiempo entre la creacion de la solicitud y su confirmacion.",
        "- **Como se calcula:** `updated_at - created_at` para reservas confirmadas/completadas.",
        "- **Limitacion declarada:** la version final NO almacena una marca temporal",
        "  explicita de aprobacion (`approved_at`). Para reservas sin aprobacion la",
        "  confirmacion es inmediata (misma transaccion de creacion), de modo que el",
        "  valor es ~0. Para reservas que exigieron aprobacion, `updated_at` es una",
        "  **cota superior** (puede incluir otras modificaciones posteriores).",
        f"- **Resultado:** confirmadas/completadas en la base = {tot['I-01_confirmadas']} "
        f"(con aprobacion registrada: {tot['I-01_con_aprobacion']}); por eso n de tiempo = "
        f"{tot['I-01_tiempo_min'].get('n', 0)}.",
        "",
        "### I-02 - Conflictos de programacion",
        "",
        "- **Definicion:** numero de reservas activas (PENDING/CONFIRMED) que se solapan",
        "  en el mismo espacio y franja horaria.",
        "- **Como se calcula:** comparacion por pares de las reservas activas enumeradas.",
        f"- **Resultado real:** **{tot['I-02_conflictos_persistidos']}** conflictos persistidos.",
        "  La integridad se garantiza por el anti-solapamiento en la transaccion de",
        "  creacion (validacion + `select_for_update` sobre el espacio).",
        "- **Intentos de solapamiento rechazados:** se miden en pruebas controladas",
        "  (no quedan registrados en la base porque la solicitud se rechaza). Evidencia:",
        "  `evidencias/benchmark_aplicativo.md` (30 intentos, 30 rechazos) y",
        "  `evidencias/validacion_railway.md` (1 intento, 1 rechazo).",
        "",
        "### I-03 - Cancelaciones",
        "",
        "- **Definicion:** numero y proporcion de reservas canceladas respecto al total.",
        f"- **Resultado real:** {tot['canceladas']} canceladas de {tot['reservas']} "
        f"(tasa {tot['tasa_cancelacion_pct']}%). Conjunto operativo: "
        f"{ope['canceladas']} de {ope['reservas']} (tasa {ope['tasa_cancelacion_pct']}%).",
        "- **Nota:** el motivo de cancelacion se registra cuando el usuario lo informa.",
        "",
        "### I-04 - Satisfaccion de los usuarios",
        "",
        "- **Definicion:** facilidad percibida, claridad y satisfaccion general (escala 1-5).",
        "- **Estado:** **pendiente**. No se puede derivar del sistema; requiere aplicar el",
        "  instrumento a participantes reales (`evidencias/instrumento_evaluacion_usuarios.md`).",
        "- **Advertencia:** las puntuaciones de `evidencias/simulacion_aceptacion.*` son",
        "  **simuladas** y NO sustituyen esta medicion con personas.",
        "",
        "## Ejecutado vs. Planificado",
        "",
        "| Indicador | Estado | Comentario |",
        "|---|---|---|",
        "| I-01 Tiempo de confirmacion | Aproximado (Ejecutado) | Medible hoy como cota superior; requeriria `approved_at` para ser exacto. |",
        "| I-02 Conflictos de programacion | Ejecutado | Se verifica que no haya conflictos persistidos. |",
        "| I-03 Cancelaciones | Ejecutado | Calculable a partir del estado de las reservas. |",
        "| I-04 Satisfaccion | Planificado (Pendiente) | Requiere usuarios reales; instrumento ya disenado. |",
        "",
        "## Como el club determina mejoras (sin atribuciones sin sustento)",
        "",
        "Estos indicadores establecen una **linea base medible**. El club podra comparar",
        "periodos futuros contra esta base cuando existan **registros suficientes**. No se",
        "atribuye ningun porcentaje de mejora frente a WhatsApp o planillas: esa conclusion",
        "requiere un diseno de medicion con volumen y periodo comparables.",
        "",
        "## Comandos de reproduccion",
        "",
        "```powershell",
        "cd c:\\Family_Health_MF",
        '$env:FH_PASS_ADMIN="<contrasena demo admin>"',
        ".venv\\Scripts\\python.exe tests\\indicadores_impacto.py",
        "```",
        "",
    ]
    (DIR_EVIDENCIAS / "indicadores_impacto.md").write_text(
        "\n".join(lineas), encoding="utf-8")
    print(f"    archivo: {DIR_EVIDENCIAS / 'indicadores_impacto.md'}")


def main() -> int:
    if not CLAVE_ADMIN:
        raise SystemExit("Falta FH_PASS_ADMIN en el entorno.")
    token = login_admin()
    h = cabecera(token)
    sello = datetime.now(timezone.utc).isoformat(timespec="seconds")
    print("=" * 74)
    print("INDICADORES DE IMPACTO - CLUB FAMILY HEALTH MF")
    print(f"URL: {BASE}")
    print(f"Fecha/hora (UTC): {sello}")
    print("=" * 74)

    reservas = obtener_todo(f"{API}/reservations/reservations/", h)
    print(f">>> reservations/ -> {len(reservas)} reservas enumeradas")

    datos = calcular(reservas)
    tot, ope = datos["total"], datos["operativas"]
    print(f">>> I-01 (todos) confirmadas/completadas: {tot['I-01_confirmadas']} "
          f"-> tiempo {tot['I-01_tiempo_min']}")
    print(f">>> I-02 conflictos persistidos: todos={tot['I-02_conflictos_persistidos']} "
          f"operativas={ope['I-02_conflictos_persistidos']}")
    print(f">>> I-03 canceladas: todos={tot['canceladas']}/{tot['reservas']} "
          f"({tot['tasa_cancelacion_pct']}%) | operativas={ope['canceladas']}/{ope['reservas']} "
          f"({ope['tasa_cancelacion_pct']}%)")
    print(">>> I-04 satisfaccion: NO CALCULABLE (requiere usuarios reales)")

    exportar(sello, datos)
    return 0


if __name__ == "__main__":
    sys.exit(main())
