"""
Benchmark controlado del aplicativo (punto 7 del cierre tecnico).

Mide, contra la version final desplegada, los tiempos reales de los escenarios
operativos equivalentes a la linea base manual:

    S1  consultar disponibilidad
    S2  registrar una reserva (creacion + confirmacion del estado en BD)
    S3  detectar solapamiento (la segunda reserva debe ser rechazada)
    S4  cancelar la reserva registrada

Cada iteracion se ejecuta realmente contra la API. Al final, TODAS las reservas
creadas se eliminan para no dejar datos de prueba en la base operativa.

Los valores NO se inventan: cada fila del CSV procede de una peticion HTTP real.
La columna `linea_base_manual` queda vacia para incorporar, si se dispone de
ella, la medicion manual documentada externamente.

Uso:
    python tests/benchmark_aplicativo.py
    (las credenciales se leen de .env.evidencias o de variables FH_*)

Salidas:
    evidencias/benchmark_aplicativo.csv
    evidencias/benchmark_aplicativo.md
    evidencias/benchmark_iteraciones.csv
"""
from __future__ import annotations

import csv
import json
import os
import statistics
import sys
import time
from datetime import datetime, timedelta, timezone as dt_tz
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from credenciales import cargar_en_entorno  # noqa: E402

cargar_en_entorno()

RAIZ = Path(__file__).resolve().parent.parent
DIR_EV = RAIZ / "evidencias"
DIR_EV.mkdir(exist_ok=True)

BASE = os.getenv("FH_BASE", "https://familyhealthmf-production.up.railway.app").rstrip("/")
API = f"{BASE}/api/v1"
TIMEOUT = 90
ITERACIONES = int(os.getenv("BENCH_ITERS", "30"))

USUARIO_ADMIN = os.getenv("FH_USER_ADMIN", "admin_fh")
CLAVE_ADMIN = os.getenv("FH_PASS_ADMIN", "")

NOTA = "BENCHMARK CONTROLADO - dato de prueba controlado"
HUSO = dt_tz(timedelta(hours=-5))  # America/Bogota

ITERACIONES_CSV: list[dict] = []


