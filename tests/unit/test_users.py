"""
Pruebas unitarias - Gestión de usuarios y registro público (U07 - U11).
"""
from apps.authentication.models import User
from tests.base import BasePruebas, crear_usuario, siguiente_documento
from tests.harness import registrar


class UsuariosTests(BasePruebas):

    def test_u07_registro_sin_politica_privacidad(self):
        """U07 | RQF-USR-01 | Usuarios | POST /api/v1/auth/register/ sin aceptar política de privacidad | HTTP 400 indicando aceptación obligatoria (Ley 1581)"""
        doc = siguiente_documento()
        resp = self.client.post("/api/v1/auth/register/", {
            "username": "u07_prueba",
            "email": "u07_prueba@prueba.local",
            "first_name": "U07",
            "last_name": "Prueba",
            "document_type": "CC",
            "document_number": doc,
            "password": "PruebaFH2026*!",
            "password_confirm": "PruebaFH2026*!",
            "accepted_privacy_policy": False,
            "accepted_terms": True,
        }, format="json")
        cuerpo = resp.json()
        registrar("U07", (
            f"HTTP {resp.status_code}; claves={sorted(cuerpo.keys())}; "
            f"creado={User.objects.filter(username='u07_prueba').exists()}"
        ))
        self.assertEqual(resp.status_code, 400)
        self.assertFalse(User.objects.filter(username="u07_prueba").exists())

    def test_u08_registro_valido_crea_cliente_inactivo(self):
        """U08 | RQF-USR-02 | Usuarios | POST /api/v1/auth/register/ con datos válidos y política aceptada | HTTP 201 y usuario CLIENT creado con is_active=False (requiere aprobación)"""
        doc = siguiente_documento()
        resp = self.client.post("/api/v1/auth/register/", {
            "username": "u08_prueba",
            "email": "u08_prueba@prueba.local",
            "first_name": "U08",
            "last_name": "Prueba",
            "document_type": "CC",
            "document_number": doc,
            "password": "PruebaFH2026*!",
            "password_confirm": "PruebaFH2026*!",
            "accepted_privacy_policy": True,
            "accepted_terms": True,
        }, format="json")
        usuario = User.objects.filter(username="u08_prueba").first()
        registrar("U08", (
            f"HTTP {resp.status_code}; creado={usuario is not None}; "
            f"role={getattr(usuario, 'role', None)}; "
            f"is_active={getattr(usuario, 'is_active', None)}"
        ))
        self.assertEqual(resp.status_code, 201)
        self.assertIsNotNone(usuario)
        self.assertEqual(usuario.role, User.ROLE_CLIENT)
        self.assertFalse(usuario.is_active)

    def test_u09_admin_crea_usuario(self):
        """U09 | RQF-USR-03 | Roles/permisos | POST /api/v1/auth/admin/users/ autenticado como ADMIN | HTTP 201 y usuario persistido con el rol indicado"""
        self.autenticar(self.admin)
        doc = siguiente_documento()
        resp = self.client.post("/api/v1/auth/admin/users/", {
            "username": "u09_nuevo",
            "email": "u09_nuevo@prueba.local",
            "first_name": "U09",
            "last_name": "Nuevo",
            "document_type": "CC",
            "document_number": doc,
            "role": User.ROLE_RECEPCION,
            "password": "PruebaFH2026*!",
            "is_active": True,
        }, format="json")
        usuario = User.objects.filter(username="u09_nuevo").first()
        registrar("U09", (
            f"HTTP {resp.status_code}; creado={usuario is not None}; "
            f"role={getattr(usuario, 'role', None)}"
        ))
        self.assertEqual(resp.status_code, 201)
        self.assertIsNotNone(usuario)
        self.assertEqual(usuario.role, User.ROLE_RECEPCION)

    def test_u10_cliente_no_accede_gestion_usuarios(self):
        """U10 | RQF-USR-04 | Roles/permisos | GET /api/v1/auth/admin/users/ autenticado como CLIENT | HTTP 403 y sin listado de usuarios"""
        self.autenticar(self.cliente)
        resp = self.client.get("/api/v1/auth/admin/users/")
        cuerpo = resp.json()
        registrar("U10", (
            f"HTTP {resp.status_code}; claves={sorted(cuerpo.keys())}"
        ))
        self.assertEqual(resp.status_code, 403)
        self.assertNotIn("results", cuerpo)

    def test_u11_recepcion_lista_solo_clientes(self):
        """U11 | RQF-USR-05 | Roles/permisos | GET /api/v1/auth/clients/ autenticado como RECEPCION | HTTP 200 y todos los resultados con role=CLIENT"""
        crear_usuario("u11_cliente_extra", User.ROLE_CLIENT)
        self.autenticar(self.recepcion)
        resp = self.client.get("/api/v1/auth/clients/")
        datos = resp.json()
        resultados = datos.get("results", datos) if isinstance(datos, dict) else datos
        roles = sorted({r.get("role") for r in resultados})
        registrar("U11", (
            f"HTTP {resp.status_code}; n={len(resultados)}; roles={roles}"
        ))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(all(r.get("role") == User.ROLE_CLIENT for r in resultados))
