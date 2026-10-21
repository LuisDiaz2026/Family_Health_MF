"""
Evaluacion SIMULADA de aceptacion y usabilidad con usuarios sinteticos.

IMPORTANTE (rigor academico):
  - NO participan personas reales. Las sesiones las ejecuta este script.
  - Los tiempos, codigos HTTP, errores y resultados SON REALES (medidos contra
    el despliegue).
  - Las puntuaciones de facilidad, claridad y satisfaccion (1-5) NO provienen de
    personas: se derivan de un modelo determinista declarado en este archivo y
    en el informe. Se etiquetan siempre como SIMULADAS.
  - Se crean cuentas y reservas marcadas como dato de prueba controlado y se
    ELIMINAN al final (fase de limpieza), salvo que se invoque "sin-limpiar".

Uso (desde la raiz del repositorio):
    python tests/simulacion_aceptacion.py            # ejecuta y limpia
    python tests/simulacion_aceptacion.py sin-limpiar  # conserva los datos
    python tests/simulacion_aceptacion.py limpiar      # solo limpia restos

Salidas:
    evidencias/simulacion_aceptacion_tareas.csv
    evidencias/simulacion_aceptacion_sesiones.csv
    evidencias/simulacion_aceptacion.json
    evidencias/simulacion_aceptacion.md
"""
from __future__ import annotations

import csv
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from credenciales import cargar_en_entorno, obtener  # noqa: E402

cargar_en_entorno()

RAIZ = Path(__file__).resolve().parent.parent
DIR_EVIDENCIAS = RAIZ / "evidencias"
DIR_EVIDENCIAS.mkdir(exist_ok=True)

BASE = os.getenv("FH_BASE", "https://familyhealthmf-production.up.railway.app").rstrip("/")
API = f"{BASE}/api/v1"
TIMEOUT = 60

MARCA = "SIMULACION ACEPTACION - dato de prueba controlado"
CLAVE_SIM = "SimFH2026*!"

ADMIN_DEMO = (os.getenv("FH_USER_ADMIN", "admin_fh"), os.getenv("FH_PASS_ADMIN", ""))

# ---------------------------------------------------------------------------
# Usuarios sinteticos: 2 por rol. La "competencia" alimenta el modelo de
# percepcion (NO representa a una persona real).
# ---------------------------------------------------------------------------
USUARIOS_SINTETICOS = [
    {"codigo": "SIM-ADM-A", "rol": "ADMIN", "usuario": "sim_adm_a", "competencia": "Intermedia"},
    {"codigo": "SIM-ADM-B", "rol": "ADMIN", "usuario": "sim_adm_b", "competencia": "Basica"},
    {"codigo": "SIM-REC-A", "rol": "RECEPCION", "usuario": "sim_rec_a", "competencia": "Intermedia"},
    {"codigo": "SIM-REC-B", "rol": "RECEPCION", "usuario": "sim_rec_b", "competencia": "Basica"},
    {"codigo": "SIM-CLI-A", "rol": "CLIENT", "usuario": "sim_cli_a", "competencia": "Intermedia"},
    {"codigo": "SIM-CLI-B", "rol": "CLIENT", "usuario": "sim_cli_b", "competencia": "Basica"},
]

# Pensamiento modelado por interaccion (segundos), segun competencia declarada.
PENSAR = {"Intermedia": 3.0, "Basica": 6.0}


def huella(valor: str | None) -> str:
    if not valor:
        return "(vacio)"
    return f"{valor[:10]}...{valor[-4:]} ({len(valor)} car.)"


def peticion(metodo: str, ruta: str, token: str | None = None,
             json_body=None, params=None) -> dict:
    """Ejecuta una peticion real y devuelve estado, cuerpo y duracion real."""
    url = f"{API}{ruta}"
    cabeceras = {"Authorization": f"Bearer {token}"} if token else {}
    t0 = time.perf_counter()
    try:
        r = requests.request(metodo, url, json=json_body, params=params,
                             headers=cabeceras, timeout=TIMEOUT)
        duracion = time.perf_counter() - t0
        try:
            cuerpo = r.json()
        except Exception:  # noqa: BLE001
            cuerpo = {}
        return {"status": r.status_code, "cuerpo": cuerpo, "dur": duracion, "error": None}
    except Exception as e:  # noqa: BLE001
        return {"status": 0, "cuerpo": {}, "dur": time.perf_counter() - t0,
                "error": str(e)[:150]}


def lista(cuerpo) -> list:
    """Normaliza respuestas paginadas o planas de DRF."""
    if isinstance(cuerpo, dict) and "results" in cuerpo:
        return cuerpo["results"] or []
    return cuerpo if isinstance(cuerpo, list) else []


def login(usuario: str, clave: str) -> dict:
    return peticion("POST", "/auth/login/",
                    json_body={"username": usuario, "password": clave})


