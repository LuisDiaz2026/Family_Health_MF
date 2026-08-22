<template>
  <div class="page-padding space-y-4">
    <div>
      <h1 class="title-page">Panel principal</h1>
      <p class="subtitle-page">{{ auth.isAdmin ? 'Panel Administrador' : 'Panel Recepción' }}</p>
    </div>

    <SkeletonLoader v-if="loading" />
    <template v-else-if="summary">
      <div class="grid grid-cols-2 gap-3">
        <Kpi icon="Users" color="#0ea5e9" label="Usuarios activos" :value="summary.users_total ?? summary.total_users" />
        <Kpi icon="UserPlus" color="#10b981" label="Clientes" :value="summary.clients_total" />
        <Kpi icon="MapPin" color="#8b5cf6" label="Espacios club" :value="summary.spaces_total" />
        <Kpi icon="CalendarCheck" color="#f59e0b" label="Reservas totales" :value="summary.reservations_total" />
        <Kpi icon="ShoppingBag" color="#ef4444" label="Pedidos refrescos" :value="summary.orders_total" />
        <Kpi icon="DollarSign" color="#10b981" label="Ingresos mes" :value="'$' + formatMoney(summary.total_revenue_month ?? 0)" money />
      </div>

      <div class="grid grid-cols-4 gap-2 text-center">
        <StatBox icon="Clock" bg="bg-club-amber/15" text="text-[#b45309]" label="Pendientes" :value="summary.reservations_pending" />
        <StatBox icon="CheckCircle2" bg="bg-club-blue/15" text="text-club-blue-dark" label="Confirmadas" :value="summary.reservations_confirmed" />
        <StatBox icon="XCircle" bg="bg-club-red/15" text="text-club-red" label="Canceladas" :value="summary.reservations_cancelled" />
        <StatBox icon="Trophy" bg="bg-club-green/15" text="text-club-green-dark" label="Completadas" :value="(summary.reservations_total||0) - ((summary.reservations_pending||0)+(summary.reservations_confirmed||0)+(summary.reservations_cancelled||0))" />
      </div>

      <div class="card">
        <div class="section-title"><Award class="w-4 h-4 text-club-amber" /> Niveles de fidelidad</div>
        <div class="grid grid-cols-2 gap-2">
          <div v-for="t in summary.active_tiers || []" :key="t.id" class="p-3 rounded-xl bg-club-gray-50 border border-club-gray-100">
            <div class="flex items-center justify-between">
              <span class="font-bold text-sm text-club-gray-900">{{ t.name }}</span>
              <span class="chip text-[10px] !py-0.5" :style="{ background: (t.color || '#94a3b8') + '20', color: (t.color || '#94a3b8') }">{{ t.users }} clientes</span>
            </div>
            <div class="mt-1 h-2 rounded-full bg-club-gray-200 overflow-hidden">
              <div class="h-full rounded-full" :style="{ background: t.color || '#94a3b8', width: Math.min(100, (t.users / Math.max(1, summary.clients_total || 1)) * 100) + '%' }"></div>
            </div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="flex items-center justify-between">
          <div class="section-title !mb-0"><Crown class="w-4 h-4 text-club-amber" /> Top 5 clientes</div>
          <button class="text-xs font-bold text-club-blue hover:underline" @click="$router.push({ name: 'staff-clients' })">Ver todos</button>
        </div>
        <SkeletonLoader v-if="loadingClients" />
        <div v-else class="space-y-2 mt-3">
          <div v-for="(c, i) in topClients" :key="c.id" class="flex items-center gap-3 p-2.5 rounded-xl bg-club-gray-50">
            <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-club-blue to-club-green text-white font-black flex items-center justify-center text-sm">
              {{ i + 1 }}
            </div>
            <div class="flex-1 min-w-0">
              <div class="font-bold text-sm text-club-gray-900 truncate">{{ c.first_name }} {{ c.last_name }} ({{ c.username }})</div>
              <div class="text-[11px] text-club-gray-500">
                {{ c.reservations_count || 0 }} reservas · {{ c.orders_count || 0 }} pedidos
              </div>
            </div>
            <div class="text-right">
              <div class="font-black text-club-green">${{ formatMoney(c.total_spent || 0) }}</div>
              <div class="text-[10px] text-club-gray-500 uppercase font-bold">Gastado</div>
            </div>
          </div>
          <EmptyState v-if="!topClients.length" icon="Users" title="Sin datos" description="Aún no hay clientes con gasto." />
        </div>
      </div>

      <div class="grid grid-cols-2 gap-3">
        <button class="card !text-left !p-4 hover:-translate-y-0.5 transition-all" @click="$router.push({ name: 'staff-reservations' })">
          <Calendar class="w-8 h-8 text-club-blue mb-2" />
          <div class="font-bold text-club-gray-900">Gestionar reservas</div>
          <div class="text-xs text-club-gray-500">Aprobar, cancelar y ver horarios</div>
        </button>
        <button class="card !text-left !p-4 hover:-translate-y-0.5 transition-all" @click="$router.push({ name: 'staff-orders' })">
          <Package class="w-8 h-8 text-club-green mb-2" />
          <div class="font-bold text-club-gray-900">Pedidos barra</div>
          <div class="text-xs text-club-gray-500">Marcar como listos y cobrar</div>
        </button>
        <button class="card !text-left !p-4 hover:-translate-y-0.5 transition-all" @click="$router.push({ name: 'staff-products' })">
          <ShoppingBag class="w-8 h-8 text-club-red mb-2" />
          <div class="font-bold text-club-gray-900">Inventario productos</div>
          <div class="text-xs text-club-gray-500">Stock, precios y SKU</div>
        </button>
        <button class="card !text-left !p-4 hover:-translate-y-0.5 transition-all" @click="$router.push({ name: 'staff-reports' })">
          <BarChart3 class="w-8 h-8 text-club-purple mb-2" />
          <div class="font-bold text-club-gray-900">Reportes</div>
          <div class="text-xs text-club-gray-500">Ingresos, ocupación, tendencias</div>
        </button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, h } from 'vue'
