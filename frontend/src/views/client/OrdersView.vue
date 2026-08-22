<template>
  <div class="page-padding space-y-4">
    <div class="flex items-center justify-between flex-wrap gap-2">
      <div>
        <h1 class="title-page">Mis pedidos</h1>
        <p class="subtitle-page">Refresquería · historial</p>
      </div>
      <button class="btn-primary" @click="$router.push({ name: 'client-refreshments' })">
        <Plus class="w-4 h-4" /> Nuevo pedido
      </button>
    </div>

    <div class="flex gap-2 overflow-x-auto pb-2 -mx-4 px-4">
      <button
        v-for="f in filters" :key="f.value"
        class="chip whitespace-nowrap !px-3 !py-1.5 !text-xs"
        :class="active === f.value ? 'bg-club-green text-white' : 'bg-white border border-club-gray-200 text-club-gray-700'"
        @click="active = f.value"
      >{{ f.label }}</button>
    </div>

    <SkeletonLoader v-if="loading" />
    <EmptyState v-else-if="!filtered.length" icon="ClipboardList" title="Sin pedidos" description="Aún no has realizado pedidos." cta-label="Ir a catálogo" @cta="$router.push({ name: 'client-refreshments' })" />
    <div v-else class="space-y-3">
      <div v-for="o in filtered" :key="o.id" class="card">
        <div class="flex items-start justify-between gap-2 mb-2">
          <div>
            <div class="font-bold text-club-gray-900">Pedido #{{ o.id }}</div>
            <div class="text-xs text-club-gray-500">{{ formatDate(o.created_at) }}</div>
          </div>
          <span class="chip" :class="statusChip(o.status)">{{ statusLabel(o.status) }}</span>
        </div>
        <div class="space-y-1.5 text-xs">
          <div v-for="it in (o.items || []).slice(0, 5)" :key="it.id || it.product_id" class="flex justify-between text-club-gray-600">
            <span>{{ it.quantity }}x {{ it.product_name || it.product?.name || 'Producto' }}</span>
            <span class="font-semibold">${{ Number(it.price || 0 * it.quantity).toLocaleString('es-CO') }}</span>
          </div>
        </div>
        <div class="mt-3 pt-3 border-t flex items-center justify-between text-sm">
          <div>
            <div class="text-xs text-club-gray-500">Total</div>
            <div class="font-black text-club-green text-lg">${{ Number(o.total_amount || 0).toLocaleString('es-CO') }}</div>
          </div>
          <span class="chip bg-club-gray-100 text-club-gray-700">{{ methodLabel(o.payment_method) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { Plus } from 'lucide-vue-next'
import { useRefreshmentsStore } from '@/stores/refreshments'
import EmptyState from '@/components/EmptyState.vue'
import SkeletonLoader from '@/components/SkeletonLoader.vue'

const store = useRefreshmentsStore()
const loading = computed(() => store.loading)
const active = ref('ALL')

const filters = [
  { label: 'Todos', value: 'ALL' },
  { label: 'Pendientes', value: 'PENDING' },
  { label: 'Preparando', value: 'PREPARING' },
  { label: 'Listos', value: 'READY' },
  { label: 'Pagados', value: 'PAID' },
  { label: 'Cancelados', value: 'CANCELLED' },
]

const filtered = computed(() => {
  const list = store.orders || []
  if (active.value === 'ALL') return list
  return list.filter(o => o.status === active.value)
})

const STATUS = {
  PENDING: ['chip bg-club-amber/15 text-[#b45309]', 'Pendiente'],
  PREPARING: ['chip bg-club-blue/15 text-club-blue-dark', 'Preparando'],
  READY: ['chip bg-club-purple/15 text-club-purple', 'Listo para retirar'],
  DELIVERED: ['chip bg-club-green/15 text-club-green-dark', 'Entregado'],
  PAID: ['chip bg-club-green/15 text-club-green-dark', 'Pagado'],
  CANCELLED: ['chip bg-club-red/15 text-club-red', 'Cancelado'],
}
function statusChip(s) { return STATUS[s]?.[0] || STATUS.PENDING[0] }
function statusLabel(s) { return STATUS[s]?.[1] || s || 'Pendiente' }

function methodLabel(m) {
  return { CASH: 'Efectivo', TRANSFER: 'Transferencia', CARD: 'Tarjeta', MEMBERSHIP: 'Prepagada' }[m] || m || 'Presencial'
}
function formatDate(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  return `${d.getDate()}/${d.getMonth() + 1}/${d.getFullYear()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

onMounted(() => store.listMyOrders().catch(() => {}))
</script>
