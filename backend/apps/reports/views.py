"""
Reports Serializers & Views
Notificaciones + Panel Admin reportes básicos
"""
from datetime import timedelta
from decimal import Decimal

from django.db.models import Avg, Count, F, Q, Sum, Value
from django.db.models.functions import Coalesce, TruncDate, TruncMonth
from django.utils import timezone
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.authentication.models import User
from apps.authentication.permissions import IsAdmin, IsAdminOrEmployee
from apps.reservations.models import Reservation
from apps.refreshments.models import Order
from apps.rewards.models import LoyaltyProfile, PointsTransaction
from apps.gym.models import WorkoutLog
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source="get_type_display", read_only=True)

    class Meta:
        model = Notification
        fields = "__all__"
        read_only_fields = ("is_read", "read_at", "created_at")


class NotificationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all().order_by("-created_at")

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user=self.request.user)

    def perform_create(self, serializer):
        if self.request.user.role != User.ROLE_CLIENT:
            return super().perform_create(serializer)
        raise serializers.ValidationError("No puede crear notificaciones")

    @action(detail=False, methods=["post"], url_path="mark-all-read")
    def mark_all_read(self, request):
        updated = Notification.objects.filter(
            user=request.user, is_read=False
        ).update(is_read=True, read_at=timezone.now())
        return Response({"marked": updated})

    @action(detail=False, methods=["get"], url_path="unread")
    def unread(self, request):
        qs = self.get_queryset().filter(is_read=False)
        return Response(NotificationSerializer(qs, many=True).data)


# ======= REPORTES =======

class DashboardAdminSerializer(serializers.Serializer):
    """Agregados para panel admin."""
    users_total = serializers.IntegerField()
    total_users = serializers.IntegerField(required=False)
    spaces_total = serializers.IntegerField(required=False)
    clients_total = serializers.IntegerField()
    employees_total = serializers.IntegerField()
    new_clients_last_30_days = serializers.IntegerField()
    reservations_total = serializers.IntegerField()
    reservations_today = serializers.IntegerField()
    reservations_confirmed = serializers.IntegerField()
    reservations_pending = serializers.IntegerField()
    reservations_cancelled = serializers.IntegerField()
    occupancy_rate_last_7 = serializers.FloatField()
    orders_total = serializers.IntegerField()
    orders_today = serializers.IntegerField()
    orders_revenue_month = serializers.DecimalField(max_digits=16, decimal_places=2)
    reservations_revenue_month = serializers.DecimalField(max_digits=16, decimal_places=2)
    total_revenue_month = serializers.DecimalField(max_digits=16, decimal_places=2)
    points_distributed = serializers.IntegerField()
    points_redeemed = serializers.IntegerField()
    active_tiers = serializers.ListField()
    gym_logs_last_30 = serializers.IntegerField()


@api_view(["GET"])
@permission_classes([IsAuthenticated & (IsAdmin | IsAdminOrEmployee)])
def dashboard_summary(request):
    """Resumen operativo general (Dashboard Panel Admin)."""
    now = timezone.now()
    today = now.date()
    first_of_month = today.replace(day=1)
    month_ago = now - timedelta(days=30)
    week_ago = now - timedelta(days=7)

    users_qs = User.objects.filter(is_active=True)
    users_total = users_qs.count()
    clients_total = users_qs.filter(role=User.ROLE_CLIENT).count()
    employees_total = users_qs.filter(role=User.ROLE_EMPLOYEE).count()
    new_clients_last_30 = users_qs.filter(
        role=User.ROLE_CLIENT, created_at__gte=month_ago
    ).count()

    res_total = Reservation.objects.count()
    res_today = Reservation.objects.filter(start_time__date=today).count()
    res_confirmed = Reservation.objects.filter(
        status=Reservation.STATUS_CONFIRMED
    ).count()
    res_pending = Reservation.objects.filter(
        status=Reservation.STATUS_PENDING
    ).count()
    res_cancelled = Reservation.objects.filter(
        status=Reservation.STATUS_CANCELLED
    ).count()

    # Ocupación 7 días: ratio reservas confirmadas/completadas sobre espacios * días
    res_last_7 = Reservation.objects.filter(
        status__in=[Reservation.STATUS_CONFIRMED, Reservation.STATUS_COMPLETED],
        start_time__gte=week_ago,
    ).aggregate(total=Sum("total_minutes"))["total"] or 0
    capacity = 10080  # 7 días * 1440 minutos * 1 espacio base normalizado
    occupancy = round(float(res_last_7) / capacity * 100, 2) if capacity > 0 else 0.0

    orders_total = Order.objects.count()
    orders_today = Order.objects.filter(created_at__date=today).count()
    orders_rev = Order.objects.filter(
        created_at__gte=first_of_month, status=Order.STATUS_PAID
    ).aggregate(sum=Coalesce(Sum("total_amount"), Value(Decimal(0))))["sum"]
    reservations_rev = Reservation.objects.filter(
        start_time__gte=first_of_month, payment_status=Reservation.PAYMENT_STATUS_PAID
    ).aggregate(sum=Coalesce(Sum("total_amount"), Value(Decimal(0))))["sum"]

    pts_dist = PointsTransaction.objects.filter(
        transaction_type=PointsTransaction.TYPE_EARN
    ).aggregate(sum=Sum("amount"))["sum"] or 0
    pts_red = abs(PointsTransaction.objects.filter(
        transaction_type=PointsTransaction.TYPE_REDEEM
    ).aggregate(sum=Sum("amount"))["sum"] or 0)

    from apps.rewards.models import LoyaltyTier
    tiers = []
    for t in LoyaltyTier.objects.filter(is_active=True):
        count = LoyaltyProfile.objects.filter(tier=t).count()
        tiers.append({"id": t.id, "name": t.name, "color": t.color, "users": count})

    gym_logs_30 = WorkoutLog.objects.filter(session_date__gte=month_ago).count()

    from apps.reservations.models import Space
    spaces_total = Space.objects.count()

    return Response(DashboardAdminSerializer({
        "users_total": users_total,
        "total_users": users_total,
        "spaces_total": spaces_total,
        "clients_total": clients_total,
        "employees_total": employees_total,
        "new_clients_last_30_days": new_clients_last_30,
        "reservations_total": res_total,
        "reservations_today": res_today,
        "reservations_confirmed": res_confirmed,
        "reservations_pending": res_pending,
        "reservations_cancelled": res_cancelled,
        "occupancy_rate_last_7": min(occupancy, 100.0),
        "orders_total": orders_total,
        "orders_today": orders_today,
        "orders_revenue_month": orders_rev,
        "reservations_revenue_month": reservations_rev,
        "total_revenue_month": orders_rev + reservations_rev,
        "points_distributed": pts_dist,
        "points_redeemed": pts_red,
        "active_tiers": tiers,
        "gym_logs_last_30": gym_logs_30,
    }).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated & (IsAdmin | IsAdminOrEmployee)])
