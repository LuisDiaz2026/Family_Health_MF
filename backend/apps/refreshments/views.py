"""
Refreshments Views
"""
from django.db.models import Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.authentication.models import User
from apps.authentication.permissions import IsAdmin, IsAdminOrEmployee, IsClient
from .models import Order, OrderItem, Product, ProductCategory
from .serializers import (
    OrderSerializer, OrderUpdateStatusSerializer,
    ProductCategorySerializer, ProductSerializer,
)


class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.order_by("order", "name")
    serializer_class = ProductCategorySerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            self.permission_classes = [IsAuthenticated & IsAdmin]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            self.permission_classes = [IsAuthenticated & IsAdminOrEmployee]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        qs = Product.objects.select_related("category").all()
        if self.request.user.role == User.ROLE_CLIENT:
            qs = qs.filter(is_available=True)
        category_id = self.request.query_params.get("category")
        q = self.request.query_params.get("q")
        low_stock = self.request.query_params.get("low_stock")
        if category_id:
            qs = qs.filter(category_id=category_id)
        if q:
            qs = qs.filter(
                Q(name__icontains=q) | Q(sku__icontains=q)
                | Q(description__icontains=q)
            )
        if low_stock == "1":
            qs = [p for p in qs if p.stock_low]
        return qs

    @action(detail=False, methods=["get"], url_path="available-catalog")
    def available_catalog(self, request):
        categories = ProductCategory.objects.filter(is_active=True).order_by("order")
        data = []
        for cat in categories:
            prods = ProductSerializer(
                Product.objects.filter(category=cat, is_available=True, stock__gt=0),
                many=True, context={"request": request}
            ).data
            data.append({
                "category": ProductCategorySerializer(cat).data,
                "products": prods,
            })
        return Response(data)


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer

    def get_permissions(self):
        if self.action == "destroy":
            self.permission_classes = [IsAuthenticated & IsAdmin]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        qs = Order.objects.select_related("client", "reservation").all()
        if user.role == User.ROLE_CLIENT:
            qs = qs.filter(client=user)
        status_val = self.request.query_params.get("status")
        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")
        client_id = self.request.query_params.get("client_id")
        if status_val:
            qs = qs.filter(status=status_val)
        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)
        if client_id and user.role != User.ROLE_CLIENT:
            qs = qs.filter(client_id=client_id)
        return qs.order_by("-created_at")

    @action(detail=True, methods=["post"], url_path="next-status",
            permission_classes=[IsAuthenticated & IsAdminOrEmployee])
    def next_status(self, request, pk=None):
        order = self.get_object()
        order_map = {
            Order.STATUS_PENDING: Order.STATUS_PREPARING,
            Order.STATUS_PREPARING: Order.STATUS_READY,
            Order.STATUS_READY: Order.STATUS_DELIVERED,
        }
        if order.status in order_map:
            order.status = order_map[order.status]
            if order.status == Order.STATUS_DELIVERED:
                order.delivered_at = timezone.now()
            order.save(update_fields=["status", "delivered_at"])
        return Response(OrderSerializer(order, context={"request": request}).data)

    @action(detail=True, methods=["post"], url_path="mark-paid",
            permission_classes=[IsAuthenticated & IsAdminOrEmployee])
    def mark_paid(self, request, pk=None):
        order = self.get_object()
        order.payment_method = request.data.get(
            "payment_method", Order.PAYMENT_CASH
        )
        order.paid_amount = request.data.get("paid_amount", order.total_amount)
        order.paid_at = timezone.now()
        order.paid_by = request.user
        order.status = Order.STATUS_PAID
        order.save()
        return Response(OrderSerializer(order, context={"request": request}).data)

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        order = self.get_object()
        if request.user.role == User.ROLE_CLIENT and order.status not in (
            Order.STATUS_PENDING,
        ):
            return Response(
                {"error": "No puede cancelar este pedido en este estado"},
                status=status.HTTP_400_BAD_REQUEST
            )
        order.status = Order.STATUS_CANCELLED
        order.cancelled_by = request.user
        order.cancelled_at = timezone.now()
        order.cancellation_reason = request.data.get(
            "reason", "Cancelado"
        )
        order.save(update_fields=["status", "cancelled_by",
                                   "cancelled_at", "cancellation_reason"])
        return Response(OrderSerializer(order, context={"request": request}).data)

    @action(detail=False, methods=["get"], url_path="my-orders",
            permission_classes=[IsAuthenticated & IsClient])
    def my_orders(self, request):
        qs = self.get_queryset().filter(client=request.user)
        return Response(OrderSerializer(qs, many=True,
                                         context={"request": request}).data)
