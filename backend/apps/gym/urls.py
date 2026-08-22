"""
Gym URLs
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    EquipmentViewSet, ExerciseViewSet, MuscleGroupViewSet,
    RoutineViewSet, WorkoutLogViewSet,
)

app_name = "gym"
router = DefaultRouter()
router.register(r"muscle-groups", MuscleGroupViewSet, basename="muscle-groups")
router.register(r"equipment", EquipmentViewSet, basename="equipment")
router.register(r"exercises", ExerciseViewSet, basename="exercises")
router.register(r"routines", RoutineViewSet, basename="routines")
router.register(r"logs", WorkoutLogViewSet, basename="logs")

urlpatterns = [path("", include(router.urls))]
