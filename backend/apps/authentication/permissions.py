"""
Authentication Permissions - RBAC para 3 roles.
"""
from rest_framework.permissions import BasePermission, SAFE_METHODS

from .models import User


class IsAdmin(BasePermission):
    """Solo rol ADMIN."""
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == User.ROLE_ADMIN
        )


class IsEmployee(BasePermission):
    """Solo rol EMPLOYEE."""
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == User.ROLE_EMPLOYEE
        )


class IsClient(BasePermission):
    """Solo rol CLIENT."""
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == User.ROLE_CLIENT
        )


class IsAdminOrEmployee(BasePermission):
    """Staff operativo: ADMIN o EMPLOYEE."""
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in (User.ROLE_ADMIN, User.ROLE_EMPLOYEE)
        )


class IsAdminOrOwner(BasePermission):
    """ADMIN puede gestionar todo; usuario solo su propio recurso."""
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.user.role == User.ROLE_ADMIN:
            return True
        return obj == request.user or getattr(obj, "user", None) == request.user


class IsStaffOrReadOnly(BasePermission):
    """Lectura todos autenticados, escritura solo staff (admin/employee)."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.role in (User.ROLE_ADMIN, User.ROLE_EMPLOYEE)