import { Users, UserPlus, MapPin, CalendarCheck, ShoppingBag, DollarSign, Clock, CheckCircle2, XCircle, Trophy, Crown, Calendar, Package, BarChart3, Award } from 'lucide-vue-next'
import { useReportsStore } from '@/stores/reports'
import { useAuthStore } from '@/stores/auth'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import EmptyState from '@/components/EmptyState.vue'

const reports = useReportsStore()
const auth = useAuthStore()
const summary = ref(null)
const topClients = ref([])
const loadingClients = ref(false)

const loading = computed(() => reports.loading && !summary.value)

const iconMap = { Users, UserPlus, MapPin, CalendarCheck, ShoppingBag, DollarSign, Clock, CheckCircle2, XCircle, Trophy }
const Kpi = {
  props: ['icon', 'color', 'label', 'value', 'money'],
  setup(props) {
    const I = iconMap[props.icon] || DollarSign
    return () => h('div', { class: 'card !p-4' }, [
      h('div', { class: 'flex items-center justify-between' }, [
        h('span', { class: 'text-xs font-bold uppercase text-club-gray-500' }, props.label),
        h('div', {
          class: 'w-9 h-9 rounded-xl flex items-center justify-center text-white shrink-0',
          style: { background: props.color }
        }, [h(I, { class: 'w-4 h-4' })])
      ]),
      h('div', { class: 'text-2xl font-black mt-2 text-club-gray-900' }, props.value)
    ])
  }
}

const StatBox = {
  props: ['icon', 'bg', 'text', 'label', 'value'],
  setup(props) {
    const I = iconMap[props.icon] || CheckCircle2
    return () => h('div', { class: ['p-2.5 rounded-xl border border-club-gray-100 bg-white'], key: props.label }, [
      h('div', { class: ['w-9 h-9 mx-auto rounded-xl flex items-center justify-center', props.bg] }, [
        h(I, { class: ['w-4 h-4', props.text] })
      ]),
      h('div', { class: 'text-center mt-1.5 text-lg font-black text-club-gray-900' }, props.value),
      h('div', { class: 'text-center text-[10px] uppercase font-bold text-club-gray-500' }, props.label),
    ])
  }
}

function formatMoney(n) {
  const v = Number(n || 0)
  return v.toLocaleString('es-CO')
}

onMounted(async () => {
  try { summary.value = await reports.getDashboardSummary() } catch (_) {}
  try {
    loadingClients.value = true
    topClients.value = await reports.getTopClients(5)
  } catch (_) {} finally {
    loadingClients.value = false
  }
})
</script>
