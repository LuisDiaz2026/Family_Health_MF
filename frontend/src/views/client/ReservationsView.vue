<template>
  <div class="page-padding space-y-4">
    <div class="flex items-center justify-between flex-wrap gap-3">
      <div>
        <h1 class="title-page">Mis reservas</h1>
        <p class="subtitle-page">Canchas, piscina, salones y gimnasio</p>
      </div>
      <button class="btn-primary" @click="$router.push({ name: 'client-reserve-create' })">
        <Plus class="w-4 h-4" /> Nueva reserva
      </button>
    </div>

    <div class="flex gap-2 overflow-x-auto pb-2 -mx-4 px-4">
      <button
        v-for="f in filters" :key="f.value"
        class="chip whitespace-nowrap !px-3 !py-1.5 !text-xs transition-all"
        :class="activeFilter === f.value
          ? 'bg-club-blue text-white'
          : 'bg-white border border-club-gray-200 text-club-gray-700'"
        @click="activeFilter = f.value"
      >{{ f.label }}</button>
    </div>

    <SkeletonLoader v-if="loading" />
    <EmptyState
      v-else-if="!filtered.length"
      icon="Calendar"
      title="Sin reservas en este estado"
      description="Selecciona otro filtro o crea una reserva nueva."
      cta-label="Crear reserva"
      @cta="$router.push({ name: 'client-reserve-create' })"
    />
    <div v-else class="space-y-3">
      <ReservationCard
        v-for="r in filtered"
        :key="r.id"
        v-bind="r"
        @cancel="cancelR(r)"
      />
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { Plus } from 'lucide-vue-next'
import { useReservationsStore } from '@/stores/reservations'
import ReservationCard from '@/components/ReservationCard.vue'
import EmptyState from '@/components/EmptyState.vue'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import { showToast } from '@/utils/toast'

const store = useReservationsStore()
const loading = computed(() => store.loading)
const activeFilter = ref('ALL')

const filters = [
  { label: 'Todas', value: 'ALL' },
  { label: 'Pendientes', value: 'PENDING' },
  { label: 'Confirmadas', value: 'CONFIRMED' },
  { label: 'Completadas', value: 'COMPLETED' },
  { label: 'Canceladas', value: 'CANCELLED' },
]

const filtered = computed(() => {
  const list = store.myReservations || []
  if (activeFilter.value === 'ALL') return list
  return list.filter(r => r.status === activeFilter.value)
})

async function cancelR(r) {
  try {
    await store.cancelReservation(r.id)
    await store.listMyReservations()
    showToast('Reserva cancelada.', 'success')
  } catch (e) {
    showToast(e || 'No se pudo cancelar.', 'error')
  }
}

onMounted(() => store.listMyReservations().catch(() => {}))
</script>