def reservations_by_date(request):
    """Serie de reservas por fecha (últimos N días, default 30)."""
    days = int(request.query_params.get("days", 30))
    start = timezone.localdate() - timedelta(days=days)
    data = (
        Reservation.objects.filter(start_time__date__gte=start)
        .annotate(date=TruncDate("start_time"))
        .values("date")
        .annotate(total=Count("id"),
                  confirmed=Count("id", filter=Q(status=Reservation.STATUS_CONFIRMED)),
                  cancelled=Count("id", filter=Q(status=Reservation.STATUS_CANCELLED)),
                  )
        .order_by("date")
    )
    return Response(list(data))


@api_view(["GET"])
@permission_classes([IsAuthenticated & (IsAdmin | IsAdminOrEmployee)])
def revenue_by_month(request):
    months = int(request.query_params.get("months", 6))
    first = timezone.localdate().replace(day=1)
    while months > 1:
        if first.month == 1:
            first = first.replace(year=first.year - 1, month=12)
        else:
            first = first.replace(month=first.month - 1)
        months -= 1
    orders = (
        Order.objects.filter(status=Order.STATUS_PAID, created_at__gte=first)
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(orders=Count("id"),
                  revenue=Coalesce(Sum("total_amount"), Value(Decimal(0))))
        .order_by("month")
    )
    reservations = (
        Reservation.objects.filter(
            payment_status=Reservation.PAYMENT_STATUS_PAID,
            start_time__gte=first,
        )
        .annotate(month=TruncMonth("start_time"))
        .values("month")
        .annotate(reservations=Count("id"),
                  revenue=Coalesce(Sum("total_amount"), Value(Decimal(0))))
        .order_by("month")
    )
    return Response({"orders": list(orders), "reservations": list(reservations)})


@api_view(["GET"])
@permission_classes([IsAuthenticated & (IsAdmin | IsAdminOrEmployee)])
def top_clients(request):
    n = int(request.query_params.get("n", 10))
    data = (
        User.objects.filter(role=User.ROLE_CLIENT, is_active=True)
        .annotate(reservations_count=Count("reservations", distinct=True),
                  orders_count=Count("orders", distinct=True),
                  total_spent=Coalesce(
                      Sum("reservations__total_amount",
                          filter=Q(reservations__payment_status=Reservation.PAYMENT_STATUS_PAID))
                      + Sum("orders__total_amount",
                            filter=Q(orders__status=Order.STATUS_PAID)),
                      Value(Decimal(0))
                  ))
        .values("id", "username", "first_name", "last_name", "membership_type",
                "reservations_count", "orders_count", "total_spent")
        .order_by("-total_spent")[:n]
    )
    return Response(list(data))


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    return Response({
        "status": "ok",
        "timestamp": timezone.now().isoformat(),
        "version": "1.0.0",
        "app": "Club Family Health MF API",
        "club_name": "Club Family Health",
        "club": {
            "name": "Club Family Health",
            "nit": "32739028-5",
            "city": "Maicao, La Guajira",
        },
        "database": "ok",
    })
