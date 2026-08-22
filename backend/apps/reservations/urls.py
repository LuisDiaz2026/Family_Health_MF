"""
Reservations URLs
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    HolidayViewSet, OperatingHoursViewSet, ReservationViewSet,
    SpaceTypeViewSet, SpaceViewSet,
)

app_name = "reservations"
router = DefaultRouter()
router.register(r"space-types", SpaceTypeViewSet, basename="space-types")
router.register(r"spaces", SpaceViewSet, basename="spaces")
router.register(r"operating-hours", OperatingHoursViewSet, basename="operating-hours")
router.register(r"holidays", HolidayViewSet, basename="holidays")
router.register(r"reservations", ReservationViewSet, basename="reservations")

urlpatterns = [
    path("", include(router.urls)),
]
