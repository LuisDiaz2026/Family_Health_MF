"""
Reports Models - Club Family Health
Reportes operativos básicos (modelos de datos auxiliares y vistas).
No hay tablas persistentes propias; las vistas calculan data en runtime.
"""
import logging

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.authentication.models import User

logger = logging.getLogger(__name__)


class Notification(models.Model):
    """
    Notificaciones push/local al usuario (panel + móvil).
    Útil para el panel administrativo y alertas al cliente.
    """
    TYPE_INFO = "INFO"
    TYPE_SUCCESS = "SUCCESS"
    TYPE_WARNING = "WARNING"
    TYPE_DANGER = "DANGER"
    TYPE_RESERVATION = "RESERVATION"
    TYPE_ORDER = "ORDER"
    TYPE_REWARD = "REWARD"
    TYPE_CHOICES = (
        (TYPE_INFO, "Informativa"),
        (TYPE_SUCCESS, "Éxito"),
        (TYPE_WARNING, "Advertencia"),
        (TYPE_DANGER, "Urgente"),
        (TYPE_RESERVATION, "Actualización Reserva"),
        (TYPE_ORDER, "Actualización Pedido"),
        (TYPE_REWARD, "Recompensa"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name=_("Usuario Destino"),
    )
    type = models.CharField(
        max_length=20, choices=TYPE_CHOICES, default=TYPE_INFO, db_index=True
    )
    title = models.CharField(verbose_name=_("Título"), max_length=120)
    message = models.TextField(verbose_name=_("Mensaje"), max_length=500)
    related_url = models.CharField(
        verbose_name=_("Ruta Relacionada"), max_length=255, null=True, blank=True
    )
    is_read = models.BooleanField(verbose_name=_("Leída"), default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _("Notificación")
        verbose_name_plural = _("Notificaciones")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_read", "created_at"]),
        ]

    def __str__(self):
        return f"{self.user.username} | {self.type}: {self.title}"

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=["is_read", "read_at"])
