"""
Reservations Views
"""
from datetime import datetime, timedelta

from django.db.models import Q
from django.utils import timezone
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.authentication.models import User
from apps.authentication.permissions import (
    IsAdmin, IsAdminOrEmployee, IsClient,
)
from .models import (
    Holiday, OperatingHours, Reservation, Space, SpaceType,
)
from .serializers import (
    HolidaySerializer,
    OperatingHoursSerializer,
    ReservationAvailabilitySerializer,
    ReservationSerializer,
    ReservationUpdateStatusSerializer,
    SpaceSerializer,
    SpaceSummarySerializer,
    SpaceTypeSerializer,
)


class SpaceTypeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = SpaceType.objects.filter(is_active=True).order_by("name")
    serializer_class = SpaceTypeSerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            self.permission_classes = [IsAuthenticated & IsAdmin]
        return super().get_permissions()


class SpaceViewSet(viewsets.ModelViewSet):
    queryset = Space.objects.select_related("space_type").all()
    serializer_class = SpaceSerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            self.permission_classes = [IsAuthenticated & IsAdmin]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        qs = super().get_queryset()
        status = self.request.query_params.get("status")
        type_id = self.request.query_params.get("type")
        q = self.request.query_params.get("q")
        if status:
            qs = qs.filter(status=status)
        if type_id:
            qs = qs.filter(space_type_id=type_id)
        if q:
            qs = qs.filter(
                Q(name__icontains=q) | Q(code__icontains=q)
                | Q(description__icontains=q)
            )
        return qs.prefetch_related("operating_hours")

    @action(detail=True, methods=["get"], url_path="availability")
    def availability(self, request, pk=None):
        space = self.get_object()
        date_str = request.query_params.get("date", timezone.localdate().isoformat())
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response({"error": "Fecha inválida (YYYY-MM-DD)"},
                            status=status.HTTP_400_BAD_REQUEST)

        start_dt = timezone.make_aware(datetime.combine(date, datetime.min.time()))
        end_dt = start_dt + timedelta(days=1)

        occupied_slots = Reservation.objects.filter(
            space=space, status__in=[Reservation.STATUS_PENDING,
                                     Reservation.STATUS_CONFIRMED],
            start_time__lt=end_dt, end_time__gt=start_dt,
        ).values("start_time", "end_time", "id", "status")

        # Horario operativo para el día
        weekday = date.weekday()
        oh = OperatingHours.objects.filter(
            space=space, weekday=weekday
        ).first()
        holiday = Holiday.objects.filter(date=date).first()

        slots = []
        if not holiday or (holiday and space.id not in list(
            holiday.spaces_closed.values_list("id", flat=True)
        )):
            if oh and not oh.is_closed:
                t = datetime.combine(date, oh.open_time)
                close = datetime.combine(date, oh.close_time)
                t = timezone.make_aware(t)
                close = timezone.make_aware(close)
                while t < close:
                    slots.append({
                        "time": t.strftime("%H:%M"),
                        "datetime": t.isoformat(),
                    })
                    t += timedelta(minutes=30)

        return Response({
            "date": date.isoformat(),
            "weekday": weekday,
            "holiday": {
                "name": holiday.name if holiday else None,
                "space_closed": (
                    holiday is not None
                    and (not holiday.spaces_closed.exists()
                         or space.id in list(
                             holiday.spaces_closed.values_list("id", flat=True)))
                )
            } if holiday else None,
            "operating_hours": OperatingHoursSerializer(oh).data if oh else None,
            "occupied_slots": list(occupied_slots),
            "thirty_minute_slots": slots,
        })


class OperatingHoursViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated & IsAdmin]
    queryset = OperatingHours.objects.all()
    serializer_class = OperatingHoursSerializer


class HolidayViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated & IsAdmin]
    queryset = Holiday.objects.all().order_by("-date")
    serializer_class = HolidaySerializer


class ReservationViewSet(viewsets.ModelViewSet):
    serializer_class = ReservationSerializer

    def get_permissions(self):
        if self.action in ("destroy",):
            self.permission_classes = [IsAuthenticated & IsAdmin]
        elif self.action in ("list", "retrieve"):
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        qs = Reservation.objects.select_related(
            "space", "space__space_type", "user"
        ).all()
        if user.role == User.ROLE_CLIENT:
            qs = qs.filter(user=user)
        # Filtros comunes
        status = self.request.query_params.get("status")
        space_id = self.request.query_params.get("space_id")
        user_id = self.request.query_params.get("user_id")
        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")
        if status:
            qs = qs.filter(status=status)
        if space_id:
            qs = qs.filter(space_id=space_id)
        if user_id and user.role != User.ROLE_CLIENT:
            qs = qs.filter(user_id=user_id)
        if date_from:
            qs = qs.filter(start_time__date__gte=date_from)
        if date_to:
            qs = qs.filter(start_time__date__lte=date_to)
        return qs.order_by("-start_time")

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        r = self.get_object()
        if not r.can_cancel and request.user.role == User.ROLE_CLIENT:
            return Response(
                {"error": "Fuera de plazo para cancelar sin penalidad"},
                status=status.HTTP_400_BAD_REQUEST
            )
        r.status = Reservation.STATUS_CANCELLED
        r.cancellation_reason = request.data.get("reason", "Cancelado por usuario")
        r.cancelled_by = request.user
        r.cancelled_at = timezone.now()
        r.save(update_fields=["status", "cancellation_reason",
                              "cancelled_by", "cancelled_at"])
        return Response(ReservationSerializer(r, context={"request": request}).data)

    @action(detail=True, methods=["post"], url_path="approve",
            permission_classes=[IsAuthenticated & IsAdminOrEmployee])
    def approve(self, request, pk=None):
        r = self.get_object()
        r.status = Reservation.STATUS_CONFIRMED
        r.approved_by = request.user
        r.save(update_fields=["status", "approved_by"])
        return Response(ReservationSerializer(r, context={"request": request}).data)

    @action(detail=True, methods=["post"], url_path="reject",
            permission_classes=[IsAuthenticated & IsAdminOrEmployee])
    def reject(self, request, pk=None):
        r = self.get_object()
        r.status = Reservation.STATUS_REJECTED
        r.approved_by = request.user
        r.cancellation_reason = request.data.get("reason", "Rechazada por administración")
        r.save(update_fields=["status", "approved_by", "cancellation_reason"])
        return Response(ReservationSerializer(r, context={"request": request}).data)

    @action(detail=True, methods=["post"], url_path="mark-paid",
            permission_classes=[IsAuthenticated & IsAdminOrEmployee])
    def mark_paid(self, request, pk=None):
        r = self.get_object()
        r.payment_status = Reservation.PAYMENT_STATUS_PAID
        r.payment_received_by = request.user
        r.payment_received_at = timezone.now()
        r.save(update_fields=["payment_status", "payment_received_by",
                              "payment_received_at"])
        return Response(ReservationSerializer(r, context={"request": request}).data)

    @action(detail=False, methods=["get"], url_path="my-upcoming",
            permission_classes=[IsAuthenticated & IsClient])
    def my_upcoming(self, request):
        qs = self.get_queryset().filter(
            user=request.user,
            start_time__gte=timezone.now(),
            status__in=[Reservation.STATUS_PENDING, Reservation.STATUS_CONFIRMED],
        )
        return Response(ReservationSerializer(qs, many=True,
                                              context={"request": request}).data)
