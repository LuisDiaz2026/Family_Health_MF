"""
Pruebas unitarias - Autenticación, JWT y ciclo de sesión (U01 - U06).
"""
from tests.base import BasePruebas, PASSWORD_PRUEBA, crear_usuario
from tests.harness import registrar


class AutenticacionTests(BasePruebas):

    def test_u01_login_admin_correcto(self):
        """U01 | RQF-AUT-01 | Autenticación | POST /api/v1/auth/login/ {t_admin, ****} | HTTP 200 con access, refresh y role=ADMIN"""
        resp = self.client.post(
            "/api/v1/auth/login/",
            {"username": "t_admin", "password": PASSWORD_PRUEBA},
            format="json",
        )
        cuerpo = resp.json()
        registrar("U01", (
            f"HTTP {resp.status_code}; access={'access' in cuerpo}; "
            f"refresh={'refresh' in cuerpo}; role={cuerpo.get('role')}"
        ))
        self.assertEqual(resp.status_code, 200)
        self.assertIn("access", cuerpo)
        self.assertIn("refresh", cuerpo)
        self.assertEqual(cuerpo.get("role"), "ADMIN")

    def test_u02_login_credenciales_incorrectas(self):
        """U02 | RQF-AUT-02 | Autenticación | POST /api/v1/auth/login/ con contraseña errónea | HTTP 401 y sin tokens"""
        resp = self.client.post(
            "/api/v1/auth/login/",
            {"username": "t_admin", "password": "ContrasenaIncorrecta9*"},
            format="json",
        )
        cuerpo = resp.json()
        registrar("U02", (
            f"HTTP {resp.status_code}; access={'access' in cuerpo}; "
            f"claves={sorted(cuerpo.keys())}"
        ))
        self.assertEqual(resp.status_code, 401)
        self.assertNotIn("access", cuerpo)

    def test_u03_login_usuario_inactivo(self):
        """U03 | RQF-AUT-03 | Usuarios inactivos | POST /api/v1/auth/login/ con usuario is_active=False | HTTP 400 con mensaje de cuenta inactiva"""
        crear_usuario("t_inactivo", "CLIENT", activo=False)
        resp = self.client.post(
            "/api/v1/auth/login/",
            {"username": "t_inactivo", "password": PASSWORD_PRUEBA},
            format="json",
        )
        cuerpo = resp.json()
        texto = str(cuerpo).upper()
        registrar("U03", (
            f"HTTP {resp.status_code}; mensaje_inactivo="
            f"{'INACTIVA' in texto}; access={'access' in cuerpo}"
        ))
        self.assertEqual(resp.status_code, 400)
        self.assertIn("INACTIVA", texto)
        self.assertNotIn("access", cuerpo)

    def test_u04_refresh_token_valido(self):
        """U04 | RQF-AUT-04 | JWT | POST /api/v1/auth/token/refresh/ con refresh válido | HTTP 200 y nuevo access"""
        login = self.client.post(
            "/api/v1/auth/login/",
            {"username": "t_cliente", "password": PASSWORD_PRUEBA},
            format="json",
        )
        refresh = login.json()["refresh"]
        resp = self.client.post(
            "/api/v1/auth/token/refresh/", {"refresh": refresh}, format="json",
        )
        cuerpo = resp.json()
        registrar("U04", (
            f"HTTP {resp.status_code}; nuevo_access={'access' in cuerpo}; "
            f"longitud_access={len(cuerpo.get('access', ''))}"
        ))
        self.assertEqual(resp.status_code, 200)
        self.assertIn("access", cuerpo)
        self.assertTrue(len(cuerpo["access"]) > 20)

    def test_u05_logout_invalida_refresh(self):
        """U05 | RQF-AUT-05 | JWT | POST /api/v1/auth/logout/ y reintento de refresh | HTTP 200 al salir y HTTP 401 al reusar el refresh (blacklist)"""
        login = self.client.post(
            "/api/v1/auth/login/",
            {"username": "t_cliente", "password": PASSWORD_PRUEBA},
            format="json",
        )
        refresh = login.json()["refresh"]
        salida = self.client.post(
            "/api/v1/auth/logout/", {"refresh": refresh}, format="json",
        )
        reuso = self.client.post(
            "/api/v1/auth/token/refresh/", {"refresh": refresh}, format="json",
        )
        registrar("U05", (
            f"logout HTTP {salida.status_code}; "
            f"reuso_refresh HTTP {reuso.status_code} (blacklist activa)"
        ))
        self.assertEqual(salida.status_code, 200)
        self.assertEqual(reuso.status_code, 401)

    def test_u06_me_sin_token(self):
        """U06 | RQF-AUT-06 | JWT | GET /api/v1/auth/me/ sin cabecera Authorization | HTTP 401 sin datos de usuario"""
        resp = self.client.get("/api/v1/auth/me/")
        cuerpo = resp.json()
        registrar("U06", (
            f"HTTP {resp.status_code}; claves={sorted(cuerpo.keys())}; "
            f"expone_datos={'username' in cuerpo}"
        ))
        self.assertEqual(resp.status_code, 401)
        self.assertNotIn("username", cuerpo)
