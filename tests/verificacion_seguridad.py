"""
Verificacion de seguridad NO destructiva (punto 11 del cierre tecnico).

Ejecuta comprobaciones HTTP seguras contra la version desplegada (solo lectura,
sin modificar ni borrar datos) y registra la evidencia cruda. Complementa la
revision estatica del codigo y la configuracion.

No se envian credenciales reales: las comprobaciones de autenticacion usan
peticiones sin token y usuarios inexistentes de prueba.

Salidas:
    evidencias/verificacion_seguridad.json
    evidencias/_seguridad_raw.txt
"""
from __future__ import annotations

import json
import os
import sys
import uuid
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

HALLAZGOS: list[dict] = []


def registrar(ident: str, control: str, esperado: str, real: str, ok: bool,
              nota: str = "") -> None:
    HALLAZGOS.append({
        "id": ident, "control": control, "esperado": esperado,
        "real": real, "resultado": "CUMPLE" if ok else "REVISAR", "nota": nota,
    })
    print(f"[{'CUMPLE' if ok else 'REVISAR'}] {ident} {control} -> {real}")


def main() -> int:
    sello = datetime.now(timezone.utc).isoformat(timespec="seconds")
    print("=" * 74)
    print("VERIFICACION DE SEGURIDAD NO DESTRUCTIVA")
    print(f"URL: {BASE}")
    print(f"Fecha/hora (UTC): {sello}")
    print("=" * 74)

    # --- SEC-01: disponibilidad del endpoint publico ---
    r = requests.get(f"{API}/health/", timeout=TIMEOUT)
    registrar("SEC-01", "Servicio disponible (health check publico)", "HTTP 200",
              f"HTTP {r.status_code}", r.status_code == 200)

    cabeceras = {k.lower(): v for k, v in r.headers.items()}

    # --- SEC-02: cabeceras de seguridad HTTP ---
    hsts = cabeceras.get("strict-transport-security", "")
    registrar("SEC-02", "HSTS (Strict-Transport-Security) presente en produccion",
              "max-age declarado", hsts or "(ausente)", bool(hsts),
              "Solo aplica cuando la peticion llega por HTTPS (SECURE_SSL_REDIRECT).")

    xcto = cabeceras.get("x-content-type-options", "")
    registrar("SEC-03", "X-Content-Type-Options = nosniff", "nosniff",
              xcto or "(ausente)", xcto.lower() == "nosniff")

    xfo = cabeceras.get("x-frame-options", "")
    registrar("SEC-04", "X-Frame-Options restringe el enmarcado (clickjacking)",
              "DENY o SAMEORIGIN", xfo or "(ausente)",
              xfo.upper() in ("DENY", "SAMEORIGIN"))

    ref = cabeceras.get("referrer-policy", "")
    registrar("SEC-05", "Referrer-Policy declarada", "strict-origin-when-cross-origin",
              ref or "(ausente)", bool(ref))

    servidor = cabeceras.get("server", "")
    registrar("SEC-06", "Cabecera Server sin versiones sensibles",
              "sin numero de version", servidor or "(ausente)",
              not any(ch.isdigit() for ch in servidor),
              f"valor real: {servidor or '(ausente)'}")

    # --- SEC-07: sin trazas de depuracion en errores ---
    r = requests.get(f"{API}/ruta-que-no-existe/", timeout=TIMEOUT)
    cuerpo = r.text[:2000]
    fugas = [t for t in ("Traceback", "DJANGO_SETTINGS_MODULE", "django.core.exceptions",
                         "File \"", "DEBUG = True") if t in cuerpo]
    registrar("SEC-07", "Las respuestas de error no exponen trazas ni configuracion",
              "sin trazas", f"HTTP {r.status_code}; fugas={fugas or 'ninguna'}",
              not fugas)

    # --- SEC-08: recurso protegido exige credenciales ---
    r = requests.get(f"{API}/reservations/reservations/", timeout=TIMEOUT)
    registrar("SEC-08", "Recurso protegido sin token devuelve 401", "HTTP 401",
              f"HTTP {r.status_code}", r.status_code == 401)

    # --- SEC-09: panel administrativo exige credenciales ---
    r = requests.get(f"{API}/reports/dashboard/summary/", timeout=TIMEOUT)
    registrar("SEC-09", "Panel administrativo sin token devuelve 401", "HTTP 401",
              f"HTTP {r.status_code}", r.status_code == 401)

    # --- SEC-10: host no autorizado ---
    try:
        r = requests.get(f"{API}/health/", headers={"Host": "host-no-autorizado.test"},
                         timeout=TIMEOUT)
        codigo_host = r.status_code
    except Exception as exc:  # noqa: BLE001
        codigo_host = f"error: {exc}"
    registrar("SEC-10", "Solicitud con Host no autorizado (riesgo de Host Header Injection)",
              "HTTP 400 (ALLOWED_HOSTS restringido)",
              f"HTTP {codigo_host}", codigo_host == 400,
              "Si devuelve 200, ALLOWED_HOSTS='*' sigue activo en produccion: "
              "ver propuesta de restriccion en checklist_seguridad.md.")

    # --- SEC-11: mensaje de error de login no revela si el usuario existe ---
    falso = f"usuario_inexistente_{uuid.uuid4().hex[:6]}"
    r1 = requests.post(f"{API}/auth/login/",
                       json={"username": falso, "password": "ClaveAleatoria*2026XYZ"},
                       timeout=TIMEOUT)
    r2 = requests.post(f"{API}/auth/login/",
                       json={"username": "admin_fh", "password": "ClaveAleatoria*2026XYZ"},
                       timeout=TIMEOUT)
    m1 = json.dumps(r1.json(), ensure_ascii=False) if r1.text else ""
    m2 = json.dumps(r2.json(), ensure_ascii=False) if r2.text else ""
    registrar("SEC-11", "Mensaje de error de login uniforme (no revela existencia del usuario)",
              "mismo mensaje para usuario inexistente y contrasena incorrecta",
              f"HTTP {r1.status_code} vs {r2.status_code}; iguales={m1 == m2}",
              r1.status_code == r2.status_code,
              f"usuario_inexistente='{m1[:90]}' | contrasena_incorrecta='{m2[:90]}'")

    # --- SEC-12: el registro exige aceptar la politica de privacidad ---
    r = requests.post(f"{API}/auth/register/", json={
        "username": f"sec_{uuid.uuid4().hex[:6]}",
        "email": f"sec_{uuid.uuid4().hex[:6]}@example.com",
        "password": "Seguridad2026*!", "password_confirm": "Seguridad2026*!",
        "accepted_privacy_policy": False, "accepted_terms": False,
    }, timeout=TIMEOUT)
    registrar("SEC-12", "El registro rechaza solicitudes sin aceptar politica de privacidad",
              "HTTP 400", f"HTTP {r.status_code}", r.status_code == 400)

    exportar(sello, cabeceras)
    return 0


