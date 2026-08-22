<template>
  <div class="page-padding space-y-4">
    <button class="inline-flex items-center gap-1 text-club-blue font-bold text-sm hover:underline" @click="$router.back()">
      <ArrowLeft class="w-4 h-4" /> Volver a rutinas
    </button>

    <SkeletonLoader v-if="loading && !routine" />

    <template v-else-if="routine">
      <section class="rounded-2xl p-5 text-white relative overflow-hidden" :style="{ background: `linear-gradient(135deg, ${color}, #0f172a)` }">
        <div class="absolute -right-10 -bottom-10 w-40 h-40 rounded-full bg-white/10" />
        <div class="relative">
          <div class="chip bg-white/20 backdrop-blur text-white">{{ goalLabel }}</div>
          <h1 class="text-2xl font-black mt-2">{{ routine.name }}</h1>
          <p v-if="routine.description" class="mt-1 text-sm opacity-90">{{ routine.description }}</p>
          <div class="mt-4 grid grid-cols-4 gap-2 text-center">
            <div class="rounded-xl bg-white/15 backdrop-blur py-2">
              <div class="text-[10px] uppercase opacity-80 font-bold">Días</div>
              <div class="text-lg font-black">{{ routine.frequency_days }}</div>
            </div>
            <div class="rounded-xl bg-white/15 backdrop-blur py-2">
              <div class="text-[10px] uppercase opacity-80 font-bold">Semanas</div>
              <div class="text-lg font-black">{{ routine.estimated_weeks }}</div>
            </div>
            <div class="rounded-xl bg-white/15 backdrop-blur py-2">
              <div class="text-[10px] uppercase opacity-80 font-bold">Nivel</div>
              <div class="text-lg font-black">{{ levelShort }}</div>
            </div>
            <div class="rounded-xl bg-white/15 backdrop-blur py-2">
              <div class="text-[10px] uppercase opacity-80 font-bold">Ejs.</div>
              <div class="text-lg font-black">{{ exercises.length }}</div>
            </div>
          </div>
        </div>
      </section>

      <section v-if="routine.warm_up" class="card">
        <div class="section-title"><Flame class="w-4 h-4 text-club-amber" /> Calentamiento</div>
        <p class="text-sm text-club-gray-700 whitespace-pre-line leading-relaxed">{{ routine.warm_up }}</p>
      </section>

      <section>
        <div class="section-title">Ejercicios ({{ exercises.length }})</div>
        <div class="space-y-3">
          <div v-for="(e, i) in exercises" :key="(e.id || e.exercise_id || i)" class="card !p-3">
            <div class="flex items-start gap-3">
              <div class="w-10 h-10 rounded-xl bg-club-blue/10 text-club-blue flex items-center justify-center shrink-0 font-black">
                {{ i + 1 }}
              </div>
              <div class="flex-1 min-w-0">
                <div class="flex items-start justify-between gap-2">
                  <div class="min-w-0">
                    <h4 class="font-bold text-sm text-club-gray-900">{{ e.name || e.exercise?.name || ('Ejercicio ' + (i + 1)) }}</h4>
                    <div class="text-[11px] text-club-gray-500 mt-0.5">
                      {{ (e.muscle_group?.name) || (e.exercise?.muscle_group?.name) || '' }}
                      <span v-if="e.difficulty_level || e.exercise?.difficulty_level">
                        · Dificultad: {{ difficultyLabel(e.difficulty_level || e.exercise?.difficulty_level) }}
                      </span>
                    </div>
                  </div>
                  <span class="chip bg-club-blue/10 text-club-blue-dark whitespace-nowrap">{{ formatSets(e.sets || e.recommended_sets) }} × {{ e.reps || e.recommended_reps_min || '12' }}</span>
                </div>
                <div class="mt-2 grid grid-cols-3 gap-2 text-[11px]">
                  <div class="rounded-lg bg-club-gray-50 p-2 text-center">
                    <div class="text-club-gray-500">Series</div>
                    <div class="font-bold text-club-gray-900">{{ e.sets || e.recommended_sets || 3 }}</div>
                  </div>
                  <div class="rounded-lg bg-club-gray-50 p-2 text-center">
                    <div class="text-club-gray-500">Reps</div>
                    <div class="font-bold text-club-gray-900">{{ e.reps || (e.recommended_reps_min ? (e.recommended_reps_min + '-' + (e.recommended_reps_max || e.recommended_reps_min)) : '12-15') }}</div>
                  </div>
                  <div class="rounded-lg bg-club-gray-50 p-2 text-center">
                    <div class="text-club-gray-500">Descanso</div>
                    <div class="font-bold text-club-gray-900">{{ (e.rest_seconds || 60) }}s</div>
                  </div>
                </div>
                <p v-if="e.notes || e.description" class="mt-2 text-xs text-club-gray-600 italic">{{ e.notes || e.description }}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section v-if="routine.cool_down || routine.nutrition_tips" class="space-y-3">
        <div v-if="routine.cool_down" class="card">
          <div class="section-title"><Snowflake class="w-4 h-4 text-club-blue" /> Enfriamiento / estiramientos</div>
          <p class="text-sm text-club-gray-700 whitespace-pre-line leading-relaxed">{{ routine.cool_down }}</p>
        </div>
        <div v-if="routine.nutrition_tips" class="card">
          <div class="section-title"><Apple class="w-4 h-4 text-club-green" /> Tips nutricionales</div>
          <p class="text-sm text-club-gray-700 whitespace-pre-line leading-relaxed">{{ routine.nutrition_tips }}</p>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ArrowLeft, Flame, Snowflake, Apple } from 'lucide-vue-next'
import { useGymStore } from '@/stores/gym'
import SkeletonLoader from '@/components/SkeletonLoader.vue'

const route = useRoute()
const store = useGymStore()

const routine = ref(null)
const loading = computed(() => store.loading)

const GOALS = {
  STRENGTH: ['Fuerza', '#0ea5e9'],
  HYPERTROPHY: ['Hipertrofia', '#8b5cf6'],
  DEFINITION: ['Definición', '#10b981'],
  WEIGHT_LOSS: ['Pérdida de grasa', '#f59e0b'],
  GENERAL: ['General', '#0f172a'],
}
const goalLabel = computed(() => GOALS[routine.value?.goal]?.[0] || 'Rutina')
const color = computed(() => GOALS[routine.value?.goal]?.[1] || '#0ea5e9')
const levelShort = computed(() => {
  const levels = { BEGINNER: 'Princ', INTERMEDIATE: 'Inter', ADVANCED: 'Avan' }
  return levels[routine.value?.difficulty_level] || 'Prin'
})
const exercises = computed(() => {
  if (!routine.value) return []
  if (Array.isArray(routine.value.routine_exercises)) return routine.value.routine_exercises
  if (Array.isArray(routine.value.exercises)) return routine.value.exercises
  return []
})

function formatSets(n) { return n || 3 }
function difficultyLabel(l) {
  return { BEGINNER: 'Principiante', INTERMEDIATE: 'Intermedio', ADVANCED: 'Avanzado' }[l] || l || 'Intermedio'
}

onMounted(async () => {
  try {
    routine.value = await store.getRoutine(route.params.id)
  } catch (_) {
    routine.value = null
  }
})
</script>
