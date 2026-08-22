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
        <h3 class="font-bold text-club-gray-900 mt-1">{{ routine.name }}</h3>
      </div>
      <div class="shrink-0 w-10 h-10 rounded-xl bg-gradient-to-br flex items-center justify-center text-white"
           :style="{ background: `linear-gradient(135deg, ${color}, #0f172a)` }">
        <Dumbbell class="w-5 h-5" />
      </div>
    </div>
    <div class="grid grid-cols-3 gap-2 text-xs text-club-gray-600">
      <div class="flex flex-col items-center text-center p-2 bg-club-gray-50 rounded-lg">
        <Dumbbell class="w-4 h-4 text-club-blue mb-1" />
        <span class="font-semibold text-club-gray-800">{{ countExercises }}</span>
        <span class="text-[11px]">Ejercicios</span>
      </div>
      <div class="flex flex-col items-center text-center p-2 bg-club-gray-50 rounded-lg">
        <CalendarDays class="w-4 h-4 text-club-green mb-1" />
        <span class="font-semibold text-club-gray-800">{{ routine.frequency_days || 3 }}</span>
        <span class="text-[11px]">Días / sem</span>
      </div>
      <div class="flex flex-col items-center text-center p-2 bg-club-gray-50 rounded-lg">
        <Trophy class="w-4 h-4 text-club-amber mb-1" />
        <span class="font-semibold text-club-gray-800">{{ routine.estimated_weeks || 8 }}</span>
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
  STRENGTH: ['Fuerza', '#0ea5e9'],
  HYPERTROPHY: ['Hipertrofia', '#8b5cf6'],
  DEFINITION: ['Definición', '#10b981'],
  WEIGHT_LOSS: ['Pérdida de grasa', '#f59e0b'],
  GENERAL: ['General', '#0f172a'],
}
const goalDisplay = computed(() => GOALS[props.routine.goal]?.[0] || props.routine.goal || 'Rutina')
const color = computed(() => GOALS[props.routine.goal]?.[1] || '#0ea5e9')
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
