"""
Authentication Models - Club Family Health
RBAC: 3 Roles (ADMIN / EMPLOYEE / CLIENT)
Cumplimiento Ley 1581/2012 Protección Datos Personales
"""
import logging

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.validators import EmailValidator, RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

logger = logging.getLogger("apps.authentication")


class UserManager(BaseUserManager):
    """Manager personalizado para User con email como identificador primario."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_("El email es obligatorio"))
        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        logger.info(f"Nuevo usuario creado: {email} | Rol: {extra_fields.get('role', 'N/A')}")
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "ADMIN")
        extra_fields.setdefault("is_active", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser debe tener is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser debe tener is_superuser=True."))
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Usuario del sistema Family Health MF.
    Implementa RBAC con 3 roles y protección de datos.
    """

    ROLE_ADMIN = "ADMIN"
    ROLE_EMPLOYEE = "EMPLOYEE"
    ROLE_CLIENT = "CLIENT"
    ROLE_CHOICES = (
        (ROLE_ADMIN, _("Administrador")),
        (ROLE_EMPLOYEE, _("Empleado / Recepción")),
        (ROLE_CLIENT, _("Cliente")),
    )

    DOC_TYPE_CC = "CC"
    DOC_TYPE_CE = "CE"
    DOC_TYPE_PA = "PA"
    DOC_TYPE_NIT = "NIT"
    DOC_TYPE_CHOICES = (
        (DOC_TYPE_CC, "Cédula de Ciudadanía"),
        (DOC_TYPE_CE, "Cédula de Extranjería"),
        (DOC_TYPE_PA, "Pasaporte"),
        (DOC_TYPE_NIT, "NIT"),
    )

    GENDER_M = "M"
    GENDER_F = "F"
    GENDER_O = "O"
    GENDER_CHOICES = (
        (GENDER_M, "Masculino"),
        (GENDER_F, "Femenino"),
        (GENDER_O, "Otro"),
    )

    # --- Credenciales ---
    email = models.EmailField(
        verbose_name=_("Correo Electrónico"),
        unique=True,
        validators=[EmailValidator(message=_("Email inválido"))],
        error_messages={"unique": _("Este email ya se encuentra registrado")},
    )
    username = models.CharField(
        verbose_name=_("Nombre de usuario"),
        max_length=50,
        unique=True,
        db_index=True,
        validators=[
            RegexValidator(
                regex=r"^[a-zA-Z0-9_.+-]+$",
                message=_("Solo letras, números, ., _ , + y - permitidos"),
                code="invalid_username",
            )
        ],
    )

    # --- Roles y estado ---
    role = models.CharField(
        verbose_name=_("Rol del sistema"),
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_CLIENT,
        db_index=True,
    )
    is_active = models.BooleanField(
        verbose_name=_("Activo"),
        default=True,
        help_text=_("Inactivo = no puede iniciar sesión (Ley 1581 - desautorización)"),
    )
    is_staff = models.BooleanField(
        verbose_name=_("Staff"),
        default=False,
        help_text=_("Puede acceder al panel administrativo Django"),
    )
    is_verified = models.BooleanField(
        verbose_name=_("Email Verificado"),
        default=False,
        help_text=_("El usuario validó su correo"),
    )
    accepted_privacy_policy = models.BooleanField(
        verbose_name=_("Aceptó Política Privacidad (Ley 1581)"),
        default=False,
        help_text=_("Requerido por Ley 1581/2012 Protección de Datos"),
    )
    accepted_terms = models.BooleanField(
        verbose_name=_("Aceptó Términos y Condiciones"),
        default=False,
    )

    # --- Datos personales ---
    first_name = models.CharField(verbose_name=_("Nombres"), max_length=80)
    last_name = models.CharField(verbose_name=_("Apellidos"), max_length=80)
    document_type = models.CharField(
        verbose_name=_("Tipo Documento"),
        max_length=5,
        choices=DOC_TYPE_CHOICES,
        default=DOC_TYPE_CC,
    )
    document_number = models.CharField(
        verbose_name=_("Número Documento"),
        max_length=20,
        db_index=True,
        unique=True,
        null=True,
        blank=True,
    )
    gender = models.CharField(
        verbose_name=_("Género"),
        max_length=2,
        choices=GENDER_CHOICES,
        default=GENDER_O,
    )
    birth_date = models.DateField(
        verbose_name=_("Fecha Nacimiento"),
        null=True,
        blank=True,
    )
    phone = PhoneNumberField(
        verbose_name=_("Teléfono / Celular"),
        region="CO",
        null=True,
        blank=True,
    )
    address = models.TextField(
        verbose_name=_("Dirección Residencia"),
        max_length=255,
        null=True,
        blank=True,
    )
    city = models.CharField(
        verbose_name=_("Ciudad"),
        max_length=80,
        default="Maicao",
    )
    department = models.CharField(
        verbose_name=_("Departamento"),
        max_length=80,
        default="La Guajira",
    )
    emergency_contact = models.CharField(
        verbose_name=_("Contacto Emergencia (Nombre)"),
        max_length=100,
        null=True,
        blank=True,
    )
    emergency_phone = PhoneNumberField(
        verbose_name=_("Teléfono Emergencia"),
        region="CO",
        null=True,
        blank=True,
    )

    # --- Datos membresía / perfil cliente ---
    membership_type = models.CharField(
        verbose_name=_("Tipo Membresía"),
        max_length=50,
        null=True,
        blank=True,
        help_text=_("Ej: Básico, Premium, Oro"),
    )
    membership_expires_at = models.DateTimeField(
        verbose_name=_("Vencimiento Membresía"),
        null=True,
        blank=True,
    )

    # --- Auditoría ---
    last_login_ip = models.GenericIPAddressField(
        verbose_name=_("IP Último Login"),
        unpack_ipv4=True,
        null=True,
        blank=True,
    )
    last_login_user_agent = models.TextField(
        verbose_name=_("User-Agent Último Login"),
        null=True,
        blank=True,
    )
    privacy_policy_accepted_at = models.DateTimeField(
        verbose_name=_("Fecha Aceptación Privacidad"),
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(
        verbose_name=_("Fecha Registro"),
        default=timezone.now,
        editable=False,
    )
    updated_at = models.DateTimeField(
        verbose_name=_("Última Actualización"),
        auto_now=True,
    )

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "first_name", "last_name"]

    class Meta:
        verbose_name = _("Usuario")
        verbose_name_plural = _("Usuarios")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["role", "is_active"]),
            models.Index(fields=["last_name", "first_name"]),
        ]
        permissions = (
            ("can_view_dashboard_admin", "Puede ver panel admin"),
            ("can_manage_users", "Puede gestionar usuarios"),
            ("can_manage_all_reservations", "Puede gestionar todas las reservas"),
            ("can_manage_refreshments", "Puede gestionar refresquería"),
            ("can_manage_rewards", "Puede gestionar recompensas"),
            ("can_manage_gym", "Puede gestionar gimnasio"),
            ("can_view_reports", "Puede ver reportes"),
        )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def role_display(self) -> str:
        return dict(self.ROLE_CHOICES).get(self.role, self.role)

    @property
    def membership_active(self) -> bool:
        if self.membership_expires_at is None:
            return True
        return self.membership_expires_at >= timezone.now()

    def __str__(self) -> str:
        return f"{self.full_name} ({self.username} - {self.role})"

    def log_audit(self, action: str, detail: str = "") -> None:
        """Registro de auditoría manual para cumplimiento Ley 1581."""
        AuditLog.objects.create(
            user=self,
            action=action,
            detail=detail,
        )


