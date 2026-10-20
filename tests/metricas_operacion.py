"""
Metricas operativas REALES del aplicativo (punto 6 del cierre tecnico).

Consulta el despliegue de Railway con credenciales de administrador y calcula
UNICAMENTE los indicadores que pueden derivarse legitimamente de los datos
expuestos por la API (misma fuente que usa la base de datos PostgreSQL).

No se inventan valores: todos los resultados provienen de las respuestas HTTP
reales. Los indicadores que el software NO registra (por ejemplo tiempos de
atencion) se excluyen y se documentan como limitacion.

Uso:
    $env:FH_PASS_ADMIN="..."; python tests/metricas_operacion.py

Salidas:
    evidencias/metricas_operacion_real.csv
    evidencias/metricas_operacion_real.md
    evidencias/metricas_operacion_raw.json
"""
from __future__ import annotations

import json
import os
import statistics
import sys
from collections import Counter
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

INDICADORES: list[dict] = []
CRUDOS: dict = {}


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


def agregar(ident: str, nombre: str, formula: str, fuente: str, consulta: str,
            periodo: str, muestra, resultado) -> None:
    INDICADORES.append({
        "id": ident,
        "indicador": nombre,
        "formula": formula,
        "fuente": fuente,
        "consulta": consulta,
        "periodo": periodo,
        "tamano_muestra": str(muestra),
        "resultado": str(resultado),
    })
    print(f"[MET] {ident} {nombre} = {resultado}  (muestra={muestra})")


