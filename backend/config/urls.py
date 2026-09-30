"""
Family Health MF - URL Configuration
Trabajo de Grado - Universidad Antonio Nariño
"""
from pathlib import Path

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse, Http404
from django.urls import include, path, re_path


def spa_index(request):
    candidates = [
        Path(settings.PROJECT_ROOT) / "frontend" / "dist" / "index.html",
        Path(settings.BASE_DIR) / "staticfiles" / "index.html",
    ]
    for candidate in candidates:
        if candidate.exists():
            content = candidate.read_text(encoding="utf-8")
            return HttpResponse(content, content_type="text/html")
    raise Http404("SPA build not found. Run `cd frontend && npm run build`.")


urlpatterns = [
    # Django Admin
    path("admin/", admin.site.urls),

    # Apps
    path("api/v1/auth/", include("apps.authentication.urls", namespace="auth")),
    path("api/v1/reservations/", include("apps.reservations.urls", namespace="reservations")),
    path("api/v1/refreshments/", include("apps.refreshments.urls", namespace="refreshments")),
    path("api/v1/rewards/", include("apps.rewards.urls", namespace="rewards")),
    path("api/v1/gym/", include("apps.gym.urls", namespace="gym")),
    path("api/v1/reports/", include("apps.reports.urls", namespace="reports")),

    # Root health check
    path("api/v1/health/", include("apps.reports.urls_health")),

    # SPA Vue (debe ir al final)
    re_path(r"^(?!admin|api|media|static|robots\.txt|favicon\.ico).*$", spa_index, name="spa-index"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = "Club Family Health - Panel Administrativo"
admin.site.site_title = "Family Health MF | TFM UAN"
admin.site.index_title = "Gestión Integral de Reservas"
