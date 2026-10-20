"""
Punto de entrada de la suite de pruebas con evidencias.

Ejecuta realmente las pruebas y genera:
    evidencias/pruebas_unitarias.{txt,json,csv}
    evidencias/pruebas_integracion.{txt,json,csv}

Uso (desde la raíz del repositorio):
    python tests/run_suite.py unit
    python tests/run_suite.py integration
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "backend"))

# Las evidencias se generan SIEMPRE sobre SQLite de prueba aislada.
# Se neutraliza cualquier DATABASE_URL (global de Windows o del entorno) que
# apunte a PostgreSQL/Neon, para no mezclar datos de desarrollo con pruebas.
os.environ["DATABASE_URL"] = ""
os.environ["DB_ENGINE"] = "django.db.backends.sqlite3"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django  # noqa: E402

django.setup()

from tests.runner import ejecutar  # noqa: E402


def _git(*args):
    exe = shutil.which("git") or r"C:\Program Files\Git\cmd\git.exe"
    try:
        return subprocess.check_output(
            [exe, "-C", str(RAIZ), *args], text=True
        ).strip()
    except Exception:
        return "desconocido"


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("unit", "integration"):
        print("Uso: python tests/run_suite.py [unit|integration]")
        return 2

    tipo = sys.argv[1]
    if tipo == "unit":
        prefijo = "pruebas_unitarias"
        ruta = RAIZ / "tests" / "unit"
    else:
        prefijo = "pruebas_integracion"
        ruta = RAIZ / "tests" / "integration"

    commit = _git("rev-parse", "HEAD")
    entorno = f"Local ({sys.platform}) / Django test runner"
    base_datos = "SQLite en memoria (base de datos de prueba aislada)"

    print(f">>> Ejecutando pruebas '{tipo}' desde {ruta}")
    resumen, codigo = ejecutar(prefijo, ruta, commit, entorno, base_datos)
    print("\n>>> RESUMEN")
    for clave, valor in resumen.items():
        print(f"    {clave}: {valor}")
    return codigo


if __name__ == "__main__":
    sys.exit(main())
