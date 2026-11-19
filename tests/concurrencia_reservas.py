"""
Prueba de concurrencia del anti-solapamiento de reservas (cierre del bloque 2).

Lanza N solicitudes SIMULTANEAS (hilos + barrera de sincronizacion) que piden el
MISMO espacio en la MISMA franja horaria. El sistema debe aceptar UNA sola reserva
(HTTP 201) y rechazar el resto por conflicto (HTTP 400), sin dejar duplicados en
la base de datos.

A diferencia del smoke test (solapamiento secuencial), aqui las peticiones se
lanzan en paralelo para ejercitar la proteccion real de la transaccion:
`Space.is_available_at` + `SELECT ... FOR UPDATE` sobre el espacio dentro de
`Reservation.save`.

Al final, la reserva aceptada se CANCELA para no dejar la franja ocupada.

Uso:
    python tests/concurrencia_reservas.py [N]     (N = numero de solicitudes; 10 por defecto)

Salidas:
    evidencias/concurrencia_reservas.json
    evidencias/concurrencia_reservas.md
"""
from __future__ import annotations

import json
import os
import sys
import threading
import time
from datetime import datetime, timedelta, timezone as dt_tz
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
TIMEOUT = 90

USUARIO_CLIENTE1 = os.getenv("FH_USER_CLIENTE1", "cliente1_fh")
CLAVE_CLIENTE1 = os.getenv("FH_PASS_CLIENTE1", "")
USUARIO_CLIENTE2 = os.getenv("FH_USER_CLIENTE2", "cliente2_fh")
CLAVE_CLIENTE2 = os.getenv("FH_PASS_CLIENTE2", "")

NOTA = "CONCURRENCIA - dato de prueba controlado (se cancela al final)"
CODIGO_PREFERIDO = "CANCHA-BASKET-01"
DURACION_MIN = 60
MAX_DETALLE = 120
HUSO = dt_tz(timedelta(hours=-5))  # America/Bogota


