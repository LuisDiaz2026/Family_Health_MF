from django.contrib import admin
from .models import (
    RewardRule, LoyaltyTier, PointsTransaction, LoyaltyProfile, RewardCatalogItem,
)


@admin.register(RewardRule)
class RewardRuleAdmin(admin.ModelAdmin):
    list_display = ("action_type", "points_amount", "points_per_currency", "is_active")
    list_filter = ("is_active", "action_type")


@admin.register(LoyaltyTier)
class LoyaltyTierAdmin(admin.ModelAdmin):
    list_display = ("name", "min_points", "color", "discount_percent", "is_active")
    list_filter = ("is_active",)
    ordering = ("min_points",)


@admin.register(LoyaltyProfile)
class LoyaltyProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "tier", "current_points", "lifetime_points",
                    "redeemed_points", "referrals_count")
    list_filter = ("tier",)
    search_fields = ("user__username", "user__email",
                     "user__first_name", "user__last_name")
    raw_id_fields = ("user", "referred_by")


@admin.register(PointsTransaction)
class PointsTransactionAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "transaction_type", "amount",
                    "balance_after", "rule", "description")
    list_filter = ("transaction_type", ("created_at", admin.DateFieldListFilter))
    search_fields = ("user__username", "user__email", "description")
    date_hierarchy = "created_at"
    readonly_fields = ("balance_after",)
    raw_id_fields = ("user", "rule", "reservation", "order", "reward", "performed_by")


@admin.register(RewardCatalogItem)
class RewardCatalogItemAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "points_required", "stock", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("name", "description")
