"""
Refreshments Serializers
"""
from rest_framework import serializers
from django.utils import timezone
from .models import (
    ProductCategory, Product, Order, OrderItem,
)
from apps.authentication.models import User
from apps.authentication.serializers import UserMeSerializer


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    category = ProductCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source="category", write_only=True, queryset=ProductCategory.objects.all()
    )
    stock_low = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = (
            "id", "category", "category_id", "name", "sku", "description",
            "unit_measure", "unit_content", "price", "cost", "stock",
            "min_stock", "is_available", "image", "allergens", "calories",
            "stock_low", "created_at", "updated_at",
        )


class ProductSummarySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Product
        fields = ("id", "name", "sku", "category_name", "price",
                  "stock", "is_available", "image")


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSummarySerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        source="product", write_only=True, queryset=Product.objects.all()
    )

    class Meta:
        model = OrderItem
        fields = (
            "id", "product", "product_id", "quantity",
            "unit_price_at_purchase", "line_total", "notes",
        )
        read_only_fields = ("unit_price_at_purchase", "line_total")


class OrderSerializer(serializers.ModelSerializer):
    client = UserMeSerializer(read_only=True)
    client_id = serializers.PrimaryKeyRelatedField(
        source="client", write_only=True,
        queryset=User.objects.filter(role=User.ROLE_CLIENT),
        required=False,
    )
    items = OrderItemSerializer(many=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    payment_method_display = serializers.CharField(
        source="get_payment_method_display", read_only=True
    )

    class Meta:
        model = Order
        fields = (
            "id", "order_number", "client", "client_id", "taken_by",
            "reservation", "status", "status_display",
            "payment_method", "payment_method_display",
            "subtotal", "tax_percent", "tax_amount",
            "discount_percent", "discount_amount", "total_amount",
            "paid_amount", "points_used", "notes",
            "pickup_window_start", "pickup_window_end",
            "delivered_at", "paid_at", "paid_by",
            "cancelled_at", "cancelled_by", "cancellation_reason",
            "points_awarded", "items",
            "created_at", "updated_at",
        )
        read_only_fields = ("order_number", "subtotal", "tax_amount",
                            "discount_amount", "total_amount", "created_at")

    def validate(self, data):
        request = self.context.get("request")
        if request and request.user.role == User.ROLE_CLIENT and "client" not in data:
            data["client"] = request.user
        return data

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        from django.db import transaction
        with transaction.atomic():
            order = Order.objects.create(**validated_data)
            for item in items_data:
                OrderItem.objects.create(order=order, **item)
        order.recalculate_totals()
        return order


class OrderUpdateStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("status", "payment_method", "paid_amount",
                  "cancellation_reason")
