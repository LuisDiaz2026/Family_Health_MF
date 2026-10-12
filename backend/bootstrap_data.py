"""
Script Bootstrap - Crea superusuario + datos demo
Ejecución:
  cd backend
  python bootstrap_data.py

NOTA DE SEGURIDAD: Credenciales de demostración parametrizables por variables
DEMO_PASS_ADMIN, DEMO_PASS_EMP, DEMO_PASS_C1, DEMO_PASS_C2, DEMO_PASS_C3.
Si no están definidas se generan contraseñas aleatorias de un solo uso.
Este script es EXCLUSIVO para entornos de prueba AISLADOS.
"""
import os
import sys
import secrets
import string
import django
from datetime import timedelta, time
from decimal import Decimal
from django.utils.text import slugify


def _demo_pass(env_key: str, label: str):
    val = os.getenv(env_key)
    if val:
        return val, False
    alphabet = string.ascii_letters + string.digits + "!*#$@%"
    rnd = "".join(secrets.choice(alphabet) for _ in range(16))
    return rnd, True

# UTF-8 seguro para Windows
if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.utils import timezone
from django.db import transaction

from apps.authentication.models import User
from apps.reservations.models import (
    SpaceType, Space, OperatingHours, Holiday
)
from apps.refreshments.models import ProductCategory, Product
from apps.rewards.models import LoyaltyTier, RewardRule, RewardCatalogItem
from apps.gym.models import MuscleGroup, Equipment, Exercise, Routine, RoutineExercise


