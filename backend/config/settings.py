"""
Family Health MF - Django Settings
Trabajo de Grado - Universidad Antonio Nariño
Autor: Luis Fermín Díaz Choles

Python 3.10.x | Django 5.0.x
Seguridad integrada: Ley 1581/2012 Protección de Datos
"""

import os
import sys
from datetime import timedelta
from pathlib import Path

import environ

env = environ.Env(
    DJANGO_DEBUG=(bool, False),
    DJANGO_SECRET_KEY=(str, ""),
    DJANGO_ALLOWED_HOSTS=(list, []),
    DATABASE_URL=(str, ""),
    DB_ENGINE=(str, "django.db.backends.sqlite3"),
    DB_NAME=(str, "db.sqlite3"),
    DB_USER=(str, ""),
    DB_PASSWORD=(str, ""),
    DB_HOST=(str, ""),
    DB_PORT=(str, ""),
    HASHID_FIELD_SALT=(str, "change-me-please-32-characters-or-more"),
    ACCESS_TOKEN_LIFETIME_MINUTES=(int, 60),
    REFRESH_TOKEN_LIFETIME_DAYS=(int, 7),
    CORS_ALLOWED_ORIGINS=(list, []),
    CSRF_TRUSTED_ORIGINS=(list, []),
    RAILWAY_VOLUME_MOUNT_PATH=(str, ""),
    LOGIN_MAX_ATTEMPTS=(int, 5),
    LOGIN_COOLDOWN_MINUTES=(int, 15),
    CLUB_NAME=(str, "Club Family Health"),
    CLUB_NIT=(str, "32739028-5"),
    CLUB_CITY=(str, "Maicao, La Guajira"),
)

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent

ENV_FILE = PROJECT_ROOT / ".env"
if ENV_FILE.exists():
    environ.Env.read_env(str(ENV_FILE))

SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env("DJANGO_DEBUG")

# --- Seguridad SECRET_KEY: si es producción (DEBUG=False) y NO hay SECRET_KEY, fallar
#     con mensaje claro. En desarrollo local (DEBUG=True), si no hay, autogenerar.
if not SECRET_KEY:
    if DEBUG:
        from django.core.management.utils import get_random_secret_key  # noqa: WPS433
        SECRET_KEY = "dev-insecure-" + get_random_secret_key()
        import warnings  # noqa: WPS433
        warnings.warn(
            "ATENCIÓN: estás usando DJANGO_SECRET_KEY AUTOGENERADA (solo desarrollo). "
            "Para producción configúrela como variable de entorno.",
            stacklevel=2,
        )
    else:
        raise RuntimeError(
            "ERROR CRÍTICO PRODUCCIÓN: la variable DJANGO_SECRET_KEY NO está configurada. "
            "Configúrela en Railway Variables / .env. Nunca use la clave autogenerada en producción."
        )
ALLOWED_HOSTS = list(env("DJANGO_ALLOWED_HOSTS") or [])
if DEBUG:
    LAN_HOSTS = [
        "127.0.0.1", "localhost", "testserver",
        "192.168.0.0/16", "10.0.0.0/8", "172.16.0.0/12",
    ]
    for host in LAN_HOSTS:
        if host not in ALLOWED_HOSTS:
            ALLOWED_HOSTS.append(host)

RAILWAY_DOMAIN = os.getenv("RAILWAY_PUBLIC_DOMAIN", "").strip()
# Railway Docker NO inyecta RAILWAY_PUBLIC_DOMAIN dentro del container siempre.
# Variable manual fallback para usuario principiante (solo copia/pega su dominio 1 vez):
DJANGO_PUBLIC_DOMAIN = os.getenv("DJANGO_PUBLIC_DOMAIN", "").strip()
if DJANGO_PUBLIC_DOMAIN and not RAILWAY_DOMAIN:
    RAILWAY_DOMAIN = DJANGO_PUBLIC_DOMAIN

if RAILWAY_DOMAIN and RAILWAY_DOMAIN not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(RAILWAY_DOMAIN)
# También el wildcard .railway.app para futuros redeploys (railway cambia subdominio a veces):
if ".railway.app" not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(".railway.app")
if ".up.railway.app" not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(".up.railway.app")
    if f"*.{RAILWAY_DOMAIN}" not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(f"*.{RAILWAY_DOMAIN}")

