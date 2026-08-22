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
        :class="{ 'ring-2 ring-club-blue/30 bg-club-blue/5': !n.is_read }"
        @click="markRead(n)"
      >
        <div class="w-10 h-10 rounded-xl flex items-center justify-center shrink-0" :class="styleFor(n.type).bg">
          <component :is="styleFor(n.type).icon" :class="styleFor(n.type).text + ' w-5 h-5'" />
        </div>
        <div class="flex-1 min-w-0">
          <div class="flex items-start justify-between gap-2">
            <div class="font-bold text-sm text-club-gray-900 truncate">{{ n.title || n.type }}</div>
            <div class="flex items-center gap-1.5 shrink-0">
              <span v-if="!n.is_read" class="w-2 h-2 rounded-full bg-club-blue"></span>
              <span class="text-[10px] text-club-gray-500 whitespace-nowrap">{{ formatDate(n.created_at) }}</span>
            </div>
          </div>
          <p class="text-xs text-club-gray-700 mt-1 leading-snug">{{ n.message || n.body }}</p>
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
  RESERVATION: { icon: Calendar, bg: 'bg-club-blue/15', text: 'text-club-blue' },
  ORDER: { icon: DollarSign, bg: 'bg-club-green/15', text: 'text-club-green' },
  REWARD: { icon: Gift, bg: 'bg-club-amber/15', text: 'text-[#b45309]' },
  POINTS: { icon: Award, bg: 'bg-club-purple/15', text: 'text-club-purple' },
  INFO: { icon: Info, bg: 'bg-club-gray-200', text: 'text-club-gray-700' },
  WARNING: { icon: AlertTriangle, bg: 'bg-club-red/15', text: 'text-club-red' },
  GENERAL: { icon: BellRing, bg: 'bg-club-blue/10', text: 'text-club-blue' },
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
