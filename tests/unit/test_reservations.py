"""
Pruebas unitarias - Reservas: creación, cálculo, validaciones y estados (U17 - U31).
"""
from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

from apps.reservations.models import Reservation
from tests.base import BasePruebas, crear_espacio
from tests.harness import registrar


class ReservasTests(BasePruebas):

    # ---------- utilidades ----------
    def _resultados(self, resp):
        datos = resp.json()
        if isinstance(datos, dict) and "results" in datos:
            return datos["results"]
        return datos

    def _crear_reserva(self, space=None, user=None, dias=4, hora=10,
                       duracion_min=60, **extra):
        """Crea una reserva controlada directamente en el modelo."""
        space = space or self.space
        user = user or self.cliente
        inicio = self.futuro(dias, hora)
        fin = inicio + timedelta(minutes=duracion_min)
        return Reservation.objects.create(
            space=space, user=user, created_by=user,
            start_time=inicio, end_time=fin, **extra
        )

    def _payload(self, space, inicio, fin, invitados=1, **extra):
        datos = {
            "space_id": space.id,
            "start_time": inicio.isoformat(),
            "end_time": fin.isoformat(),
            "guests_count": invitados,
        }
        datos.update(extra)
        return datos

    # ---------- creación y cálculo ----------
    def test_u17_cliente_crea_reserva_valida(self):
        """U17 | RQF-RES-01 | Reservas | POST reservations/ como CLIENT en espacio sin aprobación | HTTP 201 con status CONFIRMED y usuario = cliente"""
        self.autenticar(self.cliente)
        resp = self.client.post(
            "/api/v1/reservations/reservations/",
            self._payload(self.space, self.futuro(4, 10), self.futuro(4, 11),
                          invitados=2),
            format="json",
        )
        datos = resp.json()
        reserva = Reservation.objects.filter(pk=datos.get("id")).first()
        registrar("U17", (
            f"HTTP {resp.status_code}; status={datos.get('status')}; "
            f"user_id={getattr(reserva, 'user_id', None)}"
        ))
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(datos["status"], Reservation.STATUS_CONFIRMED)
        self.assertIsNotNone(reserva)
        self.assertEqual(reserva.user_id, self.cliente.id)

    def test_u18_espacio_con_aprobacion_crea_pendiente(self):
        """U18 | RQF-RES-02 | Workflow | POST como CLIENT en espacio con requires_employee_approval=True | HTTP 201 con status PENDING"""
        espacio = crear_espacio(
            self.tipo, "ESP-APROB-01", "Espacio con aprobación",
            requires_employee_approval=True,
        )
        self.autenticar(self.cliente)
        resp = self.client.post(
            "/api/v1/reservations/reservations/",
            self._payload(espacio, self.futuro(4, 12), self.futuro(4, 13)),
            format="json",
        )
        datos = resp.json()
        registrar("U18", f"HTTP {resp.status_code}; status={datos.get('status')}")
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(datos["status"], Reservation.STATUS_PENDING)

    def test_u19_calculo_total_amount(self):
        """U19 | RQF-RES-03 | Cálculo | Reserva de 90 minutos con tarifa 50000 COP/hora | total_minutes=90 y total_amount=75000.00"""
        self.autenticar(self.cliente)
        resp = self.client.post(
            "/api/v1/reservations/reservations/",
            self._payload(self.space, self.futuro(4, 10), self.futuro(4, 11, 30)),
            format="json",
        )
        datos = resp.json()
        registrar("U19", (
            f"HTTP {resp.status_code}; total_minutes={datos.get('total_minutes')}; "
            f"total_amount={datos.get('total_amount')}"
        ))
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(datos["total_minutes"], 90)
        self.assertEqual(Decimal(str(datos["total_amount"])), Decimal("75000.00"))

    # ---------- validaciones de duración y fecha ----------
    def test_u20_duracion_menor_al_minimo(self):
        """U20 | RQF-RES-04 | Validación duración | POST de 15 minutos (mínimo del espacio = 30) | HTTP 400 y sin reserva creada"""
        self.autenticar(self.cliente)
        antes = Reservation.objects.count()
        resp = self.client.post(
            "/api/v1/reservations/reservations/",
            self._payload(self.space, self.futuro(4, 10), self.futuro(4, 10, 15)),
            format="json",
        )
        registrar("U20", (
            f"HTTP {resp.status_code}; reservas_antes={antes}; "
            f"reservas_despues={Reservation.objects.count()}"
        ))
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(Reservation.objects.count(), antes)

    def test_u21_duracion_mayor_al_maximo(self):
        """U21 | RQF-RES-05 | Validación duración | POST de 240 minutos (máximo del espacio = 180) | HTTP 400 y sin reserva creada"""
        self.autenticar(self.cliente)
        antes = Reservation.objects.count()
        resp = self.client.post(
            "/api/v1/reservations/reservations/",
            self._payload(self.space, self.futuro(4, 8), self.futuro(4, 12)),
            format="json",
        )
        registrar("U21", (
            f"HTTP {resp.status_code}; duracion_solicitada_min=240; "
            f"reservas_despues={Reservation.objects.count()}"
        ))
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(Reservation.objects.count(), antes)

    def test_u22_reserva_en_el_pasado(self):
        """U22 | RQF-RES-06 | Validación fecha | POST con start_time en el pasado | HTTP 400 (la reserva debe ser en el futuro)"""
        self.autenticar(self.cliente)
        ayer = timezone.localtime(timezone.now()) - timedelta(days=1)
        resp = self.client.post(
            "/api/v1/reservations/reservations/",
            self._payload(self.space, ayer, ayer + timedelta(hours=1)),
            format="json",
        )
        registrar("U22", f"HTTP {resp.status_code}; detalle={str(resp.json())[:140]}")
        self.assertEqual(resp.status_code, 400)

    # ---------- anti-solapamiento ----------
    def test_u23_solapamiento_exacto_rechazado(self):
        """U23 | RQF-RES-07 | Anti-solapamiento | POST con la misma franja de una reserva existente | HTTP 400 y la reserva total no aumenta"""
        self._crear_reserva(dias=5, hora=10, duracion_min=60)
        self.autenticar(self.cliente)
        resp = self.client.post(
            "/api/v1/reservations/reservations/",
            self._payload(self.space, self.futuro(5, 10), self.futuro(5, 11)),
            format="json",
        )
        registrar("U23", (
            f"HTTP {resp.status_code}; total_reservas={Reservation.objects.count()}"
        ))
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(Reservation.objects.count(), 1)

    def test_u24_solapamiento_parcial_rechazado(self):
        """U24 | RQF-RES-08 | Anti-solapamiento | POST 10:30-11:30 solapando con reserva existente 10:00-11:00 | HTTP 400 por conflicto"""
        self._crear_reserva(dias=5, hora=10, duracion_min=60)
        self.autenticar(self.cliente)
        resp = self.client.post(
            "/api/v1/reservations/reservations/",
            self._payload(self.space, self.futuro(5, 10, 30), self.futuro(5, 11, 30)),
            format="json",
        )
        registrar("U24", (
            f"HTTP {resp.status_code}; total_reservas={Reservation.objects.count()}"
        ))
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(Reservation.objects.count(), 1)

    def test_u25_reserva_adyacente_permitida(self):
        """U25 | RQF-RES-09 | Anti-solapamiento | POST 11:00-12:00 contigua a reserva 10:00-11:00 | HTTP 201 (no hay solapamiento real)"""
        self._crear_reserva(dias=5, hora=10, duracion_min=60)
        self.autenticar(self.cliente)
        resp = self.client.post(
            "/api/v1/reservations/reservations/",
            self._payload(self.space, self.futuro(5, 11), self.futuro(5, 12)),
            format="json",
        )
        registrar("U25", (
            f"HTTP {resp.status_code}; total_reservas={Reservation.objects.count()}"
        ))
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Reservation.objects.count(), 2)

    # ---------- visibilidad y permisos ----------
    def test_u26_cliente_no_lista_ni_elimina(self):
        """U26 | RQF-RES-10 | Roles/permisos | CLIENT: GET listado global y DELETE de reserva | HTTP 403 en ambos casos y la reserva persiste"""
        reserva = self._crear_reserva(dias=5, hora=10, duracion_min=60)
        self.autenticar(self.cliente)
        listado = self.client.get("/api/v1/reservations/reservations/")
        borrado = self.client.delete(
            f"/api/v1/reservations/reservations/{reserva.id}/"
        )
        registrar("U26", (
            f"listado HTTP {listado.status_code}; borrado HTTP {borrado.status_code}; "
            f"reserva_persiste={Reservation.objects.filter(pk=reserva.id).exists()}"
        ))
        self.assertEqual(listado.status_code, 403)
        self.assertEqual(borrado.status_code, 403)
        self.assertTrue(Reservation.objects.filter(pk=reserva.id).exists())

    def test_u27_my_upcoming_solo_propias(self):
        """U27 | RQF-RES-11 | Reservas | GET reservations/my-upcoming/ como CLIENT | HTTP 200 y solo las reservas del propio cliente"""
        self._crear_reserva(dias=5, hora=10, duracion_min=60, user=self.cliente)
        self._crear_reserva(dias=5, hora=14, duracion_min=60, user=self.cliente2)
        self.autenticar(self.cliente)
        resp = self.client.get("/api/v1/reservations/reservations/my-upcoming/")
        datos = resp.json()
        usuarios = sorted({r["user"]["username"] for r in datos})
        registrar("U27", (
            f"HTTP {resp.status_code}; n={len(datos)}; usuarios={usuarios}"
        ))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(datos), 1)
        self.assertEqual(usuarios, [self.cliente.username])

    def test_u28_recepcion_lista_todas(self):
        """U28 | RQF-RES-12 | Roles/permisos | GET listado como RECEPCION | HTTP 200 y aparecen reservas de distintos clientes"""
        self._crear_reserva(dias=6, hora=10, duracion_min=60, user=self.cliente)
        self._crear_reserva(dias=6, hora=14, duracion_min=60, user=self.cliente2)
        self.autenticar(self.recepcion)
        resp = self.client.get("/api/v1/reservations/reservations/")
        resultados = self._resultados(resp)
        usuarios = sorted({r["user"]["username"] for r in resultados})
        registrar("U28", (
            f"HTTP {resp.status_code}; n={len(resultados)}; usuarios={usuarios}"
        ))
        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(len(resultados), 2)
        self.assertEqual(
            usuarios, sorted([self.cliente.username, self.cliente2.username])
        )

    # ---------- transiciones de estado ----------
    def test_u29_aprobar_reserva(self):
        """U29 | RQF-RES-13 | Estados | POST reservations/{id}/approve/ como RECEPCION sobre reserva PENDING | HTTP 200 con status CONFIRMED"""
        espacio = crear_espacio(
            self.tipo, "ESP-APROB-02", "Espacio aprobación 2",
            requires_employee_approval=True,
        )
        reserva = self._crear_reserva(
            space=espacio, dias=6, hora=10, duracion_min=60,
            status=Reservation.STATUS_PENDING,
        )
        self.autenticar(self.recepcion)
        resp = self.client.post(
            f"/api/v1/reservations/reservations/{reserva.id}/approve/"
        )
        datos = resp.json()
        reserva.refresh_from_db()
        registrar("U29", (
            f"HTTP {resp.status_code}; status={datos.get('status')}; "
            f"approved_by_id={reserva.approved_by_id}"
        ))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(datos["status"], Reservation.STATUS_CONFIRMED)
        self.assertEqual(reserva.approved_by_id, self.recepcion.id)

    def test_u30_rechazar_reserva(self):
        """U30 | RQF-RES-14 | Estados | POST reservations/{id}/reject/ como ADMIN sobre reserva PENDING | HTTP 200 con status REJECTED"""
        reserva = self._crear_reserva(
            dias=6, hora=15, duracion_min=60, status=Reservation.STATUS_PENDING,
        )
        self.autenticar(self.admin)
        resp = self.client.post(
            f"/api/v1/reservations/reservations/{reserva.id}/reject/",
            {"reason": "Sin disponibilidad de personal"}, format="json",
        )
        datos = resp.json()
        registrar("U30", f"HTTP {resp.status_code}; status={datos.get('status')}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(datos["status"], Reservation.STATUS_REJECTED)

    def test_u31_marcar_pagada(self):
        """U31 | RQF-RES-15 | Pagos | POST reservations/{id}/mark-paid/ como RECEPCION | HTTP 200 con payment_status=PAID y fecha de pago registrada"""
        reserva = self._crear_reserva(dias=6, hora=16, duracion_min=60)
        self.autenticar(self.recepcion)
        resp = self.client.post(
            f"/api/v1/reservations/reservations/{reserva.id}/mark-paid/"
        )
        datos = resp.json()
        registrar("U31", (
            f"HTTP {resp.status_code}; payment_status={datos.get('payment_status')}; "
            f"fecha_pago_registrada={datos.get('payment_received_at') is not None}"
        ))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(datos["payment_status"], Reservation.PAYMENT_STATUS_PAID)
        self.assertIsNotNone(datos["payment_received_at"])