# --- Aplicaciones instaladas ---
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "axes",
    "phonenumber_field",
    "hashid_field",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
]

LOCAL_APPS = [
    "apps.authentication",
    "apps.reservations",
    "apps.refreshments",
    "apps.rewards",
    "apps.gym",
    "apps.reports",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

SITE_ID = 1

# --- Middleware (orden de seguridad estricto) ---
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "axes.middleware.AxesMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# --- Base de Datos ---
# LECTURA DATABASE_URL: en DEBUG=TRUE (desarrollo local) SÓLO se lee desde el
# archivo .env con django-environ, IGNORANDO por completo la variable global
# de sistema de Windows (que podría pertenecer a OTRO proyecto, ej: SENA).
# En producción (DEBUG=False) sí se permite DATABASE_URL global de Railway.
if DEBUG:
    _DATABASE_URL_FROM_ENV = env("DATABASE_URL", default="")
else:
    _DATABASE_URL_FROM_ENV = env("DATABASE_URL", default="") or os.getenv(
        "DATABASE_URL", ""
    )

if _DATABASE_URL_FROM_ENV and _DATABASE_URL_FROM_ENV.startswith("postgres"):
    try:
        import dj_database_url  # noqa: WPS433
    except ImportError:  # pragma: no cover - Railway build lo instala desde requirements
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": str(BASE_DIR / "fallback.sqlite3"),
                "ATOMIC_REQUESTS": True,
                "CONN_MAX_AGE": 60,
            }
        }
    else:
        DATABASES = {
            "default": dj_database_url.parse(
                _DATABASE_URL_FROM_ENV,
                conn_max_age=600,
                ssl_require=False,
            )
        }
        DATABASES["default"]["ATOMIC_REQUESTS"] = True
        if "OPTIONS" not in DATABASES["default"]:
            DATABASES["default"]["OPTIONS"] = {}
else:
    VOLUME_PATH = env("RAILWAY_VOLUME_MOUNT_PATH", default="") or os.getenv(
        "RAILWAY_VOLUME_MOUNT_PATH", ""
    )
    _db_name = env("DB_NAME")
    if env("DB_ENGINE") == "django.db.backends.sqlite3" and VOLUME_PATH:
        _db_name = str(Path(VOLUME_PATH) / _db_name)
    elif env("DB_ENGINE") == "django.db.backends.sqlite3":
        _db_name = str(BASE_DIR / _db_name)
    DATABASES = {
        "default": {
            "ENGINE": env("DB_ENGINE"),
            "NAME": _db_name,
            "USER": env("DB_USER"),
            "PASSWORD": env("DB_PASSWORD"),
            "HOST": env("DB_HOST"),
            "PORT": env("DB_PORT"),
            "ATOMIC_REQUESTS": True,
            "CONN_MAX_AGE": 60,
        }
    }

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Autenticación Custom ---
AUTH_USER_MODEL = "authentication.User"
AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# --- Validación de contraseñas (Ley 1581 seguridad) ---
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
     "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]

# --- Internacionalización ---
LANGUAGE_CODE = "es-CO"
TIME_ZONE = "America/Bogota"
USE_I18N = True
USE_TZ = True

# --- Static y Media ---
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
SPA_BUILD_DIR = PROJECT_ROOT / "frontend" / "dist"
STATICFILES_DIRS = [BASE_DIR / "static"]
if SPA_BUILD_DIR.exists():
    STATICFILES_DIRS.append(SPA_BUILD_DIR)
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
VOLUME_MEDIA = env("RAILWAY_VOLUME_MOUNT_PATH") or os.getenv("RAILWAY_VOLUME_MOUNT_PATH", "")
if VOLUME_MEDIA:
    MEDIA_ROOT = Path(VOLUME_MEDIA) / "media"
else:
    MEDIA_ROOT = BASE_DIR / "media"

FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5 MB

# --- REST Framework ---
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
    ),
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",
        "user": "1000/hour",
        "login": "10/minute",
        "register": "5/hour",
    },
    "DEFAULT_FILTER_BACKENDS": (
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
}

