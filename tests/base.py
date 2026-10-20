"""
Datos y utilidades compartidas por la suite de pruebas.

Las cuentas/espacios/reservas creadas aquí son DATOS DE PRUEBA CONTROLADOS:
se crean dentro de la base de datos de prueba aislada de Django y se destruyen
al finalizar la ejecución, por lo que no se mezclan con datos operativos.
"""
from datetime import time, timedelta
from decimal import Decimal

from django.utils import timezone
from rest_framework.test import APITestCase

from apps.authentication.models import User
from apps.reservations.models import (
    Holiday, OperatingHours, Reservation, Space, SpaceType,
)

PASSWORD_PRUEBA = "PruebaFH2026*!"
_contador_documento = {"n": 900000000}


def siguiente_documento() -> str:
    _contador_documento["n"] += 1
    return str(_contador_documento["n"])


def crear_usuario(username, role, activo=True, password=PASSWORD_PRUEBA, **extra):
    """Crea un usuario de prueba controlado."""
    extra.setdefault("first_name", username.capitalize())
    extra.setdefault("last_name", "Prueba")
    extra.setdefault("document_type", "CC")
    extra.setdefault("document_number", siguiente_documento())
    extra.setdefault("is_active", activo)
    email = extra.pop("email", f"{username}@prueba.local")
    return User.objects.create_user(
        username=username, email=email, password=password, role=role, **extra,
    )


def crear_espacio(tipo, codigo, nombre=None, **kwargs):
    """Crea un espacio de prueba controlado con valores por defecto razonables."""
    nombre = nombre or f"Espacio {codigo}"
    valores = {
        "space_type": tipo,
        "name": nombre,
        "code": codigo,
        "capacity": 20,
        "hourly_rate": Decimal("50000.00"),
        "requires_employee_approval": False,
        "min_reservation_minutes": 30,
        "max_reservation_minutes": 180,
        "advance_days_limit": 30,
        "cancellation_penalty_hours": 6,
        "status": Space.STATUS_ACTIVE,
    }
    valores.update(kwargs)
    return Space.objects.create(**valores)


def crear_horario(space, weekday=0, apertura=time(6, 0), cierre=time(22, 0),
                  cerrado=False):
    return OperatingHours.objects.create(
        space=space, weekday=weekday, open_time=apertura,
        close_time=cierre, is_closed=cerrado,
    )


class BasePruebas(APITestCase):
    """Base con usuarios y espacio de prueba controlados."""

    @classmethod
    def setUpTestData(cls):
        cls.tipo = SpaceType.objects.create(
            name="Tipo Test", description="Tipo de prueba", icon="🏟️",
        )
        cls.space = crear_espacio(cls.tipo, "ESP-TEST-01", "Espacio Test")
        cls.admin = crear_usuario("t_admin", User.ROLE_ADMIN)
        cls.admin.is_staff = True
        cls.admin.is_superuser = True
        cls.admin.save(update_fields=["is_staff", "is_superuser"])
        cls.recepcion = crear_usuario("t_recepcion", User.ROLE_RECEPCION)
        cls.cliente = crear_usuario("t_cliente", User.ROLE_CLIENT)
        cls.cliente2 = crear_usuario("t_cliente2", User.ROLE_CLIENT)

    def setUp(self):
        # Limpia el caché (throttling DRF y bloqueos de django-axes) para que
        # cada prueba se ejecute en condiciones controladas y reproducibles.
        from django.core.cache import cache
        cache.clear()

    # ---------- utilidades ----------
    def autenticar(self, usuario):
        """Fuerza autenticación JWT real obteniendo tokens del endpoint de login."""
        resp = self.client.post(
            "/api/v1/auth/login/",
            {"username": usuario.username, "password": PASSWORD_PRUEBA},
            format="json",
        )
        assert resp.status_code == 200, (
            f"Login de prueba falló para {usuario.username}: "
            f"{resp.status_code} {resp.content[:300]}"
        )
        token = resp.json()["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return token

    def cerrar_sesion(self):
        self.client.credentials()

    @staticmethod
    def futuro(dias=2, hora=10, minuto=0):
        base = timezone.localtime(timezone.now()) + timedelta(days=dias)
        return base.replace(hour=hora, minute=minuto, second=0, microsecond=0)
