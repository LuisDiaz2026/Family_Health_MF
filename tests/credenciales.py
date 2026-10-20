"""
Carga de credenciales de prueba para los scripts de evidencia.

Las contrasenas NUNCA se escriben en el codigo ni en los comandos. Se leen,
por orden de prioridad, desde:

    1. Variables de entorno del sistema (FH_PASS_ADMIN, ...).
    2. El archivo local `.env.evidencias` (ignorado por Git), con el formato
       CLAVE=valor, una por linea (ver `.env.evidencias.example`).

Si el usuario prefiere, puede colocar temporalmente los valores en el archivo
y borrarlos despues; los scripts solo los leen en memoria.
"""
from __future__ import annotations

import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ARCHIVO_LOCAL = RAIZ / ".env.evidencias"

_CLAVES = (
    "FH_USER_ADMIN", "FH_PASS_ADMIN",
    "FH_USER_RECEPCION", "FH_PASS_RECEPCION",
    "FH_USER_CAFETERIA", "FH_PASS_CAFETERIA",
    "FH_USER_CLIENTE1", "FH_PASS_CLIENTE1",
    "FH_USER_CLIENTE2", "FH_PASS_CLIENTE2",
    "FH_BASE",
)


def _leer_archivo() -> dict:
    valores: dict = {}
    if not ARCHIVO_LOCAL.exists():
        return valores
    try:
        for linea in ARCHIVO_LOCAL.read_text(encoding="utf-8").splitlines():
            linea = linea.strip()
            if not linea or linea.startswith("#") or "=" not in linea:
                continue
            clave, valor = linea.split("=", 1)
            valores[clave.strip()] = valor.strip().strip('"').strip("'")
    except OSError:  # pragma: no cover - proteccion ante archivo ilegible
        return {}
    return valores


def obtener(clave: str, defecto: str = "") -> str:
    """Devuelve el valor de `clave` (entorno primero, luego archivo local)."""
    return os.getenv(clave) or _leer_archivo().get(clave, "") or defecto


def cargar_en_entorno() -> None:
    """Exporta al entorno las claves del archivo local que aun no existan."""
    for clave, valor in _leer_archivo().items():
        if clave in _CLAVES and not os.getenv(clave):
            os.environ[clave] = valor
