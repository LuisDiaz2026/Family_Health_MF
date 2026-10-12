"""
Authentication Permissions - RBAC para 4 roles.
Roles: ADMIN, RECEPCION, CAFETERIA, CLIENT (EMPLOYEE por compatibilidad).
"""
from rest_framework.permissions import BasePermission, SAFE_METHODS

from .models import User


class IsAdmin(BasePermission):
    """Solo rol ADMIN (RBAC) o is_superuser=True por compatibilidad createsuperuser."""
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.role == User.ROLE_ADMIN or request.user.is_superuser)
        )


class IsEmployee(BasePermission):
    """Solo rol EMPLOYEE (compatibilidad)."""
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == User.ROLE_EMPLOYEE
        )


class IsReception(BasePermission):
    """Rol RECEPCION (o EMPLOYEE por compatibilidad)."""
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in (User.ROLE_RECEPCION, User.ROLE_EMPLOYEE)
        )


class IsCafeteria(BasePermission):
    """Rol CAFETERIA (o EMPLOYEE por compatibilidad)."""
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in (User.ROLE_CAFETERIA, User.ROLE_EMPLOYEE)
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
    """Staff operativo general: ADMIN, RECEPCION, CAFETERIA o EMPLOYEE (compat)."""
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (
                request.user.role in (
                    User.ROLE_ADMIN, User.ROLE_RECEPCION,
                    User.ROLE_CAFETERIA, User.ROLE_EMPLOYEE,
                )
                or request.user.is_staff
                or request.user.is_superuser
            )
        )


class IsAdminOrReception(BasePermission):
    """ADMIN o RECEPCION (para reservas, espacios, clientes)."""
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (
                request.user.role in (
                    User.ROLE_ADMIN, User.ROLE_RECEPCION, User.ROLE_EMPLOYEE,
                )
                or request.user.is_staff
                or request.user.is_superuser
            )
        )


class IsAdminOrCafeteria(BasePermission):
    """ADMIN o CAFETERIA (para productos y pedidos)."""
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (
                request.user.role in (
                    User.ROLE_ADMIN, User.ROLE_CAFETERIA, User.ROLE_EMPLOYEE,
                )
                or request.user.is_staff
                or request.user.is_superuser
            )
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
    """Lectura todos autenticados, escritura solo staff (admin/recepcion/cafeteria)."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.role in (
            User.ROLE_ADMIN, User.ROLE_RECEPCION,
            User.ROLE_CAFETERIA, User.ROLE_EMPLOYEE,
        )
