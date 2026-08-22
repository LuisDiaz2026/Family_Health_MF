"""
Refreshments URLs
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import OrderViewSet, ProductCategoryViewSet, ProductViewSet

app_name = "refreshments"
router = DefaultRouter()
router.register(r"categories", ProductCategoryViewSet, basename="categories")
router.register(r"products", ProductViewSet, basename="products")
router.register(r"orders", OrderViewSet, basename="orders")

urlpatterns = [path("", include(router.urls))]
