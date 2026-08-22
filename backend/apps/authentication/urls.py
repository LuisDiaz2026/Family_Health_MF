"""
Authentication URLs
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenBlacklistView, TokenRefreshView

from .views import (
    CustomTokenObtainPairView,
    EmployeeClientViewSet,
    MeViewSet,
    RegisterView,
    UserAdminViewSet,
)

app_name = "authentication"
router = DefaultRouter()
router.register(r"admin/users", UserAdminViewSet, basename="admin-users")
router.register(r"clients", EmployeeClientViewSet, basename="clients")
router.register(r"me", MeViewSet, basename="me")

urlpatterns = [
    # Tokens JWT
    path("login/", CustomTokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("logout/", TokenBlacklistView.as_view(), name="logout"),
    # Registro público de clientes
    path("register/", RegisterView.as_view(), name="register"),
    # Routers
    path("", include(router.urls)),
]
