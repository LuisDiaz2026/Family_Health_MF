<template>
  <div class="card flex flex-col gap-3">
    <div class="flex items-start justify-between gap-2">
      <div>
        <div class="flex items-center gap-2">
          <component :is="spaceIcon" class="w-4 h-4 text-club-blue" />
          <h3 class="font-bold text-club-gray-900">{{ space?.name || 'Espacio' }}</h3>
        </div>
        <div class="mt-0.5 text-xs text-club-gray-500">
          {{ formatDate(start_time) }} · {{ formatHour(start_time) }} - {{ formatHour(end_time) }}
        </div>
      </div>
      <span class="chip" :class="statusChip(status)">{{ statusDisplay }}</span>
    </div>
    <div class="flex items-center justify-between text-xs">
      <div class="flex items-center gap-3 text-club-gray-600">
        <span class="inline-flex items-center gap-1"><Users class="w-3.5 h-3.5" /> {{ guests }}</span>
        <span class="inline-flex items-center gap-1"><Clock class="w-3.5 h-3.5" /> {{ durationMin }} min</span>
      </div>
      <div class="font-bold text-club-gray-900">${{ Number(total_amount || 0).toLocaleString('es-CO') }}</div>
    </div>
    <div v-if="showActions && !cancelled && !completed" class="pt-2 flex items-center justify-end gap-2">
      <button
        v-if="showCancel"
        class="btn-secondary !py-2 !text-xs"
        @click="$emit('cancel')"
      >Cancelar</button>
      <button
        v-if="showDetails"
        class="btn-primary !py-2 !text-xs"
        @click="$emit('details')"
      >Ver detalles</button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { CalendarDays, Users, Clock, MapPin, Dumbbell, Droplets, Gamepad2, Trophy } from 'lucide-vue-next'

const props = defineProps({
  id: Number,
  space: Object,
  space_name: String,
  space_icon: String,
  start_time: String,
  end_time: String,
  guests: Number,
  total_amount: [Number, String],
  status: String,
  payment_status: String,
  showActions: { type: Boolean, default: true },
  showCancel: { type: Boolean, default: true },
  showDetails: { type: Boolean, default: false },
})

defineEmits(['cancel', 'details'])

const STATUS = {
  PENDING: ['chip bg-club-amber/15 text-[#b45309] border border-club-amber/30', 'Pendiente'],
  CONFIRMED: ['chip bg-club-blue/15 text-club-blue-dark border border-club-blue/30', 'Confirmada'],
  COMPLETED: ['chip bg-club-green/15 text-club-green-dark border border-club-green/30', 'Completada'],
  CANCELLED: ['chip bg-club-red/15 text-club-red border border-club-red/30', 'Cancelada'],
  NO_SHOW: ['chip bg-club-gray-200 text-club-gray-700', 'No asistió'],
}

function statusChip(st) { return STATUS[st]?.[0] || STATUS.PENDING[0] }
const statusDisplay = computed(() => STATUS[props.status]?.[1] || props.status)
const cancelled = computed(() => props.status === 'CANCELLED')
const completed = computed(() => props.status === 'COMPLETED')

const spaceIcon = computed(() => {
  const name = (props.space?.name || props.space_name || '').toLowerCase()
  if (name.includes('gimnasio') || name.includes('gym')) return Dumbbell
  if (name.includes('piscina')) return Droplets
  if (name.includes('infantil') || name.includes('parque')) return Gamepad2
  if (name.includes('cancha')) return Trophy
  return MapPin
})

function pad(n) { return String(n).padStart(2, '0') }
function formatDate(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  return `${pad(d.getDate())}/${pad(d.getMonth() + 1)}/${d.getFullYear()}`
}
function formatHour(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  return `${pad(d.getHours())}:${pad(d.getMinutes())}`
}
const durationMin = computed(() => {
  if (!props.start_time || !props.end_time) return 0
  return Math.round((new Date(props.end_time) - new Date(props.start_time)) / 60000)
})
</script>
