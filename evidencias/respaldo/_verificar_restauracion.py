"""Script temporal de verificacion de restauracion (Family Health MF).

Apunta Django a un archivo SQLite restaurado (pasado por argumento) ANTES de
django.setup(), sin tocar backend\\db.sqlite3 ni produccion.
Uso:  python _verificar_restauracion.py <ruta_archivo_sqlite_restaurado>
"""
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Python usa como sys.path[0] la carpeta del script; se agrega manualmente el
# directorio del backend del proyecto para poder importar 'config' y 'apps'.
BACKEND_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "backend")
)
sys.path.insert(0, BACKEND_DIR)

ruta = sys.argv[1]

import django  # noqa: E402
from django.conf import settings  # noqa: E402

settings.DATABASES["default"]["NAME"] = ruta

django.setup()

from apps.authentication.models import User  # noqa: E402
from apps.refreshments.models import Product  # noqa: E402
from apps.reservations.models import Reservation, Space  # noqa: E402

print("ARCHIVO_VERIFICADO=", settings.DATABASES["default"]["NAME"])
print("RESTAURADO usuarios=", User.objects.count())
print("RESTAURADO espacios=", Space.objects.count())
print("RESTAURADO reservas=", Reservation.objects.count())
print("RESTAURADO productos=", Product.objects.count())
