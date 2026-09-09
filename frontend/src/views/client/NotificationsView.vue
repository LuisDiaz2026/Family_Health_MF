<template>
  <div class="page-padding space-y-4">
    <div>
      <h1 class="title-page">Notificaciones</h1>
      <p class="subtitle-page">Mantente informado sobre tu actividad</p>
    </div>

    <SkeletonLoader v-if="loading" />
    <EmptyState v-else-if="!list.length" icon="BellRing" title="Sin notificaciones" description="Tu bandeja está vacía." />
    <div v-else class="space-y-2">
      <div
        v-for="n in list"
        :key="n.id"
        class="card !p-3 flex gap-3 cursor-pointer transition-all"
        :class="{ 'ring-2 ring-club-forest/30 bg-club-forest/5': !n.is_read }"
        @click="markRead(n)"
      >
        <div class="w-10 h-10 rounded-xl flex items-center justify-center shrink-0" :class="styleFor(n.type).bg">
          <component :is="styleFor(n.type).icon" :class="styleFor(n.type).text + ' w-5 h-5'" />
        </div>
        <div class="flex-1 min-w-0">
          <div class="flex items-start justify-between gap-2">
            <div class="font-bold text-sm text-club-graphite truncate">{{ n.title || n.type }}</div>
            <div class="flex items-center justify-between gap-2 shrink-0">
              <span v-if="!n.is_read" class="w-2 h-2 rounded-full bg-club-forest"></span>
              <span class="text-[10px] text-club-gray-500 whitespace-nowrap">{{ formatDate(n.created_at) }}</span>
            </div>
          </div>
          <p class="text-xs text-club-graphite-light mt-1 leading-snug">{{ n.message || n.body }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { BellRing, Calendar, Gift, DollarSign, Info, AlertTriangle, Award } from 'lucide-vue-next'
import { useReportsStore } from '@/stores/reports'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import EmptyState from '@/components/EmptyState.vue'

const store = useReportsStore()
const loading = computed(() => store.loading)
const list = ref([])

const TYPES = {
  RESERVATION: { icon: Calendar, bg: 'bg-club-forest/15', text: 'text-club-forest' },
  ORDER: { icon: DollarSign, bg: 'bg-club-wellness/15', text: 'text-club-wellness-dark' },
  REWARD: { icon: Gift, bg: 'bg-club-gold/15', text: 'text-club-gold-dark' },
  POINTS: { icon: Award, bg: 'bg-club-coral/15', text: 'text-club-coral-dark' },
  INFO: { icon: Info, bg: 'bg-club-gray-200', text: 'text-club-graphite-light' },
  WARNING: { icon: AlertTriangle, bg: 'bg-club-red/15', text: 'text-club-red' },
  GENERAL: { icon: BellRing, bg: 'bg-club-forest/10', text: 'text-club-forest' },
}
function styleFor(t) { return TYPES[t] || TYPES.GENERAL }
function formatDate(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  return `${d.getDate()}/${d.getMonth() + 1} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

async function markRead(n) {
  if (n.is_read) return
  n.is_read = true
  await store.markNotificationRead(n.id)
}

onMounted(async () => {
  try { list.value = await store.listNotifications() } catch (_) {}
})
</script>