# --- JWT (Simple JWT) ---
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(env("ACCESS_TOKEN_LIFETIME_MINUTES"))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(env("REFRESH_TOKEN_LIFETIME_DAYS"))),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS512",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUDIENCE": "family-health-mf",
    "ISSUER": "club-family-health",
    "JWK_URL": None,
    "LEEWAY": timedelta(seconds=10),
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "JTI_CLAIM": "jti",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=120),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=7),
    "TOKEN_OBTAIN_SERIALIZER": "apps.authentication.serializers.CustomTokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
}

# --- CORS ---
CORS_ALLOWED_ORIGINS = list(env("CORS_ALLOWED_ORIGINS") or [])
CORS_ALLOW_CREDENTIALS = True
# Permitir todos los orígenes SÓLO en desarrollo local (DEBUG=True), así el
# móvil/celular en LAN (192.168.x.x:5173 / 10.x.x.x:5173) funciona sin bloqueos.
# En producción (DEBUG=False) se respeta estrictamente CORS_ALLOWED_ORIGINS.
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
if RAILWAY_DOMAIN:
    for proto in ("https://", "http://"):
        _url = f"{proto}{RAILWAY_DOMAIN}"
        if _url not in CORS_ALLOWED_ORIGINS:
            CORS_ALLOWED_ORIGINS.append(_url)
CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

# --- CSRF ---
CSRF_TRUSTED_ORIGINS = list(env("CSRF_TRUSTED_ORIGINS") or [])
if RAILWAY_DOMAIN:
    for proto in ("https://", "http://"):
        _url = f"{proto}{RAILWAY_DOMAIN}"
        if _url not in CSRF_TRUSTED_ORIGINS:
            CSRF_TRUSTED_ORIGINS.append(_url)
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"

# --- Session Cookies (seguridad) ---
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7

# --- Seguridad adicional (Solo HTTPS en producción) ---
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
    X_FRAME_OPTIONS = "DENY"
else:
    SECURE_SSL_REDIRECT = False
    SECURE_HSTS_SECONDS = 0
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "SAMEORIGIN"

# --- Django Axes (Bloqueo por intentos fallidos) ---
AXES_FAILURE_LIMIT = int(env("LOGIN_MAX_ATTEMPTS", default=5))
AXES_COOLOFF_TIME = timedelta(minutes=int(env("LOGIN_COOLDOWN_MINUTES", default=15)))
AXES_LOCK_OUT_AT_FAILURE = True
AXES_RESET_ON_SUCCESS = True
AXES_LOCKOUT_PARAMETERS = ["username", "ip_address", "user_agent"]
AXES_VERBOSE = True
AXES_CACHE = "default"

# --- Django Allauth (formato Colombia) ---
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = "optional"
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True

# --- Hash ID Field ---
HASHID_FIELD_SALT = env("HASHID_FIELD_SALT")
HASHID_FIELD_ALLOW_INT_LOOKUP = True
HASHID_FIELD_ENABLE_HASHID_OBJECT = False

# --- Logging (Cumplimiento Ley 1581 trazabilidad) ---
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {asctime} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file_security": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": str(BASE_DIR / "security.log"),
            "formatter": "verbose",
        },
        "file_audit": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": str(BASE_DIR / "audit.log"),
            "formatter": "verbose",
        },
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO" if DEBUG else "WARNING",
    },
    "loggers": {
        "django.security": {
            "handlers": ["file_security", "console"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "axes.watch_login": {
            "handlers": ["file_security"],
            "level": "INFO",
            "propagate": False,
        },
        "apps.authentication": {
            "handlers": ["file_audit", "console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# --- Constantes específicas del club ---
CLUB_NAME = env("CLUB_NAME", default="Club Family Health")
CLUB_NIT = env("CLUB_NIT", default="32739028-5")
CLUB_CITY = env("CLUB_CITY", default="Maicao, La Guajira")

# --- Roles RBAC ---
ROLE_ADMIN = "ADMIN"
ROLE_EMPLOYEE = "EMPLOYEE"
ROLE_CLIENT = "CLIENT"
USER_ROLES = (
    (ROLE_ADMIN, "Administrador"),
    (ROLE_EMPLOYEE, "Empleado / Recepción"),
    (ROLE_CLIENT, "Cliente"),
)
