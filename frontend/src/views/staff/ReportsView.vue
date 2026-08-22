<template>
  <div class="page-padding space-y-4">
    <div>
      <h1 class="title-page">Reportes operativos</h1>
      <p class="subtitle-page">Métricas y tendencias del club</p>
    </div>

    <SkeletonLoader v-if="loading" />
    <template v-else>
      <div v-if="summary" class="card space-y-4">
        <div class="section-title">📊 Resumen</div>
        <div class="grid grid-cols-2 gap-3 text-sm">
          <Metric label="Usuarios activos" :value="summary.users_total" />
          <Metric label="Clientes registrados" :value="summary.clients_total" />
          <Metric label="Empleados" :value="summary.employees_total" />
          <Metric label="Nuevos clientes (30d)" :value="summary.new_clients_last_30_days" />
          <Metric label="Reservas totales" :value="summary.reservations_total" />
          <Metric label="Reservas hoy" :value="summary.reservations_today" />
          <Metric label="Pedidos refrescos" :value="summary.orders_total" />
          <Metric label="Pedidos hoy" :value="summary.orders_today" />
        </div>
      </div>

      <div class="card space-y-4">
        <div class="section-title">💰 Ingresos y ocupación</div>
        <div class="grid grid-cols-2 gap-3">
          <Metric label="Ingresos mes (reservas)" :value="'$' + formatMoney(summary?.reservations_revenue_month)" money />
          <Metric label="Ingresos mes (barra)" :value="'$' + formatMoney(summary?.orders_revenue_month)" money />
          <Metric label="TOTAL MES" highlight :value="'$' + formatMoney(summary?.total_revenue_month)" money />
          <Metric label="% Ocupación (7d)" :value="(summary?.occupancy_rate_last_7 ?? 0) + '%'" />
        </div>
      </div>

      <div class="card space-y-4">
        <div class="section-title">🏆 Puntos y fidelidad</div>
        <div class="grid grid-cols-2 gap-3">
          <Metric label="Puntos distribuidos" :value="summary?.points_distributed || 0" />
          <Metric label="Puntos canjeados" :value="summary?.points_redeemed || 0" />
        </div>
        <div class="mt-2">
          <div class="text-xs font-bold uppercase text-club-gray-500 mb-2">Distribución por niveles</div>
          <div v-for="t in (summary?.active_tiers || [])" :key="t.id" class="mb-2">
            <div class="flex justify-between text-xs mb-1">
              <span class="font-bold text-club-gray-700">{{ t.name }}</span>
              <span class="text-club-gray-500">{{ t.users }} clientes</span>
            </div>
            <div class="h-2 rounded-full bg-club-gray-200 overflow-hidden">
              <div class="h-full rounded-full transition-all"
                   :style="{ background: t.color || '#0ea5e9', width: pct(t.users) + '%' }"></div>
            </div>
          </div>
        </div>
      </div>

      <div class="card space-y-4">
        <div class="section-title">🥇 Top 10 clientes por gasto</div>
        <SkeletonLoader v-if="loadingTop" />
        <EmptyState v-else-if="!topClients.length" icon="Users" title="Sin datos" />
        <div v-else class="space-y-1.5">
          <div v-for="(c, i) in topClients" :key="c.id" class="flex items-center gap-3 p-2 rounded-lg hover:bg-club-gray-50">
            <div class="w-7 h-7 rounded-lg bg-gradient-to-br from-club-amber to-club-red text-white text-xs font-black flex items-center justify-center shrink-0">
              {{ i + 1 }}
            </div>
            <div class="flex-1 min-w-0 text-xs">
              <div class="font-bold text-club-gray-900 truncate">{{ c.first_name }} {{ c.last_name }}</div>
              <div class="text-club-gray-500">{{ c.username }}</div>
            </div>
            <div class="text-right shrink-0 text-xs">
              <div class="font-black text-club-green">${{ formatMoney(c.total_spent || 0) }}</div>
              <div class="text-club-gray-500">{{ c.reservations_count || 0 }}R · {{ c.orders_count || 0 }}P</div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, h } from 'vue'
import { Users } from 'lucide-vue-next'
import { useReportsStore } from '@/stores/reports'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import EmptyState from '@/components/EmptyState.vue'

const reports = useReportsStore()
const summary = ref(null)
const topClients = ref([])
const loadingTop = ref(false)

const loading = computed(() => reports.loading && !summary.value)

const Metric = {
  props: ['label', 'value', 'money', 'highlight'],
  setup(props) {
    return () => h('div', {
      class: [
        'p-3 rounded-xl border',
        props.highlight ? 'border-club-green/30 bg-club-green/5' : 'border-club-gray-100 bg-white'
      ]
    }, [
      h('div', { class: 'text-[10px] uppercase tracking-wide font-bold text-club-gray-500' }, props.label),
      h('div', {
        class: ['mt-1 font-black text-club-gray-900 text-lg', props.highlight ? '!text-club-green-dark !text-xl' : '']
      }, props.value ?? 0)
    ])
  }
}

const totalClients = computed(() => Math.max(1, summary.value?.clients_total || 1))
function pct(users) { return Math.min(100, Math.round((users || 0) / totalClients.value * 100)) }
function formatMoney(n) { return Number(n || 0).toLocaleString('es-CO') }

onMounted(async () => {
  try { summary.value = await reports.getDashboardSummary() } catch (_) {}
  try {
    loadingTop.value = true
    topClients.value = await reports.getTopClients(10)
  } catch (_) {} finally { loadingTop.value = false }
})
</script>
