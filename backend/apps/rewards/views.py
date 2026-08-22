"""
Rewards Views
"""
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone

from apps.authentication.models import User
from apps.authentication.permissions import IsAdmin, IsAdminOrEmployee, IsClient
from .models import (
    RewardRule, LoyaltyTier, PointsTransaction, LoyaltyProfile, RewardCatalogItem,
)
from .serializers import (
    LoyaltyProfileSerializer, LoyaltyTierSerializer, PointsAdjustSerializer,
    PointsTransactionSerializer, RedeemRewardSerializer,
    RewardCatalogItemSerializer, RewardRuleSerializer,
)


class RewardRuleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated & IsAdmin]
    queryset = RewardRule.objects.all()
    serializer_class = RewardRuleSerializer


class LoyaltyTierViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated & IsAdmin]
    queryset = LoyaltyTier.objects.all().order_by("min_points")
    serializer_class = LoyaltyTierSerializer


class LoyaltyProfileViewSet(viewsets.ModelViewSet):
    queryset = LoyaltyProfile.objects.select_related("user", "tier").all()
    serializer_class = LoyaltyProfileSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            self.permission_classes = [IsAuthenticated & (IsAdmin | IsAdminOrEmployee)]
        else:
            self.permission_classes = [IsAuthenticated & IsAdmin]
        return super().get_permissions()

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.query_params.get("q")
        tier = self.request.query_params.get("tier")
        if q:
            qs = qs.filter(
                user__username__icontains=q
            ) | qs.filter(user__first_name__icontains=q) | qs.filter(
                user__last_name__icontains=q
            )
        if tier:
            qs = qs.filter(tier_id=tier)
        return qs

    @action(detail=False, methods=["get"], url_path="me",
            permission_classes=[IsAuthenticated & IsClient])
    def my_profile(self, request):
        p, _ = LoyaltyProfile.objects.get_or_create(user=request.user, defaults={
            "current_points": 0,
        })
        return Response(LoyaltyProfileSerializer(p,
                                                  context={"request": request}).data)

    @action(detail=True, methods=["post"], url_path="adjust-points",
            permission_classes=[IsAuthenticated & IsAdmin])
    def adjust_points(self, request, pk=None):
        profile = self.get_object()
        sz = PointsAdjustSerializer(data=request.data)
        if sz.is_valid():
            PointsTransaction.objects.create(
                user=profile.user,
                transaction_type=PointsTransaction.TYPE_ADJUST,
                amount=sz.validated_data["amount"],
                description=sz.validated_data["description"],
                performed_by=request.user,
            )
            return Response({"message": "Puntos actualizados"})
        return Response(sz.errors, status=status.HTTP_400_BAD_REQUEST)


class PointsTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = PointsTransactionSerializer
    queryset = PointsTransaction.objects.select_related(
        "user", "rule", "reward"
    ).all().order_by("-created_at")

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == User.ROLE_CLIENT:
            qs = qs.filter(user=user)
        user_id = self.request.query_params.get("user_id")
        type_val = self.request.query_params.get("type")
        if user_id and user.role != User.ROLE_CLIENT:
            qs = qs.filter(user_id=user_id)
        if type_val:
            qs = qs.filter(transaction_type=type_val)
        return qs


class RewardCatalogItemViewSet(viewsets.ModelViewSet):
    serializer_class = RewardCatalogItemSerializer
    queryset = RewardCatalogItem.objects.order_by("category", "points_required")

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsAuthenticated & IsAdmin]
        return super().get_permissions()

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.role == User.ROLE_CLIENT:
            qs = qs.filter(is_active=True)
        cat = self.request.query_params.get("category")
        if cat:
            qs = qs.filter(category=cat)
        return qs

    @action(detail=False, methods=["post"], url_path="redeem",
            permission_classes=[IsAuthenticated & IsClient])
    def redeem(self, request):
        sz = RedeemRewardSerializer(data=request.data)
        if not sz.is_valid():
            return Response(sz.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            reward = RewardCatalogItem.objects.get(
                pk=sz.validated_data["reward_id"], is_active=True
            )
        except RewardCatalogItem.DoesNotExist:
            return Response({"error": "Premio no disponible"},
                            status=status.HTTP_404_NOT_FOUND)
        profile = request.user.loyalty_profile
        if profile.current_points < reward.points_required:
            return Response({"error": "Puntos insuficientes"},
                            status=status.HTTP_400_BAD_REQUEST)
        if reward.stock > 0:
            reward.stock -= 1
            reward.save(update_fields=["stock"])
        PointsTransaction.objects.create(
            user=request.user,
            transaction_type=PointsTransaction.TYPE_REDEEM,
            amount=-reward.points_required,
            reward=reward,
            description=f"Canje: {reward.name}",
        )
        profile.redeemed_points += reward.points_required
        profile.save(update_fields=["redeemed_points"])
        return Response({"message": "Premio canjeado exitosamente",
                         "points_left": profile.current_points})
