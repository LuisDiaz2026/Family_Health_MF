<template>
  <div class="page-padding space-y-4">
    <div>
      <h1 class="title-page">Pedidos de barra</h1>
      <p class="subtitle-page">Prepara, entrega y marca como pagados.</p>
    </div>

    <div class="flex gap-2 overflow-x-auto pb-2 -mx-4 px-4">
      <button
        v-for="f in filters"
        :key="f.value"
        class="chip whitespace-nowrap !px-3 !py-1.5 !text-xs"
        :class="active === f.value ? 'bg-club-green text-white' : 'bg-white border border-club-gray-200 text-club-gray-700'"
        @click="active = f.value"
      >{{ f.label }}</button>
    </div>

    <SkeletonLoader v-if="loading" />
    <EmptyState v-else-if="!filtered.length" icon="ClipboardList" title="Sin pedidos en este estado" />
    <div v-else class="space-y-3">
      <div v-for="o in filtered" :key="o.id" class="card space-y-3">
        <div class="flex items-start justify-between gap-2">
          <div>
            <div class="flex items-center gap-2">
              <span class="chip" :class="statusChip(o.status)">{{ statusLabel(o.status) }}</span>
              <span class="chip bg-club-gray-100 text-club-gray-700 !text-[10px]">Pedido #{{ o.id }}</span>
            </div>
            <div class="mt-1 text-xs text-club-gray-600">
              <span class="font-bold">Cliente:</span> {{ clientName(o) }}
            </div>
            <div class="text-xs text-club-gray-500">{{ formatDateTime(o.created_at) }}</div>
          </div>
          <div class="text-right shrink-0">
            <div class="text-xs text-club-gray-500">Total</div>
            <div class="font-black text-club-green text-lg">${{ formatMoney(o.total_amount) }}</div>
            <div class="text-[10px] text-club-gray-500 mt-0.5">{{ methodLabel(o.payment_method) }}</div>
          </div>
        </div>
        <div class="rounded-xl bg-club-gray-50 divide-y divide-club-gray-200">
          <div v-for="it in (o.items || []).slice(0, 10)" :key="it.id || it.product_id" class="flex items-center justify-between p-2 text-xs">
            <div>
              <span class="font-bold text-club-gray-900">{{ it.quantity }}x</span>
              <span class="ml-1 text-club-gray-800">{{ it.product_name || it.product?.name }}</span>
            </div>
            <span class="font-semibold text-club-gray-700">${{ formatMoney(Number(it.price || 0) * Number(it.quantity || 1)) }}</span>
          </div>
        </div>
        <div v-if="o.notes" class="text-xs text-club-gray-600 bg-club-amber/5 p-2 rounded-lg border border-club-amber/20">
          <span class="font-bold">Notas:</span> {{ o.notes }}
        </div>
        <div class="flex flex-wrap gap-2 pt-2 border-t">
          <button v-if="o.status === 'PENDING'" class="btn-primary !py-1.5 !text-xs" @click="update(o, 'PREPARING')">Preparar</button>
          <button v-if="o.status === 'PREPARING'" class="btn-success !py-1.5 !text-xs" @click="update(o, 'READY')">Listo para retirar</button>
          <button v-if="['READY', 'DELIVERED'].includes(o.status) && o.status !== 'PAID'" class="btn-success !py-1.5 !text-xs" @click="update(o, 'PAID')">Marcar pagado y entregado</button>
          <button v-if="['PENDING', 'PREPARING', 'READY'].includes(o.status)" class="btn-danger !py-1.5 !text-xs" @click="update(o, 'CANCELLED')">Cancelar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ClipboardList } from 'lucide-vue-next'
import api from '@/api/client'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import EmptyState from '@/components/EmptyState.vue'
import { showToast } from '@/utils/toast'

const list = ref([])
const loading = ref(true)
const active = ref('ALL')

const filters = [
  { label: 'Todos', value: 'ALL' },
  { label: 'Pendientes', value: 'PENDING' },
  { label: 'Preparando', value: 'PREPARING' },
  { label: 'Listos', value: 'READY' },
  { label: 'Pagados/Entregados', value: 'PAID' },
  { label: 'Cancelados', value: 'CANCELLED' },
]
const filtered = computed(() => active.value === 'ALL' ? list.value : list.value.filter(o => o.status === active.value))

const STATUS = {
  PENDING: ['chip bg-club-amber/15 text-[#b45309]', 'Pendiente'],
  PREPARING: ['chip bg-club-blue/15 text-club-blue-dark', 'Preparando'],
  READY: ['chip bg-club-purple/15 text-club-purple', 'Listo'],
  DELIVERED: ['chip bg-club-green/15 text-club-green-dark', 'Entregado'],
  PAID: ['chip bg-club-green/15 text-club-green-dark', 'Pagado'],
  CANCELLED: ['chip bg-club-red/15 text-club-red', 'Cancelado'],
}
function statusChip(s) { return STATUS[s]?.[0] || STATUS.PENDING[0] }
function statusLabel(s) { return STATUS[s]?.[1] || s || 'Pendiente' }

function clientName(o) {
  if (o.client?.first_name) return `${o.client.first_name} ${o.client.last_name} (${o.client.username})`
  return o.client?.username || 'N/A'
}
function methodLabel(m) { return { CASH: 'Efectivo', TRANSFER: 'Transferencia', CARD: 'Tarjeta', MEMBERSHIP: 'Prepagada' }[m] || m || 'Presencial' }
function pad(n) { return String(n).padStart(2, '0') }
function formatDateTime(iso) { const d = new Date(iso); return `${pad(d.getDate())}/${pad(d.getMonth() + 1)}/${d.getFullYear()} ${pad(d.getHours())}:${pad(d.getMinutes())}` }
function formatMoney(n) { return Number(n || 0).toLocaleString('es-CO') }

async function load() {
  loading.value = true
  try {
    const resp = await api.get('/refreshments/orders/?all=1&page_size=200')
    list.value = resp.data?.results || resp.data || []
  } finally {
    loading.value = false
  }
}

async function update(o, status) {
  try {
    await api.patch(`/refreshments/orders/${o.id}/`, { status })
    showToast('Pedido actualizado.', 'success')
    await load()
  } catch (e) {
    showToast('No se pudo actualizar el pedido.', 'error')
  }
}

onMounted(load)
</script>
