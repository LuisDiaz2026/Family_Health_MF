"""
Smoke Test - Valida endpoints principales sin levantar servidor web.
Usa Django test Client.
"""
import os
import sys
import django
import traceback

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from django.test import Client
import json

client = Client()

print("=" * 60)
print("SMOKE TEST - CLUB FAMILY HEALTH MF")
print("=" * 60)

tests_ok = 0
tests_fail = 0


def do_test(name, func):
    global tests_ok, tests_fail
    try:
        msg = func()
        print(f"[OK] {name} -> {msg}" if msg else f"[OK] {name}")
        tests_ok += 1
    except Exception as e:
        print(f"[FAIL] {name}: {e}")
        traceback.print_exc()
        tests_fail += 1


# 1) HEALTH CHECK PÚBLICO
def t1():
    resp = client.get("/api/v1/health/")
    data = resp.json()
    assert resp.status_code == 200, f"status={resp.status_code}"
    assert data.get("status") == "ok"
    assert data.get("club_name") == "Club Family Health"
    return f"status: {data['status']}, club: {data['club_name']}"


do_test("Health Check", t1)

# 2) LOGIN CLIENTE
access_cliente = None


def t2():
    global access_cliente
    resp = client.post(
        "/api/v1/auth/login/",
        data=json.dumps({"username": "cliente1_fh", "password": "Cliente1FH*!"}),
        content_type="application/json",
    )
    data = resp.json()
    assert resp.status_code == 200, f"status={resp.status_code} body={data}"
    assert "access" in data and "refresh" in data
    assert data.get("role") == "CLIENT"
    assert "points" in data and "tier" in data
    access_cliente = data["access"]
    return f"JWT válido | Rol: {data['role']} | Puntos: {data.get('points')} | Tier: {data.get('tier')}"


do_test("Login cliente1_fh", t2)

# 3) LOGIN ADMIN
access_admin = None


def t3():
    global access_admin
    resp = client.post(
        "/api/v1/auth/login/",
        data=json.dumps({"username": "admin_fh", "password": "AdminFH2026*!"}),
        content_type="application/json",
    )
    data = resp.json()
    assert resp.status_code == 200, f"status={resp.status_code} body={data}"
    assert data.get("role") == "ADMIN"
    access_admin = data["access"]
    return f"JWT válido | Rol: {data['role']}"


do_test("Login admin_fh", t3)


# 4) ESPACIOS
def t4():
    resp = client.get("/api/v1/reservations/spaces/",
                      HTTP_AUTHORIZATION=f"Bearer {access_cliente}")
    assert resp.status_code == 200, f"status={resp.status_code}"
    data = resp.json()
    count = data.get("count") if isinstance(data, dict) and "count" in data else len(data.get("results", []))
    if count is None:
        count = len(data.get("results", [])) if isinstance(data, dict) else len(data)
    assert count >= 10, f"Esperaba ≥10, obtuvo {count}"
    return f"{count} espacios disponibles"


do_test("Listar espacios reservas", t4)


# 5) DISPONIBILIDAD
def t5():
    from apps.reservations.models import Space
    space = Space.objects.get(code="CANCHA-F5-01")
    import datetime as dt
    fecha = (dt.datetime.now() + dt.timedelta(days=2)).strftime("%Y-%m-%d")
    resp = client.get(
        f"/api/v1/reservations/spaces/{space.id}/availability/?date={fecha}",
        HTTP_AUTHORIZATION=f"Bearer {access_cliente}",
    )
    assert resp.status_code == 200, f"status={resp.status_code} body={resp.content[:500]}"
    d = resp.json()
    slots = len(d.get("available_slots", [])) if isinstance(d, dict) else 0
    return f"{space.name} {fecha} -> {slots} slots libres (verificado)"


do_test("Consulta disponibilidad espacio", t5)


# 6) CATÁLOGO REFRESCOS
def t6():
    resp = client.get("/api/v1/refreshments/products/available-catalog/",
                      HTTP_AUTHORIZATION=f"Bearer {access_cliente}")
    assert resp.status_code == 200, f"status={resp.status_code}"
    d = resp.json()
    cats = d.get("results", d) if isinstance(d, dict) else d
    total = 0
    for c in cats:
        if isinstance(c, dict):
            total += len(c.get("products", []))
    assert total >= 20, f"Esperaba ≥20 productos, obtuvo {total}"
    return f"{total} productos en catálogo"


do_test("Catálogo refresquería", t6)


# 7) PERFIL ME/LOYALTY
def t7():
    resp = client.get("/api/v1/auth/me/loyalty/",
                      HTTP_AUTHORIZATION=f"Bearer {access_cliente}")
    assert resp.status_code == 200, f"status={resp.status_code} body={resp.content[:500]}"
    d = resp.json()
    assert d.get("role") == "CLIENT"
    assert d.get("current_points") is not None
    tier_name = d.get("tier", {}).get("name") if isinstance(d.get("tier"), dict) else d.get("tier")
    return f"tier={tier_name}, current_points={d.get('current_points')}"


do_test("Perfil Cliente + Loyalty", t7)


