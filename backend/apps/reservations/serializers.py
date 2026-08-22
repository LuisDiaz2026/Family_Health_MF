"""
Reservations Serializers
"""
from rest_framework import serializers
from django.utils import timezone
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import (
    Space, SpaceType, OperatingHours, Holiday, Reservation,
)
from apps.authentication.models import User
from apps.authentication.serializers import UserMeSerializer


class SpaceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpaceType
        fields = "__all__"


class OperatingHoursSerializer(serializers.ModelSerializer):
    weekday_display = serializers.CharField(source="get_weekday_display", read_only=True)

    class Meta:
        model = OperatingHours
        fields = "__all__"


class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        fields = "__all__"


class SpaceSerializer(serializers.ModelSerializer):
    space_type = SpaceTypeSerializer(read_only=True)
    space_type_id = serializers.PrimaryKeyRelatedField(
        source="space_type", write_only=True, queryset=SpaceType.objects.all()
    )
    operating_hours = OperatingHoursSerializer(read_only=True, many=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Space
        fields = (
            "id", "space_type", "space_type_id", "name", "code", "description",
            "location", "capacity", "hourly_rate", "requires_employee_approval",
            "min_reservation_minutes", "max_reservation_minutes",
            "advance_days_limit", "cancellation_penalty_hours",
            "status", "status_display", "image", "operating_hours",
            "created_at", "updated_at",
        )


class SpaceSummarySerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    space_type_name = serializers.CharField(source="space_type.name", read_only=True)

    class Meta:
        model = Space
        fields = ("id", "code", "name", "space_type_name", "capacity",
                  "hourly_rate", "status", "status_display", "image")


class ReservationSerializer(serializers.ModelSerializer):
    space = SpaceSummarySerializer(read_only=True)
    space_id = serializers.PrimaryKeyRelatedField(
        source="space", write_only=True, queryset=Space.objects.all()
    )
    user = UserMeSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        source="user", write_only=True, queryset=User.objects.filter(role=User.ROLE_CLIENT),
        required=False
    )
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    payment_status_display = serializers.CharField(
        source="get_payment_status_display", read_only=True
    )
    can_cancel = serializers.BooleanField(read_only=True)
    is_upcoming = serializers.BooleanField(read_only=True)
    is_active_now = serializers.BooleanField(read_only=True)

    class Meta:
        model = Reservation
        fields = (
            "id", "space", "space_id", "user", "user_id", "created_by",
            "approved_by", "start_time", "end_time", "total_minutes",
            "total_amount", "status", "status_display",
            "payment_status", "payment_status_display",
            "payment_received_by", "payment_received_at", "guests_count",
            "notes", "cancellation_reason", "cancelled_by", "cancelled_at",
            "completed_at", "points_awarded", "can_cancel",
            "is_upcoming", "is_active_now", "created_at", "updated_at",
        )
        read_only_fields = ("total_minutes", "points_awarded",)

    def validate(self, data):
        request = self.context.get("request")
        start = data.get("start_time")
        end = data.get("end_time")
        if not start or not end:
            return data
        if start <= timezone.now():
            raise serializers.ValidationError({
                "start_time": "La reserva debe ser en el futuro"
            })
        if "user" in data and data["user"]:
            pass
        elif request and request.user.role == User.ROLE_CLIENT:
            data["user"] = request.user
            data["created_by"] = request.user
        return data

    def create(self, validated_data):
        space = validated_data["space"]
        # Set automático: si requiere aprobación empleado, marcar pending
        if (
            space.requires_employee_approval
            and validated_data.get("status") == Reservation.STATUS_CONFIRMED
        ):
            request = self.context.get("request")
            if request and request.user.role == User.ROLE_CLIENT:
                validated_data["status"] = Reservation.STATUS_PENDING
        request = self.context.get("request")
        if request:
            validated_data["created_by"] = validated_data.get("created_by") or request.user
        try:
            return super().create(validated_data)
        except DjangoValidationError as e:
            raise serializers.ValidationError({"detail": str(e)})


class ReservationAvailabilitySerializer(serializers.Serializer):
    space_id = serializers.IntegerField(required=True)
    date = serializers.DateField(required=True)

    def validate_space_id(self, value):
        if not Space.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Espacio no existe")
        return value


class ReservationUpdateStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ("status", "cancellation_reason", "payment_status",
                  "payment_received_at", "payment_received_by")