def main() -> int:  # noqa: WPS231
    if not CLAVE_ADMIN:
        raise SystemExit("Falta FH_PASS_ADMIN en el entorno.")
    token = login_admin()
    h = cabecera(token)
    sello = datetime.now(timezone.utc).isoformat(timespec="seconds")
    print("=" * 74)
    print("METRICAS OPERATIVAS REALES - CLUB FAMILY HEALTH MF")
    print(f"URL: {BASE}")
    print(f"Fecha/hora (UTC): {sello}")
    print("=" * 74)

    # ---------- Fuente 1: resumen del panel ----------
    r = requests.get(f"{API}/reports/dashboard/summary/", headers=h, timeout=TIMEOUT)
    resumen = r.json() if r.status_code == 200 else {}
    CRUDOS["dashboard_summary"] = resumen
    print(f">>> dashboard/summary -> HTTP {r.status_code}")

    # ---------- Fuente 2: reservas por fecha (30 dias) ----------
    r = requests.get(f"{API}/reports/dashboard/reservations-by-date/",
                     params={"days": 30}, headers=h, timeout=TIMEOUT)
    serie = r.json() if r.status_code == 200 else []
    CRUDOS["reservations_by_date"] = serie
    print(f">>> reservations-by-date -> HTTP {r.status_code} ({len(serie)} fechas)")

    # ---------- Fuente 3: listado completo de reservas ----------
    reservas = obtener_todo(f"{API}/reservations/reservations/", h)
    CRUDOS["reservations_total_enumeradas"] = len(reservas)
    print(f">>> reservations/ -> {len(reservas)} reservas enumeradas")

    # ---------- Fuente 4: ranking de clientes ----------
    r = requests.get(f"{API}/reports/dashboard/top-clients/", params={"n": 20},
                     headers=h, timeout=TIMEOUT)
    top = r.json() if r.status_code == 200 else []
    CRUDOS["top_clients"] = top
    print(f">>> top-clients -> HTTP {r.status_code} ({len(top)} clientes)")

    # ---------- Fuente 5: usuarios ----------
    usuarios = obtener_todo(f"{API}/auth/admin/users/", h)
    CRUDOS["usuarios_enumerados"] = len(usuarios)
    print(f">>> admin/users -> {len(usuarios)} usuarios enumerados")

    # ======================= INDICADORES =======================

    # --- Panel (fuente: dashboard/summary) ---
    agregar("M01", "Usuarios activos totales", "count(is_active=True)",
            "API /reports/dashboard/summary/ -> users_total",
            "GET /api/v1/reports/dashboard/summary/", "Actual", resumen.get("users_total"),
            resumen.get("users_total"))
    agregar("M02", "Clientes activos", "count(role=CLIENT, is_active=True)",
            "API /reports/dashboard/summary/ -> clients_total",
            "GET /api/v1/reports/dashboard/summary/", "Actual", resumen.get("clients_total"),
            resumen.get("clients_total"))
    agregar("M03", "Empleados activos (recepción/cafetería)", "count(role=EMPLOYEE, is_active=True)",
            "API /reports/dashboard/summary/ -> employees_total",
            "GET /api/v1/reports/dashboard/summary/", "Actual", resumen.get("employees_total"),
            resumen.get("employees_total"))
    agregar("M04", "Clientes nuevos en los últimos 30 días",
            "count(role=CLIENT, created_at >= hoy-30d)",
            "API /reports/dashboard/summary/ -> new_clients_last_30_days",
            "GET /api/v1/reports/dashboard/summary/", "Últimos 30 días",
            resumen.get("new_clients_last_30_days"), resumen.get("new_clients_last_30_days"))
    agregar("M05", "Reservas registradas (histórico)", "count(Reservation)",
            "API /reports/dashboard/summary/ -> reservations_total",
            "GET /api/v1/reports/dashboard/summary/", "Histórico completo",
            resumen.get("reservations_total"), resumen.get("reservations_total"))
    agregar("M06", "Reservas con inicio hoy", "count(start_time__date=hoy)",
            "API /reports/dashboard/summary/ -> reservations_today",
            "GET /api/v1/reports/dashboard/summary/", "Hoy", resumen.get("reservations_today"),
            resumen.get("reservations_today"))
    agregar("M07", "Reservas confirmadas", "count(status=CONFIRMED)",
            "API /reports/dashboard/summary/ -> reservations_confirmed",
            "GET /api/v1/reports/dashboard/summary/", "Histórico completo",
            resumen.get("reservations_confirmed"), resumen.get("reservations_confirmed"))
    agregar("M08", "Reservas pendientes de aprobación", "count(status=PENDING)",
            "API /reports/dashboard/summary/ -> reservations_pending",
            "GET /api/v1/reports/dashboard/summary/", "Histórico completo",
            resumen.get("reservations_pending"), resumen.get("reservations_pending"))
    agregar("M09", "Reservas canceladas", "count(status=CANCELLED)",
            "API /reports/dashboard/summary/ -> reservations_cancelled",
            "GET /api/v1/reports/dashboard/summary/", "Histórico completo",
            resumen.get("reservations_cancelled"), resumen.get("reservations_cancelled"))
    agregar("M10", "Ocupación de los últimos 7 días (%)",
            "sum(total_minutes confirmadas+completadas 7d) / 10080 * 100",
            "API /reports/dashboard/summary/ -> occupancy_rate_last_7",
            "GET /api/v1/reports/dashboard/summary/", "Últimos 7 días",
            resumen.get("reservations_confirmed"), resumen.get("occupancy_rate_last_7"))
    agregar("M11", "Pedidos de refresquería registrados", "count(Order)",
            "API /reports/dashboard/summary/ -> orders_total",
            "GET /api/v1/reports/dashboard/summary/", "Histórico completo",
            resumen.get("orders_total"), resumen.get("orders_total"))
    agregar("M12", "Pedidos creados hoy", "count(Order, created_at__date=hoy)",
            "API /reports/dashboard/summary/ -> orders_today",
            "GET /api/v1/reports/dashboard/summary/", "Hoy", resumen.get("orders_today"),
            resumen.get("orders_today"))
    agregar("M13", "Ingresos por pedidos del mes (COP)",
            "sum(total_amount) de pedidos PAID del mes",
            "API /reports/dashboard/summary/ -> orders_revenue_month",
            "GET /api/v1/reports/dashboard/summary/", "Mes en curso",
            resumen.get("orders_total"), resumen.get("orders_revenue_month"))
    agregar("M14", "Ingresos por reservas del mes (COP)",
            "sum(total_amount) de reservas PAID del mes",
            "API /reports/dashboard/summary/ -> reservations_revenue_month",
            "GET /api/v1/reports/dashboard/summary/", "Mes en curso",
            resumen.get("reservations_total"), resumen.get("reservations_revenue_month"))
    agregar("M15", "Puntos de fidelización distribuidos",
            "sum(amount) transacciones EARN",
            "API /reports/dashboard/summary/ -> points_distributed",
            "GET /api/v1/reports/dashboard/summary/", "Histórico completo",
            resumen.get("clients_total"), resumen.get("points_distributed"))
    agregar("M16", "Puntos de fidelización redimidos",
            "abs(sum(amount) transacciones REDEEM)",
            "API /reports/dashboard/summary/ -> points_redeemed",
            "GET /api/v1/reports/dashboard/summary/", "Histórico completo",
            resumen.get("clients_total"), resumen.get("points_redeemed"))
    agregar("M17", "Registros de gimnasio en 30 días", "count(WorkoutLog session_date >= hoy-30d)",
            "API /reports/dashboard/summary/ -> gym_logs_last_30",
            "GET /api/v1/reports/dashboard/summary/", "Últimos 30 días",
            resumen.get("clients_total"), resumen.get("gym_logs_last_30"))

    # --- Listado enumerado de reservas ---
    estados = Counter(r_.get("status") for r_ in reservas)
    pagos = Counter(r_.get("payment_status") for r_ in reservas)
    total_res = len(reservas)
    creados = [r_["created_at"] for r_ in reservas if r_.get("created_at")]
    modificados = [r_ for r_ in reservas
                   if r_.get("updated_at") and r_.get("created_at")
                   and r_["updated_at"] > r_["created_at"]]
    de_prueba = [r_ for r_ in reservas
                 if "prueba controlado" in (r_.get("notes") or "").lower()
                 or "validacion railway" in (r_.get("notes") or "").lower()]

    agregar("M18", "Reservas rechazadas", "count(status=REJECTED)",
            "API /reservations/reservations/ (enumeración paginada)",
            "GET /api/v1/reservations/reservations/?page=N", "Histórico completo",
            total_res, estados.get("REJECTED", 0))
    agregar("M19", "Reservas completadas", "count(status=COMPLETED)",
            "API /reservations/reservations/ (enumeración paginada)",
            "GET /api/v1/reservations/reservations/?page=N", "Histórico completo",
            total_res, estados.get("COMPLETED", 0))
    agregar("M20", "Reservas con inasistencia", "count(status=NO_SHOW)",
            "API /reservations/reservations/ (enumeración paginada)",
            "GET /api/v1/reservations/reservations/?page=N", "Histórico completo",
            total_res, estados.get("NO_SHOW", 0))
    agregar("M21", "Total de reservas enumeradas (control de consistencia)",
            "len(enumeración paginada)",
            "API /reservations/reservations/",
            "GET /api/v1/reservations/reservations/?page=N", "Histórico completo",
            total_res, total_res)
    agregar("M22", "Tasa de cancelación (%)",
            "canceladas / total * 100",
            "API /reservations/reservations/ (enumeración paginada)",
            "GET /api/v1/reservations/reservations/?page=N", "Histórico completo",
            f"{total_res} reservas", 0.0 if total_res == 0
            else round(estados.get("CANCELLED", 0) / total_res * 100, 2))
    agregar("M23", "Tasa de rechazo (%)",
            "rechazadas / total * 100",
            "API /reservations/reservations/ (enumeración paginada)",
            "GET /api/v1/reservations/reservations/?page=N", "Histórico completo",
            f"{total_res} reservas", 0.0 if total_res == 0
            else round(estados.get("REJECTED", 0) / total_res * 100, 2))
    agregar("M24", "Reservas modificadas después de su creación",
            "count(updated_at > created_at)",
            "API /reservations/reservations/ (updated_at/created_at)",
            "GET /api/v1/reservations/reservations/?page=N", "Histórico completo",
            total_res, len(modificados))
    agregar("M25", "Reservas pagadas", "count(payment_status=PAID)",
            "API /reservations/reservations/ (payment_status)",
            "GET /api/v1/reservations/reservations/?page=N", "Histórico completo",
            total_res, pagos.get("PAID", 0))
    agregar("M26", "Reservas identificadas como dato de prueba controlado",
            "count(notes contiene 'dato de prueba controlado'/'validacion railway')",
            "API /reservations/reservations/ (notes)",
            "GET /api/v1/reservations/reservations/?page=N", "Histórico completo",
            total_res, len(de_prueba))
    agregar("M27", "Reservas operativas (excluye datos de prueba controlados)",
            "total - datos_de_prueba",
            "API /reservations/reservations/",
            "GET /api/v1/reservations/reservations/?page=N", "Histórico completo",
            total_res, total_res - len(de_prueba))

    if creados:
        c_ord = sorted(creados)
        agregar("M28", "Primera reserva registrada (created_at)", "min(created_at)",
                "API /reservations/reservations/ (created_at)",
                "GET /api/v1/reservations/reservations/?page=N", "Histórico completo",
                total_res, c_ord[0])
        agregar("M29", "Última reserva registrada (created_at)", "max(created_at)",
                "API /reservations/reservations/ (created_at)",
                "GET /api/v1/reservations/reservations/?page=N", "Histórico completo",
                total_res, c_ord[-1])
        dias = sorted({c[:10] for c in creados})
        agregar("M30", "Días distintos con creación de reservas", "count(distinct date(created_at))",
                "API /reservations/reservations/ (created_at)",
                "GET /api/v1/reservations/reservations/?page=N", "Histórico completo",
                total_res, len(dias))

    # --- Serie por fecha ---
    if serie:
        dias_activos = [d for d in serie if (d.get("total") or 0) > 0]
        totales = [d.get("total") or 0 for d in dias_activos]
        agregar("M31", "Días con al menos una reserva (últimos 30 días)",
                "count(días con total>0)",
                "API /reports/dashboard/reservations-by-date/?days=30",
                "GET /api/v1/reports/dashboard/reservations-by-date/?days=30",
                "Últimos 30 días", len(serie), len(dias_activos))
        agregar("M32", "Promedio de reservas por día con actividad",
                "mean(total de días con actividad)",
                "API /reports/dashboard/reservations-by-date/?days=30",
                "GET /api/v1/reports/dashboard/reservations-by-date/?days=30",
                "Últimos 30 días", len(dias_activos),
                round(statistics.mean(totales), 2) if totales else 0)
        agregar("M33", "Cancelaciones registradas en la serie de 30 días",
                "sum(cancelled)",
                "API /reports/dashboard/reservations-by-date/?days=30",
                "GET /api/v1/reports/dashboard/reservations-by-date/?days=30",
                "Últimos 30 días", len(serie),
                sum(d.get("cancelled") or 0 for d in serie))

    # --- Ranking de clientes ---
    agregar("M34", "Clientes con actividad registrada (ranking)",
            "count(clientes en ranking)",
            "API /reports/dashboard/top-clients/",
            "GET /api/v1/reports/dashboard/top-clients/?n=20", "Histórico completo",
            len(usuarios), len(top))

    # --- Usuarios enumerados ---
    if usuarios:
        roles = Counter(u.get("role") for u in usuarios)
        activos = sum(1 for u in usuarios if u.get("is_active"))
        agregar("M35", "Usuarios totales enumerados (activos + inactivos)",
                "len(enumeración de usuarios)",
                "API /auth/admin/users/", "GET /api/v1/auth/admin/users/?page=N",
                "Histórico completo", len(usuarios), len(usuarios))
        agregar("M36", "Usuarios activos enumerados", "count(is_active=True)",
                "API /auth/admin/users/ (is_active)", "GET /api/v1/auth/admin/users/?page=N",
                "Histórico completo", len(usuarios), activos)
        agregar("M37", "Usuarios con rol CLIENT", "count(role=CLIENT)",
                "API /auth/admin/users/ (role)", "GET /api/v1/auth/admin/users/?page=N",
                "Histórico completo", len(usuarios), roles.get("CLIENT", 0))
        agregar("M38", "Usuarios con rol ADMIN", "count(role=ADMIN)",
                "API /auth/admin/users/ (role)", "GET /api/v1/auth/admin/users/?page=N",
                "Histórico completo", len(usuarios), roles.get("ADMIN", 0))
        agregar("M39", "Usuarios con rol RECEPCION", "count(role=RECEPCION)",
                "API /auth/admin/users/ (role)", "GET /api/v1/auth/admin/users/?page=N",
                "Histórico completo", len(usuarios), roles.get("RECEPCION", 0))
        agregar("M40", "Usuarios con rol CAFETERIA", "count(role=CAFETERIA)",
                "API /auth/admin/users/ (role)", "GET /api/v1/auth/admin/users/?page=N",
                "Histórico completo", len(usuarios), roles.get("CAFETERIA", 0))
        fechas_u = sorted(u["created_at"] for u in usuarios if u.get("created_at"))
        if fechas_u:
            agregar("M41", "Primer usuario registrado (created_at)", "min(created_at)",
                    "API /auth/admin/users/ (created_at)",
                    "GET /api/v1/auth/admin/users/?page=N", "Histórico completo",
                    len(fechas_u), fechas_u[0])
            agregar("M42", "Último usuario registrado (created_at)", "max(created_at)",
                    "API /auth/admin/users/ (created_at)",
                    "GET /api/v1/auth/admin/users/?page=N", "Histórico completo",
                    len(fechas_u), fechas_u[-1])

    exportar(sello)
    return 0


