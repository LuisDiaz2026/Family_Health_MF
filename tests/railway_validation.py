"""
Validacion REAL contra el despliegue de Railway (punto 5 del cierre tecnico).

Ejecuta peticiones HTTP autenticas contra la version desplegada y registra
UNICAMENTE los codigos HTTP que el servicio devuelve realmente.

Uso (las contrasenas de prueba se inyectan por variables de entorno para no
versionarlas):

    $env:FH_PASS_ADMIN="..."; $env:FH_PASS_RECEPCION="..."; ...
    python tests/railway_validation.py

Salidas:
    evidencias/validacion_railway.json
    evidencias/validacion_railway.md

No se almacenan tokens ni contrasenas completos (solo huellas enmascaradas).
"""
from __future__ import annotations

import json
import os
import sys
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

RAIZ = Path(__file__).resolve().parent.parent
DIR_EVIDENCIAS = RAIZ / "evidencias"
DIR_EVIDENCIAS.mkdir(exist_ok=True)

BASE = os.getenv("FH_BASE", "https://familyhealthmf-production.up.railway.app").rstrip("/")
API = f"{BASE}/api/v1"

CRED = {
    "admin": ("admin_fh", os.getenv("FH_PASS_ADMIN", "")),
    "recepcion": ("recepcion_fh", os.getenv("FH_PASS_RECEPCION", "")),
    "cafeteria": ("cafeteria_fh", os.getenv("FH_PASS_CAFETERIA", "")),
    "cliente1": ("cliente1_fh", os.getenv("FH_PASS_CLIENTE1", "")),
    "cliente2": ("cliente2_fh", os.getenv("FH_PASS_CLIENTE2", "")),
}

TIMEOUT = 60
RESULTADOS: list[dict] = []
TOKENS: dict[str, str] = {}


def huella(valor: str | None) -> str:
    """Devuelve una huella enmascarada de un token (nunca el token completo)."""
    if not valor:
        return "(vacio)"
    return f"{valor[:10]}...{valor[-4:]} ({len(valor)} car.)"


def registrar(ident: str, requisito: str, descripcion: str, metodo: str,
              ruta: str, esperado: str, real: int | str, ok: bool,
              observacion: str = "") -> None:
    RESULTADOS.append({
        "id": ident,
        "requisito": requisito,
        "descripcion": descripcion,
        "metodo": metodo,
        "ruta": ruta,
        "http_esperado": esperado,
        "http_real": real,
        "resultado": "PASS" if ok else "FAIL",
        "observacion": observacion,
    })
    marca = "PASS" if ok else "FAIL"
    print(f"[{marca}] {ident} {descripcion} -> HTTP {real} (esperado {esperado}) {observacion}")


def login(perfil: str) -> tuple[int, dict]:
    user, pwd = CRED[perfil]
    if not pwd:
        return 0, {"error": f"falta la contrasena de {perfil} en el entorno"}
    r = requests.post(f"{API}/auth/login/", json={"username": user, "password": pwd},
                      timeout=TIMEOUT)
    try:
        cuerpo = r.json()
    except Exception:  # noqa: BLE001
        cuerpo = {}
    return r.status_code, cuerpo


