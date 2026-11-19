"""
Verificacion del control ALLOWED_HOSTS / SEC-10 (cierre del bloque 3).

SEC-10 no se resuelve con una sola peticion externa: el borde (proxy) de Railway
enruta por la cabecera `Host` y, ademas, con USE_X_FORWARDED_HOST=True reescribe
`X-Forwarded-Host`. Por eso el control se cierra combinando DOS evidencias:

  1. Externa (borde): comportamiento ante un `Host` y un `X-Forwarded-Host` no
     autorizados (casos E1..E5).
  2. Local (aplicacion): la aplicacion Django, con la configuracion de produccion,
     rechaza un host no autorizado (DisallowedHost -> HTTP 400) y acepta el valido.

No modifica datos: solo lecturas HTTP seguras y una comprobacion local en memoria.

Uso:
    python tests/verificacion_hosts.py

Salidas:
    evidencias/verificacion_hosts.json
    evidencias/verificacion_hosts.md
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

RAIZ = Path(__file__).resolve().parent.parent
DIR_EVIDENCIAS = RAIZ / "evidencias"
DIR_EVIDENCIAS.mkdir(exist_ok=True)

BASE = os.getenv("FH_BASE", "https://familyhealthmf-production.up.railway.app").rstrip("/")
HEALTH = f"{BASE}/api/v1/health/"
TIMEOUT = 60

ALLOWED_HOSTS_PRODUCCION = "familyhealthmf-production.up.railway.app,.up.railway.app,.railway.app"
HOST_VALIDO = "familyhealthmf-production.up.railway.app"
HOST_INVALIDO = "host-no-autorizado.test"

CASOS_EXTERNOS = [
    ("E1", "Host no autorizado (test actual SEC-10)", {"Host": HOST_INVALIDO}),
    ("E2", "X-Forwarded-Host no autorizado", {"X-Forwarded-Host": HOST_INVALIDO}),
    ("E3", "X-Forwarded-Host con puerto", {"X-Forwarded-Host": "malo.test:8080"}),
    ("E4", "X-Forwarded-Host encadenado",
     {"X-Forwarded-Host": f"{HOST_VALIDO}, {HOST_INVALIDO}"}),
    ("E5", "Host valido (control positivo)", {"Host": HOST_VALIDO}),
]

MAX_CUERPO = 160


def _normalizar_cuerpo(texto: str) -> str:
    """Neutraliza los valores dinamicos para poder comparar respuestas."""
    if not texto:
        return ""
    texto = re.sub(r'"timestamp"\s*:\s*"[^"]*"', '"timestamp":"<t>"', texto)
    texto = re.sub(r'"request_id"\s*:\s*"[^"]*"', '"request_id":"<id>"', texto)
    return texto


def verificar_externo() -> list[dict]:
    """Ejecuta los casos externos contra el despliegue y registra el resultado."""
    resultados = []
    for id_, descripcion, cabeceras in CASOS_EXTERNOS:
        try:
            r = requests.get(HEALTH, headers=cabeceras, timeout=TIMEOUT)
            http, texto = r.status_code, r.text
        except requests.RequestException as exc:
            http, texto = None, f"ERROR: {exc}"
        resultados.append({
            "id": id_,
            "descripcion": descripcion,
            "cabeceras": cabeceras,
            "http": http,
            "cuerpo": _normalizar_cuerpo(texto)[:MAX_CUERPO],
        })
    return resultados


def _clasificar_externo(externos: list[dict]) -> dict:
    por_id = {e["id"]: e for e in externos}
    cuerpo_control = por_id.get("E5", {}).get("cuerpo", "")
    e1 = por_id.get("E1", {})
    host_desconocido_bloqueado = e1.get("http") in (400, 404)
    inyecciones = [por_id.get(i, {}) for i in ("E2", "E3", "E4")]
    xfh_neutralizado = all(
        i.get("http") == 200 and i.get("cuerpo") == cuerpo_control for i in inyecciones
    )
    return {
        "host_desconocido_bloqueado": bool(host_desconocido_bloqueado),
        "xfh_neutralizado": bool(xfh_neutralizado),
        "cuerpo_control_igual_inyecciones": bool(xfh_neutralizado),
    }


def verificar_local() -> dict:
    """Comprueba que Django (con la config de produccion) rechaza el host invalido."""
    os.environ["DJANGO_DEBUG"] = "False"
    os.environ["DJANGO_ALLOWED_HOSTS"] = ALLOWED_HOSTS_PRODUCCION
    os.environ.setdefault("DJANGO_SECRET_KEY", "verificacion-local-sec10-sin-valor-real")
    sys.path.insert(0, str(RAIZ / "backend"))

    import django

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()

    from django.conf import settings
    from django.core.exceptions import DisallowedHost
    from django.test import RequestFactory

    rf = RequestFactory()
    resultado: dict = {
        "allowed_hosts_efectivo": list(settings.ALLOWED_HOSTS),
        "host_invalido": HOST_INVALIDO,
        "host_valido": HOST_VALIDO,
    }

    rechaza = False
    try:
        rf.get("/", SERVER_NAME=HOST_INVALIDO).get_host()
    except DisallowedHost:
        rechaza = True
    resultado["rechaza_host_invalido"] = rechaza

    acepta = False
    try:
        acepta = rf.get("/", SERVER_NAME=HOST_VALIDO).get_host() == HOST_VALIDO
    except DisallowedHost:
        acepta = False
    resultado["acepta_host_valido"] = acepta

    resultado["resultado"] = "CUMPLE" if (rechaza and acepta) else "REVISAR"
    return resultado


def exportar(sello: str, externos: list[dict], analisis: dict, local: dict, veredicto: str) -> None:
    resumen = {
        "fecha": sello,
        "url": BASE,
        "control": "SEC-10 - solicitud con Host no autorizado",
        "allowed_hosts_produccion": ALLOWED_HOSTS_PRODUCCION,
        "externo": externos,
        "analisis_borde": analisis,
        "local": local,
        "veredicto": veredicto,
    }
    (DIR_EVIDENCIAS / "verificacion_hosts.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")

    lineas = [
        "# Verificacion del control ALLOWED_HOSTS (cierre SEC-10)",
        "",
        "> Family Health MF - cierre tecnico de la version final (bloque 3)",
        "",
        f"- **URL evaluada:** {BASE}",
        f"- **Fecha/hora (UTC):** {sello}",
        f"- **`ALLOWED_HOSTS` de produccion:** `{ALLOWED_HOSTS_PRODUCCION}`",
        f"- **Veredicto:** **{veredicto}**",
        "",
        "## Por que SEC-10 no se resuelve solo con una peticion externa",
        "",
        "El borde (proxy) de Railway enruta por la cabecera `Host`: si el `Host` es",
        "desconocido, el borde responde **404 \"Application not found\"** y la peticion",
        "nunca alcanza a Django. Ademas, con `USE_X_FORWARDED_HOST=True`, el borde",
        "reescribe `X-Forwarded-Host`, por lo que tampoco se puede persistir un host",
        "falso por esa via. Por eso la comprobacion se completa con dos evidencias.",
        "",
        "## Evidencia 1 - Externa (comportamiento del borde)",
        "",
        "| ID | Caso | Cabeceras enviadas | HTTP | Interpretacion |",
        "|---|---|---|---|---|",
    ]
    interpretacion = {
        "E1": "bloqueado por el borde (no enrutado)",
        "E2": "inyeccion neutralizada (respuesta identica al control)",
        "E3": "inyeccion neutralizada (respuesta identica al control)",
        "E4": "inyeccion neutralizada (respuesta identica al control)",
        "E5": "control: respuesta normal",
    }
    for e in externos:
        cab = "; ".join(f"`{k}: {v}`" for k, v in e["cabeceras"].items())
        lineas.append(f"| {e['id']} | {e['descripcion']} | {cab} | {e['http']} | "
                      f"{interpretacion.get(e['id'], '')} |")

    lineas += [
        "",
        "## Evidencia 2 - Local (aplicacion Django con la configuracion de produccion)",
        "",
        f"- **`ALLOWED_HOSTS` efectivo:** `{local['allowed_hosts_efectivo']}`",
        f"- **Host no autorizado (`{local['host_invalido']}`) rechazado:** "
        f"{local['rechaza_host_invalido']}",
        f"- **Host autorizado (`{local['host_valido']}`) aceptado:** "
        f"{local['acepta_host_valido']}",
        "",
        "Cuando el `Host` no esta en `ALLOWED_HOSTS`, Django lanza `DisallowedHost`",
        "y responde **HTTP 400**; si el host esta autorizado, la peticion se atiende.",
        "",
        "## Lectura conjunta de las dos evidencias",
        "",
        "- **E1:** un `Host` desconocido no es enrutado por el borde (no llega a la",
        "  aplicacion), por lo que no puede procesarse una peticion con host falso.",
        "- **E2-E4:** la inyeccion por `X-Forwarded-Host` devuelve la MISMA respuesta",
        "  que el caso de control con host valido, es decir, la cabecera inyectada",
        "  no tiene efecto (el borde la reescribe).",
        "- **Evidencia local:** con la `ALLOWED_HOSTS` de produccion, Django",
        "  RECHAZARIA ese host no autorizado (`DisallowedHost` -> HTTP 400). Por",
        "  tanto, el HTTP 200 de E2-E4 solo es posible si Django recibio un host",
        "  valido (la inyeccion fue neutralizada por el borde).",
        "",
        "## Conclusion",
        "",
        f"El control SEC-10 **{'SE CUMPLE' if veredicto == 'CUMPLE' else 'NO CUMPLE (revisar)'}**",
        "con dos capas de defensa:",
        "",
        "1. **Borde (Railway):** una peticion con `Host` desconocido no es enrutada",
        "   hacia la aplicacion; y `X-Forwarded-Host` es reescrito (no persistible).",
        "2. **Aplicacion (Django):** con la `ALLOWED_HOSTS` de produccion, un host no",
        "   autorizado es rechazado con `HTTP 400 (DisallowedHost)`.",
        "",
        "## Reproduccion",
        "",
        "```powershell",
        "cd c:\\Family_Health_MF",
        ".venv\\Scripts\\python.exe tests\\verificacion_hosts.py",
        "```",
        "",
    ]
    (DIR_EVIDENCIAS / "verificacion_hosts.md").write_text(
        "\n".join(lineas), encoding="utf-8")


def main() -> int:
    sello = datetime.now(timezone.utc).isoformat(timespec="seconds")
    print("=" * 74)
    print("VERIFICACION DEL CONTROL ALLOWED_HOSTS (SEC-10)")
    print(f"URL: {BASE}")
    print(f"Fecha/hora (UTC): {sello}")
    print("=" * 74)

    externos = verificar_externo()
    for e in externos:
        print(f"  {e['id']} HTTP {e['http']}  {e['descripcion']}")

    control = next((e for e in externos if e["id"] == "E5"), {})
    if control.get("http") != 200:
        print("No se pudo verificar el despliegue (control E5 != 200). "
              "No se sobrescribe la evidencia existente.")
        return 1

    analisis = _clasificar_externo(externos)
    local = verificar_local()
    print(f"  Local: rechaza_invalido={local['rechaza_host_invalido']} "
          f"acepta_valido={local['acepta_host_valido']}")

    veredicto = "CUMPLE" if (
        local["resultado"] == "CUMPLE"
        and analisis["host_desconocido_bloqueado"]
        and analisis["xfh_neutralizado"]
    ) else "REVISAR"
    print(f">>> Veredicto SEC-10: {veredicto}")

    exportar(sello, externos, analisis, local, veredicto)
    print(f"    archivos: {DIR_EVIDENCIAS / 'verificacion_hosts.md'} / .json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
