"""
Rewards URLs
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    LoyaltyProfileViewSet, LoyaltyTierViewSet, PointsTransactionViewSet,
    RewardCatalogItemViewSet, RewardRuleViewSet,
)

app_name = "rewards"
router = DefaultRouter()
router.register(r"rules", RewardRuleViewSet, basename="rules")
router.register(r"tiers", LoyaltyTierViewSet, basename="tiers")
router.register(r"profiles", LoyaltyProfileViewSet, basename="profiles")
router.register(r"transactions", PointsTransactionViewSet, basename="transactions")
router.register(r"catalog", RewardCatalogItemViewSet, basename="catalog")

urlpatterns = [path("", include(router.urls))]
