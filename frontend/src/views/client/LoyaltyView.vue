<template>
  <div class="page-padding space-y-4">
    <section class="rounded-2xl p-5 text-white relative overflow-hidden"
             :style="{ background: `linear-gradient(135deg, ${tierColor || '#0ea5e9'}, #0f172a)` }">
      <div class="absolute -right-10 -bottom-10 w-40 h-40 rounded-full bg-white/10" />
      <div class="relative flex items-center gap-3">
        <div class="w-14 h-14 rounded-2xl bg-white/20 backdrop-blur flex items-center justify-center text-2xl font-black border border-white/30">
          {{ initials }}
        </div>
        <div class="flex-1 min-w-0">
          <div class="text-xs uppercase tracking-wide opacity-80 font-bold">Nivel fidelidad</div>
          <div class="text-2xl font-black mt-0.5">{{ tier?.name || 'Bronce' }}</div>
          <div class="text-xs opacity-90 mt-1">{{ auth.displayName }}</div>
        </div>
      </div>
      <div class="mt-4 grid grid-cols-3 gap-2 text-center">
        <div class="rounded-xl bg-white/15 backdrop-blur px-2 py-3">
          <div class="text-[10px] uppercase opacity-80 font-bold">Puntos</div>
          <div class="text-2xl font-black">{{ auth.currentPoints }}</div>
        </div>
        <div class="rounded-xl bg-white/15 backdrop-blur px-2 py-3">
          <div class="text-[10px] uppercase opacity-80 font-bold">% Dcto</div>
          <div class="text-2xl font-black">{{ tier?.discount_percent || 0 }}%</div>
        </div>
        <div class="rounded-xl bg-white/15 backdrop-blur px-2 py-3">
          <div class="text-[10px] uppercase opacity-80 font-bold">Referidos</div>
          <div class="text-2xl font-black">{{ referrals }}</div>
        </div>
      </div>
      <div class="mt-4">
        <div class="flex justify-between text-[11px] opacity-90 font-semibold mb-1">
          <span>Progreso al próximo nivel</span>
          <span>{{ nextTier ? `${nextTier.min_points - current} pts faltantes` : '¡Máximo nivel!' }}</span>
        </div>
        <div class="h-2 rounded-full bg-white/20 overflow-hidden">
          <div class="h-full bg-white rounded-full" :style="{ width: progressPct + '%' }"></div>
        </div>
      </div>
    </section>

    <section>
      <div class="flex items-center justify-between">
        <div class="section-title">Niveles de fidelidad</div>
        <button class="text-xs font-bold text-club-blue hover:underline" @click="$router.push({ name: 'client-rewards' })">
          Canjear puntos
        </button>
      </div>
      <div class="space-y-2">
        <div v-for="t in tiers" :key="t.id"
             class="card flex items-center gap-3 !p-3"
             :class="{ 'ring-2 ring-club-blue bg-club-blue/5': t.name === tierName }">
          <div class="w-10 h-10 rounded-full flex items-center justify-center text-white font-black" :style="{ background: colorFor(t.name) }">
            {{ t.name.charAt(0) }}
          </div>
          <div class="flex-1 min-w-0">
            <div class="font-bold text-club-gray-900">{{ t.name }}</div>
            <div class="text-xs text-club-gray-500">Desde {{ t.min_points }} pts · {{ t.discount_percent }}% descuento</div>
          </div>
          <component v-if="t.name === tierName" :is="CheckCircle2" class="w-5 h-5 text-club-blue" />
        </div>
      </div>
    </section>

    <section>
      <div class="section-title">¿Cómo ganar puntos?</div>
      <div class="grid grid-cols-2 gap-3">
        <div v-for="r in rules" :key="r.id || r.action_type" class="card !p-3 flex flex-col gap-1">
          <div class="text-xs font-bold text-club-blue uppercase">{{ r.action_type }}</div>
          <div class="font-bold text-club-gray-900">{{ r.points_amount || 0 }} pts</div>
          <div class="text-[11px] text-club-gray-500 leading-snug">{{ r.description || '' }}</div>
        </div>
      </div>
    </section>

    <section>
      <div class="section-title">Movimientos recientes</div>
      <SkeletonLoader v-if="loadingTx" />
      <EmptyState v-else-if="!txList.length" icon="Receipt" title="Sin movimientos" description="Empieza a reservar y comprar para acumular puntos." />
      <div v-else class="space-y-2">
        <div v-for="t in txList" :key="t.id" class="card flex items-center gap-3 !p-3">
          <div class="w-9 h-9 rounded-xl flex items-center justify-center shrink-0"
               :class="t.amount >= 0 ? 'bg-club-green/15 text-club-green' : 'bg-club-red/15 text-club-red'">
            <TrendingUp v-if="t.amount >= 0" class="w-4 h-4" />
            <TrendingDown v-else class="w-4 h-4" />
          </div>
          <div class="flex-1 min-w-0">
            <div class="font-bold text-sm text-club-gray-900 truncate">{{ t.description || t.transaction_type }}</div>
            <div class="text-[11px] text-club-gray-500">{{ formatDate(t.created_at) }}</div>
          </div>
          <div class="font-black" :class="t.amount >= 0 ? 'text-club-green' : 'text-club-red'">
            {{ t.amount >= 0 ? '+' : '' }}{{ t.amount }}
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { CheckCircle2, TrendingUp, TrendingDown, Gift } from 'lucide-vue-next'
import { useRewardsStore } from '@/stores/rewards'
import { useAuthStore } from '@/stores/auth'
import EmptyState from '@/components/EmptyState.vue'
import SkeletonLoader from '@/components/SkeletonLoader.vue'

