"""
Gym Views
"""
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.authentication.models import User
from apps.authentication.permissions import IsAdmin, IsAdminOrEmployee, IsClient
from .models import (
    MuscleGroup, Equipment, Exercise, Routine, RoutineExercise, WorkoutLog,
)
from .serializers import (
    EquipmentSerializer, ExerciseSerializer, MuscleGroupSerializer,
    RoutineSerializer, WorkoutLogSerializer,
)


class MuscleGroupViewSet(viewsets.ModelViewSet):
    queryset = MuscleGroup.objects.order_by("order", "name")
    serializer_class = MuscleGroupSerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            self.permission_classes = [IsAuthenticated & IsAdminOrEmployee]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()


class EquipmentViewSet(viewsets.ModelViewSet):
    queryset = Equipment.objects.all().order_by("name")
    serializer_class = EquipmentSerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            self.permission_classes = [IsAuthenticated & IsAdminOrEmployee]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()


class ExerciseViewSet(viewsets.ModelViewSet):
    serializer_class = ExerciseSerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            self.permission_classes = [IsAuthenticated & IsAdminOrEmployee]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        qs = Exercise.objects.select_related(
            "muscle_group", "equipment"
        ).all()
        if self.request.user.role == User.ROLE_CLIENT:
            qs = qs.filter(is_active=True)
        muscle = self.request.query_params.get("muscle")
        level = self.request.query_params.get("level")
        equipment = self.request.query_params.get("equipment")
        q = self.request.query_params.get("q")
        if muscle:
            qs = qs.filter(Q(muscle_group_id=muscle) | Q(secondary_groups__id=muscle))
        if level:
            qs = qs.filter(difficulty_level=level)
        if equipment:
            qs = qs.filter(equipment_id=equipment)
        if q:
            qs = qs.filter(
                Q(name__icontains=q) | Q(description__icontains=q)
            )
        return qs.distinct()


class RoutineViewSet(viewsets.ModelViewSet):
    serializer_class = RoutineSerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            self.permission_classes = [IsAuthenticated & IsAdminOrEmployee]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        qs = Routine.objects.prefetch_related(
            "exercises__exercise", "muscle_groups"
        ).filter(is_active=True)
        if user.role == User.ROLE_CLIENT:
            qs = qs.filter(
                Q(is_generic=True) | Q(assigned_client=user)
            )
        goal = self.request.query_params.get("goal")
        level = self.request.query_params.get("level")
        duration = self.request.query_params.get("duration")
        assigned = self.request.query_params.get("assigned_client")
        if goal:
            qs = qs.filter(goal=goal)
        if level:
            qs = qs.filter(difficulty_level=level)
        if duration:
            qs = qs.filter(duration=duration)
        if assigned and user.role != User.ROLE_CLIENT:
            qs = qs.filter(assigned_client_id=assigned)
        return qs.order_by("-created_at")

    @action(detail=False, methods=["get"], url_path="my-routines",
            permission_classes=[IsAuthenticated & IsClient])
    def my_routines(self, request):
        qs = self.get_queryset().filter(
            Q(is_generic=True) | Q(assigned_client=request.user)
        )
        return Response(RoutineSerializer(qs, many=True,
                                           context={"request": request}).data)


class WorkoutLogViewSet(viewsets.ModelViewSet):
    serializer_class = WorkoutLogSerializer

    def get_permissions(self):
        if self.action == "destroy":
            self.permission_classes = [IsAuthenticated & IsAdminOrEmployee]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        qs = WorkoutLog.objects.select_related("client", "routine").all()
        user = self.request.user
        if user.role == User.ROLE_CLIENT:
            qs = qs.filter(client=user)
        client_id = self.request.query_params.get("client_id")
        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")
        if client_id and user.role != User.ROLE_CLIENT:
            qs = qs.filter(client_id=client_id)
        if date_from:
            qs = qs.filter(session_date__gte=date_from)
        if date_to:
            qs = qs.filter(session_date__lte=date_to)
        return qs.order_by("-session_date")

    def create(self, request, *args, **kwargs):
        if request.user.role == User.ROLE_CLIENT:
            request.data["client_id"] = request.user.pk
        return super().create(request, *args, **kwargs)
