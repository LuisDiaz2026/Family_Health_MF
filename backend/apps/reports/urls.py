"""
Reports URLs
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    NotificationViewSet, dashboard_summary, reservations_by_date,
    revenue_by_month, top_clients,
)

app_name = "reports"
router = DefaultRouter()
router.register(r"notifications", NotificationViewSet, basename="notifications")

urlpatterns = [
    path("", include(router.urls)),
    # Reportes panel admin
    path("dashboard/summary/", dashboard_summary, name="dashboard-summary"),
    path("dashboard/reservations-by-date/", reservations_by_date,
         name="reservations-by-date"),
    path("dashboard/revenue-by-month/", revenue_by_month,
         name="revenue-by-month"),
    path("dashboard/top-clients/", top_clients, name="top-clients"),
    # Alias cortos (sin dashboard/)
    path("top-clients/", top_clients, name="top-clients-short"),
]
