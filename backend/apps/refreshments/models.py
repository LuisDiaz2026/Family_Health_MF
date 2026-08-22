"""
Refreshments Models - Club Family Health
Pedidos de refresquería (productos, categorías, pedidos y detalle)
Pago 100% presencial (sin integración pasarela)
"""
import logging

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.authentication.models import User

logger = logging.getLogger(__name__)


class ProductCategory(models.Model):
    """Categorías de productos (bebidas, snacks, comidas, proteínas, etc.)"""
    name = models.CharField(
        verbose_name=_("Nombre Categoría"),
        max_length=80,
        unique=True,
        db_index=True,
    )
    description = models.TextField(
        verbose_name=_("Descripción"),
        max_length=250,
        null=True,
        blank=True,
    )
    icon = models.CharField(
        verbose_name=_("Icono"),
        max_length=20,
        default="🥤",
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(verbose_name=_("Activo"), default=True)
    order = models.PositiveIntegerField(verbose_name=_("Orden visual"), default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Categoría Producto")
        verbose_name_plural = _("Categorías Productos")
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    """Producto del inventario de la refresquería."""

    UNIT_UNIT = "UNIT"
    UNIT_LITER = "LITER"
    UNIT_KILO = "KILO"
    UNIT_ML = "ML"
    UNIT_CHOICES = (
        (UNIT_UNIT, "Unidad"),
        (UNIT_LITER, "Litro"),
        (UNIT_KILO, "Kilo"),
        (UNIT_ML, "Mililitro"),
    )

    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name=_("Categoría"),
    )
    name = models.CharField(
        verbose_name=_("Nombre Producto"),
        max_length=120,
        db_index=True,
    )
    sku = models.CharField(
        verbose_name=_("Código SKU"),
        max_length=50,
        unique=True,
        db_index=True,
        null=True,
        blank=True,
    )
    description = models.TextField(
        verbose_name=_("Descripción"),
        max_length=500,
        null=True,
        blank=True,
    )
    unit_measure = models.CharField(
        verbose_name=_("Unidad Medida"),
        max_length=10,
        choices=UNIT_CHOICES,
        default=UNIT_UNIT,
    )
    unit_content = models.DecimalField(
        verbose_name=_("Contenido por unidad"),
        max_digits=10,
        decimal_places=2,
        default=1,
        help_text=_("Ej: 330 para gaseosa 330ml"),
    )
    price = models.DecimalField(
        verbose_name=_("Precio Venta (COP)"),
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    cost = models.DecimalField(
        verbose_name=_("Costo Unitario (COP)"),
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    stock = models.PositiveIntegerField(
        verbose_name=_("Stock Actual"),
        default=0,
    )
    min_stock = models.PositiveIntegerField(
        verbose_name=_("Stock Mínimo"),
        default=5,
        help_text=_("Alerta cuando baja de este valor"),
    )
    is_available = models.BooleanField(
        verbose_name=_("Disponible para pedidos"),
        default=True,
        db_index=True,
    )
    image = models.ImageField(
        upload_to="products/%Y/%m/",
        null=True,
        blank=True,
        verbose_name=_("Foto Producto"),
    )
    allergens = models.TextField(
        verbose_name=_("Alérgenos / Advertencias"),
        max_length=300,
        null=True,
        blank=True,
    )
    calories = models.PositiveIntegerField(
        verbose_name=_("Calorías (kcal)"),
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Producto")
        verbose_name_plural = _("Productos")
        ordering = ["category__name", "name"]
        unique_together = ("category", "name")

    def __str__(self):
        return f"{self.name} (${self.price:,.0f})"

    @property
    def stock_low(self) -> bool:
        return self.stock <= self.min_stock


class Order(models.Model):
    """
    Pedido de refresquería.
    Pago 100% presencial, no hay pasarela de pago (fuera de alcance).
    """

    STATUS_PENDING = "PENDING"
    STATUS_PREPARING = "PREPARING"
    STATUS_READY = "READY"
    STATUS_DELIVERED = "DELIVERED"
    STATUS_PAID = "PAID"
    STATUS_CANCELLED = "CANCELLED"
    STATUS_CHOICES = (
        (STATUS_PENDING, "Pendiente (Sin pagar)"),
        (STATUS_PREPARING, "Preparando"),
        (STATUS_READY, "Listo para Entregar"),
        (STATUS_DELIVERED, "Entregado"),
        (STATUS_PAID, "Pagado y Completado"),
        (STATUS_CANCELLED, "Cancelado"),
    )

    PAYMENT_CASH = "CASH"
    PAYMENT_CARD_PHYSICAL = "CARD"
    PAYMENT_TRANSFER = "TRANSFER"
    PAYMENT_MEMBERSHIP = "MEMBERSHIP"
    PAYMENT_METHOD_CHOICES = (
        (PAYMENT_CASH, "Efectivo"),
        (PAYMENT_CARD_PHYSICAL, "Tarjeta (Presencial)"),
        (PAYMENT_TRANSFER, "Transferencia Bancaria"),
        (PAYMENT_MEMBERSHIP, "Descuento Membresía"),
    )

    client = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="orders",
        verbose_name=_("Cliente"),
        limit_choices_to={"role": User.ROLE_CLIENT, "is_active": True},
    )
    taken_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="orders_taken",
        verbose_name=_("Tomado por (Empleado/Admin)"),
        limit_choices_to={"role__in": [User.ROLE_ADMIN, User.ROLE_EMPLOYEE],
                           "is_active": True},
        null=True,
        blank=True,
    )
    reservation = models.ForeignKey(
        "reservations.Reservation",
        on_delete=models.SET_NULL,
        related_name="refreshment_orders",
        verbose_name=_("Reserva asociada (opcional)"),
        null=True,
        blank=True,
    )
    order_number = models.CharField(
        verbose_name=_("Número Pedido"),
        max_length=30,
        unique=True,
        db_index=True,
        editable=False,
    )
    status = models.CharField(
        verbose_name=_("Estado Pedido"),
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        db_index=True,
    )
    payment_method = models.CharField(
        verbose_name=_("Método Pago"),
        max_length=30,
        choices=PAYMENT_METHOD_CHOICES,
        null=True,
        blank=True,
    )
    subtotal = models.DecimalField(
        verbose_name=_("Subtotal"),
        max_digits=14,
        decimal_places=2,
        default=0,
    )
    tax_percent = models.DecimalField(
        verbose_name=_("% Impuesto"),
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    tax_amount = models.DecimalField(
        verbose_name=_("Valor Impuesto"),
        max_digits=14,
        decimal_places=2,
        default=0,
    )
    discount_percent = models.DecimalField(
        verbose_name=_("% Descuento"),
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    discount_amount = models.DecimalField(
        verbose_name=_("Valor Descuento"),
        max_digits=14,
        decimal_places=2,
        default=0,
    )
    total_amount = models.DecimalField(
        verbose_name=_("Total a Pagar"),
        max_digits=14,
        decimal_places=2,
        default=0,
        editable=False,
    )
    paid_amount = models.DecimalField(
        verbose_name=_("Monto Pagado"),
        max_digits=14,
        decimal_places=2,
        default=0,
    )
    points_used = models.PositiveIntegerField(
        verbose_name=_("Puntos Fidelización Utilizados"),
        default=0,
    )
    notes = models.TextField(
        verbose_name=_("Notas Pedido"),
        max_length=500,
        null=True,
        blank=True,
    )
    pickup_window_start = models.DateTimeField(
        verbose_name=_("Horario Recogida Inicio"),
        null=True,
        blank=True,
    )
    pickup_window_end = models.DateTimeField(
        verbose_name=_("Horario Recogida Fin"),
        null=True,
        blank=True,
    )
    delivered_at = models.DateTimeField(
        verbose_name=_("Fecha Entregado"),
        null=True,
        blank=True,
    )
    paid_at = models.DateTimeField(
        verbose_name=_("Fecha Pago"),
        null=True,
        blank=True,
    )
    paid_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="orders_paid",
        verbose_name=_("Pago Registrado por"),
        null=True,
        blank=True,
    )
    cancelled_at = models.DateTimeField(
        verbose_name=_("Fecha Cancelación"),
        null=True,
        blank=True,
    )
    cancelled_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="orders_cancelled",
        null=True,
        blank=True,
    )
    cancellation_reason = models.TextField(
        verbose_name=_("Motivo Cancelación"),
        max_length=300,
        null=True,
        blank=True,
    )
    points_awarded = models.PositiveIntegerField(
        verbose_name=_("Puntos Fidelización Otorgados"),
        default=0,
    )
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Pedido Refresquería")
        verbose_name_plural = _("Pedidos Refresquería")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["client", "status"]),
            models.Index(fields=["status", "created_at"]),
        ]

    def __str__(self):
        return f"Pedido {self.order_number} | {self.client.username} | {self.status}"

    def save(self, *args, **kwargs):
        if not self.order_number and not self.pk:
            last = Order.objects.order_by("-id").first()
            next_id = (last.id + 1) if last else 1
            self.order_number = (
                f"PED-{timezone.now().strftime('%Y%m%d')}-{next_id:05d}"
            )
        super().save(*args, **kwargs)

    def recalculate_totals(self):
        """Recalcula subtotal, impuestos, descuentos y total."""
        items = self.items.all()
        subtotal = sum(float(i.line_total) for i in items)
        self.subtotal = round(subtotal, 2)
        self.tax_amount = round(subtotal * float(self.tax_percent) / 100, 2)
        self.discount_amount = round(
            (subtotal + float(self.tax_amount)) * float(self.discount_percent) / 100, 2
        )
        self.total_amount = round(
            subtotal + float(self.tax_amount) - float(self.discount_amount), 2
        )
        self.save(update_fields=["subtotal", "tax_amount", "discount_amount",
                                 "total_amount"])


