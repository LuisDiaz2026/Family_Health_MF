"""
Rewards Models - Club Family Health
Sistema básico de fidelización: puntos, niveles, beneficios.
"""
import logging
from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.authentication.models import User

logger = logging.getLogger(__name__)


class RewardRule(models.Model):
    """
    Reglas de fidelización: cuántos puntos por tipo de acción.
    """
    ACTION_RESERVATION = "RESERVATION"
    ACTION_REFRESHMENT = "REFRESHMENT"
    ACTION_REFERRAL = "REFERRAL"
    ACTION_BIRTHDAY = "BIRTHDAY"
    ACTION_MEMBERSHIP = "MEMBERSHIP"
    ACTION_CHOICES = (
        (ACTION_RESERVATION, "Reserva Completada"),
        (ACTION_REFRESHMENT, "Pedido Refresquería Pagado"),
        (ACTION_REFERRAL, "Referido Nuevo Miembro"),
        (ACTION_BIRTHDAY, "Regalo Cumpleaños"),
        (ACTION_MEMBERSHIP, "Renovación Membresía"),
    )

    action_type = models.CharField(
        verbose_name=_("Tipo de Acción"),
        max_length=30,
        choices=ACTION_CHOICES,
        unique=True,
        db_index=True,
    )
    points_amount = models.PositiveIntegerField(
        verbose_name=_("Puntos Base"),
        default=10,
    )
    points_per_currency = models.DecimalField(
        verbose_name=_("Puntos por cada $1000 COP"),
        max_digits=8,
        decimal_places=2,
        default=0,
        help_text=_("Opcional: puntos adicionales por monto gastado"),
        validators=[MinValueValidator(0)],
    )
    is_active = models.BooleanField(verbose_name=_("Activo"), default=True)
    description = models.TextField(
        verbose_name=_("Descripción Regla"),
        max_length=250,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Regla de Fidelización")
        verbose_name_plural = _("Reglas de Fidelización")
        ordering = ["action_type"]

    def __str__(self):
        return f"{self.action_type}: {self.points_amount} pts"

    @classmethod
    def calculate_points(cls, action_type: str, amount: Decimal = Decimal("0")) -> int:
        try:
            rule = cls.objects.get(action_type=action_type, is_active=True)
        except cls.DoesNotExist:
            return 0
        points = rule.points_amount
        if rule.points_per_currency > 0 and amount > 0:
            points += int((amount / Decimal("1000")) * rule.points_per_currency)
        return points


class LoyaltyTier(models.Model):
    """Niveles de fidelización (Bronce, Plata, Oro, etc.)"""
    name = models.CharField(
        verbose_name=_("Nombre Nivel"),
        max_length=50,
        unique=True,
    )
    min_points = models.PositiveIntegerField(
        verbose_name=_("Puntos Mínimos"),
        unique=True,
    )
    color = models.CharField(
        verbose_name=_("Color (hex)"),
        max_length=10,
        default="#808080",
    )
    discount_percent = models.DecimalField(
        verbose_name=_("% Descuento Base"),
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(50)],
    )
    benefits = models.TextField(
        verbose_name=_("Beneficios"),
        max_length=500,
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(verbose_name=_("Activo"), default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _("Nivel Fidelización")
        verbose_name_plural = _("Niveles Fidelización")
        ordering = ["min_points"]

    def __str__(self):
        return f"{self.name} (≥ {self.min_points} pts)"


class PointsTransaction(models.Model):
    """
    Movimiento de puntos (acumulación o redención).
    """
    TYPE_EARN = "EARN"
    TYPE_REDEEM = "REDEEM"
    TYPE_EXPIRE = "EXPIRE"
    TYPE_ADJUST = "ADJUST"
    TYPE_CHOICES = (
        (TYPE_EARN, "Ganados"),
        (TYPE_REDEEM, "Canjeados"),
        (TYPE_EXPIRE, "Expirados"),
        (TYPE_ADJUST, "Ajuste Manual"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="points_transactions",
        verbose_name=_("Usuario"),
    )
    transaction_type = models.CharField(
        verbose_name=_("Tipo Movimiento"),
        max_length=10,
        choices=TYPE_CHOICES,
        db_index=True,
    )
    amount = models.IntegerField(
        verbose_name=_("Puntos (positivo=ganados, negativo=canjeados)"),
    )
    balance_after = models.IntegerField(
        verbose_name=_("Saldo después"),
        editable=False,
    )
    rule = models.ForeignKey(
        RewardRule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Regla Aplicada"),
    )
    reservation = models.ForeignKey(
        "reservations.Reservation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="points_tx",
        verbose_name=_("Reserva asociada"),
    )
    order = models.ForeignKey(
        "refreshments.Order",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="points_tx",
        verbose_name=_("Pedido asociado"),
    )
    reward = models.ForeignKey(
        "RewardCatalogItem",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="redeemed_tx",
        verbose_name=_("Premio canjeado"),
    )
    description = models.CharField(
        verbose_name=_("Descripción"),
        max_length=250,
        null=True,
        blank=True,
    )
    performed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="points_performed",
        verbose_name=_("Registrado por"),
    )
    expires_at = models.DateTimeField(
        verbose_name=_("Fecha Expiración (solo ganados)"),
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        verbose_name = _("Transacción Puntos")
        verbose_name_plural = _("Transacciones Puntos")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "transaction_type", "created_at"]),
        ]

    def __str__(self):
        return f"{self.user.username} | {self.transaction_type} | {self.amount:+d}"

    def save(self, *args, **kwargs):
        self.balance_after = self.user.loyalty_profile.current_points + self.amount
        super().save(*args, **kwargs)
        profile = self.user.loyalty_profile
        profile.current_points = self.balance_after
        profile._update_tier()
        profile.save(update_fields=["current_points", "tier", "updated_at"])


