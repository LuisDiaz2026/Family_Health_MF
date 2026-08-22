from django.contrib import admin
from .models import (
    MuscleGroup, Equipment, Exercise, Routine, RoutineExercise, WorkoutLog,
)


@admin.register(MuscleGroup)
class MuscleGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "icon", "order", "is_active")
    list_filter = ("is_active",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "is_active")
    list_filter = ("is_active",)
    filter_horizontal = ("muscle_groups",)
    search_fields = ("name", "location")


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ("name", "muscle_group", "equipment", "difficulty_level",
                    "recommended_sets", "is_active")
    list_filter = ("muscle_group", "difficulty_level", "is_active")
    search_fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}
    raw_id_fields = ("created_by",)
    filter_horizontal = ("secondary_groups",)


class RoutineExerciseInline(admin.TabularInline):
    model = RoutineExercise
    extra = 5
    raw_id_fields = ("exercise",)


@admin.register(Routine)
class RoutineAdmin(admin.ModelAdmin):
    list_display = ("name", "goal", "duration", "difficulty_level",
                    "frequency_days", "is_generic", "assigned_client",
                    "is_active")
    list_filter = ("goal", "duration", "difficulty_level",
                   "is_generic", "is_active")
    search_fields = ("name", "description")
    raw_id_fields = ("assigned_client", "assigned_by")
    filter_horizontal = ("muscle_groups",)
    inlines = [RoutineExerciseInline]


@admin.register(WorkoutLog)
class WorkoutLogAdmin(admin.ModelAdmin):
    list_display = ("client", "session_date", "routine", "duration_minutes",
                    "calories_burned", "feeling")
    list_filter = ("session_date",)
    search_fields = ("client__username", "client__first_name")
    date_hierarchy = "session_date"
    raw_id_fields = ("client", "routine")
