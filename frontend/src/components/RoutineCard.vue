<template>
  <div
    class="card flex flex-col gap-3 border-l-4 transition-all hover:shadow-lg cursor-pointer"
    :style="{ borderLeftColor: color }"
    @click="$emit('click')"
  >
    <div class="flex items-start justify-between gap-3">
      <div class="min-w-0">
        <div class="flex items-center gap-2">
          <span class="chip" :class="chipClasses">{{ goalDisplay }}</span>
          <span class="text-xs text-club-gray-500">{{ frequencyLabel }}</span>
        </div>
        <h3 class="font-bold text-club-graphite mt-1">{{ routine.name }}</h3>
      </div>
      <div class="shrink-0 w-10 h-10 rounded-xl bg-gradient-to-br flex items-center justify-center text-white"
           :style="{ background: `linear-gradient(135deg, ${color}, #232927)` }">
        <Dumbbell class="w-5 h-5" />
      </div>
    </div>
    <div class="grid grid-cols-3 gap-2 text-xs text-club-gray-600">
      <div class="flex flex-col items-center text-center p-2 bg-club-ivory rounded-lg">
        <Dumbbell class="w-4 h-4 text-club-area-gym mb-1" />
        <span class="font-semibold text-club-graphite-light">{{ countExercises }}</span>
        <span class="text-[11px]">Ejercicios</span>
      </div>
      <div class="flex flex-col items-center text-center p-2 bg-club-ivory rounded-lg">
        <CalendarDays class="w-4 h-4 text-club-wellness mb-1" />
        <span class="font-semibold text-club-graphite-light">{{ routine.frequency_days || 3 }}</span>
        <span class="text-[11px]">Días / sem</span>
      </div>
      <div class="flex flex-col items-center text-center p-2 bg-club-ivory rounded-lg">
        <Trophy class="w-4 h-4 text-club-gold mb-1" />
        <span class="font-semibold text-club-graphite-light">{{ routine.estimated_weeks || 8 }}</span>
        <span class="text-[11px]">Semanas</span>
      </div>
    </div>
    <p v-if="routine.description" class="text-xs text-club-gray-600 line-clamp-2">{{ routine.description }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Dumbbell, CalendarDays, Trophy } from 'lucide-vue-next'

const props = defineProps({
  routine: { type: Object, required: true },
})
defineEmits(['click'])

const GOALS = {
  STRENGTH: ['Fuerza', '#174C3C'],
  HYPERTROPHY: ['Hipertrofia', '#3B8064'],
  DEFINITION: ['Definición', '#D7AE58'],
  WEIGHT_LOSS: ['Pérdida de grasa', '#E9784A'],
  GENERAL: ['General', '#232927'],
}
const goalDisplay = computed(() => GOALS[props.routine.goal]?.[0] || props.routine.goal || 'Rutina')
const color = computed(() => GOALS[props.routine.goal]?.[1] || '#174C3C')
const chipClasses = computed(() => `bg-${color} text-white`.replace('bg-#', 'bg-[' + color.value + '] text-white'))
const countExercises = computed(() =>
  Array.isArray(props.routine.exercises) ? props.routine.exercises.length :
    (props.routine.exercises_count || props.routine.routine_exercises?.length || 0)
)
const frequencyLabel = computed(() => {
  if (props.routine.duration === 'SHORT') return 'Corta duración'
  if (props.routine.duration === 'LONG') return 'Larga duración'
  return 'Duración media'
})
</script>
