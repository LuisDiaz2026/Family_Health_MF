"""
Gym Serializers
"""
from rest_framework import serializers
from .models import (
    MuscleGroup, Equipment, Exercise, Routine, RoutineExercise, WorkoutLog,
)
from apps.authentication.models import User
from apps.authentication.serializers import UserMeSerializer


class MuscleGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = MuscleGroup
        fields = "__all__"


class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = "__all__"


class ExerciseSerializer(serializers.ModelSerializer):
    muscle_group = MuscleGroupSerializer(read_only=True)
    muscle_group_id = serializers.PrimaryKeyRelatedField(
        source="muscle_group", write_only=True, queryset=MuscleGroup.objects.all()
    )
    equipment = EquipmentSerializer(read_only=True)
    equipment_id = serializers.PrimaryKeyRelatedField(
        source="equipment", write_only=True, queryset=Equipment.objects.all(),
        required=False, allow_null=True,
    )
    difficulty_level_display = serializers.CharField(
        source="get_difficulty_level_display", read_only=True
    )

    class Meta:
        model = Exercise
        fields = (
            "id", "name", "slug", "muscle_group", "muscle_group_id",
            "equipment", "equipment_id",
            "difficulty_level", "difficulty_level_display",
            "description", "tips", "common_mistakes",
            "recommended_sets", "recommended_reps_min", "recommended_reps_max",
            "rest_seconds", "estimated_calories_per_set", "video_url",
            "image", "is_active", "created_at", "updated_at",
        )


class RoutineExerciseSerializer(serializers.ModelSerializer):
    exercise = ExerciseSerializer(read_only=True)
    exercise_id = serializers.PrimaryKeyRelatedField(
        source="exercise", write_only=True, queryset=Exercise.objects.all()
    )

    class Meta:
        model = RoutineExercise
        fields = (
            "id", "exercise", "exercise_id", "order", "sets", "reps",
            "weight_kg", "rest_seconds", "notes",
        )


class RoutineSerializer(serializers.ModelSerializer):
    muscle_groups = MuscleGroupSerializer(read_only=True, many=True)
    muscle_group_ids = serializers.PrimaryKeyRelatedField(
        source="muscle_groups", write_only=True, many=True,
        queryset=MuscleGroup.objects.all(), required=False,
    )
    assigned_client = UserMeSerializer(read_only=True)
    assigned_client_id = serializers.PrimaryKeyRelatedField(
        source="assigned_client", write_only=True,
        queryset=User.objects.filter(role=User.ROLE_CLIENT),
        required=False, allow_null=True,
    )
    goal_display = serializers.CharField(source="get_goal_display", read_only=True)
    duration_display = serializers.CharField(source="get_duration_display", read_only=True)
    difficulty_level_display = serializers.CharField(
        source="get_difficulty_level_display", read_only=True
    )
    exercises = RoutineExerciseSerializer(many=True, required=False)

    class Meta:
        model = Routine
        fields = (
            "id", "name", "description", "goal", "goal_display",
            "duration", "duration_display", "difficulty_level",
            "difficulty_level_display", "frequency_days", "estimated_weeks",
            "muscle_groups", "muscle_group_ids", "is_generic",
            "assigned_client", "assigned_client_id", "assigned_by",
            "valid_from", "valid_until", "warm_up", "cool_down",
            "nutrition_tips", "is_active", "image",
            "exercises", "created_at", "updated_at",
        )

    def create(self, validated_data):
        exercises_data = validated_data.pop("exercises", [])
        from django.db import transaction
        with transaction.atomic():
            mg_ids = validated_data.pop("muscle_groups", [])
            routine = Routine.objects.create(**validated_data)
            if mg_ids:
                routine.muscle_groups.set(mg_ids)
            for i, ex in enumerate(exercises_data):
                ex.setdefault("order", i)
                RoutineExercise.objects.create(routine=routine, **ex)
        return routine


class WorkoutLogSerializer(serializers.ModelSerializer):
    client = UserMeSerializer(read_only=True)
    client_id = serializers.PrimaryKeyRelatedField(
        source="client", write_only=True,
        queryset=User.objects.filter(role=User.ROLE_CLIENT), required=False
    )
    routine = RoutineSerializer(read_only=True)
    routine_id = serializers.PrimaryKeyRelatedField(
        source="routine", write_only=True, queryset=Routine.objects.all(),
        required=False, allow_null=True
    )

    class Meta:
        model = WorkoutLog
        fields = "__all__"
