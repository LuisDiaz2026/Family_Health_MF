from django.contrib import admin
from .models import ProductCategory, Product, Order, OrderItem


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "icon", "order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "sku", "price", "stock", "min_stock",
                    "is_available", "stock_low")
    list_filter = ("category", "is_available")
    search_fields = ("name", "sku", "description")
    list_editable = ("price", "stock", "is_available")
    raw_id_fields = ()

    def stock_low(self, obj):
        return obj.stock <= obj.min_stock
    stock_low.boolean = True
    stock_low.short_description = "Stock Bajo"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("unit_price_at_purchase", "line_total")
    raw_id_fields = ("product",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "client", "status", "total_amount",
                    "payment_method", "created_at", "paid_at")
    list_filter = ("status", "payment_method", ("created_at", admin.DateFieldListFilter))
    search_fields = ("order_number", "client__username", "client__email",
                     "client__first_name", "client__last_name")
    readonly_fields = ("order_number", "created_at", "updated_at", "subtotal",
                       "tax_amount", "discount_amount", "total_amount")
    date_hierarchy = "created_at"
    raw_id_fields = ("client", "taken_by", "reservation", "paid_by",
                     "cancelled_by")
    inlines = [OrderItemInline]
