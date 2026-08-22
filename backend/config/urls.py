"""
Family Health MF - URL Configuration
Trabajo de Grado - Universidad Antonio Nariño
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenBlacklistView,
    TokenRefreshView,
)

urlpatterns = [
    # Django Admin
    path("admin/", admin.site.urls),

    # Autenticación JWT
    path(
        "api/v1/auth/token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path(
        "api/v1/auth/token/blacklist/",
        TokenBlacklistView.as_view(),
        name="token_blacklist",
    ),

    # Apps
    path("api/v1/auth/", include("apps.authentication.urls", namespace="auth")),
    path("api/v1/reservations/", include("apps.reservations.urls", namespace="reservations")),
    path("api/v1/refreshments/", include("apps.refreshments.urls", namespace="refreshments")),
    path("api/v1/rewards/", include("apps.rewards.urls", namespace="rewards")),
    path("api/v1/gym/", include("apps.gym.urls", namespace="gym")),
    path("api/v1/reports/", include("apps.reports.urls", namespace="reports")),

    # Root health check
    path("api/v1/health/", include("apps.reports.urls_health")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = "Club Family Health - Panel Administrativo"
admin.site.site_title = "Family Health MF | TFM UAN"
admin.site.index_title = "Gestión Integral de Reservas"