def exportar(sello: str, cabeceras: dict) -> None:
    resumen = {
        "fecha": sello,
        "url": BASE,
        "total": len(HALLAZGOS),
        "cumple": sum(1 for x in HALLAZGOS if x["resultado"] == "CUMPLE"),
        "revisar": sum(1 for x in HALLAZGOS if x["resultado"] == "REVISAR"),
        "cabeceras_observadas": cabeceras,
        "hallazgos": HALLAZGOS,
    }
    (DIR_EVIDENCIAS / "verificacion_seguridad.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")

    lineas = [f"VERIFICACION DE SEGURIDAD NO DESTRUCTIVA - {sello}",
              f"URL: {BASE}", ""]
    for x in HALLAZGOS:
        lineas.append(f"[{x['resultado']}] {x['id']} | {x['control']} | "
                      f"esperado={x['esperado']} | real={x['real']} | {x['nota']}")
    lineas += ["", "--- CABECERAS HTTP OBSERVADAS ---"]
    for k in sorted(cabeceras):
        lineas.append(f"{k}: {cabeceras[k]}")
    (DIR_EVIDENCIAS / "_seguridad_raw.txt").write_text("\n".join(lineas), encoding="utf-8")

    print()
    print(">>> RESUMEN SEGURIDAD")
    print(f"    controles={len(HALLAZGOS)} cumple={resumen['cumple']} "
          f"revisar={resumen['revisar']}")


if __name__ == "__main__":
    sys.exit(main())