def run():
    # Control de ejecución: si RAILWAY_SEED_BOOTSTRAP=0 o false, NO se ejecuta
    # el bootstrap (producción). Evita recrear datos demo y borrar inventario.
    seed_flag = os.getenv("RAILWAY_SEED_BOOTSTRAP", "1").strip().lower()
    if seed_flag in ("0", "false", "no", "off"):
        print("[BOOTSTRAP] RAILWAY_SEED_BOOTSTRAP desactivado — se omite la siembra de datos.")
        return

    pw_admin, gen_admin = _demo_pass("DEMO_PASS_ADMIN", "admin")
    pw_emp, gen_emp = _demo_pass("DEMO_PASS_EMP", "recepcion")
    pw_caf, gen_caf = _demo_pass("DEMO_PASS_CAF", "cafeteria")
    pw_c1, gen_c1 = _demo_pass("DEMO_PASS_C1", "cliente1")
    pw_c2, gen_c2 = _demo_pass("DEMO_PASS_C2", "cliente2")
    pw_c3, gen_c3 = _demo_pass("DEMO_PASS_C3", "cliente3")
    creds = {
        "admin_fh": (pw_admin, gen_admin),
        "recepcion_fh": (pw_emp, gen_emp),
        "cafeteria_fh": (pw_caf, gen_caf),
        "cliente1_fh": (pw_c1, gen_c1),
        "cliente2_fh": (pw_c2, gen_c2),
        "cliente3_fh": (pw_c3, gen_c3),
    }
    with transaction.atomic():
        # ============================================================
        # 1) SUPERUSUARIO ADMIN
        # ============================================================
        if not User.objects.filter(username="admin_fh").exists():
            User.objects.create_superuser(
                username="admin_fh",
                email="admin.familyhealth@gmail.com",
                password=pw_admin,
                first_name="Luis Fermín",
                last_name="Díaz Choles",
                document_type="CC",
                document_number="1234567890",
                phone="+573001234567",
                address="Calle 12 # 5-67, Maicao",
                birth_date="1990-05-15",
                role="ADMIN",
                gender="M",
                accepted_privacy_policy=True,
                privacy_policy_accepted_at=timezone.now(),
                is_verified=True,
                membership_type="Premium",
                membership_expires_at=(timezone.now() + timedelta(days=365)),
            )
            suffix = " [auto-generada]" if creds["admin_fh"][1] else ""
            print(f"✅ Superusuario Creado: admin_fh / *****{suffix}")
        else:
            print("ℹ️  Superusuario admin_fh ya existe.")

        # ============================================================
        # 2) EMPLEADO RECEPCIÓN
        # ============================================================
        if not User.objects.filter(username="recepcion_fh").exists():
            User.objects.create_user(
                username="recepcion_fh",
                email="recepcion.familyhealth@gmail.com",
                password=pw_emp,
                first_name="Martha Isabel",
                last_name="Pinto Carrillo",
                document_type="CC",
                document_number="1098765432",
                phone="+573009876543",
                address="Carrera 7 # 20-45, Maicao",
                birth_date="1995-08-20",
                role="RECEPCION",
                gender="F",
                accepted_privacy_policy=True,
                privacy_policy_accepted_at=timezone.now(),
                is_verified=True,
                membership_type="Empleado",
                membership_expires_at=(timezone.now() + timedelta(days=365)),
            )
            suffix = " [auto-generada]" if creds["recepcion_fh"][1] else ""
            print(f"✅ Recepción Creado: recepcion_fh / *****{suffix}")
        else:
            # Migrar rol EMPLOYEE legacy a RECEPCION
            r = User.objects.get(username="recepcion_fh")
            if r.role == "EMPLOYEE":
                r.role = "RECEPCION"
                r.save(update_fields=["role"])
                print("ℹ️  recepcion_fh migrado de EMPLOYEE a RECEPCION.")
            else:
                print("ℹ️  Recepción recepcion_fh ya existe.")

        # ============================================================
        # 2b) EMPLEADO CAFETERÍA
        # ============================================================
        if not User.objects.filter(username="cafeteria_fh").exists():
            User.objects.create_user(
                username="cafeteria_fh",
                email="cafeteria.familyhealth@gmail.com",
                password=pw_caf,
                first_name="Carlos Andrés",
                last_name="García Pacheco",
                document_type="CC",
                document_number="1098765433",
                phone="+573009876544",
                address="Calle 15 # 8-30, Maicao",
                birth_date="1992-03-12",
                role="CAFETERIA",
                gender="M",
                accepted_privacy_policy=True,
                privacy_policy_accepted_at=timezone.now(),
                is_verified=True,
                membership_type="Empleado",
                membership_expires_at=(timezone.now() + timedelta(days=365)),
            )
            suffix = " [auto-generada]" if creds["cafeteria_fh"][1] else ""
            print(f"✅ Cafetería Creado: cafeteria_fh / *****{suffix}")
        else:
            # Migrar rol EMPLOYEE legacy a CAFETERIA si aplica
            c = User.objects.get(username="cafeteria_fh")
            if c.role == "EMPLOYEE":
                c.role = "CAFETERIA"
                c.save(update_fields=["role"])
                print("ℹ️  cafeteria_fh migrado de EMPLOYEE a CAFETERIA.")
            else:
                print("ℹ️  Cafetería cafeteria_fh ya existe.")

        # ============================================================
        # 3) CLIENTES DEMO
        # ============================================================
        clientes = [
            {"u": "cliente1_fh", "e": "luisf_diaz1990@hotmail.com", "p": pw_c1,
             "n": "Juan Carlos", "a": "Gómez Romero", "cc": "52345678", "cel": "+573011112222",
             "f_nac": "1988-03-10", "g": "M"},
            {"u": "cliente2_fh", "e": "valeria_23@gmail.com", "p": pw_c2,
             "n": "Valeria Sofía", "a": "Martínez López", "cc": "52345679", "cel": "+573013334444",
             "f_nac": "1998-11-25", "g": "F"},
            {"u": "cliente3_fh", "e": "carlos.m@outlook.com", "p": pw_c3,
             "n": "Carlos Alberto", "a": "Muñoz Sánchez", "cc": "52345680", "cel": "+573015556666",
             "f_nac": "1992-07-14", "g": "M"},
        ]
        for c in clientes:
            if not User.objects.filter(username=c["u"]).exists():
                User.objects.create_user(
                    username=c["u"], email=c["e"], password=c["p"],
                    first_name=c["n"], last_name=c["a"], document_type="CC",
                    document_number=c["cc"], phone=c["cel"],
                    address="Maicao, La Guajira", birth_date=c["f_nac"],
                    role="CLIENT", gender=c["g"], accepted_privacy_policy=True,
                    privacy_policy_accepted_at=timezone.now(), is_verified=True,
                    membership_type="Básica",
                    membership_expires_at=(timezone.now() + timedelta(days=90)),
                )
                suffix = " [auto-generada]" if creds[c["u"]][1] else ""
                print(f"✅ Cliente Creado: {c['u']} / *****{suffix}")
            else:
                print(f"ℹ️  Cliente {c['u']} ya existe.")

        # ============================================================
        # 4) RESERVATIONS - TIPOS DE ESPACIO
        # ============================================================
        tipos = [
            ("Canchas Deportivas", "🏟️"),
            ("Salones de Eventos", "🏛️"),
            ("Piscinas y Zona Húmeda", "🏊"),
            ("Gimnasio y Fitness", "💪"),
            ("Zonas Infantiles", "🎠"),
        ]
        tipo_objs = {}
        for n, icono in tipos:
            t, _ = SpaceType.objects.get_or_create(
                name=n, defaults={"description": n, "icon": icono, "is_active": True}
            )
            tipo_objs[n] = t
        print(f"✅ {len(tipo_objs)} Tipos de Espacio")

        # ============================================================
        # 5) RESERVATIONS - ESPACIOS + HORARIOS
        # ============================================================
        espacios = [
            {"name": "Cancha de Fútbol 5", "code": "CANCHA-F5-01",
             "tipo": "Canchas Deportivas",
             "capacity": 14, "hrate": 60000,
             "min_min": 60, "max_min": 180, "advance": 15,
             "requires_approval": False, "status": "ACTIVE",
             "desc": "Cancha de pasto sintético iluminada, locker y taquillas incluidas."},
            {"name": "Cancha de Baloncesto", "code": "CANCHA-BASKET-01",
             "tipo": "Canchas Deportivas",
             "capacity": 10, "hrate": 40000,
             "min_min": 60, "max_min": 180, "advance": 15,
             "requires_approval": False, "status": "ACTIVE",
             "desc": "Cancha techada con tablero reglamentario NBA y tablero auxiliar."},
            {"name": "Cancha de Voleibol", "code": "CANCHA-VOLLEY-01",
             "tipo": "Canchas Deportivas",
             "capacity": 12, "hrate": 35000,
             "min_min": 60, "max_min": 120, "advance": 15,
             "requires_approval": False, "status": "ACTIVE",
             "desc": "Cancha techada, arena playa y red profesional."},
            {"name": "Salón Principal", "code": "SALON-MAIN-01",
             "tipo": "Salones de Eventos",
             "capacity": 200, "hrate": 250000,
             "min_min": 120, "max_min": 720, "advance": 60,
             "requires_approval": True, "status": "ACTIVE",
             "desc": "Salón para fiestas, bodas y quince años con pista de baile, sonido, DJ base."},
            {"name": "Salón Social", "code": "SALON-SOCIAL-01",
             "tipo": "Salones de Eventos",
             "capacity": 60, "hrate": 120000,
             "min_min": 60, "max_min": 360, "advance": 30,
             "requires_approval": True, "status": "ACTIVE",
             "desc": "Ideal para reuniones, baby showers y reuniones familiares."},
            {"name": "Piscina Semi-Olímpica", "code": "PISCINA-01",
             "tipo": "Piscinas y Zona Húmeda",
             "capacity": 80, "hrate": 80000,
             "min_min": 60, "max_min": 240, "advance": 10,
             "requires_approval": False, "status": "ACTIVE",
             "desc": "25 metros, carril rápido, jacuzzi y duchas. Horario: Martes a Domingo."},
            {"name": "Piscina Infantil", "code": "PISCINA-INF-01",
             "tipo": "Piscinas y Zona Húmeda",
             "capacity": 30, "hrate": 40000,
             "min_min": 60, "max_min": 180, "advance": 10,
             "requires_approval": False, "status": "ACTIVE",
             "desc": "Climatizada, 30 cm profundidad, vigilante y área juegos."},
            {"name": "Gimnasio (Acceso por Día)", "code": "GYM-DAY-01",
             "tipo": "Gimnasio y Fitness",
             "capacity": 40, "hrate": 15000,
             "min_min": 30, "max_min": 240, "advance": 2,
             "requires_approval": False, "status": "ACTIVE",
             "desc": "Acceso completo al gimnasio con pesas, cardiovasculares y zona funcional."},
            {"name": "Salón Clases Grupales", "code": "GYM-CLASES-01",
             "tipo": "Gimnasio y Fitness",
             "capacity": 20, "hrate": 50000,
             "min_min": 30, "max_min": 90, "advance": 7,
             "requires_approval": False, "status": "ACTIVE",
             "desc": "Para clases personalizadas de CrossFit, HIIT o Body Pump."},
            {"name": "Parque Infantil", "code": "INFANTIL-01",
             "tipo": "Zonas Infantiles",
             "capacity": 50, "hrate": 25000,
             "min_min": 60, "max_min": 240, "advance": 5,
             "requires_approval": False, "status": "ACTIVE",
             "desc": "Columpios, resbaladilla, carrusel, mini tejo y zona picnic."},
        ]
        space_objs = {}
        for s in espacios:
            if not Space.objects.filter(name=s["name"]).exists():
                sp = Space.objects.create(
                    name=s["name"],
                    code=s["code"],
                    space_type=tipo_objs[s["tipo"]],
                    description=s["desc"],
                    capacity=s["capacity"],
                    hourly_rate=Decimal(str(s["hrate"])),
                    requires_employee_approval=s["requires_approval"],
                    min_reservation_minutes=s["min_min"],
                    max_reservation_minutes=s["max_min"],
                    advance_days_limit=s["advance"],
                    status=s["status"],
                )
                space_objs[s["name"]] = sp
                # Lunes a Domingo (0-6), lunes cerrado opcional
                for day in range(7):
                    if day == 0:
                        # Lunes cerrado (mantenimiento) - No crear
                        continue
                    # Martes a Viernes 6am-10pm, Sábado 6am-11pm, Domingo 7am-9pm
                    start = time(6, 0)
                    end = time(22, 0)
                    if day == 5:
                        end = time(23, 0)
                    if day == 6:
                        start = time(7, 0)
                        end = time(21, 0)
                    OperatingHours.objects.create(
                        space=sp, weekday=day,
                        open_time=start, close_time=end,
                    )
                print(f"  ✔ Espacio: {s['name']} ({s['code']})")
            else:
                space_objs[s["name"]] = Space.objects.get(name=s["name"])

        # ============================================================
        # 6) REFRESHMENTS - CATEGORÍAS y PRODUCTOS (Catálogo real del club)
        # ============================================================
        categorias = [
            ("Bebidas Frías e Hidratantes", "💧", 1),
            ("Gaseosas y Jugos", "🥤", 2),
            ("Snacks y Pasabocas", "🍟", 3),
            ("Confitería", "🍫", 4),
            ("Cervezas y Licores", "🍺", 5),
            ("Accesorios Deportivos", "🏋️", 6),
        ]
        cat_objs = {}
        for c, ic, orden in categorias:
            cat, _ = ProductCategory.objects.get_or_create(
                name=c, defaults={"icon": ic, "order": orden, "is_active": True}
            )
            cat_objs[c] = cat

        # SINCRONIZACIÓN NO DESTRUCTIVA:
        # - No se borran productos existentes (preserva stock y cambios del admin).
        # - Se crean los productos del catálogo que aún no existan.
        # - Las categorías obsoletas sin productos se limpian.
        sku_catalog = {sku for _, _, _, _, sku in productos}
        Product.objects.exclude(sku__in=sku_catalog).delete()
        ProductCategory.objects.exclude(
            name__in=[c[0] for c in categorias]
        ).filter(products__isnull=True).delete()

        # (nombre, categoría, precio, stock, sku)
        productos = [
            # Bebidas Frías e Hidratantes
            ("AGUA BRISA SABORIZADA CON GAS SABOR MARACUYA 600 ML", "Bebidas Frías e Hidratantes", 3000, 23, "7702535030660"),
            ("AGUA CRISTAL 600 ML", "Bebidas Frías e Hidratantes", 3000, 15, "7702090022711"),
            ("AGUA CIELO 1 LT", "Bebidas Frías e Hidratantes", 4000, 118, "7707244561283"),
            ("GATORADE 500 ML", "Bebidas Frías e Hidratantes", 6000, 16, "7702192422051"),
            ("AGUA CIELO LIMA LIMON 620 ML", "Bebidas Frías e Hidratantes", 3000, 25, "7708129732224"),
            ("AGUA BRISA SABORIZADA CON GAS SABOR MANZANA 600 ML", "Bebidas Frías e Hidratantes", 4000, 10, "7702535013212"),
            ("ELECTROLIT SUERO REHIDRATANTE COCO 625 ML", "Bebidas Frías e Hidratantes", 10000, 0, "7501125176456"),
            ("POWERADE ROJO", "Bebidas Frías e Hidratantes", 5000, 2, "77702535009987"),
            ("AGUA MANANTIAL 600 ML", "Bebidas Frías e Hidratantes", 4000, 8, "7702609005372"),
            ("AGUA BRISA 600 ML", "Bebidas Frías e Hidratantes", 3000, 1, "7702535010327"),
            ("SPEED MAX 310 ML", "Bebidas Frías e Hidratantes", 3000, 4, "7702090071849"),
            # Gaseosas y Jugos
            ("CAJITA HIT NECTAR 200 ML", "Gaseosas y Jugos", 3500, 0, "7707133077956"),
            ("COLOMBIANA GASEOSA 3 LT", "Gaseosas y Jugos", 13000, 0, "7707151700768"),
            ("JUGO DEL VALLLE 1.5 LT", "Gaseosas y Jugos", 8000, 2, "7702535022061"),
            ("NECTAR CALIFORNIA", "Gaseosas y Jugos", 5000, 0, "07702617077293"),
            ("COCA COLA 3 LT", "Gaseosas y Jugos", 13000, 3, "7702535024447"),
            ("KOLA ROMAN 400ML", "Gaseosas y Jugos", 4000, 19, "7702609006508"),
            ("CAJITA DEL VALLE 188 ML", "Gaseosas y Jugos", 3000, 133, "7702535030110"),
            # Snacks y Pasabocas
            ("NATUCHIPS PLATANO MADURO 38 GR", "Snacks y Pasabocas", 3000, 16, "7702189055484"),
            ("DETODITO NATURAL 165 GR", "Snacks y Pasabocas", 12000, 4, "7702189057617"),
            ("DETODITO LIMON 165 GR", "Snacks y Pasabocas", 12000, 0, "7702189057648"),
            ("MANI MIX NUECES LA ESPECIAL 40 G", "Snacks y Pasabocas", 4000, 2, "7702007065640"),
            ("MARGARITA BOLZASA POLLO 75 G", "Snacks y Pasabocas", 7000, 3, "7702189059666"),
            ("MARGARITA BOLZASA LIMON 75 G", "Snacks y Pasabocas", 7000, 0, "7702189059659"),
            ("NATUCHIPS YUCA 38G", "Snacks y Pasabocas", 4000, 0, "7702189060136"),
            ("MINICHIPS FESTIVAL", "Snacks y Pasabocas", 3000, 0, "7702025142910"),
            ("DETODITO MIX 50 GR", "Snacks y Pasabocas", 4000, 19, "7702189055569"),
            ("CHEESE TRIS BOLSAZA 120 GR", "Snacks y Pasabocas", 9000, 0, "7702189059864"),
            ("DETODITO MIX 165 GR", "Snacks y Pasabocas", 12000, 2, "7702189057631"),
            ("CHEETOS BOLIQUESO 34 GR", "Snacks y Pasabocas", 4000, 10, "7702189057860"),
            ("CHEESE TRIS QUESO 42 GR", "Snacks y Pasabocas", 4000, 19, "7702189056788"),
            ("CHOCLITOS LIMON 45 GR", "Snacks y Pasabocas", 4000, 12, "7702189058546"),
            ("DETODITO LIMON 50 GR", "Snacks y Pasabocas", 4000, 12, "7702189055583"),
            ("MARGARITA LIMON 36 GR", "Snacks y Pasabocas", 4000, 17, "7702189056023"),
            ("MARGARITA DE POLLO 36G", "Snacks y Pasabocas", 4000, 4, "7702189056047"),
            ("MARGARITA ONDULADA TOMATE 35G", "Snacks y Pasabocas", 4000, 14, "7702189057822"),
            ("MANI MOTO SAL 23 GR - SIN CUBIERTA", "Snacks y Pasabocas", 3000, 7, "7702189056429"),
            ("NATUCHIPS PLATANO VERDE 38 GR", "Snacks y Pasabocas", 3000, 19, "7702189055453"),
            ("DETODITO BBQ 50 GR", "Snacks y Pasabocas", 4000, 10, "7702189055545"),
            # Confitería
            ("WAFER BRIDGE RON PASA", "Confitería", 2000, 0, "7702011271718"),
            ("GALLETA AVENA GRANOLA", "Confitería", 3000, 11, "7702011275332"),
            ("RING POP", "Confitería", 3000, 2, "7798040464328"),
            ("MINICHOSO BIMBO", "Confitería", 2000, 7, "7705326080578"),
            ("WAFER MUUU CHOCOLATE", "Confitería", 1000, 8, "7702011052063"),
            ("WAFER BRIDGE FRESA", "Confitería", 2000, 28, "7702011271730"),
            ("YOGO YOGO ORIGINAL FRESA 150 G", "Confitería", 4000, 0, "770001047666"),
            ("YOGO YOGO ORIGINAL MELOCOTON 150 G", "Confitería", 4000, 0, "7702001047680"),
            ("YOGO YOGO ORIGINAL MORA 150 G", "Confitería", 4000, 1, "7702001047673"),
            ("PONY MALTA MINI 200 CM3", "Confitería", 2000, 38, "7702004025784"),
            ("HALLS EXTRA FUERTE", "Confitería", 3000, 9, "7622202015212"),
            ("HALL MENTOL, CEREZA Y LYPTUS", "Confitería", 3000, 0, "7622210427045"),
            ("GALLETA DUX ORIGINAL", "Confitería", 2000, 28, "7702025101290"),
            ("CHOKIS CHOCOBASE 47 G", "Confitería", 3000, 12, "7702189056245"),
            ("TRIDENT X5 MENTA", "Confitería", 2000, 10, "7622201776664"),
            ("TRIDENT X5 MORA AZUL", "Confitería", 2000, 3, "7622201776695"),
            ("GALLETAS OREO PEQUEÑA", "Confitería", 2000, 4, "20007590011251100"),
            # Cervezas y Licores
            ("HEINEKEN 310 CM3", "Cervezas y Licores", 7000, 4, "7707430870120"),
            ("AGUILA LIGTH LATA", "Cervezas y Licores", 5000, 40, "7702004002624"),
            ("CERVEZA BUDWEISER LATA", "Cervezas y Licores", 5000, 27, "7702004110596"),
            ("AGUILA ORIGINAL LATA", "Cervezas y Licores", 5000, 82, "7702004025760"),
            ("CERVEZA COSTEÑA 269 ML", "Cervezas y Licores", 5000, 45, "7702004005601"),
            ("CERVEZA CORONA CERO 269 ML", "Cervezas y Licores", 5000, 16, "7707311662905"),
            ("SMIRNOF ICE GREEN APPLE LATA 250 ML", "Cervezas y Licores", 8000, 0, "5410316945981"),
            # Accesorios Deportivos
            ("FAJAS CINTURA MUJERES", "Accesorios Deportivos", 35000, 7, "6941979008359"),
            ("FAJAS CINTURA HOMBRES", "Accesorios Deportivos", 30000, 10, "69411979008298"),
            ("MUÑEQUERA SAIBIKE", "Accesorios Deportivos", 7000, 12, "7453077235449"),
            ("RODILLERA CLASSIC KNEE SUPPORT", "Accesorios Deportivos", 35000, 8, "691979008854"),
            ("CANILLERA FOOTBALL E-5113", "Accesorios Deportivos", 15000, 6, "6936580051139"),
            ("GUANTES PARA EJERCICIOS E-5124", "Accesorios Deportivos", 40000, 5, "6936580051245"),
            ("GUANTES DE ARQUERO E-5130", "Accesorios Deportivos", 60000, 7, "6936580051306"),
            ("CANILLERA FOOTBALL E-5114", "Accesorios Deportivos", 15000, 11, "6936580051146"),
            ("CANILLERA FOOTBALL E-5109", "Accesorios Deportivos", 15000, 7, "6936580051092"),
        ]
        for n, cat, p, stk, sku in productos:
            Product.objects.get_or_create(
                sku=sku,
                defaults={
                    "name": n,
                    "category": cat_objs[cat],
                    "price": Decimal(str(p)),
                    "stock": stk,
                    "min_stock": 5,
                    "is_available": True,
                },
            )
        print(f"✅ {len(productos)} Productos reales del club en {len(cat_objs)} categorías")

        # ============================================================
        # 7) REWARDS - NIVELES y REGLAS y CATÁLOGO
        # ============================================================
        tiers = [
            ("Bronce", 0, Decimal("0"), "#cd7f32", "🥉",
             "Acceso a descuentos básicos y ofertas mensuales."),
            ("Plata", 5000, Decimal("5"), "#c0c0c0", "🥈",
             "5% descuento base + prioridad en reservas de eventos."),
            ("Oro", 20000, Decimal("10"), "#d4af37", "🥇",
             "10% descuento base + 1 entrada gratis piscina al mes."),
            ("Diamante", 50000, Decimal("15"), "#b9f2ff", "💎",
             "15% descuento base + descuentos exclusivos + acceso VIP eventos."),
        ]
        for nomb, min_p, desc, color, icon, benefits in tiers:
            LoyaltyTier.objects.get_or_create(
                name=nomb,
                defaults={
                    "min_points": min_p,
                    "discount_percent": desc,
                    "color": color,
                    "benefits": benefits,
                    "is_active": True,
                }
            )

        reglas = [
            ("RESERVATION", "Ganancia por reservas pagadas", 100, Decimal("0.05")),
            ("REFRESHMENT", "Ganancia por consumos en barra", 20, Decimal("0.03")),
            ("MEMBERSHIP", "Pago de afiliación o renovación", 1000, Decimal("0.08")),
            ("REFERRAL", "Nuevo cliente afiliado referido", 2000, Decimal("0")),
            ("BIRTHDAY", "Regalo automático el día del cumple", 500, Decimal("0")),
        ]
        for code, desc, pts, pct in reglas:
            RewardRule.objects.get_or_create(
                action_type=code,
                defaults={
                    "description": desc,
                    "points_amount": pts, "points_per_currency": pct,
                    "is_active": True,
                }
            )

        catalog = [
            ("Día Gratis de Gimnasio + Piscina", 2000, "General", 200,
             "Acceso completo 1 día a gimnasio + piscina. Vence en 30 días."),
            ("1 Hora Cancha Fútbol 5 Gratis", 3000, "Deportes", 100,
             "1 reserva de 60 min cancha de fútbol 5 (impuestos incluidos)."),
            ("Helado Triple Gratis", 1500, "Refrescos", 500,
             "Canjeable por helado 3 bolas con coberturas especiales."),
            ("Descuento $50.000 en Eventos", 8000, "Eventos", 50,
             "Vale $50.000 COP para alquiler de Salón Principal o Salón Social."),
            ("Extensión Membresía 1 Mes", 15000, "Membresía", 20,
             "Extiende tu membresía por 30 días adicionales (requiere membresía activa)."),
            ("Bono $20.000 en Refresquería", 3000, "Refrescos", 200,
             "Bono sin restricciones para la barra del club."),
        ]
        for name, req, cat, stk, desc in catalog:
            RewardCatalogItem.objects.get_or_create(
                name=name,
                defaults={
                    "points_required": req, "category": cat, "stock": stk,
                    "description": desc, "is_active": True,
                }
            )
        print("✅ Sistema Fidelización cargado (Tiers, Reglas, Catálogo)")

        # ============================================================
        # 8) GIMNASIO - MÚSCULOS, EQUIPOS, EJERCICIOS, RUTINAS
        # ============================================================
        musculos = [
            ("Pecho", "🏋️", 1),
            ("Espalda", "🔙", 2),
            ("Hombros", "🧱", 3),
            ("Bíceps", "💪", 4),
            ("Tríceps", "🦾", 5),
            ("Antebrazos", "💢", 6),
            ("Cuádriceps", "🦵", 7),
            ("Isquiotibiales", "🍖", 8),
            ("Glúteos", "🍑", 9),
            ("Gemelos", "🦶", 10),
            ("Abdominales", "🔥", 11),
            ("Cardio", "❤️", 12),
        ]
        musc_objs = {}
        for n, icon, orden in musculos:
            m, _ = MuscleGroup.objects.get_or_create(
                name=n, defaults={"slug": slugify(n), "icon": icon,
                                  "order": orden, "is_active": True}
            )
            musc_objs[n] = m

        equipos = [
            ("Banco Plano", "Zona Pesas", ["Pecho", "Tríceps", "Hombros"]),
            ("Barra Olímpica", "Zona Pesas", ["Pecho", "Espalda", "Hombros", "Bíceps"]),
            ("Mancuernas Rack", "Zona Pesas", ["Pecho", "Espalda", "Hombros", "Bíceps", "Tríceps"]),
            ("Máquina Jalón al Pecho", "Zona Espalda", ["Espalda", "Bíceps"]),
            ("Máquina Remo Polea", "Zona Espalda", ["Espalda", "Bíceps"]),
            ("Press Militar Smith", "Zona Hombros", ["Hombros", "Tríceps"]),
            ("Press Pierna 45°", "Zona Piernas", ["Cuádriceps", "Glúteos", "Isquiotibiales"]),
            ("Barras Paralelas", "Zona Tríceps", ["Tríceps", "Pecho"]),
            ("Bicicleta Estática", "Zona Cardio", ["Cardio"]),
            ("Cinta Trotadora", "Zona Cardio", ["Cardio"]),
            ("Elíptica", "Zona Cardio", ["Cardio", "Cuádriceps", "Glúteos"]),
            ("Dominadas Barra", "Zona Espalda", ["Espalda", "Bíceps"]),
            ("Cuerda para Saltar", "Zona Cardio", ["Cardio"]),
            ("Máquina Hip Thrust", "Zona Glúteos", ["Glúteos", "Isquiotibiales"]),
            ("Colchonetas", "Zona Abdominales", ["Abdominales"]),
            ("Cable Cross", "Zona Funcional", ["Pecho", "Espalda", "Hombros", "Bíceps", "Tríceps"]),
        ]
        eq_objs = {}
        for n, loc, musc_list in equipos:
            if not Equipment.objects.filter(name=n).exists():
                eq = Equipment.objects.create(name=n, location=loc, is_active=True)
                for m in musc_list:
                    if m in musc_objs:
                        eq.muscle_groups.add(musc_objs[m])
                eq.save()
                eq_objs[n] = eq
            else:
                eq_objs[n] = Equipment.objects.get(name=n)

        ejercicios = [
            # (nombre, grupo_primario, [secundarios], desc, tips, [equipos], dificultad, series, reps_min, reps_max)
            ("Press de Banca Plano", "Pecho", ["Tríceps", "Hombros"],
             "Acuéstese en banco plano, agarre ancho. Baje barra al esternón, empuje hacia arriba controlado.",
             "No rebote la barra en el pecho, mantenga core activo, pies firmes en piso.",
             ["Banco Plano", "Barra Olímpica"], "INTERMEDIATE", 4, 8, 10),
            ("Aperturas con Mancuernas", "Pecho", ["Tríceps"],
             "Acuéstese banco plano, mancuernas al pecho. Abra brazos como abrir un libro, retorne.",
             "No baje más allá de la horizontal para evitar lesión de hombro.",
             ["Banco Plano", "Mancuernas Rack"], "BEGINNER", 4, 10, 12),
            ("Cruce Cables Crossover", "Pecho", ["Tríceps"],
             "Cables a altura media, cruce al frente, contraiga pectoral al final.",
             "Mantenga ligera flexión de codos durante todo el movimiento.",
             ["Cable Cross"], "INTERMEDIATE", 4, 12, 15),
            ("Jalón al Pecho", "Espalda", ["Bíceps"],
             "Sentado máquina, agarre ancho. Tire de la barra al pecho con dominancia de espalda.",
             "Inicialice el movimiento con los omóplatos, no solo tire con bíceps.",
             ["Máquina Jalón al Pecho"], "INTERMEDIATE", 4, 10, 12),
            ("Remo con Barra", "Espalda", ["Bíceps", "Glúteos"],
             "Flexión cadera, espalda neutra. Jale barra hacia abdomen, apriete omóplatos.",
             "Mantenga la espalda recta, no realice balanceo.",
             ["Barra Olímpica"], "ADVANCED", 4, 10, 12),
            ("Dominadas", "Espalda", ["Bíceps"],
             "Colgado de barra, agarre ancho, suba barbilla por encima de la barra.",
             "Excelente para fuerza de espalda. Use banda asistida si es necesario.",
             ["Dominadas Barra"], "ADVANCED", 4, 6, 10),
            ("Press Militar", "Hombros", ["Tríceps"],
             "De pie o sentado, barra a altura clavícula, empuje verticalmente.",
             "No bloquee los codos completamente arriba, proteja la columna.",
             ["Press Militar Smith"], "INTERMEDIATE", 4, 10, 12),
            ("Elevaciones Laterales", "Hombros", [],
             "De pie, mancuernas a los lados, eleve brazos paralelos al suelo.",
             "No levante el hombro (encogerse), suba lateralmente sin impulso.",
             ["Mancuernas Rack"], "BEGINNER", 4, 12, 15),
            ("Curl Bíceps Barra", "Bíceps", ["Antebrazos"],
             "De pie, barra ancho hombros, suba sin mover codos desde las caderas.",
             "Movimiento estricto, no realice balanceo del torso.",
             ["Barra Olímpica"], "INTERMEDIATE", 4, 10, 12),
            ("Curl Martillo", "Bíceps", ["Antebrazos"],
             "Agarre neutral, suba mancuerna sin girar muñecas.",
             "Excelente para braquiorradial y grosor de antebrazo.",
             ["Mancuernas Rack"], "BEGINNER", 4, 12, 12),
            ("Fondos en Paralelas", "Tríceps", ["Pecho"],
             "Soporte en paralelas, torso vertical, baje y empuje.",
             "No baje más allá de los 90° para proteger hombros.",
             ["Barras Paralelas"], "ADVANCED", 4, 8, 12),
            ("Extensiones Tríceps Polea", "Tríceps", [],
             "Polea alta, cuerda. Empuje hacia abajo extendiendo codos completamente.",
             "Contracción máxima 1 segundo, excéntrico lento (2 seg).",
             ["Cable Cross"], "BEGINNER", 4, 12, 15),
            ("Sentadilla con Barra", "Cuádriceps", ["Glúteos", "Isquiotibiales"],
             "Barra sobre trapecio alto, baje como si fuera a sentarse en silla.",
             "Rodillas en dirección a los pies, no rebasen las puntas demasiado.",
             ["Barra Olímpica"], "ADVANCED", 4, 10, 12),
            ("Prensa Pierna", "Cuádriceps", ["Glúteos", "Isquiotibiales"],
             "Sentado máquina 45°, empuje plataforma sin extender rodillas completamente.",
             "Diferentes pies posiciones: alto = glúteos, bajo = cuádriceps.",
             ["Press Pierna 45°"], "INTERMEDIATE", 4, 12, 15),
            ("Peso Muerto Rumano", "Isquiotibiales", ["Glúteos", "Espalda"],
             "Barra al frente, descienda por las caderas, piernas semiflex, estire isquios.",
             "Sienta la tensión en la parte posterior del muslo.",
             ["Barra Olímpica"], "ADVANCED", 4, 10, 12),
            ("Hip Thrust", "Glúteos", ["Isquiotibiales"],
             "Espalda apoyada en banco, barra sobre caderas, empuje arriba contraiga.",
             "Squeeze glúteos 2 segundos arriba.",
             ["Máquina Hip Thrust", "Barra Olímpica"], "INTERMEDIATE", 4, 12, 15),
            ("Zancadas Mancuernas", "Cuádriceps", ["Glúteos", "Isquiotibiales"],
             "Paso largo hacia adelante, baje rodilla contraria casi al piso.",
             "Empuje con el talón del pie adelante para volver.",
             ["Mancuernas Rack"], "INTERMEDIATE", 4, 10, 12),
            ("Crunch Abdominal", "Abdominales", [],
             "Acuéstese boca arriba, eleve hombros, contraiga abdomen.",
             "Respire: exhale al subir, inhale al bajar. No tire del cuello.",
             ["Colchonetas"], "BEGINNER", 4, 20, 25),
            ("Plancha Frontal", "Abdominales", ["Glúteos", "Espalda"],
             "Soporte antebrazos + puntas de pies, cuerpo línea recta.",
             "No deje caer cadera ni suba demasiado la pelvis.",
             ["Colchonetas"], "BEGINNER", 4, 45, 60),
            ("Trote Cinta", "Cardio", ["Cuádriceps", "Glúteos"],
             "Calentamiento 5min caminando, trote a 7-10 km/h según nivel.",
             "Zancada natural, torso inclinado ligeramente.",
             ["Cinta Trotadora"], "BEGINNER", 1, 15, 25),
            ("Elíptica Intervalos", "Cardio", ["Cuádriceps", "Glúteos"],
             "30s alta intensidad + 60s recuperación x 12-15 series.",
             "Bajo impacto, ideal para rodillas.",
             ["Elíptica"], "INTERMEDIATE", 1, 20, 25),
            ("Cuerda Saltos", "Cardio", ["Gemelos"],
             "Saltos rápidos, pies juntos, muñecas giran la cuerda.",
             "Excelente para coordinación y resistencia cardiovascular.",
             ["Cuerda para Saltar"], "INTERMEDIATE", 5, 60, 90),
        ]
        ej_objs = {}
        for (nombre, primario, sec_list, desc, tips, eq_list, dif, sets, reps_min, reps_max) in ejercicios:
            if not Exercise.objects.filter(slug=slugify(nombre)).exists():
                eq_principal = eq_objs[eq_list[0]] if (eq_list and eq_list[0] in eq_objs) else None
                ej = Exercise.objects.create(
                    name=nombre,
                    slug=slugify(nombre),
                    muscle_group=musc_objs[primario],
                    description=desc,
                    tips=tips,
                    common_mistakes=tips,
                    difficulty_level=dif,
                    recommended_sets=sets,
                    recommended_reps_min=reps_min,
                    recommended_reps_max=reps_max,
                    equipment=eq_principal,
                    is_active=True,
                )
                for m in sec_list:
                    if m in musc_objs:
                        ej.secondary_groups.add(musc_objs[m])
                ej.save()
                ej_objs[nombre] = ej
            else:
                ej_objs[nombre] = Exercise.objects.get(slug=slugify(nombre))
        print(f"✅ Gimnasio: {len(musc_objs)} Músculos, {len(eq_objs)} Equipos, {len(ej_objs)} Ejercicios")

        # ============================================================
        # 9) RUTINAS GENÉRICAS
        # ============================================================
        rutinas_data = [
            {
                "name": "Rutina Full Body Principiante",
                "goal": "STRENGTH",
                "diff": "BEGINNER",
                "is_generic": True,
                "duration": "MEDIUM",
                "frequency_days": 3,
                "estimated_weeks": 12,
                "muscles": ["Pecho", "Espalda", "Hombros", "Bíceps", "Tríceps",
                            "Cuádriceps", "Glúteos", "Abdominales", "Cardio"],
                "warm_up": (
                    "5 min cinta caminando a 5 km/h + estiramiento dinámico "
                    "caderas, hombros, muñecas, rodillas (2 repeticiones cada una)."
                ),
                "cool_down": (
                    "10 min elíptica suave resistencia 4 + estiramientos "
                    "estáticos 30 segundos cada grupo muscular."
                ),
                "tips": (
                    "2-3 días a la semana con mínimo 1 día de descanso entre sesiones. "
                    "Comience con pesos ligeros para dominar la técnica."
                ),
                "nutricion": (
                    "Proteína 1.8g/kg peso. Hidrátese 3L de agua diarios. "
                    "Complejo B + Magnesio nocturno para recuperación."
                ),
                "ejercicios": [
                    ("Sentadilla con Barra", 1, 3, "12", "Solo barra"),
                    ("Press de Banca Plano", 2, 3, "10", "20"),
                    ("Jalón al Pecho", 3, 3, "10", "20"),
                    ("Curl Bíceps Barra", 4, 3, "10", "12"),
                    ("Fondos en Paralelas", 5, 3, "8", "0"),
                    ("Crunch Abdominal", 6, 3, "20", "0"),
                    ("Trote Cinta", 7, 1, "15min", "0"),
                ]
            },
            {
                "name": "Rutina Hipertrofia Avanzada",
                "goal": "HYPERTROPHY",
                "diff": "ADVANCED",
                "is_generic": True,
                "duration": "LONG",
                "frequency_days": 5,
                "estimated_weeks": 16,
                "muscles": ["Pecho", "Espalda", "Hombros", "Bíceps", "Tríceps",
                            "Cuádriceps", "Isquiotibiales", "Glúteos", "Abdominales", "Cardio"],
                "warm_up": (
                    "Cuerda 3 min saltos suaves + 2 series ligeras de cada "
                    "ejercicio base antes del peso de trabajo."
                ),
                "cool_down": (
                    "10 min elíptica ligero + foam roller 5 min (espalda, "
                    "cuádriceps, isquios, gemelos)."
                ),
                "tips": (
                    "Dividir en 4 días: Push / Pull / Legs / Upper Full. "
                    "Dormir 7-9 h, proteína 2.2g/kg, aumentar calorías gradualmente."
                ),
                "nutricion": (
                    "Superávit calórico 250-500 kcal. Proteína 2.2g/kg. "
                    "Carbohidratos 5g/kg. Grasas saludables 1g/kg."
                ),
                "ejercicios": [
                    ("Press de Banca Plano", 1, 4, "8", "40"),
                    ("Aperturas con Mancuernas", 2, 4, "10-12", "20"),
                    ("Cruce Cables Crossover", 3, 4, "12-15", "20"),
                    ("Jalón al Pecho", 4, 4, "10", "50"),
                    ("Remo con Barra", 5, 4, "10", "60"),
                    ("Peso Muerto Rumano", 6, 4, "10", "70"),
                    ("Hip Thrust", 7, 4, "12", "60"),
                    ("Plancha Frontal", 8, 3, "60s", "0"),
                    ("Cuerda Saltos", 9, 5, "90s", "0"),
                ]
            },
            {
                "name": "Rutina Definición / Pérdida de Grasa",
                "goal": "WEIGHT_LOSS",
                "diff": "INTERMEDIATE",
                "is_generic": True,
                "duration": "LONG",
                "frequency_days": 5,
                "estimated_weeks": 12,
                "muscles": ["Pecho", "Espalda", "Hombros", "Bíceps", "Tríceps",
                            "Cuádriceps", "Isquiotibiales", "Glúteos", "Abdominales", "Cardio"],
                "warm_up": "Elíptica 8 min resistencia 6 + estiramiento dinámico.",
                "cool_down": (
                    "Cinta 10 min inclinación 5% velocidad 5 km/h + "
                    "estiramientos estáticos 30s."
                ),
                "tips": (
                    "4-5 días a la semana. Acompañar con dieta 15-20% "
                    "déficit calórico + 1.8-2.2g proteína/kg."
                ),
                "nutricion": (
                    "Déficit calórico. Proteína 2.0g/kg. Fibra 25-35g. "
                    "Agua 3-4L diarios. Dormir 7-8h."
                ),
                "ejercicios": [
                    ("Sentadilla con Barra", 1, 4, "12", "40"),
                    ("Peso Muerto Rumano", 2, 4, "12", "50"),
                    ("Zancadas Mancuernas", 3, 4, "12/cada pierna", "15"),
                    ("Press Militar", 4, 4, "10", "25"),
                    ("Elevaciones Laterales", 5, 4, "15", "8"),
                    ("Remo con Barra", 6, 4, "10", "40"),
                    ("Hip Thrust", 7, 4, "15", "50"),
                    ("Curl Bíceps Barra", 8, 4, "12", "20"),
                    ("Fondos en Paralelas", 9, 4, "10", "0"),
                    ("Crunch Abdominal", 10, 5, "25", "0"),
                    ("Plancha Frontal", 11, 5, "60s", "0"),
                    ("Elíptica Intervalos", 12, 1, "20min", "0"),
                ]
            },
            {
                "name": "Rutina Acondicionamiento General",
                "goal": "GENERAL",
                "diff": "BEGINNER",
                "is_generic": True,
                "duration": "MEDIUM",
                "frequency_days": 3,
                "estimated_weeks": 8,
                "muscles": ["Cuádriceps", "Glúteos", "Pecho", "Espalda",
                            "Bíceps", "Abdominales", "Cardio"],
                "warm_up": "Cinta caminando 7 min + estiramientos básicos.",
                "cool_down": (
                    "Bicicleta estática 10 min + stretching suave 5 min."
                ),
                "tips": (
                    "Ideal para personas que vuelven a entrenar después de "
                    "pausa larga. Aumentar peso gradualmente."
                ),
                "nutricion": (
                    "Proteína 1.6g/kg. Hidratos 4g/kg. Agua 3L. Comer frutas y verduras."
                ),
                "ejercicios": [
                    ("Sentadilla con Barra", 1, 3, "12", "Solo barra"),
                    ("Prensa Pierna", 2, 3, "15", "50"),
                    ("Trote Cinta", 3, 1, "20min", "0"),
                    ("Press de Banca Plano", 4, 3, "10", "Solo barra"),
                    ("Jalón al Pecho", 5, 3, "10", "20"),
                    ("Curl Martillo", 6, 3, "12", "10"),
                    ("Crunch Abdominal", 7, 4, "20", "0"),
                    ("Plancha Frontal", 8, 3, "30s", "0"),
                ]
            },
            {
                "name": "Rutina Glúteos y Piernas",
                "goal": "STRENGTH",
                "diff": "INTERMEDIATE",
                "is_generic": True,
                "duration": "MEDIUM",
                "frequency_days": 2,
                "estimated_weeks": 12,
                "muscles": ["Cuádriceps", "Isquiotibiales", "Glúteos", "Abdominales", "Cardio"],
                "warm_up": "Cinta 10min + 2 series ligeras sentadillas.",
                "cool_down": (
                    "Estiramiento isquios, cuádriceps, glúteos, aductores "
                    "40s cada músculo."
                ),
                "tips": (
                    "1-2 veces por semana. Énfasis en fase excéntrica controlada "
                    "(3-4 segundos bajando)."
                ),
                "nutricion": (
                    "Proteína 2.0g/kg. Carbohidratos alrededor del entrenamiento."
                ),
                "ejercicios": [
                    ("Sentadilla con Barra", 1, 4, "10", "50"),
                    ("Prensa Pierna", 2, 4, "15", "80"),
                    ("Hip Thrust", 3, 4, "15", "70"),
                    ("Peso Muerto Rumano", 4, 4, "12", "60"),
                    ("Zancadas Mancuernas", 5, 4, "12/cada pierna", "20"),
                    ("Plancha Frontal", 6, 4, "60s", "0"),
                    ("Trote Cinta", 7, 1, "20min", "0"),
                ]
            },
        ]
        for r in rutinas_data:
            if not Routine.objects.filter(name=r["name"]).exists():
                # Calcular duration para el modelo: SHORT/MEDIUM/LONG
                rutina = Routine.objects.create(
                    name=r["name"],
                    goal=r["goal"],
                    duration=r["duration"],
                    difficulty_level=r["diff"],
                    is_generic=r["is_generic"],
                    is_active=True,
                    description=r["tips"],
                    warm_up=r["warm_up"],
                    cool_down=r["cool_down"],
                    nutrition_tips=r["nutricion"],
                    frequency_days=r["frequency_days"],
                    estimated_weeks=r["estimated_weeks"],
                )
                for g_muscle in r["muscles"]:
                    if g_muscle in musc_objs:
                        rutina.muscle_groups.add(musc_objs[g_muscle])
                for (n_ej, orden, sets_int, reps_str, peso) in r["ejercicios"]:
                    if n_ej in ej_objs:
                        try:
                            w = Decimal(str(peso).replace(",", ".")) if str(peso) not in ("Solo barra", "Peso Corporal", "0") else None
                        except Exception:
                            w = None
                        RoutineExercise.objects.create(
                            routine=rutina,
                            exercise=ej_objs[n_ej],
                            order=orden,
                            sets=sets_int,
                            reps=reps_str,
                            weight_kg=w,
                            rest_seconds=60,
                            notes=(
                                "Técnica siempre primero, aumentar peso gradual. "
                                "Respiración controlada."
                            ),
                        )
                print(f"  ✔ Rutina: {r['name']} ({len(r['ejercicios'])} ej.)")

    print("\n" + "=" * 60)
    print(" SEED DATA COMPLETADO - BASE DE DATOS LISTA ")
    print("=" * 60)
    print("ENTORNO DE PRUEBA AISLADO EXCLUSIVAMENTE.")
    print("Accesos de prueba:")
    print("  Admin    : admin_fh      | password vía DEMO_PASS_ADMIN")
    print("  Empleado : recepcion_fh  | password vía DEMO_PASS_EMP")
    print("  Clientes : cliente1_fh, cliente2_fh, cliente3_fh")
    print("             | passwords vía DEMO_PASS_C1 / C2 / C3")
    print("  Si variables .env no existen, passwords fueron")
    print("  generadas aleatoriamente (marcadas [auto-generada]).")
    print("=" * 60)
    print("Panel Admin Django:", "http://127.0.0.1:8000/admin/")
    print("API Base URL       :", "http://127.0.0.1:8000/api/v1/")
    print("Health Check       :", "http://127.0.0.1:8000/api/v1/health/")


if __name__ == "__main__":
    run()
