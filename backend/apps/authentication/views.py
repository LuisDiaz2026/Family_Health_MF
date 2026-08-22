"""
Authentication Views
"""
import logging

from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import AuditLog
from .permissions import (
    IsAdmin,
    IsAdminOrEmployee,
    IsAdminOrOwner,
)
from .serializers import (
    AdminUserCreateSerializer,
    AdminUserUpdateSerializer,
    AuditLogSerializer,
    CustomTokenObtainPairSerializer,
    UserChangePasswordSerializer,
    UserMeSerializer,
    UserRegisterSerializer,
    UserUpdateProfileSerializer,
)

User = get_user_model()
logger = logging.getLogger("apps.authentication")


class LoginThrottle(AnonRateThrottle):
    rate = "10/minute"
    scope = "login"


class RegisterThrottle(AnonRateThrottle):
    rate = "5/hour"
    scope = "register"


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    throttle_classes = [LoginThrottle]


class RegisterView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [RegisterThrottle]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            AuditLog.objects.create(
                user=user, action=AuditLog.ACTION_LOGIN,
                detail="Registro exitoso de cliente nuevo"
            )
            return Response({
                "message": "Usuario registrado exitosamente",
                "user": UserMeSerializer(user, context={"request": request}).data,
            }, status=status.HTTP_201_CREATED)
        return Response({"errors": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)


class MeViewSet(viewsets.ViewSet):
    """Perfil del usuario autenticado."""
    permission_classes = [IsAuthenticated]

    def list(self, request):
        serializer = UserMeSerializer(request.user, context={"request": request})
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserUpdateProfileSerializer(
            request.user, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            AuditLog.objects.create(
                user=request.user,
                action=AuditLog.ACTION_PROFILE_EDIT,
                detail="Actualización de perfil propio"
            )
            return Response(UserMeSerializer(request.user,
                                              context={"request": request}).data)
        return Response({"errors": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        return self.patch(request)

    @action(detail=False, methods=["post"], url_path="change-password")
    def change_password(self, request):
        serializer = UserChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            request.user.set_password(serializer.validated_data["new_password"])
            request.user.save()
            return Response({"message": "Contraseña actualizada exitosamente"})
        return Response({"errors": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"], url_path="audit-logs")
    def audit_logs(self, request):
        qs = AuditLog.objects.filter(user=request.user).order_by("-created_at")[:50]
        return Response(AuditLogSerializer(qs, many=True).data)

    @action(detail=False, methods=["get"], url_path="loyalty")
    def loyalty(self, request):
        user = request.user
        base = {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role,
            "role_display": user.role_display,
            "membership_type": user.membership_type,
            "membership_expires_at": user.membership_expires_at,
            "membership_active": user.membership_active,
        }
        if user.role != User.ROLE_CLIENT or not hasattr(user, "loyalty_profile"):
            return Response({**base, "current_points": 0, "tier": None,
                             "lifetime_points": 0, "redeemed_points": 0,
                             "referrals_count": 0})
        p = user.loyalty_profile
        return Response({
            **base,
            "current_points": p.current_points,
            "lifetime_points": p.lifetime_points,
            "redeemed_points": p.redeemed_points,
            "referrals_count": p.referrals_count,
            "anniversary_date": p.anniversary_date,
            "tier": {
                "name": p.tier.name,
                "benefits": p.tier.benefits,
                "color": p.tier.color,
                "min_points": p.tier.min_points,
                "discount_percent": str(p.tier.discount_percent),
            } if p.tier else None,
        })


class UserAdminViewSet(viewsets.ModelViewSet):
    """Gestión de usuarios (solo ADMIN)."""
    permission_classes = [IsAuthenticated & IsAdmin]
    queryset = User.objects.all().order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "create":
            return AdminUserCreateSerializer
        if self.action in ("update", "partial_update"):
            return AdminUserUpdateSerializer
        return UserMeSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        role = self.request.query_params.get("role")
        q = self.request.query_params.get("q")
        if role:
            qs = qs.filter(role=role)
        if q:
            qs = qs.filter(
                Q(username__icontains=q) | Q(email__icontains=q)
                | Q(first_name__icontains=q) | Q(last_name__icontains=q)
                | Q(document_number__icontains=q)
            )
        return qs

    @action(detail=True, methods=["post"], url_path="toggle-active")
    def toggle_active(self, request, pk=None):
        user = self.get_object()
        if user == request.user:
            return Response({"error": "No puede desactivar su propio usuario"},
                            status=status.HTTP_400_BAD_REQUEST)
        user.is_active = not user.is_active
        user.save(update_fields=["is_active"])
        return Response({"is_active": user.is_active})


class EmployeeClientViewSet(viewsets.ReadOnlyModelViewSet):
    """Empleados pueden consultar datos de clientes."""
    permission_classes = [IsAuthenticated & IsAdminOrEmployee]
    serializer_class = UserMeSerializer
    queryset = User.objects.filter(role=User.ROLE_CLIENT).order_by("-created_at")

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.query_params.get("q")
        if q:
            qs = qs.filter(
                Q(username__icontains=q) | Q(email__icontains=q)
                | Q(first_name__icontains=q) | Q(last_name__icontains=q)
                | Q(document_number__icontains=q) | Q(phone__icontains=q)
            )
        return qs