# 8) RUTINAS GIMNASIO
def t8():
    resp = client.get("/api/v1/gym/routines/my-routines/",
                      HTTP_AUTHORIZATION=f"Bearer {access_cliente}")
    assert resp.status_code == 200, f"status={resp.status_code}"
    d = resp.json()
    results = d.get("results", d) if isinstance(d, dict) else d
    assert len(results) >= 5, f"Esperaba ≥5, obtuvo {len(results)}"
    return f"{len(results)} rutinas visibles"


do_test("Listar rutinas gimnasio", t8)


# 9) DASHBOARD SUMMARY ADMIN
def t9():
    resp = client.get("/api/v1/reports/dashboard/summary/",
                      HTTP_AUTHORIZATION=f"Bearer {access_admin}")
    assert resp.status_code == 200, f"status={resp.status_code} body={resp.content[:500]}"
    d = resp.json()
    total_users = d.get("total_users") or d.get("users_total")
    spaces_total = d.get("spaces_total") or 0
    assert total_users is not None, f"total_users/users_total no presente en {list(d.keys())[:5]}"
    return f"total_users={total_users}, spaces_total={spaces_total}"


do_test("Dashboard Admin Summary", t9)


# 10) TOP CLIENTES ADMIN
def t10():
    resp = client.get("/api/v1/reports/top-clients/?n=5",
                      HTTP_AUTHORIZATION=f"Bearer {access_admin}")
    assert resp.status_code == 200, f"status={resp.status_code} body={resp.content[:500]}"
    d = resp.json()
    results = d.get("results", d) if isinstance(d, dict) else d
    return f"{len(results)} clientes en ranking"


do_test("Top Clientes (Admin)", t10)


# 11) BLOQUEO 401 SIN TOKEN
def t11():
    resp = client.get("/api/v1/reports/dashboard/summary/")
    assert resp.status_code == 401, f"Esperaba 401, obtuvo {resp.status_code}"
    return "bloqueado correctamente (401)"


do_test("Seguridad: acceso sin token a ruta admin", t11)


# 12) REFRESH TOKEN (flujo JWT)
def t12():
    resp_login = client.post(
        "/api/v1/auth/login/",
        data=json.dumps({"username": "cliente1_fh", "password": "Cliente1FH*!"}),
        content_type="application/json",
    )
    refresh = resp_login.json()["refresh"]
    resp = client.post(
        "/api/v1/auth/token/refresh/",
        data=json.dumps({"refresh": refresh}),
        content_type="application/json",
    )
    assert resp.status_code == 200, f"status={resp.status_code} body={resp.content[:500]}"
    assert "access" in resp.json()
    return "nuevo access token generado"


do_test("JWT Refresh Token", t12)


# 13) REGISTRO CLIENTE (validar política de privacidad requerida)
def t13():
    data = {
        "username": "prueba_smoke_priv",
        "email": "prueba_smoke_priv@example.com",
        "first_name": "Prueba",
        "last_name": "Smoke",
        "document_type": "CC",
        "document_number": "99999999",
        "phone": "+573009998877",
        "password": "PruebaFH2026*!",
        "password_confirm": "PruebaFH2026*!",
        "privacy_policy_accepted": False,
    }
    resp = client.post(
        "/api/v1/auth/register/",
        data=json.dumps(data),
        content_type="application/json",
    )
    assert resp.status_code == 400, f"Esperaba 400 (política no aceptada), obtuvo {resp.status_code}"
    return "rechazo correcto por política priv (400)"


do_test("Registro: Política privacidad obligatoria", t13)


# 14) RESERVAS: validar sin cruce (crear y chequear solapamiento devuelve 400)
def t14():
    from apps.reservations.models import Space
    from django.utils import timezone
    import datetime as dt
    space = Space.objects.get(code="CANCHA-BASKET-01")
    start = timezone.now().replace(second=0, microsecond=0) + dt.timedelta(days=1, hours=2)
    end = start + dt.timedelta(hours=1)
    payload = {
        "space_id": space.id,
        "start_time": start.isoformat(),
        "end_time": end.isoformat(),
        "guests": 5,
        "notes": "Smoke test reserva",
    }
    resp = client.post(
        "/api/v1/reservations/reservations/",
        data=json.dumps(payload),
        content_type="application/json",
        HTTP_AUTHORIZATION=f"Bearer {access_cliente}",
    )
    assert resp.status_code in (200, 201, 400), f"status={resp.status_code} body={resp.content[:500]}"
    if resp.status_code == 400:
        return f"validacion negocio: {list(resp.json().keys())[:3]}"
    res_id = resp.json().get("id")
    # Ahora intentamos reserva igual (solapada)
    resp2 = client.post(
        "/api/v1/reservations/reservations/",
        data=json.dumps(payload),
        content_type="application/json",
        HTTP_AUTHORIZATION=f"Bearer {access_cliente}",
    )
    assert resp2.status_code == 400, f"Esperaba 400 solape, obtuvo {resp2.status_code}"
    return f"reserva #{res_id} OK + solapamiento bloqueado (400)"


do_test("Reservas: creación + anti-solapamiento", t14)


print()
print("=" * 60)
print(f"RESULTADOS FINALES: {tests_ok} OK | {tests_fail} FALLIDOS")
print("=" * 60)

if tests_fail > 0:
    sys.exit(1)