class LoyaltyProfile(models.Model):
    """
    Perfil de fidelización por usuario.
    Se crea automáticamente via signal cuando un cliente nace.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="loyalty_profile",
        verbose_name=_("Usuario"),
        limit_choices_to={"role": User.ROLE_CLIENT},
    )
    tier = models.ForeignKey(
        LoyaltyTier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Nivel Actual"),
    )
    current_points = models.IntegerField(
        verbose_name=_("Puntos Actuales"),
        default=0,
    )
    lifetime_points = models.IntegerField(
        verbose_name=_("Puntos Históricos Acumulados"),
        default=0,
    )
    redeemed_points = models.IntegerField(
        verbose_name=_("Puntos Canjeados Históricos"),
        default=0,
    )
    referrals_count = models.PositiveIntegerField(
        verbose_name=_("Amigos Referidos"),
        default=0,
    )
    anniversary_date = models.DateField(
        verbose_name=_("Aniversario (Fecha Registro Club)"),
        null=True,
        blank=True,
    )
    referred_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="referrals",
        verbose_name=_("Referido por"),
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Perfil Fidelización")
        verbose_name_plural = _("Perfiles Fidelización")
        ordering = ["-current_points"]

    def __str__(self):
        return f"Fidelidad {self.user.username}: {self.current_points} pts"

    def save(self, *args, **kwargs):
        if self.tier_id is None or "current_points" in kwargs.get("update_fields", ["current_points"]):
            self._update_tier()
        super().save(*args, **kwargs)

    def _update_tier(self):
        tiers = LoyaltyTier.objects.filter(is_active=True).order_by("-min_points")
        for tier in tiers:
            if self.current_points >= tier.min_points:
                self.tier = tier
                return
        self.tier = tiers.last() if tiers.exists() else None


class RewardCatalogItem(models.Model):
    """Catálogo de premios disponibles para canje de puntos."""
    name = models.CharField(
        verbose_name=_("Nombre Premio"),
        max_length=150,
    )
    description = models.TextField(
        verbose_name=_("Descripción"),
        max_length=500,
        null=True,
        blank=True,
    )
    points_required = models.PositiveIntegerField(
        verbose_name=_("Puntos Requeridos"),
        db_index=True,
    )
    category = models.CharField(
        verbose_name=_("Categoría"),
        max_length=80,
        null=True,
        blank=True,
        default="General",
    )
    stock = models.PositiveIntegerField(
        verbose_name=_("Unidades Disponibles"),
        default=0,
        help_text=_("0 = stock ilimitado (premio virtual)"),
    )
    is_active = models.BooleanField(verbose_name=_("Activo"), default=True)
    image = models.ImageField(
        upload_to="rewards/%Y/%m/",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Premio Catálogo")
        verbose_name_plural = _("Premios Catálogo")
        ordering = ["points_required", "name"]

    def __str__(self):
        return f"{self.name} - {self.points_required} pts"
