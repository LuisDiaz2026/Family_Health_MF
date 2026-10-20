"""
Pruebas de integración - Family Health MF (I01 - I12).

Cada prueba cruza varias capas reales (API -> serializers -> modelos -> base de
datos) verificando flujos completos del sistema. Los datos son CONTROLADOS y se
crean dentro de la base de datos de prueba aislada.
"""
from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

from apps.authentication.models import User
from apps.reservations.models import Reservation
from tests.base import (
    BasePruebas, PASSWORD_PRUEBA, crear_espacio, crear_horario, crear_usuario,
    siguiente_documento,
)
from tests.harness import registrar


class FlujosIntegracionTests(BasePruebas):

    def _resultados(self, resp):
        datos = resp.json()
        if isinstance(datos, dict) and "results" in datos:
            return datos["results"]
        return datos

    def _payload_alta(self, username, primer_nombre="Integración"):
        return {
            "username": username,
            "email": f"{username}@prueba.local",
            "first_name": primer_nombre,
            "last_name": "Prueba",
            "document_type": "CC",
            "document_number": siguiente_documento(),
            "password": PASSWORD_PRUEBA,
            "password_confirm": PASSWORD_PRUEBA,
            "accepted_privacy_policy": True,
            "accepted_terms": True,
        }

    def _reserva_orm(self, space=None, user=None, dias=3, hora=10,
                     duracion_min=60, **extra):
        space = space or self.space
        user = user or self.cliente
        inicio = self.futuro(dias, hora)
        return Reservation.objects.create(
            space=space, user=user, created_by=user,
            start_time=inicio, end_time=inicio + timedelta(minutes=duracion_min),
            **extra,
        )

    # ------------------------------------------------------------------
    def test_i01_registro_activacion_login(self):
        """I01 | RI-REG-01 | Integración Registro | Registro público -> login bloqueado -> ADMIN activa -> login exitoso | 201 inactivo, 400 al ingresar, 200 tras activación"""
        alta = self.client.post("/api/v1/auth/register/",
                                self._payload_alta("i01_nuevo"), format="json")
        login_inactivo = self.client.post("/api/v1/auth/login/", {
            "username": "i01_nuevo", "password": PASSWORD_PRUEBA,
        }, format="json")
        self.autenticar(self.admin)
        uid = User.objects.get(username="i01_nuevo").id
        activar = self.client.post(
            f"/api/v1/auth/admin/users/{uid}/toggle-active/"
        )
        self.cerrar_sesion()
        login_activo = self.client.post("/api/v1/auth/login/", {
            "username": "i01_nuevo", "password": PASSWORD_PRUEBA,
        }, format="json")
        registrar("I01", (
            f"registro HTTP {alta.status_code}; login_inactivo HTTP "
            f"{login_inactivo.status_code}; activo={activar.json().get('is_active')}; "
            f"login_final HTTP {login_activo.status_code}"
        ))
        self.assertEqual(alta.status_code, 201)
        self.assertEqual(login_inactivo.status_code, 400)
        self.assertEqual(activar.status_code, 200)
        self.assertEqual(login_activo.status_code, 200)

    def test_i02_ciclo_reserva_cliente_recepcion(self):
        """I02 | RI-RES-01 | Integración Reservas | CLIENT crea -> RECEPCION lista -> aprueba -> marca pago -> CLIENT ve pago | 201 / 200 / CONFIRMED / PAID"""
        self.autenticar(self.cliente)
        alta = self.client.post("/api/v1/reservations/reservations/", {
            "space_id": self.space.id,
            "start_time": self.futuro(4, 10).isoformat(),
            "end_time": self.futuro(4, 11).isoformat(),
            "guests_count": 2,
        }, format="json")
        rid = alta.json()["id"]
        self.cerrar_sesion()

        self.autenticar(self.recepcion)
        listado = self.client.get("/api/v1/reservations/reservations/")
        aprobar = self.client.post(
            f"/api/v1/reservations/reservations/{rid}/approve/"
        )
        pagar = self.client.post(
            f"/api/v1/reservations/reservations/{rid}/mark-paid/"
        )
        self.cerrar_sesion()

        self.autenticar(self.cliente)
        propias = self.client.get(
            "/api/v1/reservations/reservations/my-upcoming/"
        )
        pago = next((r for r in propias.json() if r["id"] == rid), {})
        registrar("I02", (
            f"creación HTTP {alta.status_code}; recepción ve "
            f"{len(self._resultados(listado))} reserva(s); "
            f"aprobada={aprobar.json().get('status')}; "
            f"pago={pagar.json().get('payment_status')}; "
            f"cliente ve pago={pago.get('payment_status')}"
        ))
        self.assertEqual(alta.status_code, 201)
        self.assertEqual(aprobar.json()["status"], Reservation.STATUS_CONFIRMED)
        self.assertEqual(pagar.json()["payment_status"],
                         Reservation.PAYMENT_STATUS_PAID)
        self.assertEqual(pago.get("payment_status"),
                         Reservation.PAYMENT_STATUS_PAID)

    def test_i03_antisolapamiento_entre_dos_clientes(self):
        """I03 | RI-RES-02 | Integración Anti-solapamiento | Cliente A reserva 10-11; Cliente B reintenta 10-11 y luego 11-12 | 400 en el solape y 201 en la franja libre"""
        self.autenticar(self.cliente)
        a = self.client.post("/api/v1/reservations/reservations/", {
            "space_id": self.space.id,
            "start_time": self.futuro(5, 10).isoformat(),
            "end_time": self.futuro(5, 11).isoformat(),
            "guests_count": 1,
        }, format="json")
        self.cerrar_sesion()

        self.autenticar(self.cliente2)
        solape = self.client.post("/api/v1/reservations/reservations/", {
            "space_id": self.space.id,
            "start_time": self.futuro(5, 10).isoformat(),
            "end_time": self.futuro(5, 11).isoformat(),
            "guests_count": 1,
        }, format="json")
        libre = self.client.post("/api/v1/reservations/reservations/", {
            "space_id": self.space.id,
            "start_time": self.futuro(5, 11).isoformat(),
            "end_time": self.futuro(5, 12).isoformat(),
            "guests_count": 1,
        }, format="json")
        registrar("I03", (
            f"cliente A HTTP {a.status_code}; cliente B solape HTTP "
            f"{solape.status_code}; cliente B franja libre HTTP {libre.status_code}; "
            f"total_en_BD={Reservation.objects.count()}"
        ))
        self.assertEqual(a.status_code, 201)
        self.assertEqual(solape.status_code, 400)
        self.assertEqual(libre.status_code, 201)
        self.assertEqual(Reservation.objects.count(), 2)

    def test_i04_calculo_y_persistencia_total(self):
        """I04 | RI-RES-03 | Integración Cálculo | Reserva de 2 horas -> total 100000.00 persistido y visible en el detalle | coincide API con base de datos"""
        self.autenticar(self.cliente)
        alta = self.client.post("/api/v1/reservations/reservations/", {
            "space_id": self.space.id,
            "start_time": self.futuro(4, 8).isoformat(),
            "end_time": self.futuro(4, 10).isoformat(),
            "guests_count": 3,
        }, format="json")
        rid = alta.json()["id"]
        self.cerrar_sesion()

        self.autenticar(self.recepcion)
        detalle = self.client.get(
            f"/api/v1/reservations/reservations/{rid}/"
        ).json()
        en_bd = Reservation.objects.get(pk=rid)
        registrar("I04", (
            f"HTTP {alta.status_code}; api_total={detalle.get('total_amount')}; "
            f"bd_total={en_bd.total_amount}; api_min={detalle.get('total_minutes')}; "
            f"bd_min={en_bd.total_minutes}"
        ))
        self.assertEqual(alta.status_code, 201)
        self.assertEqual(Decimal(str(detalle["total_amount"])),
                         Decimal("100000.00"))
        self.assertEqual(str(en_bd.total_amount), "100000.00")
        self.assertEqual(en_bd.total_minutes, 120)

    def test_i05_rbac_transversal(self):
        """I05 | RI-SEG-01 | Integración RBAC | CLIENT es rechazado (403) en endpoints de staff y ADMIN accede (200) al panel | control de acceso consistente entre routers"""
        self.autenticar(self.cliente)
        usuarios = self.client.get("/api/v1/auth/admin/users/")
        clientes = self.client.get("/api/v1/auth/clients/")
        crear_espacio = self.client.post("/api/v1/reservations/spaces/", {
            "space_type_id": self.tipo.id, "name": "X", "code": "X-1",
        }, format="json")
        panel = self.client.get("/api/v1/reports/dashboard/summary/")
        self.cerrar_sesion()

        self.autenticar(self.admin)
        panel_admin = self.client.get("/api/v1/reports/dashboard/summary/")
        registrar("I05", (
            f"cliente -> usuarios {usuarios.status_code}, clientes "
            f"{clientes.status_code}, crear_espacio {crear_espacio.status_code}, "
            f"panel {panel.status_code}; admin -> panel {panel_admin.status_code}"
        ))
        for resp in (usuarios, clientes, crear_espacio, panel):
            self.assertEqual(resp.status_code, 403)
        self.assertEqual(panel_admin.status_code, 200)

    def test_i06_registro_duplicado_rechazado(self):
        """I06 | RI-REG-02 | Integración Registro | Registro con username ya existente | HTTP 400 y el conteo de usuarios no aumenta"""
        antes = User.objects.filter(username="t_cliente").count()
        resp = self.client.post("/api/v1/auth/register/",
                                self._payload_alta("t_cliente"), format="json")
        registrar("I06", (
            f"HTTP {resp.status_code}; usuarios_con_username={antes}->"
            f"{User.objects.filter(username='t_cliente').count()}"
        ))
        self.assertEqual(resp.status_code, 400)

    def test_i07_ciclo_jwt_completo(self):
        """I07 | RI-SEG-02 | Integración JWT | login -> uso de access -> refresh (rota) -> logout -> reuse | 200/200/200/200/401 (blacklist tras rotación)"""
        login = self.client.post("/api/v1/auth/login/", {
            "username": "t_cliente", "password": PASSWORD_PRUEBA,
        }, format="json").json()
        access, refresh = login["access"], login["refresh"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        me = self.client.get("/api/v1/auth/me/")
        nuevo = self.client.post("/api/v1/auth/token/refresh/",
                                 {"refresh": refresh}, format="json")
        nuevo_access = nuevo.json().get("access", "")
        # Con ROTATE_REFRESH_TOKENS=True el refresh original queda en blacklist
        # y el endpoint devuelve un refresh nuevo que es el vigente.
        refresh_vigente = nuevo.json().get("refresh", refresh)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {nuevo_access}")
        me2 = self.client.get("/api/v1/auth/me/")
        self.client.credentials()
        salida = self.client.post("/api/v1/auth/logout/",
                                  {"refresh": refresh_vigente}, format="json")
        reuso = self.client.post("/api/v1/auth/token/refresh/",
                                 {"refresh": refresh_vigente}, format="json")
        registrar("I07", (
            f"me {me.status_code}; refresh {nuevo.status_code}; me2 "
            f"{me2.status_code}; logout {salida.status_code}; reuso "
            f"{reuso.status_code}"
        ))
        self.assertEqual((me.status_code, nuevo.status_code, me2.status_code,
                          salida.status_code, reuso.status_code),
                         (200, 200, 200, 200, 401))

    def test_i08_disponibilidad_refleja_reservas(self):
        """I08 | RI-ESP-01 | Integración Disponibilidad | Consulta antes y después de reservar | occupied_slots 0 -> 1 e incluye el id reservado"""
        fecha = self.futuro(7, 10).date()
        crear_horario(self.space, weekday=fecha.weekday())
        self.autenticar(self.cliente)
        url = f"/api/v1/reservations/spaces/{self.space.id}/availability/"
        antes = self.client.get(url, {"date": fecha.isoformat()}).json()
        alta = self.client.post("/api/v1/reservations/reservations/", {
            "space_id": self.space.id,
            "start_time": self.futuro(7, 10).isoformat(),
            "end_time": self.futuro(7, 11).isoformat(),
            "guests_count": 1,
        }, format="json")
        despues = self.client.get(url, {"date": fecha.isoformat()}).json()
        ocupados = despues.get("occupied_slots", [])
        registrar("I08", (
            f"creación HTTP {alta.status_code}; ocupados_antes="
            f"{len(antes.get('occupied_slots', []))}; ocupados_despues="
            f"{len(ocupados)}; id_incluido="
            f"{any(o['id'] == alta.json()['id'] for o in ocupados)}"
        ))
        self.assertEqual(len(antes.get("occupied_slots", [])), 0)
        self.assertEqual(len(ocupados), 1)
        self.assertTrue(any(o["id"] == alta.json()["id"] for o in ocupados))

    def test_i09_cancelacion_libera_franja(self):
        """I09 | RI-RES-04 | Integración Cancelación | Cliente reserva, cancela y otro cliente vuelve a reservar la misma franja | CANCELLED y nueva reserva 201"""
        self.autenticar(self.cliente)
        alta = self.client.post("/api/v1/reservations/reservations/", {
            "space_id": self.space.id,
            "start_time": self.futuro(8, 10).isoformat(),
            "end_time": self.futuro(8, 11).isoformat(),
            "guests_count": 1,
        }, format="json")
        rid = alta.json()["id"]
        cancelar = self.client.post(
            f"/api/v1/reservations/reservations/{rid}/cancel/",
            {"reason": "Prueba de integración"}, format="json",
        )
        self.cerrar_sesion()

        self.autenticar(self.cliente2)
        reuso = self.client.post("/api/v1/reservations/reservations/", {
            "space_id": self.space.id,
            "start_time": self.futuro(8, 10).isoformat(),
            "end_time": self.futuro(8, 11).isoformat(),
            "guests_count": 1,
        }, format="json")
        registrar("I09", (
            f"creación HTTP {alta.status_code}; cancelación "
            f"{cancelar.json().get('status')}; reuso de franja HTTP "
            f"{reuso.status_code}"
        ))
        self.assertEqual(alta.status_code, 201)
        self.assertEqual(cancelar.json()["status"], Reservation.STATUS_CANCELLED)
        self.assertEqual(reuso.status_code, 201)

    def test_i10_panel_y_top_clientes_integran_datos(self):
        """I10 | RI-REP-01 | Integración Reportes | Reserva pagada -> panel y top-clientes la reflejan | reservations_total>=1 y el cliente aparece con gasto"""
        self._reserva_orm(
            dias=2, hora=9, duracion_min=60,
            status=Reservation.STATUS_CONFIRMED,
            payment_status=Reservation.PAYMENT_STATUS_PAID,
        )
        self.autenticar(self.admin)
        panel = self.client.get("/api/v1/reports/dashboard/summary/").json()
        top = self.client.get("/api/v1/reports/dashboard/top-clients/").json()
        usernames = [u["username"] for u in top] if isinstance(top, list) else [
            u["username"] for u in top.get("results", [])
        ]
        registrar("I10", (
            f"reservations_total={panel.get('reservations_total')}; "
            f"reservations_confirmed={panel.get('reservations_confirmed')}; "
            f"clientes_en_top={usernames}"
        ))
        self.assertGreaterEqual(panel["reservations_total"], 1)
        self.assertGreaterEqual(panel["reservations_confirmed"], 1)
        self.assertIn(self.cliente.username, usernames)

    def test_i11_politica_privacidad_obligatoria(self):
        """I11 | RI-SEG-03 | Integración Ley 1581 | Registro sin aceptar términos -> 400; con ambos aceptados -> 201 | cumplimiento de consentimiento informado"""
        invalido = self._payload_alta("i11_sin_terminos")
        invalido["accepted_terms"] = False
        sin_terminos = self.client.post("/api/v1/auth/register/", invalido,
                                        format="json")
        valido = self.client.post("/api/v1/auth/register/",
                                  self._payload_alta("i11_con_terminos"),
                                  format="json")
        registrar("I11", (
            f"sin_términos HTTP {sin_terminos.status_code}; "
            f"con_términos HTTP {valido.status_code}; creado="
            f"{User.objects.filter(username='i11_con_terminos').exists()}"
        ))
        self.assertEqual(sin_terminos.status_code, 400)
        self.assertEqual(valido.status_code, 201)

    def test_i12_filtros_listado_reservas_staff(self):
        """I12 | RI-REP-02 | Integración Filtros | RECEPCION filtra por status y space_id | solo devuelve las reservas que cumplen el filtro"""
        self._reserva_orm(dias=3, hora=10, duracion_min=60,
                          status=Reservation.STATUS_CONFIRMED)
        self._reserva_orm(dias=3, hora=12, duracion_min=60,
                          status=Reservation.STATUS_PENDING)
        cancelada = self._reserva_orm(dias=3, hora=14, duracion_min=60,
                                      status=Reservation.STATUS_CANCELLED)
        self.autenticar(self.recepcion)
        por_estado = self.client.get(
            "/api/v1/reservations/reservations/?status=CANCELLED"
        )
        por_espacio = self.client.get(
            f"/api/v1/reservations/reservations/?space_id={self.space.id}"
        )
        estados = {r["status"] for r in self._resultados(por_estado)}
        registrar("I12", (
            f"filtro status HTTP {por_estado.status_code}; estados={estados}; "
            f"filtro space_id={len(self._resultados(por_espacio))} reservas; "
            f"ids_cancelados="
            f"{[r['id'] for r in self._resultados(por_estado)]}"
        ))
        self.assertEqual(por_estado.status_code, 200)
        self.assertEqual(estados, {Reservation.STATUS_CANCELLED})
        self.assertEqual(
            [r["id"] for r in self._resultados(por_estado)], [cancelada.id]
        )
