"""
Pruebas unitarias - Espacios, horarios y disponibilidad (U12 - U16).
"""
from decimal import Decimal

from apps.reservations.models import Space
from tests.base import BasePruebas, crear_horario
from tests.harness import registrar


class EspaciosTests(BasePruebas):

    def _resultados(self, resp):
        datos = resp.json()
        if isinstance(datos, dict) and "results" in datos:
            return datos["results"]
        return datos

    def test_u12_listar_espacios(self):
        """U12 | RQF-ESP-01 | Espacios | GET /api/v1/reservations/spaces/ autenticado como CLIENT | HTTP 200 e incluye el espacio ESP-TEST-01"""
        self.autenticar(self.cliente)
        resp = self.client.get("/api/v1/reservations/spaces/")
        resultados = self._resultados(resp)
        codigos = sorted(e.get("code") for e in resultados)
        registrar("U12", (
            f"HTTP {resp.status_code}; n_espacios={len(resultados)}; "
            f"codigos={codigos}"
        ))
        self.assertEqual(resp.status_code, 200)
        self.assertIn("ESP-TEST-01", codigos)

    def test_u13_detalle_espacio_tarifa_y_limites(self):
        """U13 | RQF-ESP-02 | Espacios | GET /api/v1/reservations/spaces/{id}/ | HTTP 200 con hourly_rate=50000.00, min=30 y max=180"""
        self.autenticar(self.cliente)
        resp = self.client.get(f"/api/v1/reservations/spaces/{self.space.id}/")
        datos = resp.json()
        registrar("U13", (
            f"HTTP {resp.status_code}; hourly_rate={datos.get('hourly_rate')}; "
            f"min_reservation_minutes={datos.get('min_reservation_minutes')}; "
            f"max_reservation_minutes={datos.get('max_reservation_minutes')}"
        ))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Decimal(str(datos["hourly_rate"])), Decimal("50000.00"))
        self.assertEqual(datos["min_reservation_minutes"], 30)
        self.assertEqual(datos["max_reservation_minutes"], 180)

    def test_u14_disponibilidad_franjas_30_min(self):
        """U14 | RQF-ESP-03 | Disponibilidad | GET spaces/{id}/availability/?date= (horario 06:00-22:00) | HTTP 200 y 32 franjas de 30 minutos"""
        fecha = self.futuro(dias=3).date()
        crear_horario(self.space, weekday=fecha.weekday())
        self.autenticar(self.cliente)
        resp = self.client.get(
            f"/api/v1/reservations/spaces/{self.space.id}/availability/",
            {"date": fecha.isoformat()},
        )
        datos = resp.json()
        franjas = datos.get("thirty_minute_slots", [])
        registrar("U14", (
            f"HTTP {resp.status_code}; n_franjas={len(franjas)}; "
            f"primera={franjas[0]['time'] if franjas else None}; "
            f"ultima={franjas[-1]['time'] if franjas else None}"
        ))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(franjas), 32)

    def test_u15_disponibilidad_fecha_invalida(self):
        """U15 | RQF-ESP-04 | Disponibilidad | GET availability con date=2026-13-45 | HTTP 400 con mensaje de fecha inválida"""
        self.autenticar(self.cliente)
        resp = self.client.get(
            f"/api/v1/reservations/spaces/{self.space.id}/availability/",
            {"date": "2026-13-45"},
        )
        datos = resp.json()
        registrar("U15", f"HTTP {resp.status_code}; mensaje={datos.get('error')}")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("error", datos)

    def test_u16_is_available_at_logica_modelo(self):
        """U16 | RQF-ESP-05 | Modelo Space | Space.is_available_at() en franja libre y con status=MAINTENANCE | True cuando está libre y False cuando no está ACTIVE"""
        libre = self.space.is_available_at(self.futuro(5, 9), self.futuro(5, 10))
        self.space.status = Space.STATUS_MAINTENANCE
        self.space.save(update_fields=["status"])
        mantenimiento = self.space.is_available_at(
            self.futuro(5, 9), self.futuro(5, 10)
        )
        registrar("U16", (
            f"franja_libre={libre}; status_MAINTENANCE={mantenimiento}"
        ))
        self.assertTrue(libre)
        self.assertFalse(mantenimiento)
