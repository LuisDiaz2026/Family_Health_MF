"""
Reservations Models - Club Family Health
- Espacios (canchas, salones, piscina, etc.)
- Reservas con validación de disponibilidad
- Horarios de operación
"""
import logging

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.authentication.models import User

logger = logging.getLogger(__name__)


class SpaceType(models.Model):
    """Tipo de espacio deportivo / recreativo."""
    name = models.CharField(
        verbose_name=_("Nombre Tipo"),
        max_length=80,
        unique=True,
        db_index=True,
    )
    description = models.TextField(
        verbose_name=_("Descripción"),
        max_length=300,
        null=True,
        blank=True,
    )
    icon = models.CharField(
        verbose_name=_("Icono (emoji/clase CSS)"),
        max_length=30,
        null=True,
        blank=True,
        default="🏟️",
    )
    is_active = models.BooleanField(
        verbose_name=_("Activo"),
        default=True,
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Tipo de Espacio")
        verbose_name_plural = _("Tipos de Espacios")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Space(models.Model):
    """
    Espacio físico del club (cancha, salón, piscina, área gym, etc.)
    """

    STATUS_ACTIVE = "ACTIVE"
    STATUS_MAINTENANCE = "MAINTENANCE"
    STATUS_INACTIVE = "INACTIVE"
    STATUS_CHOICES = (
        (STATUS_ACTIVE, "Activo / Disponible"),
        (STATUS_MAINTENANCE, "En Mantenimiento"),
        (STATUS_INACTIVE, "Inactivo"),
    )

    space_type = models.ForeignKey(
        SpaceType,
        on_delete=models.PROTECT,
        related_name="spaces",
        verbose_name=_("Tipo Espacio"),
    )
    name = models.CharField(
        verbose_name=_("Nombre Espacio"),
        max_length=100,
        db_index=True,
    )
    code = models.CharField(
        verbose_name=_("Código Interno"),
        max_length=30,
        unique=True,
        db_index=True,
        help_text=_("Ej: CANCHA-01, SALON-EVENTOS, PISCINA-01"),
    )
    description = models.TextField(
        verbose_name=_("Descripción"),
        max_length=500,
        null=True,
        blank=True,
    )
    location = models.CharField(
        verbose_name=_("Ubicación Referencia"),
        max_length=150,
        null=True,
        blank=True,
    )
    capacity = models.PositiveIntegerField(
        verbose_name=_("Capacidad Máxima Personas"),
        default=20,
        validators=[MinValueValidator(1), MaxValueValidator(5000)],
    )
    hourly_rate = models.DecimalField(
        verbose_name=_("Tarifa por Hora (COP)"),
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    requires_employee_approval = models.BooleanField(
        verbose_name=_("Requiere Aprobación Empleado"),
        default=False,
        help_text=_("Si es True, cliente reserva como pendiente y empleado aprueba"),
    )
    min_reservation_minutes = models.PositiveIntegerField(
        verbose_name=_("Mínimo Minutos Reserva"),
        default=30,
        validators=[MinValueValidator(15), MaxValueValidator(480)],
    )
    max_reservation_minutes = models.PositiveIntegerField(
        verbose_name=_("Máximo Minutos Reserva"),
        default=180,
        validators=[MinValueValidator(30), MaxValueValidator(720)],
    )
    advance_days_limit = models.PositiveIntegerField(
        verbose_name=_("Días Máximo Anticipación"),
        default=30,
        validators=[MinValueValidator(1), MaxValueValidator(365)],
    )
    cancellation_penalty_hours = models.PositiveIntegerField(
        verbose_name=_("Horas Penalidad Cancelación"),
        default=6,
        help_text=_("Antelación mínima para cancelar sin penalización"),
    )
    status = models.CharField(
        verbose_name=_("Estado"),
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
        db_index=True,
    )
    image = models.ImageField(
        upload_to="spaces/%Y/%m/",
        null=True,
        blank=True,
        verbose_name=_("Foto Espacio"),
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Espacio")
        verbose_name_plural = _("Espacios")
        ordering = ["space_type__name", "name"]
        unique_together = ("space_type", "name")

    def __str__(self):
        return f"{self.code} - {self.name}"

    def is_available_at(self, start_dt, end_dt, exclude_reservation_id=None):
        """Valida disponibilidad en rango horario."""
        if start_dt >= end_dt:
            return False
        if self.status != self.STATUS_ACTIVE:
            return False
        qs = Reservation.objects.filter(
            space=self,
            status__in=[
                Reservation.STATUS_CONFIRMED,
                Reservation.STATUS_PENDING,
            ],
            start_time__lt=end_dt,
            end_time__gt=start_dt,
        )
        if exclude_reservation_id:
            qs = qs.exclude(pk=exclude_reservation_id)
        return not qs.exists()


class OperatingHours(models.Model):
    """Horario de operación por espacio (por día de semana)."""
    WEEKDAYS = [
        (0, "Lunes"),
        (1, "Martes"),
        (2, "Miércoles"),
        (3, "Jueves"),
        (4, "Viernes"),
        (5, "Sábado"),
        (6, "Domingo"),
    ]

    space = models.ForeignKey(
        Space,
        on_delete=models.CASCADE,
        related_name="operating_hours",
        verbose_name=_("Espacio"),
    )
    weekday = models.IntegerField(
        verbose_name=_("Día Semana (0=Lun, 6=Dom)"),
        choices=WEEKDAYS,
    )
    open_time = models.TimeField(verbose_name=_("Hora Apertura"))
    close_time = models.TimeField(verbose_name=_("Hora Cierre"))
    is_closed = models.BooleanField(
        verbose_name=_("Cerrado este día"),
        default=False,
    )

    class Meta:
        verbose_name = _("Horario Operación")
        verbose_name_plural = _("Horarios Operación")
        unique_together = ("space", "weekday")
        ordering = ["space", "weekday"]

    def __str__(self):
        day_name = dict(self.WEEKDAYS)[self.weekday]
        if self.is_closed:
            return f"{self.space.code} | {day_name}: CERRADO"
        return f"{self.space.code} | {day_name}: {self.open_time}-{self.close_time}"


class Holiday(models.Model):
    """Días festivos / cierres especiales."""
    date = models.DateField(
        verbose_name=_("Fecha"),
        unique=True,
        db_index=True,
    )
    name = models.CharField(
        verbose_name=_("Nombre Festivo / Evento"),
        max_length=100,
    )
    spaces_closed = models.ManyToManyField(
        Space,
        blank=True,
        related_name="holidays",
        verbose_name=_("Espacios cerrados (vacíos = todos)"),
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _("Festivo / Cierre Especial")
        verbose_name_plural = _("Festivos / Cierres Especiales")
        ordering = ["date"]

    def __str__(self):
        return f"{self.date.isoformat()} - {self.name}"


class Reservation(models.Model):
    """
    Reserva de un espacio.
    Validación atómica de disponibilidad en save().
    """

    STATUS_PENDING = "PENDING"
    STATUS_CONFIRMED = "CONFIRMED"
    STATUS_CANCELLED = "CANCELLED"
    STATUS_COMPLETED = "COMPLETED"
    STATUS_REJECTED = "REJECTED"
    STATUS_NO_SHOW = "NO_SHOW"
    STATUS_CHOICES = (
        (STATUS_PENDING, "Pendiente Aprobación"),
        (STATUS_CONFIRMED, "Confirmada"),
        (STATUS_CANCELLED, "Cancelada"),
        (STATUS_COMPLETED, "Completada"),
        (STATUS_REJECTED, "Rechazada"),
        (STATUS_NO_SHOW, "No Asistió"),
    )

    PAYMENT_STATUS_PENDING = "PENDING"
    PAYMENT_STATUS_PAID = "PAID"
    PAYMENT_STATUS_EXEMPT = "EXEMPT"
    PAYMENT_STATUS_CHOICES = (
        (PAYMENT_STATUS_PENDING, "Pendiente de Pago"),
        (PAYMENT_STATUS_PAID, "Pagado (Presencial)"),
        (PAYMENT_STATUS_EXEMPT, "Exento"),
    )

    space = models.ForeignKey(
        Space,
        on_delete=models.PROTECT,
        related_name="reservations",
        verbose_name=_("Espacio Reservado"),
    )
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="reservations",
        verbose_name=_("Cliente"),
        limit_choices_to={"role": User.ROLE_CLIENT, "is_active": True},
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="reservations_created",
        verbose_name=_("Creado por"),
        help_text=_("Cliente que reserva o Empleado/Admin que agenda"),
        null=True,
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="reservations_approved",
        verbose_name=_("Aprobado por"),
        null=True,
        blank=True,
    )
    start_time = models.DateTimeField(
        verbose_name=_("Fecha/Hora Inicio"),
        db_index=True,
    )
    end_time = models.DateTimeField(
        verbose_name=_("Fecha/Hora Fin"),
        db_index=True,
    )
    total_minutes = models.PositiveIntegerField(
        verbose_name=_("Total Minutos"),
        editable=False,
    )
    total_amount = models.DecimalField(
        verbose_name=_("Total a Pagar (COP)"),
        max_digits=14,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    status = models.CharField(
        verbose_name=_("Estado Reserva"),
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_CONFIRMED,
        db_index=True,
    )
    payment_status = models.CharField(
        verbose_name=_("Estado Pago"),
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default=PAYMENT_STATUS_PENDING,
        db_index=True,
    )
    payment_received_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="payments_received",
        null=True,
        blank=True,
        verbose_name=_("Pago Recibido por"),
    )
    payment_received_at = models.DateTimeField(
        verbose_name=_("Fecha Pago"),
        null=True,
        blank=True,
    )
    guests_count = models.PositiveIntegerField(
        verbose_name=_("Número Invitados"),
        default=1,
        validators=[MinValueValidator(1)],
    )
    notes = models.TextField(
        verbose_name=_("Notas Adicionales"),
        max_length=500,
        null=True,
        blank=True,
    )
    cancellation_reason = models.TextField(
        verbose_name=_("Motivo Cancelación / Rechazo"),
        max_length=300,
        null=True,
        blank=True,
    )
    cancelled_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="reservations_cancelled",
        null=True,
        blank=True,
    )
    cancelled_at = models.DateTimeField(
        verbose_name=_("Fecha Cancelación"),
        null=True,
        blank=True,
    )
    completed_at = models.DateTimeField(
        verbose_name=_("Fecha Cumplimiento"),
        null=True,
        blank=True,
    )
    points_awarded = models.PositiveIntegerField(
        verbose_name=_("Puntos Fidelización Otorgados"),
        default=0,
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Reserva")
        verbose_name_plural = _("Reservas")
        ordering = ["-start_time"]
        indexes = [
            models.Index(fields=["space", "start_time", "end_time"]),
            models.Index(fields=["user", "status"]),
            models.Index(fields=["status", "start_time"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(start_time__lt=models.F("end_time")),
                name="chk_start_before_end",
            ),
            models.CheckConstraint(
                check=models.Q(guests_count__gte=1),
                name="chk_guests_min_1",
            ),
        ]

    def __str__(self):
        return (
            f"#{self.pk} | {self.space.code} | "
            f"{self.user.username} | {self.start_time.date()}"
        )

    def clean(self):
        super().clean()
        if self.start_time and self.end_time:
            self.total_minutes = int(
                (self.end_time - self.start_time).total_seconds() // 60
            )
            if self.total_minutes <= 0:
                raise ValidationError(
                    _("Hora fin debe ser posterior a hora inicio")
                )
            if self.space_id:
                min_min = self.space.min_reservation_minutes
                max_min = self.space.max_reservation_minutes
                if self.total_minutes < min_min:
                    raise ValidationError(
                        _(f"Mínimo de reserva: {min_min} minutos")
                    )
                if self.total_minutes > max_min:
                    raise ValidationError(
                        _(f"Máximo de reserva: {max_min} minutos")
                    )

    def save(self, *args, **kwargs):
        self.full_clean(exclude=["pk"])
        if self.total_amount == 0 and self.space_id:
            hours = self.total_minutes / 60.0
            self.total_amount = round(hours * float(self.space.hourly_rate), 2)
        if self.space_id:
            if not self.space.is_available_at(
                self.start_time, self.end_time, self.pk
            ):
                raise ValidationError(
                    _("Conflicto: Espacio no disponible en horario solicitado")
                )
        with transaction.atomic():
            return super().save(*args, **kwargs)

    @property
    def is_upcoming(self) -> bool:
        return self.start_time > timezone.now()

    @property
    def is_active_now(self) -> bool:
        now = timezone.now()
        return self.start_time <= now <= self.end_time

    @property
    def can_cancel(self) -> bool:
        if self.status in (self.STATUS_CANCELLED, self.STATUS_REJECTED,
                           self.STATUS_COMPLETED, self.STATUS_NO_SHOW):
            return False
        diff_hours = (self.start_time - timezone.now()).total_seconds() / 3600
        return diff_hours >= self.space.cancellation_penalty_hours
