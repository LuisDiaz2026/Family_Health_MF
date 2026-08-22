"""
Authentication Admin - Club Family Health
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import AuditLog, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "username", "email", "full_name", "role", "document_number",
        "phone", "is_active", "is_verified", "membership_type", "last_login"
    )
    list_filter = ("role", "is_active", "is_verified", "gender",
                   "accepted_privacy_policy")
    search_fields = ("username", "email", "first_name", "last_name",
                     "document_number", "phone")
    ordering = ("-created_at",)
    readonly_fields = ("last_login", "created_at", "updated_at",
                       "last_login_ip", "last_login_user_agent")

    fieldsets = (
        (None, {"fields": ("username", "email", "password")}),
        (_("Información Personal"), {
            "fields": (
                "first_name", "last_name", "document_type", "document_number",
                "gender", "birth_date", "phone", "address", "city",
                "department", "emergency_contact", "emergency_phone",
            )
        }),
        (_("Sistema y Roles"), {
            "fields": (
                "role", "is_staff", "is_active", "is_superuser",
                "is_verified", "accepted_privacy_policy",
                "privacy_policy_accepted_at", "accepted_terms",
                "groups", "user_permissions",
            )
        }),
        (_("Membresía"), {
            "fields": ("membership_type", "membership_expires_at"),
        }),
        (_("Auditoría"), {
            "fields": ("last_login", "last_login_ip", "last_login_user_agent",
                       "created_at", "updated_at"),
        }),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "first_name", "last_name",
                       "role", "password1", "password2", "is_active",
                       "accepted_privacy_policy", "accepted_terms"),
        }),
    )

    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = _("Nombre Completo")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "action", "ip_address", "detail")
    list_filter = ("action", "created_at")
    search_fields = ("user__username", "user__email", "ip_address", "detail")
    readonly_fields = ("created_at", "user", "action", "detail",
                       "ip_address", "user_agent")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