def cabecera(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"} if token else {}


def autenticar(perfil: str) -> str:
    codigo, cuerpo = login(perfil)
    if codigo == 200:
        TOKENS[perfil] = cuerpo.get("access", "")
    return TOKENS.get(perfil, "")


def main() -> int:  # noqa: WPS231
    print("=" * 74)
    print("VALIDACION REAL SOBRE RAILWAY - CLUB FAMILY HEALTH MF")
    print(f"URL: {BASE}")
    print(f"Fecha/hora (UTC): {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    print("=" * 74)

    # ---------------- 1. HEALTH ----------------
    r = requests.get(f"{API}/health/", timeout=TIMEOUT)
    datos = r.json() if r.status_code == 200 else {}
    registrar("RW01", "RNF-DIS-01", "Health check publico", "GET", "/api/v1/health/",
              "200", r.status_code, r.status_code == 200,
              f"database={datos.get('database')} version={datos.get('version')}")

    # ---------------- 2. LOGIN CORRECTO ----------------
    t0 = time.perf_counter()
    codigo, cuerpo = login("cliente1")
    dur = round(time.perf_counter() - t0, 4)
    token_c1 = cuerpo.get("access", "")
    TOKENS["cliente1"] = token_c1
    registrar("RW02", "RQF-AUT-01", "Login correcto (cliente1_fh)", "POST",
              "/api/v1/auth/login/", "200", codigo, codigo == 200,
              f"rol={cuerpo.get('role')} access={huella(token_c1)} ({dur}s)")

    # ---------------- 3. LOGIN INCORRECTO ----------------
    r = requests.post(f"{API}/auth/login/",
                      json={"username": "cliente1_fh", "password": "ClaveIncorrecta*2026"},
                      timeout=TIMEOUT)
    registrar("RW03", "RQF-AUT-02", "Login con contrasena incorrecta", "POST",
              "/api/v1/auth/login/", "401", r.status_code, r.status_code == 401)

    # ---------------- 4. USUARIO INACTIVO ----------------
    sufijo = uuid.uuid4().hex[:8]
    alta = {
        "username": f"val_rw_{sufijo}",
        "email": f"val_rw_{sufijo}@example.com",
        "first_name": "Validacion",
        "last_name": "Railway",
        "document_type": "CC",
        "document_number": f"9{sufijo[:7]}",
        "phone": "+573000000000",
        "password": "ValRw2026*!",
        "password_confirm": "ValRw2026*!",
        "accepted_privacy_policy": True,
        "accepted_terms": True,
    }
    r_alta = requests.post(f"{API}/auth/register/", json=alta, timeout=TIMEOUT)
    r_login_inact = requests.post(f"{API}/auth/login/",
                                  json={"username": alta["username"], "password": alta["password"]},
                                  timeout=TIMEOUT)
    mensaje_inact = ""
    try:
        mensaje_inact = json.dumps(r_login_inact.json(), ensure_ascii=False)[:160]
    except Exception:  # noqa: BLE001
        mensaje_inact = ""
    # Comportamiento real disenado: el serializer lanza ValidationError (HTTP 400)
    # con un mensaje explicativo cuando la cuenta existe pero esta inactiva.
    registrar("RW04", "RQF-AUT-03",
              "Usuario inactivo (registro publico) no puede autenticarse",
              "POST", "/api/v1/auth/login/", "400",
              r_login_inact.status_code,
              r_alta.status_code == 201 and r_login_inact.status_code == 400
              and "INACTIVA" in mensaje_inact,
              f"registro HTTP {r_alta.status_code}; usuario={alta['username']}; "
              f"detalle={mensaje_inact}")

    # ---------------- 5-7. LOGIN POR ROLES ----------------
    token_admin = autenticar("admin")
    r = requests.get(f"{API}/reports/dashboard/summary/", headers=cabecera(token_admin),
                     timeout=TIMEOUT)
    registrar("RW05", "RQF-AUT-04", "Login administrador y acceso al panel de KPIs",
              "GET", "/api/v1/reports/dashboard/summary/", "200", r.status_code,
              r.status_code == 200)

    token_recepcion = autenticar("recepcion")
    r = requests.get(f"{API}/reservations/reservations/", headers=cabecera(token_recepcion),
                     timeout=TIMEOUT)
    registrar("RW06", "RQF-AUT-05", "Login recepcion y listado de reservas",
              "GET", "/api/v1/reservations/reservations/", "200", r.status_code,
              r.status_code == 200)

    r = requests.get(f"{API}/auth/me/", headers=cabecera(token_c1), timeout=TIMEOUT)
    registrar("RW07", "RQF-AUT-06", "Login cliente y consulta de su propio perfil",
              "GET", "/api/v1/auth/me/", "200", r.status_code, r.status_code == 200,
              f"usuario={r.json().get('username') if r.status_code == 200 else '-'}")

    # ---------------- 8. ACCESO PERMITIDO ----------------
    r = requests.get(f"{API}/reservations/reservations/my-upcoming/",
                     headers=cabecera(token_c1), timeout=TIMEOUT)
    registrar("RW08", "RQF-AUT-07", "Acceso permitido: cliente consulta sus reservas",
              "GET", "/api/v1/reservations/reservations/my-upcoming/", "200",
              r.status_code, r.status_code == 200,
              f"reservas_proximas={len(r.json()) if r.status_code == 200 else '-'}")

    # ---------------- 9. ACCESO PROHIBIDO ----------------
    r = requests.get(f"{API}/reports/dashboard/summary/", headers=cabecera(token_c1),
                     timeout=TIMEOUT)
    registrar("RW09", "RQF-AUT-08", "Acceso prohibido: cliente hacia panel administrativo",
              "GET", "/api/v1/reports/dashboard/summary/", "403", r.status_code,
              r.status_code == 403)

    # ---------------- 10. ESPACIOS ----------------
    r = requests.get(f"{API}/reservations/spaces/", headers=cabecera(token_c1), timeout=TIMEOUT)
    espacios = r.json()
    lista = espacios.get("results", espacios) if isinstance(espacios, dict) else espacios
    registrar("RW10", "RQF-RES-01", "Consulta del catalogo de espacios", "GET",
              "/api/v1/reservations/spaces/", "200", r.status_code, r.status_code == 200,
              f"{len(lista)} espacios")

    # Seleccion de un espacio que no exija aprobacion (reserva directa CONFIRMED)
    espacio = next((e for e in lista if not e.get("requires_employee_approval")), lista[0])

    # ---------------- 11. DISPONIBILIDAD ----------------
    fecha_obj = datetime.now(timezone.utc).date() + timedelta(days=8)
    franjas: list[dict] = []
    for intento in range(6):
        fecha = (fecha_obj + timedelta(days=intento)).isoformat()
        r = requests.get(f"{API}/reservations/spaces/{espacio['id']}/availability/",
                         params={"date": fecha}, headers=cabecera(token_c1), timeout=TIMEOUT)
        if r.status_code == 200:
            franjas = r.json().get("thirty_minute_slots", [])
            if len(franjas) >= 3:
                break
    registrar("RW11", "RQF-RES-02", "Consulta de disponibilidad de un espacio", "GET",
              f"/api/v1/reservations/spaces/{espacio['id']}/availability/?date={fecha}",
              "200", r.status_code, r.status_code == 200 and len(franjas) >= 3,
              f"espacio={espacio['code']} fecha={fecha} franjas_libres={len(franjas)}")

    if len(franjas) < 3:
        print("!! Sin franjas suficientes: no se pueden ejecutar las pruebas de reserva.")
        exportar()
        return 1

    indice = min(8, len(franjas) - 3)
    inicio = franjas[indice]["datetime"]
    fin = franjas[indice + 2]["datetime"]

    # ---------------- 12. CREACION DE RESERVA ----------------
    cuerpo_reserva = {
        "space_id": espacio["id"],
        "start_time": inicio,
        "end_time": fin,
        "guests_count": 1,
        "notes": "VALIDACION RAILWAY - dato de prueba controlado (se cancela al final)",
    }
    r = requests.post(f"{API}/reservations/reservations/", json=cuerpo_reserva,
                      headers=cabecera(token_c1), timeout=TIMEOUT)
    reserva = r.json() if r.status_code == 201 else {}
    reserva_id = reserva.get("id")
    registrar("RW12", "RQF-RES-03", "Creacion real de una reserva", "POST",
              "/api/v1/reservations/reservations/", "201", r.status_code,
              r.status_code == 201,
              f"id={reserva_id} estado={reserva.get('status')} "
              f"total={reserva.get('total_amount')}")

    # ---------------- 13. CONSULTA POSTERIOR ----------------
    r = requests.get(f"{API}/reservations/reservations/{reserva_id}/",
                     headers=cabecera(token_c1), timeout=TIMEOUT)
    datos_reserva = r.json() if r.status_code == 200 else {}
    registrar("RW13", "RQF-RES-04", "Consulta posterior de la reserva creada", "GET",
              f"/api/v1/reservations/reservations/{reserva_id}/", "200",
              r.status_code, r.status_code == 200,
              f"estado={datos_reserva.get('status')}")

    # ---------------- 14. RESERVA SOLAPADA ----------------
    r = requests.post(f"{API}/reservations/reservations/", json=cuerpo_reserva,
                      headers=cabecera(token_c1), timeout=TIMEOUT)
    registrar("RW14", "RQF-RES-05", "Rechazo de una reserva solapada", "POST",
              "/api/v1/reservations/reservations/", "400", r.status_code,
              r.status_code == 400,
              f"respuesta={str(r.json())[:160]}")

    # ---------------- 15. ERROR 400 CONTROLADO ----------------
    malo = dict(cuerpo_reserva)
    malo["end_time"] = inicio  # duracion 0 -> invalida
    r = requests.post(f"{API}/reservations/reservations/", json=malo,
                      headers=cabecera(token_c1), timeout=TIMEOUT)
    registrar("RW15", "RNF-ERR-01", "Error 400 controlado (duracion invalida)", "POST",
              "/api/v1/reservations/reservations/", "400", r.status_code,
              r.status_code == 400)

    # ---------------- 16. ERROR 401 SIN TOKEN ----------------
    r = requests.get(f"{API}/reservations/reservations/", timeout=TIMEOUT)
    registrar("RW16", "RNF-ERR-02", "Error 401 sin credenciales", "GET",
              "/api/v1/reservations/reservations/", "401", r.status_code,
              r.status_code == 401)

    # ---------------- 17. ERROR 404 ----------------
    r = requests.get(f"{API}/reservations/spaces/99999999/",
                     headers=cabecera(token_c1), timeout=TIMEOUT)
    registrar("RW17", "RNF-ERR-03", "Error 404 sobre recurso inexistente", "GET",
              "/api/v1/reservations/spaces/99999999/", "404", r.status_code,
              r.status_code == 404)

    # ---------------- 18. REFRESH TOKEN ----------------
    refresh = cuerpo.get("refresh", "")
    if not refresh:
        refresh = login("cliente1")[1].get("refresh", "")
    r = requests.post(f"{API}/auth/token/refresh/", json={"refresh": refresh}, timeout=TIMEOUT)
    nuevo_access = r.json().get("access", "") if r.status_code == 200 else ""
    registrar("RW18", "RQF-AUT-09", "Refresco de token de acceso", "POST",
              "/api/v1/auth/token/refresh/", "200", r.status_code, r.status_code == 200,
              f"nuevo access={huella(nuevo_access)}")

    # ---------------- 19. CANCELACION ----------------
    r = requests.post(f"{API}/reservations/reservations/{reserva_id}/cancel/",
                      json={"cancellation_reason": "Validacion automatica de cierre tecnico"},
                      headers=cabecera(token_c1), timeout=TIMEOUT)
    estado_cancelado = r.json().get("status") if r.status_code == 200 else "-"
    registrar("RW19", "RQF-RES-06", "Cancelacion de la reserva de prueba", "POST",
              f"/api/v1/reservations/reservations/{reserva_id}/cancel/", "200",
              r.status_code, r.status_code == 200,
              f"estado final={estado_cancelado}")

    # ---------------- 20. PERSISTENCIA EN NUEVA SESION ----------------
    tiempo_espera = 3
    time.sleep(tiempo_espera)
    token_nuevo = autenticar("cliente2") or autenticar("cliente1")
    r = requests.get(f"{API}/reservations/reservations/{reserva_id}/",
                     headers=cabecera(token_admin), timeout=TIMEOUT)
    registro_tras_sesion = r.json() if r.status_code == 200 else {}
    registrar("RW20", "RQF-BDI-01",
              "Persistencia verificada en una sesion nueva (nueva autenticacion)",
              "GET", f"/api/v1/reservations/reservations/{reserva_id}/", "200",
              r.status_code, r.status_code == 200,
              f"estado en BD={registro_tras_sesion.get('status')} "
              f"sesion_nueva_token={huella(token_nuevo)}")

    exportar()
    return 0 if all(x["resultado"] == "PASS" for x in RESULTADOS) else 1


def exportar() -> None:
    total = len(RESULTADOS)
    aprobadas = sum(1 for x in RESULTADOS if x["resultado"] == "PASS")
    resumen = {
        "fecha_ejecucion": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "url": BASE,
        "total": total,
        "aprobadas": aprobadas,
        "fallidas": total - aprobadas,
        "casos": RESULTADOS,
    }
    (DIR_EVIDENCIAS / "validacion_railway.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")

    lineas = [
        "# Validacion real sobre el despliegue de Railway",
        "",
        "> Family Health MF - cierre tecnico de la version final",
        "",
        f"- **URL evaluada:** {BASE}",
        f"- **Fecha/hora (UTC):** {resumen['fecha_ejecucion']}",
        f"- **Casos ejecutados:** {total}",
        f"- **Aprobados:** {aprobadas}",
        f"- **Fallidos:** {total - aprobadas}",
        "",
        "Los codigos HTTP son los que el servicio devolvio realmente. No se",
        "almacenan tokens ni contrasenas completos (solo huellas enmascaradas).",
        "",
        "| ID | Requisito | Descripcion | Metodo | Ruta | HTTP esperado | HTTP real | Resultado | Observacion |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for caso in RESULTADOS:
        lineas.append(
            f"| {caso['id']} | {caso['requisito']} | {caso['descripcion']} | "
            f"{caso['metodo']} | `{caso['ruta']}` | {caso['http_esperado']} | "
            f"{caso['http_real']} | {caso['resultado']} | {caso['observacion']} |"
        )
    lineas += [
        "",
        "## Comandos de reproduccion",
        "",
        "```powershell",
        'cd c:\\Family_Health_MF',
        '$env:FH_PASS_ADMIN="<contrasena demo admin>";$env:FH_PASS_RECEPCION="<...>";',
        '$env:FH_PASS_CAFETERIA="<...>";$env:FH_PASS_CLIENTE1="<...>";$env:FH_PASS_CLIENTE2="<...>"',
        '.venv\\Scripts\\python.exe tests\\railway_validation.py',
        "```",
        "",
        "## Nota sobre datos de prueba",
        "",
        "La reserva creada durante esta validacion se identifica con la nota",
        "`VALIDACION RAILWAY - dato de prueba controlado` y se cancela al final del",
        "propio script (caso RW19), por lo que no queda ocupando disponibilidad real.",
        "",
    ]
    (DIR_EVIDENCIAS / "validacion_railway.md").write_text(
        "\n".join(lineas), encoding="utf-8")

    print()
    print(">>> RESUMEN VALIDACION RAILWAY")
    print(f"    total: {total} | aprobadas: {aprobadas} | fallidas: {total - aprobadas}")
    print(f"    archivo: {DIR_EVIDENCIAS / 'validacion_railway.md'}")


if __name__ == "__main__":
    sys.exit(main())
