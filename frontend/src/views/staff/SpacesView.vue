<template>
  <div class="page-padding space-y-4">
    <div>
      <h1 class="title-page">Espacios del club</h1>
      <p class="subtitle-page">Canchas, piscinas, salones y gimnasio</p>
    </div>

    <div class="relative">
      <Search class="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-club-gray-400" />
      <input v-model="q" class="input pl-9" placeholder="Buscar espacio..." />
    </div>

    <SkeletonLoader v-if="loading" />
    <EmptyState v-else-if="!filtered.length" icon="MapPin" title="Sin espacios" />
    <div v-else class="grid grid-cols-1 gap-3">
      <div v-for="s in filtered" :key="s.id" class="card !p-4">
        <div class="flex items-start justify-between gap-3">
          <div class="flex items-start gap-3 min-w-0 flex-1">
            <div class="w-12 h-12 rounded-xl bg-club-blue/10 text-club-blue flex items-center justify-center shrink-0">
              <MapPin class="w-5 h-5" />
            </div>
            <div class="min-w-0 flex-1">
              <div class="flex items-start justify-between gap-2">
                <div class="min-w-0">
                  <h3 class="font-bold text-club-gray-900 truncate">{{ s.name }}</h3>
                  <div class="text-xs text-club-gray-500">{{ s.space_type?.name || 'Espacio' }} · Código: {{ s.code || '-' }}</div>
                </div>
                <span class="chip whitespace-nowrap" :class="statusChip(s.status)">{{ statusLabel(s.status) }}</span>
              </div>
              <div class="mt-2 grid grid-cols-3 gap-1.5 text-[11px]">
                <div class="rounded-lg bg-club-gray-50 p-2 text-center">
                  <div class="text-club-gray-500">Tarifa</div>
                  <div class="font-bold text-club-gray-900">${{ formatMoney(s.hourly_rate) }}/h</div>
                </div>
                <div class="rounded-lg bg-club-gray-50 p-2 text-center">
                  <div class="text-club-gray-500">Capacidad</div>
                  <div class="font-bold text-club-gray-900">{{ s.max_capacity || 'N/A' }} pers</div>
                </div>
                <div class="rounded-lg bg-club-gray-50 p-2 text-center">
                  <div class="text-club-gray-500">Antelación</div>
                  <div class="font-bold text-club-gray-900">{{ s.advance_days_limit || 30 }} días</div>
                </div>
              </div>
              <div class="mt-2 flex flex-wrap gap-1.5 items-center">
                <span v-if="s.requires_employee_approval" class="chip bg-club-amber/15 text-[#b45309] !text-[10px]">Requiere aprobación</span>
                <span v-else class="chip bg-club-green/15 text-club-green-dark !text-[10px]">Confirmación instantánea</span>
                <span class="chip bg-club-blue/10 text-club-blue-dark !text-[10px]">Mín: {{ s.min_reservation_minutes || 0 }} min</span>
                <span class="chip bg-club-blue/10 text-club-blue-dark !text-[10px]">Máx: {{ s.max_reservation_minutes || 0 }} min</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { Search, MapPin } from 'lucide-vue-next'
import api from '@/api/client'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import EmptyState from '@/components/EmptyState.vue'

const spaces = ref([])
const loading = ref(true)
const q = ref('')

const filtered = computed(() => {
  const s = q.value.trim().toLowerCase()
  if (!s) return spaces.value
  return spaces.value.filter(sp =>
    String(sp.name || '').toLowerCase().includes(s) ||
    String(sp.code || '').toLowerCase().includes(s)
  )
})

const STATUS = {
  ACTIVE: ['chip bg-club-green/15 text-club-green-dark', 'Activo'],
  MAINTENANCE: ['chip bg-club-amber/15 text-[#b45309]', 'Mantenimiento'],
  INACTIVE: ['chip bg-club-gray-200 text-club-gray-700', 'Inactivo'],
}
function statusChip(s) { return STATUS[s]?.[0] || STATUS.ACTIVE[0] }
function statusLabel(s) { return STATUS[s]?.[1] || s || 'Activo' }

function formatMoney(n) { return Number(n || 0).toLocaleString('es-CO') }

onMounted(async () => {
  loading.value = true
  try {
    const resp = await api.get('/reservations/spaces/?page_size=100')
    spaces.value = resp.data?.results || resp.data || []
  } finally { loading.value = false }
})
</script>
