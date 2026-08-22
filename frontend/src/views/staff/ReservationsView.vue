<template>
  <div class="page-padding space-y-4">
    <div>
      <h1 class="title-page">Gestión de reservas</h1>
      <p class="subtitle-page">Aprobar, cancelar y marcar como completadas</p>
    </div>

    <div class="flex gap-2 overflow-x-auto pb-2 -mx-4 px-4">
      <button
        v-for="f in filters"
        :key="f.value"
        class="chip whitespace-nowrap !px-3 !py-1.5 !text-xs"
        :class="active === f.value ? 'bg-club-blue text-white' : 'bg-white border border-club-gray-200 text-club-gray-700'"
        @click="active = f.value"
      >{{ f.label }}</button>
    </div>

    <SkeletonLoader v-if="loading" />
    <EmptyState v-else-if="!list.length" icon="Calendar" title="Sin reservas" description="No hay reservas para este filtro." />
    <div v-else class="space-y-3">
      <div v-for="r in filtered" :key="r.id" class="card space-y-3">
        <div class="flex items-start justify-between gap-2">
          <div class="min-w-0">
            <div class="flex items-center gap-2">
              <span class="chip" :class="statusChip(r.status)">{{ statusLabel(r.status) }}</span>
              <span class="chip bg-club-gray-100 text-club-gray-700 !text-[10px]">#{{ r.id }}</span>
            </div>
            <div class="font-bold text-sm text-club-gray-900 mt-1.5">{{ r.space?.name || r.space_name || 'Espacio' }}</div>
            <div class="text-xs text-club-gray-500 mt-0.5">{{ formatDateTime(r.start_time) }} a {{ formatHour(r.end_time) }}</div>
            <div class="text-xs text-club-gray-600 mt-0.5">
              <span class="font-semibold">Cliente:</span>
              {{ r.client?.first_name ? `${r.client.first_name} ${r.client.last_name}` : r.client?.username || 'N/A' }}
            </div>
          </div>
          <div class="text-right shrink-0">
            <div class="text-xs text-club-gray-500">Total</div>
            <div class="font-black text-club-green text-lg">${{ formatMoney(r.total_amount) }}</div>
          </div>
        </div>
        <div class="flex gap-2 flex-wrap pt-2 border-t">
          <button v-if="r.status === 'PENDING'" class="btn-success !py-1.5 !text-xs" @click="update(r, 'confirm')">Confirmar</button>
          <button v-if="['PENDING', 'CONFIRMED'].includes(r.status)" class="btn-danger !py-1.5 !text-xs" @click="update(r, 'cancel')">Cancelar</button>
          <button v-if="r.status === 'CONFIRMED'" class="btn-primary !py-1.5 !text-xs" @click="update(r, 'complete')">Marcar completada</button>
          <button v-if="r.payment_status === 'PENDING'" class="btn-secondary !py-1.5 !text-xs" @click="update(r, 'pay')">Marcar pagado</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { Calendar } from 'lucide-vue-next'
import api from '@/api/client'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import EmptyState from '@/components/EmptyState.vue'
import { showToast } from '@/utils/toast'

const list = ref([])
const loading = ref(true)
const active = ref('ALL')

const filters = [
  { label: 'Todas', value: 'ALL' },
  { label: 'Pendientes', value: 'PENDING' },
  { label: 'Confirmadas', value: 'CONFIRMED' },
  { label: 'Completadas', value: 'COMPLETED' },
  { label: 'Canceladas', value: 'CANCELLED' },
]
const filtered = computed(() => active.value === 'ALL' ? list.value : list.value.filter(r => r.status === active.value))

const STATUS = {
  PENDING: ['chip bg-club-amber/15 text-[#b45309] border border-club-amber/30', 'Pendiente'],
  CONFIRMED: ['chip bg-club-blue/15 text-club-blue-dark border border-club-blue/30', 'Confirmada'],
  COMPLETED: ['chip bg-club-green/15 text-club-green-dark border border-club-green/30', 'Completada'],
  CANCELLED: ['chip bg-club-red/15 text-club-red border border-club-red/30', 'Cancelada'],
}
function statusChip(s) { return STATUS[s]?.[0] || STATUS.PENDING[0] }
function statusLabel(s) { return STATUS[s]?.[1] || s || 'Pendiente' }

function pad(n) { return String(n).padStart(2, '0') }
function formatHour(iso) { const d = new Date(iso); return `${pad(d.getHours())}:${pad(d.getMinutes())}` }
function formatDateTime(iso) { const d = new Date(iso); return `${pad(d.getDate())}/${pad(d.getMonth() + 1)} · ${formatHour(iso)}` }
function formatMoney(n) { return Number(n || 0).toLocaleString('es-CO') }

async function load() {
  loading.value = true
  try {
    const resp = await api.get('/reservations/reservations/?all=1&page_size=200')
    list.value = resp.data?.results || resp.data || []
  } finally {
    loading.value = false
  }
}

async function update(r, action) {
  try {
    if (action === 'confirm') await api.post(`/reservations/reservations/${r.id}/confirm/`)
    else if (action === 'cancel') await api.post(`/reservations/reservations/${r.id}/cancel/`)
    else if (action === 'complete') await api.patch(`/reservations/reservations/${r.id}/`, { status: 'COMPLETED' })
    else if (action === 'pay') await api.post(`/reservations/reservations/${r.id}/mark-paid/`)
    showToast('Reserva actualizada.', 'success')
    await load()
  } catch (e) {
    try { await api.patch(`/reservations/reservations/${r.id}/`, { status: action === 'cancel' ? 'CANCELLED' : (action === 'confirm' ? 'CONFIRMED' : r.status), payment_status: action === 'pay' ? 'PAID' : r.payment_status })
      showToast('Reserva actualizada.', 'success')
      await load()
    } catch (err) {
      showToast('No se pudo actualizar. Revisa permisos.', 'error')
    }
  }
}

onMounted(load)
</script>
