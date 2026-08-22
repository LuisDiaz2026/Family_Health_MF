<template>
  <div class="page-padding space-y-4">
    <div>
      <h1 class="title-page">Gimnasio</h1>
      <p class="subtitle-page">Rutinas preestablecidas para todos los niveles</p>
    </div>

    <div class="grid grid-cols-3 gap-2 text-center">
      <button
        v-for="g in goals"
        :key="g.value"
        class="card !p-2.5 transition-all"
        :class="goal === g.value ? 'ring-2 ring-club-blue bg-club-blue/5' : 'hover:bg-club-gray-50'"
        @click="goal = g.value"
      >
        <component :is="g.icon" class="w-5 h-5 mx-auto mb-1" :style="{ color: g.color }" />
        <div class="text-[11px] font-bold text-club-gray-800 leading-tight">{{ g.label }}</div>
      </button>
    </div>

    <SkeletonLoader v-if="loading" />
    <EmptyState v-else-if="!filtered.length" icon="Dumbbell" title="Sin rutinas" description="Ajusta el filtro de objetivo." />
    <div v-else class="space-y-3">
      <RoutineCard
        v-for="r in filtered"
        :key="r.id"
        :routine="r"
        @click="$router.push({ name: 'client-routine-detail', params: { id: r.id } })"
      />
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { Dumbbell, Heart, Target, Flame, Sparkles } from 'lucide-vue-next'
import { useGymStore } from '@/stores/gym'
import RoutineCard from '@/components/RoutineCard.vue'
import EmptyState from '@/components/EmptyState.vue'
import SkeletonLoader from '@/components/SkeletonLoader.vue'

const store = useGymStore()
const loading = computed(() => store.loading)
const goal = ref('ALL')

const goals = [
  { label: 'Todos', value: 'ALL', icon: Sparkles, color: '#0f172a' },
  { label: 'Fuerza', value: 'STRENGTH', icon: Dumbbell, color: '#0ea5e9' },
  { label: 'Hipertrofia', value: 'HYPERTROPHY', icon: Target, color: '#8b5cf6' },
  { label: 'Definición', value: 'DEFINITION', icon: Flame, color: '#10b981' },
  { label: 'Pérdida Grasa', value: 'WEIGHT_LOSS', icon: Heart, color: '#f59e0b' },
  { label: 'General', value: 'GENERAL', icon: Sparkles, color: '#0ea5e9' },
]

const filtered = computed(() => {
  const list = store.routines || []
  if (goal.value === 'ALL') return list
  return list.filter(r => r.goal === goal.value)
})

onMounted(() => store.listMyRoutines().catch(() => {}))
</script>
