"""
Gym Module Models - Club Family Health
Clientes pueden consultar rutinas preestablecidas.
Admin/Empleados pueden gestionar rutinas y asignar a clientes.
"""
import logging

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.authentication.models import User

logger = logging.getLogger(__name__)


class MuscleGroup(models.Model):
    """Grupo muscular (pecho, espalda, piernas, etc.)"""
    name = models.CharField(
        verbose_name=_("Nombre Grupo Muscular"),
        max_length=50,
        unique=True,
    )
    slug = models.SlugField(verbose_name=_("Slug"), unique=True)
    icon = models.CharField(verbose_name=_("Icono"), max_length=10, default="💪")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _("Grupo Muscular")
        verbose_name_plural = _("Grupos Musculares")
        ordering = ["order", "name"]

    def __str__(self):
        return f"{self.icon} {self.name}"


class Equipment(models.Model):
    """Máquinas / equipos disponibles en el gimnasio."""
    name = models.CharField(verbose_name=_("Equipo"), max_length=100, unique=True)
    location = models.CharField(
        verbose_name=_("Ubicación"), max_length=100, null=True, blank=True
    )
    muscle_groups = models.ManyToManyField(
        MuscleGroup, blank=True, related_name="equipment",
        verbose_name=_("Grupos Musculares que trabaja"),
    )
    notes = models.TextField(max_length=300, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _("Equipo Gimnasio")
        verbose_name_plural = _("Equipos Gimnasio")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Exercise(models.Model):
    """
    Ejercicio individual del gimnasio.
    Sólo visible por cliente (solo consulta).
    """
    LEVEL_BEGINNER = "BEGINNER"
    LEVEL_INTERMEDIATE = "INTERMEDIATE"
    LEVEL_ADVANCED = "ADVANCED"
    LEVEL_CHOICES = (
        (LEVEL_BEGINNER, "Principiante"),
        (LEVEL_INTERMEDIATE, "Intermedio"),
        (LEVEL_ADVANCED, "Avanzado"),
    )

    name = models.CharField(verbose_name=_("Nombre Ejercicio"), max_length=120)
    slug = models.SlugField(unique=True)
    muscle_group = models.ForeignKey(
        MuscleGroup,
        on_delete=models.PROTECT,
        related_name="exercises",
        verbose_name=_("Grupo Muscular Principal"),
    )
    secondary_groups = models.ManyToManyField(
        MuscleGroup,
        blank=True,
        related_name="secondary_exercises",
        verbose_name=_("Grupos Musculares Secundarios"),
    )
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="exercises",
        verbose_name=_("Equipo Principal"),
    )
    difficulty_level = models.CharField(
        verbose_name=_("Nivel Dificultad"),
        max_length=20,
        choices=LEVEL_CHOICES,
        default=LEVEL_BEGINNER,
    )
    description = models.TextField(
        verbose_name=_("Instrucciones"),
        max_length=1000,
        help_text=_("Pasos detallados para realizar el ejercicio"),
    )
    tips = models.TextField(
        verbose_name=_("Consejos / Postura"),
        max_length=500,
        null=True,
        blank=True,
    )
    common_mistakes = models.TextField(
        verbose_name=_("Errores Comunes"),
        max_length=500,
        null=True,
        blank=True,
    )
    recommended_sets = models.PositiveIntegerField(
        verbose_name=_("Series recomendadas"),
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    recommended_reps_min = models.PositiveIntegerField(
        verbose_name=_("Repeticiones mínimas"),
        default=8,
    )
    recommended_reps_max = models.PositiveIntegerField(
        verbose_name=_("Repeticiones máximas"),
        default=12,
    )
    rest_seconds = models.PositiveIntegerField(
        verbose_name=_("Descanso (segundos)"),
        default=60,
        validators=[MinValueValidator(10), MaxValueValidator(600)],
    )
    estimated_calories_per_set = models.PositiveIntegerField(
        verbose_name=_("Calorías aprox por serie"),
        null=True,
        blank=True,
    )
    video_url = models.URLField(
        verbose_name=_("URL Video tutorial"),
        max_length=300,
        null=True,
        blank=True,
    )
    image = models.ImageField(
        upload_to="gym/exercises/%Y/%m/", null=True, blank=True,
    )
    is_active = models.BooleanField(verbose_name=_("Visible a clientes"), default=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="exercises_created",
        limit_choices_to={"role__in": [User.ROLE_ADMIN, User.ROLE_EMPLOYEE]},
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Ejercicio")
        verbose_name_plural = _("Ejercicios")
        ordering = ["muscle_group__name", "name"]

    def __str__(self):
        return f"{self.name} ({self.muscle_group.name})"


class Routine(models.Model):
    """
    Rutina preestablecida (colección de ejercicios).
    Puede ser genérica o asignada a un cliente específico.
    """
    GOAL_STRENGTH = "STRENGTH"
    GOAL_HYPERTROPHY = "HYPERTROPHY"
    GOAL_DEFINITION = "DEFINITION"
    GOAL_WEIGHT_LOSS = "WEIGHT_LOSS"
    GOAL_GENERAL = "GENERAL"
    GOAL_CHOICES = (
        (GOAL_STRENGTH, "Fuerza"),
        (GOAL_HYPERTROPHY, "Hipertrofia (Volumen)"),
        (GOAL_DEFINITION, "Definición"),
        (GOAL_WEIGHT_LOSS, "Pérdida de Peso"),
        (GOAL_GENERAL, "Acondicionamiento General"),
    )

    DURATION_SHORT = "SHORT"
    DURATION_MEDIUM = "MEDIUM"
    DURATION_LONG = "LONG"
    DURATION_CHOICES = (
        (DURATION_SHORT, "Corta (< 30 min)"),
        (DURATION_MEDIUM, "Media (30-60 min)"),
        (DURATION_LONG, "Larga (> 60 min)"),
    )

    name = models.CharField(verbose_name=_("Nombre Rutina"), max_length=150)
    description = models.TextField(
        verbose_name=_("Descripción"), max_length=500, null=True, blank=True
    )
    goal = models.CharField(
        verbose_name=_("Objetivo Principal"),
        max_length=30,
        choices=GOAL_CHOICES,
        default=GOAL_GENERAL,
        db_index=True,
    )
    duration = models.CharField(
        verbose_name=_("Duración Estimada"),
        max_length=20,
        choices=DURATION_CHOICES,
        default=DURATION_MEDIUM,
    )
    difficulty_level = models.CharField(
        verbose_name=_("Nivel Recomendado"),
        max_length=20,
        choices=Exercise.LEVEL_CHOICES,
        default=Exercise.LEVEL_BEGINNER,
    )
    frequency_days = models.PositiveIntegerField(
        verbose_name=_("Días por semana sugeridos"),
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(7)],
    )
    estimated_weeks = models.PositiveIntegerField(
        verbose_name=_("Duración sugerida en semanas"),
        default=8,
        validators=[MinValueValidator(1), MaxValueValidator(52)],
    )
    muscle_groups = models.ManyToManyField(
        MuscleGroup, related_name="routines", blank=True,
        verbose_name=_("Grupos Musculares involucrados"),
    )
    is_generic = models.BooleanField(
        verbose_name=_("Rutina Genérica (todos los clientes)"),
        default=True,
        db_index=True,
    )
    assigned_client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="assigned_routines",
        limit_choices_to={"role": User.ROLE_CLIENT},
        null=True,
        blank=True,
        verbose_name=_("Cliente específico (si no es genérica)"),
    )
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="routines_assigned",
        limit_choices_to={"role__in": [User.ROLE_ADMIN, User.ROLE_EMPLOYEE]},
        null=True,
        blank=True,
        verbose_name=_("Asignada por"),
    )
    valid_from = models.DateField(
        verbose_name=_("Válida desde"), null=True, blank=True
    )
    valid_until = models.DateField(
        verbose_name=_("Válida hasta"), null=True, blank=True
    )
    warm_up = models.TextField(
        verbose_name=_("Calentamiento"),
        max_length=500,
        null=True,
        blank=True,
        default=_("5-10 min caminata elíptica o trote suave + movilidad articular"),
    )
    cool_down = models.TextField(
        verbose_name=_("Enfriamiento / Estiramiento"),
        max_length=500,
        null=True,
        blank=True,
        default=_("5-10 min estiramiento global + respiración profunda"),
    )
    nutrition_tips = models.TextField(
        verbose_name=_("Recomendaciones Nutricionales"),
        max_length=700,
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(verbose_name=_("Activa"), default=True)
    image = models.ImageField(upload_to="gym/routines/%Y/%m/", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Rutina")
        verbose_name_plural = _("Rutinas")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_generic", "is_active", "goal"]),
        ]

    def __str__(self):
        tipo = "Genérica" if self.is_generic else f"Asignada a {self.assigned_client}"
        return f"{self.name} | {self.goal} | {tipo}"


class RoutineExercise(models.Model):
    """Ejercicio dentro de una rutina, con sus parámetros específicos."""
    routine = models.ForeignKey(
        Routine,
        on_delete=models.CASCADE,
        related_name="exercises",
        verbose_name=_("Rutina"),
    )
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.PROTECT,
        related_name="routine_instances",
        verbose_name=_("Ejercicio"),
    )
    order = models.PositiveIntegerField(
        verbose_name=_("Orden en la rutina"), default=0
    )
    sets = models.PositiveIntegerField(
        verbose_name=_("Series"),
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    reps = models.CharField(
        verbose_name=_("Repeticiones (ej: 10-12)"),
        max_length=30,
        default="10-12",
    )
    weight_kg = models.DecimalField(
        verbose_name=_("Peso sugerido (kg)"),
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
    )
    rest_seconds = models.PositiveIntegerField(
        verbose_name=_("Descanso (segundos)"),
        default=60,
    )
    notes = models.TextField(
        verbose_name=_("Notas específicas cliente"),
        max_length=300,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("Ejercicio en Rutina")
        verbose_name_plural = _("Ejercicios en Rutinas")
        ordering = ["routine", "order"]
        unique_together = ("routine", "exercise", "order")

    def __str__(self):
        return f"{self.routine.name} #{self.order}: {self.exercise.name} ({self.sets}x{self.reps})"


class WorkoutLog(models.Model):
    """
    Registro de una sesión de entrenamiento completada por un cliente.
    (Opcional - módulo cliente, para futuro tracking)
    """
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="workout_logs",
        limit_choices_to={"role": User.ROLE_CLIENT},
        verbose_name=_("Cliente"),
    )
    routine = models.ForeignKey(
        Routine,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="logs",
    )
    session_date = models.DateField(
        verbose_name=_("Fecha Sesión"), default=timezone.localdate, db_index=True
    )
    duration_minutes = models.PositiveIntegerField(
        verbose_name=_("Duración (min)"),
        validators=[MinValueValidator(1), MaxValueValidator(600)],
    )
    calories_burned = models.PositiveIntegerField(
        verbose_name=_("Calorías quemadas (aprox)"), null=True, blank=True
    )
    notes = models.TextField(max_length=500, null=True, blank=True)
    feeling = models.IntegerField(
        verbose_name=_("Sensación 1-10"),
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _("Registro Entrenamiento")
        verbose_name_plural = _("Registros Entrenamientos")
        ordering = ["-session_date"]
        indexes = [models.Index(fields=["client", "session_date"])]

    def __str__(self):
        return f"{self.client.username} | {self.session_date} | {self.duration_minutes}min"
