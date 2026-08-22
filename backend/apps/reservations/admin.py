"""
Reservations Admin
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Space, SpaceType, OperatingHours, Holiday, Reservation


@admin.register(SpaceType)
class SpaceTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "icon", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
    prepopulated_fields = {}


@admin.register(OperatingHours)
class OperatingHoursAdmin(admin.ModelAdmin):
    list_display = ("space", "weekday", "open_time", "close_time", "is_closed")
    list_filter = ("weekday", "is_closed", "space")
    ordering = ("space", "weekday")


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ("date", "name")
    search_fields = ("name",)
    date_hierarchy = "date"
    filter_horizontal = ("spaces_closed",)


@admin.register(Space)
class SpaceAdmin(admin.ModelAdmin):
    list_display = (
        "code", "name", "space_type", "capacity", "hourly_rate",
        "status", "requires_employee_approval",
    )
    list_filter = ("space_type", "status", "requires_employee_approval")
    search_fields = ("name", "code", "location", "description")
    prepopulated_fields = {}
    inlines = []


class OperatingHoursInline(admin.TabularInline):
    model = OperatingHours
    extra = 7
    fk_name = "space"


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = (
        "id", "space", "user", "start_time", "end_time",
        "total_minutes", "status", "payment_status", "total_amount",
    )
    list_filter = (
        "status", "payment_status", "space",
        ("start_time", admin.DateFieldListFilter),
    )
    search_fields = (
        "user__username", "user__email", "user__first_name",
        "user__last_name", "space__name", "space__code",
    )
    date_hierarchy = "start_time"
    readonly_fields = ("total_minutes", "created_at", "updated_at")
    raw_id_fields = ("user", "created_by", "approved_by", "payment_received_by",
                   "cancelled_by")
    fieldsets = (
        (None, {"fields": (
            "space", "user", "created_by", "approved_by",
            "start_time", "end_time", "total_minutes", "guests_count",
        )}),
        ("Pago", {"fields": (
            "total_amount", "payment_status", "payment_received_by",
            "payment_received_at",
        )}),
        ("Estado", {"fields": (
            "status", "cancellation_reason", "cancelled_by", "cancelled_at",
            "completed_at", "points_awarded",
        )}),
        ("Notas", {"fields": ("notes",)}),
        ("Auditoría", {"fields": ("created_at", "updated_at")}),
    )