const store = useRewardsStore()
const auth = useAuthStore()
const tiers = ref([])
const rules = ref([])
const txList = ref([])
const loadingTx = ref(false)

const tier = computed(() => auth.tierInfo)
const tierName = computed(() => tier.value?.name || 'Bronce')
const current = computed(() => auth.currentPoints || 0)
const referrals = computed(() => auth.user?.loyalty?.referrals_count ?? auth.user?.referrals_count ?? 0)

const tierColor = computed(() => colorFor(tierName.value))
function colorFor(name) {
  switch ((name || '').toLowerCase()) {
    case 'plata': return '#94a3b8'
    case 'oro': return '#eab308'
    case 'diamante': return '#67e8f9'
    default: return '#cd7f32'
  }
}

const initials = computed(() => {
  const n = auth.displayName || 'U'
  const parts = n.split(' ').filter(Boolean)
  return (parts[0]?.[0] || '') + (parts[1]?.[0] || parts[0]?.[1] || '').toUpperCase()
})

const nextTier = computed(() => {
  const sorted = (tiers.value || []).slice().sort((a, b) => a.min_points - b.min_points)
  return sorted.find(t => t.min_points > current.value) || null
})
const progressPct = computed(() => {
  const sorted = (tiers.value || []).slice().sort((a, b) => a.min_points - b.min_points)
  const idx = sorted.findIndex(t => t.name === tierName.value)
  if (idx < 0) return 0
  const curMin = sorted[idx].min_points
  const next = sorted[idx + 1]
  if (!next) return 100
  const max = next.min_points
  const pct = Math.round((current.value - curMin) * 100 / (max - curMin))
  return Math.min(100, Math.max(0, pct))
})

function formatDate(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  return `${d.getDate()}/${d.getMonth() + 1}/${d.getFullYear()}`
}

onMounted(async () => {
  try { tiers.value = (await store.listTiers()) || tiers.value } catch (_) {}
  try {
    loadingTx.value = true
    txList.value = (await store.listMyTransactions()) || []
  } catch (_) {} finally { loadingTx.value = false }
  rules.value = [
    { action_type: 'RESERVA', points_amount: 100, description: 'Por cada reserva pagada' },
    { action_type: 'CONSUMO', points_amount: 20, description: 'Por cada $1.000 COP en barra' },
    { action_type: 'MEMBRESÍA', points_amount: 1000, description: 'Por renovación de membresía' },
    { action_type: 'REFIERE', points_amount: 2000, description: 'Cada amigo que se afilia' },
    { action_type: 'CUMPLEAÑOS', points_amount: 500, description: 'Puntos gratis en tu día' },
  ]
})
</script>