def cab(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ===========================================================================
# Estado compartido entre sesiones (flujo real entre roles)
# ===========================================================================
ESTADO = {
    "espacio_directo": None,    # sin aprobacion (CONFIRMED)
    "espacio_aprobacion": None,  # requiere aprobacion (PENDING)
    "reservas": [],              # ids creados
    "usuarios_creados": [],      # ids de usuarios sinteticos
    "clientes_ids": [],          # ids de los clientes sinteticos (para agendar)
    "pendientes": [],            # reservas PENDING creadas por clientes
    "confirmadas": [],           # reservas CONFIRMED creadas por clientes
}
TAREAS: list[dict] = []
SESIONES: list[dict] = []


# ===========================================================================
# Sesion de usuario sintetico
# ===========================================================================
class Sesion:
    def __init__(self, definicion: dict):
        self.codigo = definicion["codigo"]
        self.rol = definicion["rol"]
        self.usuario = definicion["usuario"]
        self.competencia = definicion["competencia"]
        self.pensar = PENSAR[self.competencia]
        self.token = ""
        self.refresh = ""
        self.user_id = None
        self.tareas: list[dict] = []
        self.t0 = None

    # -- utilidades ------------------------------------------------------
    def ejecutar(self, ident: str, requisito: str, descripcion: str, fn) -> bool:
        t0 = time.perf_counter()
        try:
            res = fn()
        except Exception as e:  # noqa: BLE001
            res = {"ok": False, "detalle": f"excepcion: {e}", "http": 0,
                   "interacciones": 1}
        duracion = time.perf_counter() - t0
        interacciones = res.get("interacciones", 1)
        errores = res.get("errores", 0 if res.get("ok") else 1)
        tiempo_simulado = duracion + interacciones * self.pensar
        facilidad, claridad, satisfaccion = self._percepcion(res, errores)
        fila = {
            "codigo_usuario": self.codigo,
            "rol": self.rol,
            "competencia": self.competencia,
            "id_tarea": ident,
            "requisito": requisito,
            "descripcion": descripcion,
            "http": res.get("http", 0),
            "completada": "SI" if res.get("ok") else "NO",
            "interacciones": interacciones,
            "duracion_tecnica_s": round(duracion, 3),
            "tiempo_simulado_s": round(tiempo_simulado, 3),
            "errores": errores,
            "facilidad_1_5": facilidad,
            "claridad_1_5": claridad,
            "satisfaccion_1_5": satisfaccion,
            "detalle": res.get("detalle", ""),
            "datos": json.dumps(res.get("datos", {}), ensure_ascii=False),
        }
        self.tareas.append(fila)
        TAREAS.append(fila)
        marca = "OK " if res.get("ok") else "NO "
        print(f"  [{marca}] {ident:6s} {requisito:12s} HTTP {fila['http']:>3} "
              f"{duracion:6.2f}s  {descripcion[:52]}")
        return bool(res.get("ok"))

    def _percepcion(self, res: dict, errores: int):
        """Modelo DETERMINISTA y declarado: NO son opiniones de personas.

        base = 5 si competencia Intermedia, 4 si Basica.
        Penaliza errores, tareas no completadas y respuestas de error HTTP.
        """
        base = 5 if self.competencia == "Intermedia" else 4
        facilidad = base
        if errores:
            facilidad -= min(2, errores)
        if not res.get("ok"):
            facilidad -= 2
        facilidad = max(1, min(5, facilidad))
        claridad = base
        if res.get("http", 0) >= 400:
            claridad -= 1
        if not res.get("ok"):
            claridad -= 1
        claridad = max(1, min(5, claridad))
        satisfaccion = max(1, min(5, round((facilidad + claridad) / 2)))
        return facilidad, claridad, satisfaccion

    # -- tareas comunes --------------------------------------------------
    def tarea_login(self) -> dict:
        r = login(self.usuario, CLAVE_SIM)
        self.token = r["cuerpo"].get("access", "")
        self.refresh = r["cuerpo"].get("refresh", "")
        self.user_id = (r["cuerpo"].get("user") or {}).get("id")
        ok = r["status"] == 200 and bool(self.token)
        return {"ok": ok, "http": r["status"], "interacciones": 1,
                "detalle": f"rol={r['cuerpo'].get('role')} access={huella(self.token)}"}

    def tarea_refresh(self) -> dict:
        r = peticion("POST", "/auth/token/refresh/", json_body={"refresh": self.refresh})
        nuevo = r["cuerpo"].get("access", "")
        nuevo_refresh = r["cuerpo"].get("refresh", "")
        if nuevo:
            self.token = nuevo
        if nuevo_refresh:
            # El backend rota el refresh y marca el anterior en blacklist
            # (ROTATE_REFRESH_TOKENS + BLACKLIST_AFTER_ROTATION): se conserva
            # el nuevo para que el logout posterior sea valido.
            self.refresh = nuevo_refresh
        return {"ok": r["status"] == 200 and bool(nuevo), "http": r["status"],
                "interacciones": 1, "detalle": f"nuevo access={huella(nuevo)}"}

    def tarea_logout(self) -> dict:
        r = peticion("POST", "/auth/logout/", token=self.token,
                     json_body={"refresh": self.refresh})
        return {"ok": r["status"] == 200, "http": r["status"], "interacciones": 1,
                "detalle": "sesion cerrada"}

    def tarea_me(self) -> dict:
        r = peticion("GET", "/auth/me/", token=self.token)
        perfil = r["cuerpo"]
        return {"ok": r["status"] == 200, "http": r["status"], "interacciones": 1,
                "detalle": f"usuario={perfil.get('username')} rol={perfil.get('role')}",
                "datos": {"username": perfil.get("username"), "role": perfil.get("role")}}

    def tarea_listar_espacios(self) -> dict:
        r = peticion("GET", "/reservations/spaces/", token=self.token)
        espacios = lista(r["cuerpo"])
        return {"ok": r["status"] == 200 and len(espacios) > 0, "http": r["status"],
                "interacciones": 1, "detalle": f"{len(espacios)} espacios"}

    def tarea_disponibilidad(self, espacio_id: int) -> dict:
        fecha = (datetime.now(timezone.utc).date() + timedelta(days=8)).isoformat()
        r = peticion("GET", f"/reservations/spaces/{espacio_id}/availability/",
                     token=self.token, params={"date": fecha})
        franjas = (r["cuerpo"] or {}).get("thirty_minute_slots", [])
        return {"ok": r["status"] == 200 and len(franjas) >= 3, "http": r["status"],
                "interacciones": 1, "detalle": f"franjas_libres={len(franjas)}"}

    # -- negativas -------------------------------------------------------
    def tarea_acceso_prohibido(self) -> dict:
        r = peticion("GET", "/reports/dashboard/summary/", token=self.token)
        return {"ok": r["status"] == 403, "http": r["status"], "interacciones": 1,
                "detalle": "cliente bloqueado del panel de KPIs"}

    def tarea_error_404(self) -> dict:
        r = peticion("GET", "/reservations/spaces/99999999/", token=self.token)
        return {"ok": r["status"] == 404, "http": r["status"], "interacciones": 1,
                "detalle": "recurso inexistente"}


# ===========================================================================
# Tareas por rol
# ===========================================================================
def sesion_cliente(s: Sesion, dia_offset: int) -> None:
    s.ejecutar("C01", "RQF-AUT-01", "Iniciar sesion como cliente", s.tarea_login)
    s.ejecutar("C02", "RQF-AUT-06", "Consultar su propio perfil", s.tarea_me)
    s.ejecutar("C03", "RQF-ESP-01", "Consultar el catalogo de espacios", s.tarea_listar_espacios)
    s.ejecutar("C04", "RQF-ESP-03", "Consultar disponibilidad de un espacio",
               lambda: s.tarea_disponibilidad(ESTADO["espacio_directo"]["id"]))

    # Crear reserva directa (CONFIRMED)
    def crear_directa():
        return _crear_reserva(s, ESTADO["espacio_directo"], dia_offset, 6, "")

    s.ejecutar("C05", "RQF-RES-01", "Crear una reserva (espacio sin aprobacion)", crear_directa)

    # Crear reserva en espacio con aprobacion (PENDING)
    def crear_pendiente():
        return _crear_reserva(s, ESTADO["espacio_aprobacion"], dia_offset, 20, "")

    s.ejecutar("C06", "RQF-RES-02", "Crear reserva en espacio que requiere aprobacion", crear_pendiente)

    def consultar_propias():
        r = peticion("GET", "/reservations/reservations/mis-reservas/", token=s.token)
        propias = lista(r["cuerpo"])

        def id_de(x):
            u = x.get("user")
            if isinstance(u, dict):
                return u.get("id")
            return x.get("user_id") or u

        ok = r["status"] == 200 and all(
            id_de(x) in (None, s.user_id) for x in propias
        )
        return {"ok": ok and len(propias) >= 2, "http": r["status"], "interacciones": 1,
                "detalle": f"reservas_propias={len(propias)}"}

    s.ejecutar("C07", "RQF-RES-16", "Consultar todas sus reservas (todos los estados)", consultar_propias)

    def proximas():
        r = peticion("GET", "/reservations/reservations/my-upcoming/", token=s.token)
        return {"ok": r["status"] == 200, "http": r["status"], "interacciones": 1,
                "detalle": f"proximas={len(lista(r['cuerpo']))}"}

    s.ejecutar("C08", "RQF-RES-11", "Consultar sus reservas proximas", proximas)

    # Solapamiento: repetir la misma franja de la reserva directa
    def solapamiento():
        creada = _ultima_reserva_directa(s)
        if not creada:
            return {"ok": False, "http": 0, "interacciones": 1,
                    "detalle": "no hay reserva directa previa"}
        r = peticion("POST", "/reservations/reservations/", token=s.token,
                     json_body={"space_id": creada["space_id"],
                                "start_time": creada["start_time"],
                                "end_time": creada["end_time"],
                                "guests_count": 1, "notes": MARCA})
        return {"ok": r["status"] == 400, "http": r["status"], "interacciones": 1,
                "detalle": "conflicto rechazado" if r["status"] == 400 else "no se rechazo"}

    s.ejecutar("C09", "RQF-RES-07", "Intento de solapamiento (debe rechazarse)", solapamiento)

    def duracion_invalida():
        r = peticion("POST", "/reservations/reservations/", token=s.token,
                     json_body={"space_id": ESTADO["espacio_directo"]["id"],
                                "start_time": "2030-01-01T10:00:00Z",
                                "end_time": "2030-01-01T10:00:00Z",
                                "guests_count": 1, "notes": MARCA})
        return {"ok": r["status"] == 400, "http": r["status"], "interacciones": 1,
                "detalle": "error 400 controlado"}

    s.ejecutar("C10", "RNF-ERR-01", "Validacion de datos invalidos (400)", duracion_invalida)

    def cancelar():
        creada = _ultima_reserva_directa(s)
        if not creada:
            return {"ok": False, "http": 0, "interacciones": 1, "detalle": "sin reserva"}
        r = peticion("POST", f"/reservations/reservations/{creada['id']}/cancel/",
                     token=s.token, json_body={"reason": MARCA})
        return {"ok": r["status"] == 200, "http": r["status"], "interacciones": 1,
                "detalle": f"estado={r['cuerpo'].get('status')}"}

    s.ejecutar("C11", "RQF-RES-06", "Cancelar una reserva propia", cancelar)
    s.ejecutar("C12", "RQF-AUT-08", "Verificar bloqueo del panel administrativo", s.tarea_acceso_prohibido)
    s.ejecutar("C13", "RQF-AUT-04", "Refrescar el token de acceso", s.tarea_refresh)


def sesion_recepcion(s: Sesion) -> None:
    s.ejecutar("R01", "RQF-AUT-01", "Iniciar sesion como recepcion", s.tarea_login)

    def listar_reservas():
        r = peticion("GET", "/reservations/reservations/", token=s.token)
        return {"ok": r["status"] == 200, "http": r["status"], "interacciones": 1,
                "detalle": f"reservas_visibles={len(lista(r['cuerpo']))}"}

    s.ejecutar("R02", "RQF-RES-12", "Listar las reservas del club", listar_reservas)

    def listar_clientes():
        r = peticion("GET", "/auth/clients/", token=s.token)
        clientes = lista(r["cuerpo"])
        ok = r["status"] == 200 and all(c.get("role") == "CLIENT" for c in clientes)
        return {"ok": ok, "http": r["status"], "interacciones": 1,
                "detalle": f"clientes={len(clientes)}"}

    s.ejecutar("R03", "RQF-USR-05", "Listar clientes del club", listar_clientes)

    aprobada: dict = {}

    def aprobar():
        pendiente = _tomar_pendiente()
        if not pendiente:
            return {"ok": False, "http": 0, "interacciones": 1, "detalle": "sin reserva pendiente"}
        r = peticion("POST", f"/reservations/reservations/{pendiente['id']}/approve/", token=s.token)
        if r["status"] == 200 and r["cuerpo"].get("status") == "CONFIRMED":
            aprobada["id"] = pendiente["id"]
        return {"ok": r["status"] == 200 and r["cuerpo"].get("status") == "CONFIRMED",
                "http": r["status"], "interacciones": 1,
                "detalle": f"estado={r['cuerpo'].get('status')}"}

    s.ejecutar("R04", "RQF-RES-13", "Aprobar una reserva pendiente", aprobar)

    def marcar_pagada():
        objetivo = aprobada.get("id")
        if not objetivo:
            confirmada = _tomar_confirmada()
            objetivo = (confirmada or {}).get("id")
        if not objetivo:
            return {"ok": False, "http": 0, "interacciones": 1, "detalle": "sin reserva confirmada"}
        r = peticion("POST", f"/reservations/reservations/{objetivo}/mark-paid/", token=s.token)
        return {"ok": r["status"] == 200 and r["cuerpo"].get("payment_status") == "PAID",
                "http": r["status"], "interacciones": 1,
                "detalle": f"pago={r['cuerpo'].get('payment_status')}"}

    s.ejecutar("R05", "RQF-RES-15", "Registrar el pago de una reserva", marcar_pagada)
    s.ejecutar("R06", "RQF-ESP-03", "Consultar disponibilidad de espacios",
               lambda: s.tarea_disponibilidad(ESTADO["espacio_directo"]["id"]))

    def disponibilidad_invalida():
        r = peticion("GET", f"/reservations/spaces/{ESTADO['espacio_directo']['id']}/availability/",
                     token=s.token, params={"date": "2026-13-45"})
        return {"ok": r["status"] == 400, "http": r["status"], "interacciones": 1,
                "detalle": "fecha invalida rechazada"}

    s.ejecutar("R07", "RQF-ESP-04", "Validar fecha invalida en disponibilidad", disponibilidad_invalida)
    s.ejecutar("R08", "RNF-ERR-03", "Consultar un recurso inexistente (404)", s.tarea_error_404)
    s.ejecutar("R09", "RQF-AUT-04", "Refrescar el token de acceso", s.tarea_refresh)
    s.ejecutar("R10", "RQF-AUT-05", "Cerrar sesion", s.tarea_logout)


def sesion_admin(s: Sesion) -> None:
    s.ejecutar("A01", "RQF-AUT-01", "Iniciar sesion como administrador", s.tarea_login)

    def panel():
        r = peticion("GET", "/reports/dashboard/summary/", token=s.token)
        return {"ok": r["status"] == 200, "http": r["status"], "interacciones": 1,
                "detalle": f"claves={len(r['cuerpo'])}"}

    s.ejecutar("A02", "RQF-AUT-04", "Consultar el panel de indicadores", panel)

    def reporte(ruta, nombre):
        def _f():
            r = peticion("GET", ruta, token=s.token)
            return {"ok": r["status"] == 200, "http": r["status"], "interacciones": 1,
                    "detalle": nombre}
        return _f

    s.ejecutar("A03", "RQF-REP-01", "Reservas por fecha (reporte)",
               reporte("/reports/dashboard/reservations-by-date/", "reservas por fecha"))
    s.ejecutar("A04", "RQF-REP-02", "Ingresos por mes (reporte)",
               reporte("/reports/dashboard/revenue-by-month/", "ingresos por mes"))
    s.ejecutar("A05", "RQF-REP-03", "Clientes destacados (reporte)",
               reporte("/reports/dashboard/top-clients/", "clientes destacados"))

    def listar_usuarios():
        r = peticion("GET", "/auth/admin/users/", token=s.token)
        return {"ok": r["status"] == 200, "http": r["status"], "interacciones": 1,
                "detalle": f"usuarios={len(lista(r['cuerpo']))}"}

    s.ejecutar("A06", "RQF-USR-03", "Listar y consultar usuarios del sistema", listar_usuarios)
    s.ejecutar("A07", "RQF-RES-12", "Listar todas las reservas del club",
               lambda: _listar_reservas(s))
    s.ejecutar("A08", "RQF-ESP-01", "Consultar el catalogo de espacios", s.tarea_listar_espacios)

    def crear_y_rechazar():
        # El administrador agenda a nombre de un cliente y luego rechaza
        # (flujo de gobierno). Se requiere user_id porque la reserva pertenece
        # a un cliente del club.
        creada = _crear_reserva(s, ESTADO["espacio_aprobacion"], 45, 24,
                                "creada por administrador",
                                user_id=(ESTADO["clientes_ids"] or [None])[0])
        if not creada.get("ok"):
            return {"ok": False, "http": creada.get("http", 0), "interacciones": 2,
                    "detalle": "no se pudo crear la reserva de prueba"}
        rid = creada["datos"]["id"]
        r = peticion("POST", f"/reservations/reservations/{rid}/reject/", token=s.token,
                     json_body={"reason": MARCA})
        ESTADO["reservas"].append(rid)
        return {"ok": r["status"] == 200 and r["cuerpo"].get("status") == "REJECTED",
                "http": r["status"], "interacciones": 2,
                "detalle": f"estado={r['cuerpo'].get('status')}"}

    s.ejecutar("A09", "RQF-RES-14", "Rechazar una reserva pendiente", crear_y_rechazar)
    s.ejecutar("A10", "RNF-ERR-03", "Consultar un recurso inexistente (404)", s.tarea_error_404)
    s.ejecutar("A11", "RQF-AUT-04", "Refrescar el token de acceso", s.tarea_refresh)


# ---------------------------------------------------------------------------
# Auxiliares de reservas
# ---------------------------------------------------------------------------
def _parse_dt(valor):
    try:
        return datetime.fromisoformat(str(valor).replace("Z", "+00:00"))
    except Exception:  # noqa: BLE001
        return None


def _slots_libres(espacio_id: int, token: str, fecha: str):
    """Franjas de 30 min que NO chocan con reservas activas (datos reales)."""
    r = peticion("GET", f"/reservations/spaces/{espacio_id}/availability/",
                 token=token, params={"date": fecha})
    if r["status"] != 200:
        return None
    cuerpo = r["cuerpo"] or {}
    ocupadas = [
        (_parse_dt(o.get("start_time")), _parse_dt(o.get("end_time")))
        for o in cuerpo.get("occupied_slots", [])
    ]
    libres = []
    for slot in cuerpo.get("thirty_minute_slots", []):
        ini = _parse_dt(slot.get("datetime"))
        if ini is None:
            continue
        fin = ini + timedelta(minutes=30)
        if any(a and b and ini < b and fin > a for a, b in ocupadas):
            continue
        libres.append({"ini": ini, "fin": fin})
    return libres


def _ventana(libres: list, minutos: int, indice: int):
    """Primera ventana contigua de 'minutos' desde la posicion 'indice'."""
    n = max(1, minutos // 30)
    for i in range(min(indice, max(0, len(libres) - n)), len(libres) - n + 1):
        run = libres[i:i + n]
        if all(run[j]["fin"] == run[j + 1]["ini"] for j in range(n - 1)):
            return run[0], run[-1]
    return None, None


def _crear_reserva(s: Sesion, espacio: dict, dia_offset: int, indice: int,
                   nota_extra: str, user_id=None) -> dict:
    """Crea una reserva respetando minimo/maximo del espacio y disponibilidad real."""
    minimo = int(espacio.get("min_reservation_minutes") or 30)
    maximo = int(espacio.get("max_reservation_minutes") or 180)
    minutos = min(maximo, max(minimo, 60))
    for extra in range(10):
        fecha = (datetime.now(timezone.utc).date()
                 + timedelta(days=dia_offset + extra)).isoformat()
        libres = _slots_libres(espacio["id"], s.token, fecha)
        if not libres:
            continue
        ini, fin = _ventana(libres, minutos, indice)
        if ini is None:
            continue
        cuerpo = {
            "space_id": espacio["id"],
            "start_time": ini["ini"].isoformat(),
            "end_time": fin["fin"].isoformat(),
            "guests_count": 1,
            "notes": f"{MARCA} ({s.codigo}) {nota_extra}".strip(),
        }
        if user_id:
            cuerpo["user_id"] = user_id
        r = peticion("POST", "/reservations/reservations/", token=s.token,
                     json_body=cuerpo)
        creada = r["cuerpo"] if r["status"] == 201 else {}
        detalle = (f"id={creada.get('id')} estado={creada.get('status')} "
                   f"total={creada.get('total_amount')} ({minutos} min)")
        if r["status"] != 201:
            detalle += f" | {json.dumps(r['cuerpo'], ensure_ascii=False)[:170]}"
        if r["status"] == 201:
            ESTADO["reservas"].append(creada.get("id"))
            registro = {"id": creada.get("id"), "space_id": espacio["id"],
                        "start_time": cuerpo["start_time"],
                        "end_time": cuerpo["end_time"],
                        "status": creada.get("status"), "user_id": s.user_id}
            if creada.get("status") == "PENDING":
                ESTADO["pendientes"].append(registro)
            elif creada.get("status") == "CONFIRMED":
                ESTADO["confirmadas"].append(registro)
            if s.codigo.startswith("SIM-CLI"):
                _guardar_propia(s, registro)
        return {"ok": r["status"] == 201, "http": r["status"], "interacciones": 2,
                "detalle": detalle, "datos": {"id": creada.get("id")}}
    return {"ok": False, "http": 0, "interacciones": 1,
            "detalle": "sin franjas libres suficientes"}


_PROPIAS: dict[str, list] = {}


def _guardar_propia(s: Sesion, registro: dict) -> None:
    _PROPIAS.setdefault(s.codigo, []).append(registro)


def _ultima_reserva_directa(s: Sesion) -> dict | None:
    propias = _PROPIAS.get(s.codigo, [])
    for reg in reversed(propias):
        if reg.get("status") == "CONFIRMED":
            return reg
    return None


def _tomar_pendiente() -> dict | None:
    while ESTADO["pendientes"]:
        reg = ESTADO["pendientes"].pop(0)
        return reg
    return None


def _tomar_confirmada() -> dict | None:
    while ESTADO["confirmadas"]:
        reg = ESTADO["confirmadas"].pop(0)
        return reg
    return None


def _listar_reservas(s: Sesion) -> dict:
    r = peticion("GET", "/reservations/reservations/", token=s.token)
    return {"ok": r["status"] == 200, "http": r["status"], "interacciones": 1,
            "detalle": f"reservas_visibles={len(lista(r['cuerpo']))}"}


def _todas_reservas(token: str) -> list:
    """Recorre todas las paginas del listado de reservas."""
    salida: list = []
    ruta = "/reservations/reservations/"
    for _ in range(20):
        r = peticion("GET", ruta, token=token)
        cuerpo = r["cuerpo"]
        salida.extend(lista(cuerpo))
        siguiente = cuerpo.get("next") if isinstance(cuerpo, dict) else None
        if not siguiente:
            break
        ruta = siguiente.split("/api/v1", 1)[-1]
    return salida


# ===========================================================================
# Fases
# ===========================================================================
def fase_preparar(admin_token: str) -> bool:
    print("\n=== FASE 1: preparacion (datos maestros y espacio de trabajo) ===")
    r = peticion("GET", "/reservations/spaces/", token=admin_token)
    espacios = lista(r["cuerpo"])
    if not espacios:
        print("  !! No se pudieron listar espacios.")
        return False
    directo = next((e for e in espacios if not e.get("requires_employee_approval")), None)
    aprobacion = next((e for e in espacios if e.get("requires_employee_approval")), None)
    ESTADO["espacio_directo"] = directo or espacios[0]
    ESTADO["espacio_aprobacion"] = aprobacion or espacios[-1]
    print(f"  espacio sin aprobacion : {ESTADO['espacio_directo']['code']}")
    print(f"  espacio con aprobacion : {ESTADO['espacio_aprobacion']['code']}")

    print("\n=== FASE 2: creacion de los 6 usuarios sinteticos (2 por rol) ===")
    for definicion in USUARIOS_SINTETICOS:
        alta = {
            "username": definicion["usuario"] + "_sim",
            "email": definicion["usuario"] + "_sim@example.com",
            "first_name": "Usuario",
            "last_name": definicion["codigo"].replace("-", " "),
            "document_type": "CC",
            "document_number": None,
            "phone": "+573000000000",
            "role": definicion["rol"],
            "password": CLAVE_SIM,
            "is_active": True,
        }
        alta["document_number"] = None
        r = peticion("POST", "/auth/admin/users/", token=admin_token, json_body=alta)
        if r["status"] == 201:
            definicion["usuario"] = alta["username"]  # el login usa el username real
            # La respuesta de alta no devuelve "id": se resuelve por busqueda.
            busq = peticion("GET", "/auth/admin/users/", token=admin_token,
                            params={"q": alta["username"]})
            usuario_id = next(
                (u.get("id") for u in lista(busq["cuerpo"])
                 if u.get("username") == alta["username"]), None)
            ESTADO["usuarios_creados"].append({
                "codigo": definicion["codigo"],
                "username": alta["username"],
                "id": usuario_id,
                "rol": definicion["rol"],
            })
            if definicion["rol"] == "CLIENT" and usuario_id:
                ESTADO["clientes_ids"].append(usuario_id)
            print(f"  [OK ] {definicion['codigo']} -> {alta['username']} "
                  f"(id={usuario_id}, rol={definicion['rol']})")
        else:
            print(f"  [NO ] {definicion['codigo']} -> HTTP {r['status']} "
                  f"{json.dumps(r['cuerpo'], ensure_ascii=False)[:120]}")
            return False
    return True


def fase_sesiones() -> None:
    print("\n=== FASE 3: sesiones simuladas por rol ===")
    # Orden de trabajo real: primero los clientes generan solicitudes,
    # luego recepcion las gestiona y el administrador supervisa.
    orden = [
        ("SIM-CLI-A", sesion_cliente, {"dia_offset": 30}),
        ("SIM-CLI-B", sesion_cliente, {"dia_offset": 33}),
        ("SIM-REC-A", sesion_recepcion, {}),
        ("SIM-REC-B", sesion_recepcion, {}),
        ("SIM-ADM-A", sesion_admin, {}),
        ("SIM-ADM-B", sesion_admin, {}),
    ]
    for codigo, funcion, kwargs in orden:
        definicion = next(d for d in USUARIOS_SINTETICOS if d["codigo"] == codigo)
        s = Sesion(definicion)
        s.t0 = time.perf_counter()
        print(f"\n-- Sesion {codigo} ({definicion['rol']}, competencia "
              f"{definicion['competencia']}) --")
        funcion(s, **kwargs) if kwargs else funcion(s)
        duracion = time.perf_counter() - s.t0
        completadas = sum(1 for t in s.tareas if t["completada"] == "SI")
        SESIONES.append({
            "codigo_usuario": s.codigo,
            "rol": s.rol,
            "competencia": s.competencia,
            "tareas": len(s.tareas),
            "completadas": completadas,
            "no_completadas": len(s.tareas) - completadas,
            "efectividad_pct": round(100 * completadas / len(s.tareas), 1) if s.tareas else 0,
            "duracion_tecnica_s": round(duracion, 2),
            "tiempo_simulado_s": round(
                sum(t["tiempo_simulado_s"] for t in s.tareas), 2),
            "interacciones": sum(t["interacciones"] for t in s.tareas),
            "errores": sum(t["errores"] for t in s.tareas),
            "facilidad_media": round(
                sum(t["facilidad_1_5"] for t in s.tareas) / len(s.tareas), 2) if s.tareas else 0,
            "claridad_media": round(
                sum(t["claridad_1_5"] for t in s.tareas) / len(s.tareas), 2) if s.tareas else 0,
            "satisfaccion_media": round(
                sum(t["satisfaccion_1_5"] for t in s.tareas) / len(s.tareas), 2) if s.tareas else 0,
        })
        print(f"   -> {completadas}/{len(s.tareas)} tareas completadas "
              f"({SESIONES[-1]['efectividad_pct']}%) en {duracion:.1f}s reales")


def fase_transversal(admin_token: str) -> None:
    """Verificaciones que no dependen de un rol operativo concreto."""
    print("\n=== FASE 4: verificaciones transversales ===")
    r = peticion("GET", "/health/")
    info = r["cuerpo"]
    print(f"  [{'OK ' if r['status'] == 200 else 'NO '}] RNF-DIS-01 health -> HTTP "
          f"{r['status']} database={info.get('database')} version={info.get('version')}")
    r2 = peticion("GET", "/reservations/reservations/")
    print(f"  [{'OK ' if r2['status'] == 401 else 'NO '}] RNF-ERR-02 sin credenciales -> "
          f"HTTP {r2['status']}")
    r3 = peticion("GET", "/reports/dashboard/summary/", token=admin_token)
    print(f"  [{'OK ' if r3['status'] == 200 else 'NO '}] RQF-AUT-04 panel admin -> "
          f"HTTP {r3['status']}")


def fase_limpiar(admin_token: str) -> None:
    print("\n=== FASE 5: limpieza (eliminar datos de prueba) ===")
    # 1) Reservas marcadas con MARCA
    reservas = _todas_reservas(admin_token)
    de_prueba = [x for x in reservas if MARCA in (x.get("notes") or "")]
    borradas = 0
    canceladas = 0
    for res in de_prueba:
        d = peticion("DELETE", f"/reservations/reservations/{res['id']}/",
                     token=admin_token)
        if d["status"] in (204, 200):
            borradas += 1
        else:
            c = peticion("POST", f"/reservations/reservations/{res['id']}/cancel/",
                         token=admin_token, json_body={"reason": "limpieza simulacion"})
            if c["status"] == 200:
                canceladas += 1
            else:
                print(f"  [NO ] reserva {res['id']}: DELETE HTTP {d['status']}, "
                      f"cancel HTTP {c['status']}")
    print(f"  reservas de prueba: {borradas} eliminadas, {canceladas} canceladas "
          f"de {len(de_prueba)} (total en el club: {len(reservas)})")
    restantes = [x for x in _todas_reservas(admin_token)
                 if MARCA in (x.get("notes") or "")]
    print(f"  verificacion: quedan {len(restantes)} reservas de prueba en el club")

    # 2) Usuarios sinteticos
    eliminados = 0
    for reg in ESTADO["usuarios_creados"]:
        if reg.get("id") is None:
            continue
        d = peticion("DELETE", f"/auth/admin/users/{reg['id']}/", token=admin_token)
        if d["status"] in (204, 200):
            eliminados += 1
            print(f"  [OK ] usuario eliminado: {reg['username']}")
        else:
            print(f"  [NO ] no se pudo eliminar {reg['username']} (HTTP {d['status']})")

    # 3) Restos de ejecuciones previas
    restos = peticion("GET", "/auth/admin/users/", token=admin_token, params={"q": "sim_"})
    for u in lista(restos["cuerpo"]):
        if str(u.get("username", "")).startswith("sim_"):
            peticion("DELETE", f"/auth/admin/users/{u['id']}/", token=admin_token)
    print(f"  usuarios sinteticos eliminados: {eliminados}/{len(ESTADO['usuarios_creados'])}")


# ===========================================================================
# Exportacion
# ===========================================================================
def exportar() -> None:
    def escribir_csv(nombre, campos, filas):
        ruta = DIR_EVIDENCIAS / nombre
        with ruta.open("w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=campos, delimiter=";")
            w.writeheader()
            for fila in filas:
                w.writerow({c: fila.get(c, "") for c in campos})
        print(f"  CSV: {ruta}")

    campos_t = ["codigo_usuario", "rol", "competencia", "id_tarea", "requisito",
                "descripcion", "http", "completada", "interacciones",
                "duracion_tecnica_s", "tiempo_simulado_s", "errores",
                "facilidad_1_5", "claridad_1_5", "satisfaccion_1_5", "detalle", "datos"]
    campos_s = ["codigo_usuario", "rol", "competencia", "tareas", "completadas",
                "no_completadas", "efectividad_pct", "duracion_tecnica_s",
                "tiempo_simulado_s", "interacciones", "errores", "facilidad_media",
                "claridad_media", "satisfaccion_media"]
    escribir_csv("simulacion_aceptacion_tareas.csv", campos_t, TAREAS)
    escribir_csv("simulacion_aceptacion_sesiones.csv", campos_s, SESIONES)

    total = len(TAREAS)
    completadas = sum(1 for t in TAREAS if t["completada"] == "SI")
    requisitos = sorted({t["requisito"] for t in TAREAS})
    resumen = {
        "fecha_ejecucion": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "url": BASE,
        "naturaleza": "SIMULACION con usuarios sinteticos (no participaron personas reales)",
        "usuarios_simulados": [d["codigo"] for d in USUARIOS_SINTETICOS],
        "sesiones": len(SESIONES),
        "tareas_ejecutadas": total,
        "tareas_completadas": completadas,
        "efectividad_global_pct": round(100 * completadas / total, 1) if total else 0,
        "requisitos_cubiertos": requisitos,
        "detalle_tareas": TAREAS,
        "resumen_sesiones": SESIONES,
    }
    (DIR_EVIDENCIAS / "simulacion_aceptacion.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")

    # --- Informe Markdown ---
    lineas = [
        "# Evaluacion SIMULADA de aceptacion y usabilidad (usuarios sinteticos)",
        "",
        "> Family Health MF - 2 usuarios sinteticos por rol (6 en total).",
        "> NO participaron personas reales: las sesiones las ejecuto un script.",
        "",
        f"- **URL evaluada:** {BASE}",
        f"- **Fecha/hora (UTC):** {resumen['fecha_ejecucion']}",
        f"- **Sesiones simuladas:** {len(SESIONES)}",
        f"- **Tareas ejecutadas:** {total}",
        f"- **Tareas completadas:** {completadas} "
        f"({resumen['efectividad_global_pct']} %)",
        f"- **Requisitos cubiertos:** {len(requisitos)}",
        "",
        "## Advertencia de naturaleza de los datos",
        "",
        "Los tiempos, codigos HTTP, errores y resultados SON REALES (medidos",
        "contra el despliegue). Las puntuaciones de **facilidad, claridad y",
        "satisfaccion (1-5) son SIMULADAS**: se derivan de un modelo determinista",
        "(base 5 para competencia Intermedia y 4 para Basica, con penalizacion por",
        "errores y tareas no completadas). **No son opiniones de usuarios reales y",
        "no deben presentarse como tal.**",
        "",
        "## Resumen por sesion simulada",
        "",
        "| Usuario | Rol | Competencia | Tareas | Completadas | Efectividad % | "
        "Tiempo real (s) | Tiempo simulado (s) | Facilidad* | Claridad* | Satisfaccion* |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for s in SESIONES:
        lineas.append(
            f"| {s['codigo_usuario']} | {s['rol']} | {s['competencia']} | {s['tareas']} | "
            f"{s['completadas']} | {s['efectividad_pct']} | {s['duracion_tecnica_s']} | "
            f"{s['tiempo_simulado_s']} | {s['facilidad_media']} | {s['claridad_media']} | "
            f"{s['satisfaccion_media']} |")
    lineas += ["", "\\* Puntuaciones simuladas (ver advertencia).", "",
               "## Detalle de tareas ejecutadas", "",
               "| Usuario | ID | Requisito | Descripcion | HTTP | Completada | "
               "Interacciones | Duracion real (s) | Errores |",
               "|---|---|---|---|---|---|---|---|---|"]
    for t in TAREAS:
        lineas.append(
            f"| {t['codigo_usuario']} | {t['id_tarea']} | {t['requisito']} | "
            f"{t['descripcion']} | {t['http']} | {t['completada']} | "
            f"{t['interacciones']} | {t['duracion_tecnica_s']} | {t['errores']} |")
    lineas += [
        "",
        "## Requisitos cubiertos",
        "",
        ", ".join(requisitos),
        "",
        "## Limpieza",
        "",
        "Las cuentas y reservas creadas se marcan con el texto "
        f"`{MARCA}` y se eliminan en la fase de limpieza del script",
        "(salvo que se ejecute con el argumento `sin-limpiar`).",
        "",
    ]
    (DIR_EVIDENCIAS / "simulacion_aceptacion.md").write_text(
        "\n".join(lineas), encoding="utf-8")

    print(f"\n  JSON: {DIR_EVIDENCIAS / 'simulacion_aceptacion.json'}")
    print(f"  MD  : {DIR_EVIDENCIAS / 'simulacion_aceptacion.md'}")
    print(f"\n>>> RESUMEN: {len(SESIONES)} sesiones | {total} tareas | "
          f"{completadas} completadas ({resumen['efectividad_global_pct']} %) | "
          f"{len(requisitos)} requisitos cubiertos")


# ===========================================================================
# main
# ===========================================================================
def main() -> int:
    modo = sys.argv[1] if len(sys.argv) > 1 else "completo"
    print("=" * 76)
    print("EVALUACION SIMULADA DE ACEPTACION - CLUB FAMILY HEALTH MF")
    print("Usuarios sinteticos: 2 por rol (6 en total). NO participan personas.")
    print(f"URL: {BASE}")
    print(f"Fecha/hora (UTC): {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    print("=" * 76)

    if not ADMIN_DEMO[1]:
        print("!! Falta FH_PASS_ADMIN en .env.evidencias")
        return 2

    r = login(*ADMIN_DEMO)
    if r["status"] != 200:
        print(f"!! No se pudo autenticar el administrador demo (HTTP {r['status']})")
        return 2
    admin_token = r["cuerpo"].get("access", "")
    print(f"Administrador demo autenticado: {ADMIN_DEMO[0]}")

    if modo == "limpiar":
        ESTADO["usuarios_creados"] = [
            {"codigo": u.get("username"), "username": u.get("username"), "id": u["id"]}
            for u in lista(peticion("GET", "/auth/admin/users/", token=admin_token,
                                    params={"q": "sim_"})["cuerpo"])
            if str(u.get("username", "")).startswith("sim_")
        ]
        fase_limpiar(admin_token)
        return 0

    codigo = 0
    try:
        if not fase_preparar(admin_token):
            return 1
        fase_sesiones()
        fase_transversal(admin_token)
    except Exception as e:  # noqa: BLE001
        print(f"!! Excepcion durante la simulacion: {e}")
        codigo = 1
    finally:
        exportar()
        if modo != "sin-limpiar":
            time.sleep(2)
            fase_limpiar(admin_token)
        else:
            print("\n!! Datos de prueba CONSERVADOS (modo sin-limpiar).")
    return codigo


if __name__ == "__main__":
    sys.exit(main())