def cabecera(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"} if token else {}


def login(usuario: str, clave: str) -> str:
    r = requests.post(f"{API}/auth/login/",
                      json={"username": usuario, "password": clave},
                      timeout=TIMEOUT)
    if r.status_code != 200:
        raise SystemExit(f"Login fallido para {usuario} (HTTP {r.status_code}).")
    return r.json()["access"]


def huella_token(token: str) -> str:
    if not token:
        return "(sin token)"
    return f"{token[:10]}...{token[-4:]} ({len(token)} car.)"


def _parse_dt(valor: str):
    if not valor:
        return None
    if valor.endswith("Z"):
        valor = valor[:-1] + "+00:00"
    return datetime.fromisoformat(valor)


def _overlap(a_ini, a_fin, b_ini, b_fin) -> bool:
    return a_ini < b_fin and b_ini < a_fin


def elegir_espacio(token: str) -> dict:
    """Devuelve el espacio preferido si existe; si no, el primer espacio ACTIVO."""
    r = requests.get(f"{API}/reservations/spaces/", headers=cabecera(token),
                     timeout=TIMEOUT)
    r.raise_for_status()
    espacios = r.json()
    if isinstance(espacios, dict):
        espacios = espacios.get("results", [])
    for e in espacios:
        if e.get("code") == CODIGO_PREFERIDO:
            return e
    activos = [e for e in espacios if e.get("status") == "ACTIVE"]
    if not activos:
        raise SystemExit("No hay espacios ACTIVOS en la version evaluada.")
    return activos[0]


def disponibilidad(token: str, space_id: int, fecha: str) -> dict | None:
    r = requests.get(f"{API}/reservations/spaces/{space_id}/availability/",
                     headers=cabecera(token), params={"date": fecha},
                     timeout=TIMEOUT)
    if r.status_code != 200:
        return None
    return r.json()


def _franja_libre(ini: datetime, fin: datetime, libres: list, ocupados: list) -> bool:
    """Comprueba que [ini, fin) este cubierta por franjas libres de 30 min y sin choques."""
    esperados = []
    t = ini
    while t < fin:
        esperados.append(t)
        t += timedelta(minutes=30)
    if not all(e in libres for e in esperados):
        return False
    for o_ini, o_fin in ocupados:
        if _overlap(ini, fin, o_ini, o_fin):
            return False
    return True


def elegir_franja(token: str, space_id: int, desde_dias: int = 3,
                  hasta_dias: int = 45) -> tuple[str, datetime, datetime]:
    """Busca la primera fecha futura con una franja libre contigua de DURACION_MIN."""
    hoy = datetime.now(HUSO).date()
    for offset in range(desde_dias, hasta_dias + 1):
        fecha = (hoy + timedelta(days=offset)).isoformat()
        disp = disponibilidad(token, space_id, fecha)
        if not disp:
            continue
        slots = disp.get("thirty_minute_slots") or []
        ocupados_raw = disp.get("occupied_slots") or []
        libres = [_parse_dt(s["datetime"]) for s in slots]
        ocupados = [(_parse_dt(o["start_time"]), _parse_dt(o["end_time"]))
                    for o in ocupados_raw]
        for ini in libres:
            fin = ini + timedelta(minutes=DURACION_MIN)
            if _franja_libre(ini, fin, libres, ocupados):
                return fecha, ini, fin
    raise SystemExit("No se encontro una franja libre para la prueba de concurrencia.")


def lanzar_peticiones(n: int, espacio_id: int, ini: datetime, fin: datetime,
                      tokens: list[tuple[str, str]]) -> list[dict]:
    """Lanza n peticiones simultaneas con hilos y una barrera de sincronizacion."""
    barrera = threading.Barrier(n)
    resultados: list[dict | None] = [None] * n

    def trabajador(indice: int) -> None:
        usuario, token = tokens[indice % len(tokens)]
        cuerpo = {
            "space_id": espacio_id,
            "start_time": ini.isoformat(),
            "end_time": fin.isoformat(),
            "guests_count": 1,
            "notes": NOTA,
        }
        barrera.wait()
        t0 = time.perf_counter()
        try:
            resp = requests.post(f"{API}/reservations/reservations/",
                                 headers=cabecera(token), json=cuerpo,
                                 timeout=TIMEOUT)
            http, texto = resp.status_code, resp.text
        except requests.RequestException as exc:
            http, texto = None, f"ERROR: {exc}"
        t1 = time.perf_counter()
        reserva_id = None
        if http == 201:
            try:
                reserva_id = resp.json().get("id")
            except ValueError:
                reserva_id = None
        resultados[indice] = {
            "indice": indice,
            "usuario": usuario,
            "http": http,
            "segundos": round(t1 - t0, 4),
            "detalle": texto[:MAX_DETALLE],
            "reserva_id": reserva_id,
            "token_huella": huella_token(token),
        }

    hilos = [threading.Thread(target=trabajador, args=(i,)) for i in range(n)]
    for h in hilos:
        h.start()
    for h in hilos:
        h.join()
    return [r for r in resultados if r is not None]


def reservas_activas_en_bd(token: str, space_id: int, ini: datetime,
                           fin: datetime) -> list[dict]:
    disp = disponibilidad(token, space_id, ini.date().isoformat())
    if not disp:
        return []
    activas = []
    for o in disp.get("occupied_slots") or []:
        o_ini, o_fin = _parse_dt(o["start_time"]), _parse_dt(o["end_time"])
        if _overlap(ini, fin, o_ini, o_fin):
            activas.append({
                "start_time": o["start_time"],
                "end_time": o["end_time"],
                "id": o.get("id"),
                "status": o.get("status"),
            })
    return activas


def exportar(sello: str, datos: dict) -> None:
    (DIR_EVIDENCIAS / "concurrencia_reservas.json").write_text(
        json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")

    espacio, franja = datos["espacio"], datos["franja"]
    veredicto = datos["veredicto"]
    limpieza = datos["limpieza_cancelaciones"]
    lineas = [
        "# Prueba de concurrencia del anti-solapamiento de reservas",
        "",
        "> Family Health MF - cierre tecnico de la version final (bloque 2)",
        "",
        f"- **URL evaluada:** {datos['url']}",
        f"- **Fecha/hora (UTC):** {sello}",
        f"- **Solicitudes simultaneas (N):** {datos['n_solicitudes_simultaneas']}",
        f"- **Clientes:** {', '.join(datos['clientes'])}",
        f"- **Espacio en disputa:** {espacio['code']} (id={espacio['id']})",
        f"- **Franja en disputa:** `{franja['inicio']}` -> `{franja['fin']}`",
        "",
        "## Objetivo",
        "",
        "Comprobar que, cuando **varias solicitudes piden el MISMO espacio en la",
        "MISMA franja al mismo tiempo**, el sistema acepta **una sola** reserva y",
        "rechaza el resto, sin generar duplicados en la base de datos. A diferencia",
        "del smoke test (que valida el solapamiento de forma secuencial), aqui las",
        "peticiones se lanzan en paralelo mediante hilos y una barrera de",
        "sincronizacion.",
        "",
        "## Resultado",
        "",
        f"- **Aceptadas (HTTP 201):** {datos['aceptadas_201']}",
        f"- **Rechazadas por conflicto (HTTP 400):** {datos['rechazadas_400']}",
        f"- **Otras respuestas:** {datos['otras_respuestas']}",
        f"- **Reservas activas en BD que solapan la franja:** {datos['reservas_activas_en_bd']}",
        f"- **Veredicto:** **{veredicto}**",
        "",
        "## Peticiones simultaneas",
        "",
        "| # | Usuario | HTTP | Segundos | Reserva id | Detalle |",
        "|---|---|---|---|---|---|",
    ]
    for p in datos["peticiones"]:
        rid = p["reserva_id"] if p["reserva_id"] is not None else "-"
        detalle = p["detalle"].replace("|", "\\|")
        lineas.append(f"| {p['indice']} | {p['usuario']} | {p['http']} | "
                      f"{p['segundos']} | {rid} | `{detalle}` |")

    lineas += [
        "",
        "## Verificacion en la base de datos",
        "",
        "Consultando la disponibilidad del espacio tras la prueba, las reservas",
        f"activas (PENDING/CONFIRMED) que solapan la franja son "
        f"**{datos['reservas_activas_en_bd']}**.",
        "",
    ]
    if datos["reservas_en_bd_detalle"]:
        lineas += [
            "| Reserva id | Estado | Inicio | Fin |",
            "|---|---|---|---|",
        ]
        for r in datos["reservas_en_bd_detalle"]:
            lineas.append(f"| {r['id']} | {r['status']} | {r['start_time']} | "
                          f"{r['end_time']} |")

    lineas += [
        "",
        "## Limpieza",
        "",
        "La reserva aceptada durante la prueba se cancela al final del script para",
        "no dejar ocupada la franja:",
        "",
    ]
    for c in limpieza:
        lineas.append(f"- reserva id={c['id']} -> cancelacion HTTP {c['http']}")

    lineas += [
        "",
        "## Reproduccion",
        "",
        "```powershell",
        "cd c:\\Family_Health_MF",
        '$env:FH_PASS_ADMIN="<contrasena demo admin>"',
        '$env:FH_PASS_CLIENTE1="<contrasena demo cliente1>"',
        '$env:FH_PASS_CLIENTE2="<contrasena demo cliente2>"',
        f".venv\\Scripts\\python.exe tests\\concurrencia_reservas.py "
        f"{datos['n_solicitudes_simultaneas']}",
        "```",
        "",
        "## Nota metodologica",
        "",
        "Los codigos HTTP son los que el servicio devolvio realmente. La prueba",
        "crea y luego cancela una reserva identificada con la nota",
        f"`{NOTA}`. La proteccion se apoya en `SELECT ... FOR UPDATE` sobre",
        "el espacio dentro de una transaccion (`Reservation.save`) mas la validacion",
        "`Space.is_available_at`.",
        "",
    ]
    (DIR_EVIDENCIAS / "concurrencia_reservas.md").write_text(
        "\n".join(lineas), encoding="utf-8")


def main() -> int:
    if not (CLAVE_CLIENTE1 and CLAVE_CLIENTE2):
        raise SystemExit("Faltan FH_PASS_CLIENTE1 / FH_PASS_CLIENTE2 en el entorno.")

    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    sello = datetime.now(dt_tz.utc).isoformat(timespec="seconds")

    token1 = login(USUARIO_CLIENTE1, CLAVE_CLIENTE1)
    token2 = login(USUARIO_CLIENTE2, CLAVE_CLIENTE2)
    tokens = [(USUARIO_CLIENTE1, token1), (USUARIO_CLIENTE2, token2)]

    espacio = elegir_espacio(token1)
    fecha, ini, fin = elegir_franja(token1, espacio["id"])

    print("=" * 78)
    print("PRUEBA DE CONCURRENCIA - ANTI-SOLAPAMIENTO DE RESERVAS")
    print(f"URL: {BASE}")
    print(f"Fecha/hora (UTC): {sello}")
    print(f"Espacio: {espacio['code']} (id={espacio['id']})")
    print(f"Franja: {ini.isoformat()} -> {fin.isoformat()}")
    print(f"Solicitudes simultaneas: {n}")
    print("=" * 78)

    peticiones = lanzar_peticiones(n, espacio["id"], ini, fin, tokens)
    aceptadas = sum(1 for p in peticiones if p["http"] == 201)
    rechazadas = sum(1 for p in peticiones if p["http"] == 400)
    otras = len(peticiones) - aceptadas - rechazadas

    activas = reservas_activas_en_bd(token1, espacio["id"], ini, fin)

    # Limpieza: cancelar la reserva aceptada con el token de su propietario.
    limpieza = []
    ganadoras = [p for p in peticiones if p["http"] == 201 and p["reserva_id"]]
    for p in ganadoras:
        token_ganador = token1 if p["usuario"] == USUARIO_CLIENTE1 else token2
        r = requests.post(
            f"{API}/reservations/reservations/{p['reserva_id']}/cancel/",
            headers=cabecera(token_ganador),
            json={"reason": "Fin de la prueba de concurrencia"}, timeout=TIMEOUT)
        limpieza.append({"id": p["reserva_id"], "http": r.status_code})

    veredicto = "PASS" if (
        aceptadas == 1 and rechazadas == n - 1 and otras == 0
        and len(activas) == 1
    ) else "FAIL"

    for p in peticiones:
        print(f"  #{p['indice']} {p['usuario']} HTTP {p['http']} "
              f"({p['segundos']}s) id={p['reserva_id']}")
    print(f">>> aceptadas={aceptadas} rechazadas={rechazadas} otras={otras} "
          f"activas_en_bd={len(activas)}")
    print(f">>> limpieza: {limpieza}")
    print(f">>> Veredicto: {veredicto}")

    datos = {
        "fecha_ejecucion": sello,
        "url": BASE,
        "tipo_prueba": "concurrencia - mismo espacio y misma franja horaria",
        "n_solicitudes_simultaneas": n,
        "clientes": [USUARIO_CLIENTE1, USUARIO_CLIENTE2],
        "espacio": {"id": espacio["id"], "code": espacio["code"],
                    "name": espacio.get("name")},
        "fecha": fecha,
        "franja": {"inicio": ini.isoformat(), "fin": fin.isoformat()},
        "aceptadas_201": aceptadas,
        "rechazadas_400": rechazadas,
        "otras_respuestas": otras,
        "reservas_activas_en_bd": len(activas),
        "reservas_en_bd_detalle": activas,
        "limpieza_cancelaciones": limpieza,
        "veredicto": veredicto,
        "peticiones": peticiones,
    }
    exportar(sello, datos)
    print(f"    archivos: {DIR_EVIDENCIAS / 'concurrencia_reservas.md'} / .json")
    return 0 if veredicto == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