class AuditLog(models.Model):
    """
    Registro de auditoría para cumplimiento Ley 1581/2012.
    Rastrea acciones de usuarios sobre datos personales.
    """

    ACTION_LOGIN = "LOGIN"
    ACTION_LOGIN_FAIL = "LOGIN_FAIL"
    ACTION_LOGOUT = "LOGOUT"
    ACTION_PROFILE_VIEW = "PROFILE_VIEW"
    ACTION_PROFILE_EDIT = "PROFILE_EDIT"
    ACTION_DATA_EXPORT = "DATA_EXPORT"
    ACTION_DATA_DELETE = "DATA_DELETE"
    ACTION_CHOICES = (
        (ACTION_LOGIN, "Inicio de Sesión"),
        (ACTION_LOGIN_FAIL, "Login Fallido"),
        (ACTION_LOGOUT, "Cierre de Sesión"),
        (ACTION_PROFILE_VIEW, "Visualización Perfil"),
        (ACTION_PROFILE_EDIT, "Edición Perfil"),
        (ACTION_DATA_EXPORT, "Exportación Datos"),
        (ACTION_DATA_DELETE, "Eliminación Datos"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="audit_logs",
        verbose_name=_("Usuario"),
    )
    action = models.CharField(
        verbose_name=_("Acción"),
        max_length=30,
        choices=ACTION_CHOICES,
        db_index=True,
    )
    detail = models.TextField(
        verbose_name=_("Detalle"),
        null=True,
        blank=True,
    )
    ip_address = models.GenericIPAddressField(
        verbose_name=_("IP"),
        unpack_ipv4=True,
        null=True,
        blank=True,
    )
    user_agent = models.TextField(
        verbose_name=_("User-Agent"),
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(
        verbose_name=_("Fecha/Hora"),
        default=timezone.now,
        db_index=True,
    )

    class Meta:
        verbose_name = _("Registro Auditoría")
        verbose_name_plural = _("Registros Auditoría")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "action", "created_at"]),
        ]

    def __str__(self):
        return f"[{self.created_at}] {self.user.username} - {self.action}"