def cabecera(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"} if token else {}


def login(usuario: str, clave: str) -> str:
    r = requests.post(f"{API}/auth/login/",
                      json={"username": usuario, "password": clave}, timeout=TIMEOUT)
    if r.status_code != 200:
        raise SystemExit(f"Login fallido para {usuario} (HTTP {r.status_code}).")
    return r.json()["access"]


def registrar(escenario: str, iteracion: int, inicio: datetime, t0: float,
              t1: float, resultado: str, http, estado_bd: str,
              pass_fail: str, observacion: str = "") -> None:
    ITERACIONES_CSV.append({
        "escenario": escenario,
        "iteracion": iteracion,
        "inicio": inicio.isoformat(timespec="milliseconds"),
        "fin": datetime.now(HUSO).isoformat(timespec="milliseconds"),
        "duracion_ms": round((t1 - t0) * 1000, 2),
        "resultado": resultado,
        "http": "" if http is None else str(http),
        "estado_final_bd": estado_bd,
        "pass_fail": pass_fail,
        "observacion": observacion,
    })


def preparar_espacio_y_cliente(h: dict) -> tuple[dict, int]:
    r = requests.get(f"{API}/reservations/spaces/", headers=h, timeout=TIMEOUT)
    r.raise_for_status()
    espacios = r.json()
    if isinstance(espacios, dict):
        espacios = espacios.get("results", [])
    activos = [e for e in espacios if e.get("status") == "ACTIVE"]
    if not activos:
        raise SystemExit("No hay espacios ACTIVOS en la version evaluada.")
    # Se usa el primer espacio activo cuyo catalogo sea estable para el benchmark.
    espacio = activos[0]

    ru = requests.get(f"{API}/auth/admin/users/", headers=h,
                      params={"role": "CLIENT"}, timeout=TIMEOUT)
    usuarios = ru.json() if ru.status_code == 200 else []
    if isinstance(usuarios, dict):
        usuarios = usuarios.get("results", [])
    clientes = [u for u in usuarios if u.get("role") == "CLIENT"
                and u.get("is_active", True)]
    if not clientes:
        raise SystemExit("No hay usuarios CLIENT activos para agendar la reserva.")
    return espacio, clientes[0]["id"]


def fecha_hora_base() -> datetime:
    """Fecha futura y hora de baja operacion para aislar los datos de prueba."""
    dia = datetime.now(HUSO).date() + timedelta(days=120)
    return datetime(dia.year, dia.month, dia.day, 3, 0, 0, tzinfo=HUSO)


def main() -> int:
    if not CLAVE_ADMIN:
        raise SystemExit("Falta FH_PASS_ADMIN (variable de entorno o .env.evidencias).")

    token = login(USUARIO_ADMIN, CLAVE_ADMIN)
    h = cabecera(token)
    espacio, cliente_id = preparar_espacio_y_cliente(h)
    base_dt = fecha_hora_base()
    duracion_min = max(espacio.get("min_reservation_minutes", 30), 30)
    sello = datetime.now(dt_tz.utc).isoformat(timespec="seconds")

    print("=" * 78)
    print("BENCHMARK CONTROLADO - CLUB FAMILY HEALTH MF")
    print(f"URL: {BASE}")
    print(f"Fecha/hora (UTC): {sello}")
    print(f"Espacio: {espacio['code']} (id={espacio['id']})  "
          f"cliente_id={cliente_id}  iteraciones por escenario={ITERACIONES}")
    print(f"Franja de prueba: {base_dt.date().isoformat()} 03:00 (America/Bogota)")
    print("=" * 78)

    creadas: list[int] = []
    resultados: dict[str, list[dict]] = {
        "S1_consultar_disponibilidad": [],
        "S2_registrar_reserva": [],
        "S3_detectar_solapamiento": [],
        "S4_cancelar_reserva": [],
    }

    try:
        # ---------------- S1: consultar disponibilidad ----------------
        for i in range(1, ITERACIONES + 1):
            fecha = (base_dt.date() + timedelta(days=i)).isoformat()
            inicio = datetime.now(HUSO)
            t0 = time.perf_counter()
            r = requests.get(
                f"{API}/reservations/spaces/{espacio['id']}/availability/",
                headers=h, params={"date": fecha}, timeout=TIMEOUT)
            t1 = time.perf_counter()
            ok = r.status_code == 200
            registrar("S1_consultar_disponibilidad", i, inicio, t0, t1,
                      "200 OK" if ok else f"HTTP {r.status_code}", r.status_code,
                      "n/a (consulta)", "PASS" if ok else "FAIL")
            resultados["S1_consultar_disponibilidad"].append(
                {"ms": (t1 - t0) * 1000, "ok": ok, "http": r.status_code})

        # ---------------- S2: registrar reserva ----------------
        for i in range(1, ITERACIONES + 1):
            ini_slot = base_dt + timedelta(days=i)
            fin_slot = ini_slot + timedelta(minutes=duracion_min)
            cuerpo = {
                "space_id": espacio["id"],
                "user_id": cliente_id,
                "start_time": ini_slot.isoformat(),
                "end_time": fin_slot.isoformat(),
                "guests_count": 1,
                "notes": f"{NOTA} iter={i}",
            }
            inicio = datetime.now(HUSO)
            t0 = time.perf_counter()
            r = requests.post(f"{API}/reservations/reservations/", headers=h,
                              json=cuerpo, timeout=TIMEOUT)
            t1 = time.perf_counter()
            http = r.status_code
            rid = None
            estado = "no persistida"
            if http == 201:
                rid = r.json().get("id")
                creadas.append(rid)
                # verificacion 1: lectura posterior del estado real
                rv = requests.get(f"{API}/reservations/reservations/{rid}/",
                                  headers=h, timeout=TIMEOUT)
                estado = rv.json().get("status", "?") if rv.status_code == 200 else f"HTTP {rv.status_code}"
            ok = http == 201 and estado in ("CONFIRMED", "PENDING")
            registrar("S2_registrar_reserva", i, inicio, t0, t1,
                      f"HTTP {http}", http, estado, "PASS" if ok else "FAIL",
                      f"id={rid} verificaciones=1")
            resultados["S2_registrar_reserva"].append(
                {"ms": (t1 - t0) * 1000, "ok": ok, "http": http, "id": rid})

        # ---------------- S3: detectar solapamiento ----------------
        pares_ok = 0
        for i in range(1, ITERACIONES + 1):
            ini_slot = base_dt + timedelta(days=i)
            fin_slot = ini_slot + timedelta(minutes=duracion_min)
            cuerpo = {
                "space_id": espacio["id"],
                "user_id": cliente_id,
                "start_time": ini_slot.isoformat(),
                "end_time": fin_slot.isoformat(),
                "guests_count": 1,
                "notes": f"{NOTA} solapamiento iter={i}",
            }
            inicio = datetime.now(HUSO)
            t0 = time.perf_counter()
            r = requests.post(f"{API}/reservations/reservations/", headers=h,
                              json=cuerpo, timeout=TIMEOUT)
            t1 = time.perf_counter()
            http = r.status_code
            # Verificacion en BD: cuantas reservas activas existen en la franja.
            # Se filtra por la fecha exacta del intento para no depender de la
            # paginacion del listado (20 por pagina).
            rl = requests.get(f"{API}/reservations/reservations/", headers=h,
                              params={"space_id": espacio["id"],
                                      "date_from": ini_slot.date().isoformat(),
                                      "date_to": ini_slot.date().isoformat()},
                              timeout=TIMEOUT)
            activas = 0
            if rl.status_code == 200:
                datos = rl.json()
                lista = datos.get("results", datos) if isinstance(datos, dict) else datos
                for res in lista:
                    if (res.get("start_time") == ini_slot.isoformat()
                            and res.get("status") in ("CONFIRMED", "PENDING")):
                        activas += 1
            rechazada = http == 400
            persistidas = 1 if rechazada and activas == 1 else activas
            if rechazada and persistidas == 1:
                pares_ok += 1
            registrar("S3_detectar_solapamiento", i, inicio, t0, t1,
                      "rechazada 400" if rechazada else f"HTTP {http}", http,
                      f"reservas activas en la franja={persistidas}",
                      "PASS" if (rechazada and persistidas == 1) else "FAIL")
            resultados["S3_detectar_solapamiento"].append(
                {"ms": (t1 - t0) * 1000, "ok": rechazada and persistidas == 1,
                 "http": http, "tamano_franja": persistidas})

        # ---------------- S4: cancelar reserva ----------------
        for i, rid in enumerate(creadas[:ITERACIONES], start=1):
            inicio = datetime.now(HUSO)
            t0 = time.perf_counter()
            r = requests.post(f"{API}/reservations/reservations/{rid}/cancel/",
                              headers=h, json={"reason": f"{NOTA} fin de benchmark"},
                              timeout=TIMEOUT)
            t1 = time.perf_counter()
            http = r.status_code
            estado = "?"
            if http == 200:
                estado = r.json().get("status", "?")
            ok = http == 200 and estado == "CANCELLED"
            registrar("S4_cancelar_reserva", i, inicio, t0, t1,
                      f"HTTP {http}", http, estado, "PASS" if ok else "FAIL",
                      f"id={rid}")
            resultados["S4_cancelar_reserva"].append(
                {"ms": (t1 - t0) * 1000, "ok": ok, "http": http, "id": rid})
    finally:
        # ---------------- Limpieza: eliminar datos de prueba ----------------
        eliminadas, fallos = 0, 0
        for rid in creadas:
            rd = requests.delete(f"{API}/reservations/reservations/{rid}/",
                                 headers=h, timeout=TIMEOUT)
            if rd.status_code in (204, 200):
                eliminadas += 1
            else:
                fallos += 1
        print(f">>> limpieza: {eliminadas} reservas de prueba eliminadas, {fallos} fallos")
        resumen = construir_resumen(resultados, pares_ok, eliminadas, fallos)
        exportar(sello, espacio, base_dt, resumen, eliminadas, fallos)

    # Verificacion final: no deben quedar datos de prueba
    rr = requests.get(f"{API}/reservations/reservations/", headers=h,
                      params={"space_id": espacio["id"]}, timeout=TIMEOUT)
    restantes = 0
    if rr.status_code == 200:
        datos = rr.json()
        lista = datos.get("results", datos) if isinstance(datos, dict) else datos
        restantes = sum(1 for x in lista
                        if NOTA in (x.get("notes") or ""))
    print(f">>> datos de prueba remanentes en BD: {restantes}")
    return 0


def construir_resumen(resultados: dict, pares_ok: int, eliminadas: int,
                      fallos: int) -> list[dict]:
    filas = []
    for escenario, items in resultados.items():
        if not items:
            continue
        tiempos = [x["ms"] for x in items]
        exitos = sum(1 for x in items if x["ok"])
        filas.append({
            "escenario": escenario,
            "n": len(items),
            "media_ms": round(statistics.mean(tiempos), 2),
            "mediana_ms": round(statistics.median(tiempos), 2),
            "min_ms": round(min(tiempos), 2),
            "max_ms": round(max(tiempos), 2),
            "desviacion_ms": round(statistics.pstdev(tiempos), 2) if len(tiempos) > 1 else 0.0,
            "exito_pct": round(exitos / len(items) * 100, 2),
            "conflictos_persistidos_pct": (
                0.0 if escenario != "S3_detectar_solapamiento"
                else round((len(items) - pares_ok) / len(items) * 100, 2)),
            "resolucion_primer_intento_pct": round(exitos / len(items) * 100, 2),
            "reprocesos_tecnicos": 0,
            "linea_base_manual": "",
        })
    return filas


def exportar(sello: str, espacio: dict, base_dt: datetime, resumen: list[dict],
             eliminadas: int, fallos: int) -> None:
    # 1) Detalle por iteracion
    ruta_it = DIR_EV / "benchmark_iteraciones.csv"
    with ruta_it.open("w", newline="", encoding="utf-8-sig") as fh:
        campos = ["escenario", "iteracion", "inicio", "fin", "duracion_ms",
                  "resultado", "http", "estado_final_bd", "pass_fail", "observacion"]
        w = csv.DictWriter(fh, fieldnames=campos)
        w.writeheader()
        w.writerows(ITERACIONES_CSV)

    # 2) Resumen agregado
    ruta_csv = DIR_EV / "benchmark_aplicativo.csv"
    with ruta_csv.open("w", newline="", encoding="utf-8-sig") as fh:
        campos = ["escenario", "n", "media_ms", "mediana_ms", "min_ms", "max_ms",
                  "desviacion_ms", "exito_pct", "conflictos_persistidos_pct",
                  "resolucion_primer_intento_pct", "reprocesos_tecnicos",
                  "linea_base_manual"]
        w = csv.DictWriter(fh, fieldnames=campos)
        w.writeheader()
        w.writerows(resumen)

    lineas = [
        "# Benchmark controlado del aplicativo",
        "",
        "> Family Health MF · cierre tecnico de la version final · punto 7",
        "",
        f"- **Version evaluada:** despliegue de Railway `{BASE}`",
        f"- **Fecha/hora (UTC):** {sello}",
        f"- **Escenarios ejecutados:** {len(resumen)}",
        f"- **Iteraciones por escenario:** {ITERACIONES}",
        f"- **Espacio utilizado:** `{espacio['code']}` (id={espacio['id']})",
        f"- **Franja aislada de prueba:** {base_dt.date().isoformat()} 03:00 en adelante"
        " (America/Bogota)",
        f"- **Reservas de prueba creadas y eliminadas:** {eliminadas}"
        f" (fallos de limpieza: {fallos})",
        "",
        "Todos los tiempos son mediciones reales obtenidas con el reloj monotono",
        "(`time.perf_counter`) sobre peticiones HTTP reales contra la API desplegada.",
        "No se declara ningun resultado que no provenga de una ejecucion efectiva.",
        "",
        "## Resumen",
        "",
        "| Escenario | n | Media (ms) | Mediana (ms) | Min (ms) | Max (ms) | Desv. (ms) | Exito % | Conflictos persistidos % | Resolucion 1er intento % | Reprocesos tecnicos | Linea base manual |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for f in resumen:
        lineas.append(
            f"| {f['escenario']} | {f['n']} | {f['media_ms']} | {f['mediana_ms']} | "
            f"{f['min_ms']} | {f['max_ms']} | {f['desviacion_ms']} | {f['exito_pct']} | "
            f"{f['conflictos_persistidos_pct']} | {f['resolucion_primer_intento_pct']} | "
            f"{f['reprocesos_tecnicos']} | {f['linea_base_manual'] or '(no proporcionada)'} |")

    lineas += [
        "",
        "## Correspondencia con los indicadores solicitados",
        "",
        "| Indicador solicitado | Escenario que lo mide |",
        "|---|---|",
        "| Tiempo para consultar disponibilidad | `S1_consultar_disponibilidad` |",
        "| Tiempo para registrar una reserva | `S2_registrar_reserva` |",
        "| Tiempo hasta confirmacion/rechazo | `S2_registrar_reserva` (lectura posterior del estado) |",
        "| Numero de verificaciones necesarias | 1 lectura de verificacion por reserva |",
        "| Conflictos persistidos | `S3_detectar_solapamiento` |",
        "| Reprocesos tecnicos | columna `reprocesos_tecnicos` (0 = ningun reintento) |",
        "| Resolucion en primer intento | `resolucion_primer_intento_pct` |",
        "",
        "## Notas metodologicas",
        "",
        "- Los tiempos incluyen la latencia de red real entre el equipo de medicion y",
        "  el despliegue de Railway, por lo que representan el tiempo percibido por el",
        "  usuario final.",
        "- La franja `03:00` sobre una fecha a 120 dias se eligio para aislar los datos",
        "  de prueba de la operacion real; todas las reservas creadas se eliminan al",
        "  terminar (`DELETE` con rol administrador) y se verifica que no queden restos.",
        "- La columna `linea_base_manual` queda vacia a proposito: no se inventan",
        "  valores de la linea base manual.",
        "",
        "## Comandos de reproduccion",
        "",
        "```powershell",
        "cd c:\\Family_Health_MF",
        "$env:BENCH_ITERS=\"30\"",
        ".venv\\Scripts\\python.exe tests\\benchmark_aplicativo.py",
        "```",
        "",
        f"- Detalle por iteracion: `evidencias/benchmark_iteraciones.csv`",
    ]
    (DIR_EV / "benchmark_aplicativo.md").write_text("\n".join(lineas), encoding="utf-8")

    print()
    print(">>> RESUMEN BENCHMARK")
    for f in resumen:
        print(f"    {f['escenario']}: n={f['n']} media={f['media_ms']}ms "
              f"mediana={f['mediana_ms']}ms exito={f['exito_pct']}%")
    print(f"    archivos: {ruta_csv.name}, benchmark_aplicativo.md, {ruta_it.name}")


if __name__ == "__main__":
    sys.exit(main())