class OrderItem(models.Model):
    """Línea de detalle de un pedido."""
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("Pedido"),
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="order_items",
        verbose_name=_("Producto"),
    )
    quantity = models.PositiveIntegerField(
        verbose_name=_("Cantidad"),
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(999)],
    )
    unit_price_at_purchase = models.DecimalField(
        verbose_name=_("Precio Unitario en el momento"),
        max_digits=12,
        decimal_places=2,
        editable=False,
    )
    line_total = models.DecimalField(
        verbose_name=_("Total Línea"),
        max_digits=14,
        decimal_places=2,
        editable=False,
    )
    notes = models.CharField(
        verbose_name=_("Nota item"),
        max_length=200,
        null=True,
        blank=True,
        help_text=_("Ej: Sin azúcar, sin hielo, etc."),
    )

    class Meta:
        verbose_name = _("Item Pedido")
        verbose_name_plural = _("Items Pedido")
        ordering = ["order", "id"]
        unique_together = ("order", "product")

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    @transaction.atomic
    def save(self, *args, **kwargs):
        if not self.unit_price_at_purchase:
            self.unit_price_at_purchase = self.product.price
        self.line_total = round(
            float(self.unit_price_at_purchase) * int(self.quantity), 2
        )
        if self.pk is None:
            if self.product.stock < self.quantity:
                raise ValueError(
                    f"Stock insuficiente para {self.product.name}: "
                    f"disponible {self.product.stock}, solicitado {self.quantity}"
                )
            self.product.stock = models.F("stock") - self.quantity
            self.product.save(update_fields=["stock"])
        super().save(*args, **kwargs)
        self.order.recalculate_totals()
