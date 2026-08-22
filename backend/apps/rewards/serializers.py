"""
Rewards Serializers
"""
from rest_framework import serializers
from .models import (
    RewardRule, LoyaltyTier, PointsTransaction, LoyaltyProfile, RewardCatalogItem,
)
from apps.authentication.serializers import UserMeSerializer


class RewardRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RewardRule
        fields = "__all__"


class LoyaltyTierSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoyaltyTier
        fields = "__all__"


class LoyaltyProfileSerializer(serializers.ModelSerializer):
    user = UserMeSerializer(read_only=True)
    tier = LoyaltyTierSerializer(read_only=True)

    class Meta:
        model = LoyaltyProfile
        fields = (
            "id", "user", "tier", "current_points", "lifetime_points",
            "redeemed_points", "referrals_count", "anniversary_date",
            "referred_by", "created_at", "updated_at",
        )


class RewardCatalogItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = RewardCatalogItem
        fields = "__all__"


class PointsTransactionSerializer(serializers.ModelSerializer):
    rule = RewardRuleSerializer(read_only=True)
    reward = RewardCatalogItemSerializer(read_only=True)
    transaction_type_display = serializers.CharField(
        source="get_transaction_type_display", read_only=True
    )

    class Meta:
        model = PointsTransaction
        fields = (
            "id", "transaction_type", "transaction_type_display",
            "amount", "balance_after", "rule", "reservation",
            "order", "reward", "description", "expires_at", "created_at",
        )
        read_only_fields = ("balance_after", "created_at")


class PointsAdjustSerializer(serializers.Serializer):
    amount = serializers.IntegerField(required=True)
    description = serializers.CharField(max_length=250, required=True)


class RedeemRewardSerializer(serializers.Serializer):
    reward_id = serializers.IntegerField(required=True)
