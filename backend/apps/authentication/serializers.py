"""
Authentication Serializers - JWT + Perfiles
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer as BaseTokenObtainPairSerializer,
)

from .models import AuditLog

User = get_user_model()


class CustomTokenObtainPairSerializer(BaseTokenObtainPairSerializer):
    """JWT Token serializer con datos del usuario + rol."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["email"] = user.email
        token["username"] = user.username
        token["full_name"] = user.full_name
        token["membership_active"] = user.membership_active
        if hasattr(user, "loyalty_profile") and user.loyalty_profile:
            token["points"] = user.loyalty_profile.current_points
            if user.loyalty_profile.tier:
                token["tier"] = user.loyalty_profile.tier.name
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        AuditLog.objects.create(
            user=user,
            action=AuditLog.ACTION_LOGIN,
            detail="Login exitoso vía JWT",
        )
        user_ser = UserMeSerializer(user, context=self.context).data
        data["user"] = user_ser
        data["role"] = user.role
        data["full_name"] = user.full_name
        data["membership_active"] = user.membership_active
        if hasattr(user, "loyalty_profile") and user.loyalty_profile:
            data["points"] = user.loyalty_profile.current_points
            data["tier"] = user.loyalty_profile.tier.name if user.loyalty_profile.tier else None
        else:
            data["points"] = 0
            data["tier"] = None
        return data


class UserRegisterSerializer(serializers.ModelSerializer):
    """Registro público de clientes."""
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
    )
    password_confirm = serializers.CharField(
        write_only=True, min_length=8, style={"input_type": "password"}
    )
    accepted_privacy_policy = serializers.BooleanField(required=True)
    accepted_terms = serializers.BooleanField(required=True)

    class Meta:
        model = User
        fields = (
            "username", "email", "first_name", "last_name",
            "document_type", "document_number", "phone",
            "gender", "birth_date",
            "password", "password_confirm",
            "accepted_privacy_policy", "accepted_terms",
        )
        extra_kwargs = {
            "email": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
        }

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Las contraseñas no coinciden"})
        if not data["accepted_privacy_policy"]:
            raise serializers.ValidationError({
                "accepted_privacy_policy": "Debe aceptar la política de privacidad (Ley 1581/2012)"
            })
        if not data["accepted_terms"]:
            raise serializers.ValidationError({
                "accepted_terms": "Debe aceptar los términos y condiciones"
            })
        return data

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        validated_data["password"] = make_password(validated_data["password"])
        validated_data["role"] = User.ROLE_CLIENT
        validated_data["privacy_policy_accepted_at"] = timezone.now()
        return super().create(validated_data)


class UserMeSerializer(serializers.ModelSerializer):
    """Perfil propio del usuario autenticado (lectura)."""
    role_display = serializers.CharField(read_only=True)
    full_name = serializers.CharField(read_only=True)
    membership_active = serializers.BooleanField(read_only=True)
    loyalty = serializers.SerializerMethodField(read_only=True)
    unread_notifications_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id", "username", "email", "role", "role_display",
            "first_name", "last_name", "full_name",
            "document_type", "document_number", "phone",
            "gender", "birth_date", "address", "city", "department",
            "emergency_contact", "emergency_phone",
            "membership_type", "membership_expires_at", "membership_active",
            "is_verified", "accepted_privacy_policy",
            "created_at", "updated_at", "loyalty",
            "unread_notifications_count",
        )
        read_only_fields = ("id", "role", "email", "is_verified", "created_at")

    def get_loyalty(self, obj):
        if obj.role != User.ROLE_CLIENT:
            return None
        try:
            p = obj.loyalty_profile
            return {
                "current_points": p.current_points,
                "lifetime_points": p.lifetime_points,
                "redeemed_points": p.redeemed_points,
                "tier": {"name": p.tier.name, "color": p.tier.color,
                         "discount_percent": str(p.tier.discount_percent)}
                if p.tier else None,
                "referrals_count": p.referrals_count,
            }
        except Exception:
            return {"current_points": 0, "tier": None}

    def get_unread_notifications_count(self, obj):
        return obj.notifications.filter(is_read=False).count()


class UserUpdateProfileSerializer(serializers.ModelSerializer):
    """Actualización del perfil por el propio usuario (restricciones)."""

    class Meta:
        model = User
        fields = (
            "first_name", "last_name", "phone", "gender", "birth_date",
            "address", "city", "department", "emergency_contact",
            "emergency_phone",
        )


class UserChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(
        write_only=True, style={"input_type": "password"}
    )
    new_password = serializers.CharField(
        write_only=True, min_length=8, style={"input_type": "password"}
    )
    new_password_confirm = serializers.CharField(
        write_only=True, min_length=8, style={"input_type": "password"}
    )

    def validate_current_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Contraseña actual incorrecta")
        return value

    def validate(self, data):
        if data["new_password"] != data["new_password_confirm"]:
            raise serializers.ValidationError({"new_password_confirm":
                                               "No coincide con la nueva contraseña"})
        if data["current_password"] == data["new_password"]:
            raise serializers.ValidationError({"new_password":
                                               "La nueva contraseña debe ser diferente"})
        return data


class AdminUserCreateSerializer(serializers.ModelSerializer):
    """Creación de usuarios (empleados / admin) vía panel administrativo API."""
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = (
            "username", "email", "first_name", "last_name",
            "document_type", "document_number", "phone",
            "role", "password", "is_active", "membership_type",
        )

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    """Actualización total de usuarios vía admin API."""

    class Meta:
        model = User
        fields = (
            "username", "email", "first_name", "last_name",
            "document_type", "document_number", "phone",
            "role", "is_active", "is_verified",
            "membership_type", "membership_expires_at",
            "gender", "birth_date", "address", "city", "department",
            "emergency_contact", "emergency_phone",
        )


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = "__all__"