def exportar(sello: str) -> None:
    import csv

    ruta_csv = DIR_EVIDENCIAS / "metricas_operacion_real.csv"
    with ruta_csv.open("w", newline="", encoding="utf-8-sig") as fh:
        campos = ["id", "indicador", "formula", "fuente", "consulta",
                  "periodo", "tamano_muestra", "resultado"]
        w = csv.DictWriter(fh, fieldnames=campos)
        w.writeheader()
        w.writerows(INDICADORES)

    (DIR_EVIDENCIAS / "metricas_operacion_raw.json").write_text(
        json.dumps({"fecha": sello, "url": BASE, "crudos": CRUDOS},
                   ensure_ascii=False, indent=2, default=str),
        encoding="utf-8")

    lineas = [
        "# Métricas operativas reales - Club Family Health MF",
        "",
        "> Cierre técnico de la versión final · punto 6",
        "",
        f"- **Fuente:** API pública de la versión desplegada ({BASE}) consultada con",
        "  credenciales de administrador; la API lee directamente de PostgreSQL.",
        f"- **Fecha/hora de la consulta (UTC):** {sello}",
        f"- **Indicadores calculados:** {len(INDICADORES)}",
        "",
        "Todos los valores provienen de respuestas HTTP reales. Los indicadores que el",
        "software no registra (por ejemplo tiempos de atención) no se calculan y se",
        "documentan en la sección de limitaciones del informe final.",
        "",
        "> Nota: las cuentas creadas para pruebas (`*_fh`, `val_rw_*`, `t_*@prueba.local`)",
        "> son **datos de prueba/controlados** y NO se presentan como usuarios reales.",
        "> Las reservas con nota identificada como dato de prueba controlado se contabilizan",
        "> por separado (M26/M27).",
        "",
        "| ID | Indicador | Fórmula | Fuente exacta | Consulta utilizada | Periodo | Muestra | Resultado |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for it in INDICADORES:
        lineas.append(
            f"| {it['id']} | {it['indicador']} | `{it['formula']}` | {it['fuente']} | "
            f"`{it['consulta']}` | {it['periodo']} | {it['tamano_muestra']} | **{it['resultado']}** |"
        )

    lineas += [
        "",
        "## Indicadores NO calculables (información que el software no registra)",
        "",
        "- Tiempo de atención por reserva: el modelo no registra marcas de tiempo de",
        "  atención presencial ni duración de gestión.",
        "- Intentos de inicio de sesión y auditoría por rol: el modelo `AuditLog` los",
        "  registra internamente, pero la API de la versión final no expone un endpoint",
        "  de lectura de auditoría, por lo que no pueden derivarse retrospectivamente.",
        "- Tasa de ocupación real por espacio: el resumen calcula una ocupación",
        "  normalizada de 7 días, no una tasa por espacio individual.",
        "",
        "## Comandos de reproducción",
        "",
        "```powershell",
        "cd c:\\Family_Health_MF",
        '$env:FH_PASS_ADMIN="<contraseña demo admin>"',
        ".venv\\Scripts\\python.exe tests\\metricas_operacion.py",
        "```",
        "",
    ]
    (DIR_EVIDENCIAS / "metricas_operacion_real.md").write_text(
        "\n".join(lineas), encoding="utf-8")

    print()
    print(">>> RESUMEN METRICAS")
    print(f"    indicadores: {len(INDICADORES)}")
    print(f"    archivo: {ruta_csv}")


if __name__ == "__main__":
    sys.exit(main())
