<template>
  <div class="page-padding space-y-4">
    <button class="inline-flex items-center gap-1 text-club-blue font-bold text-sm hover:underline" @click="$router.back()">
      <ArrowLeft class="w-4 h-4" /> Volver
    </button>

    <div>
      <h1 class="title-page">{{ spaceId ? 'Crear reserva' : 'Reservar espacio' }}</h1>
      <p class="subtitle-page">Selecciona una fecha y franja horaria disponible</p>
    </div>

    <SkeletonLoader v-if="loading && !spaces.length" />

    <template v-else>
      <div class="section-title">1. Elige el espacio</div>
      <div class="grid grid-cols-2 gap-3">
        <button
          v-for="s in spaces" :key="s.id"
          class="card !p-3 text-left transition-all"
          :class="selectedSpace?.id === s.id
            ? 'ring-2 ring-club-blue bg-club-blue/5'
            : 'hover:bg-club-gray-50'"
          @click="selectSpace(s)"
        >
          <div class="flex items-center gap-2 mb-1.5">
            <div class="w-9 h-9 rounded-lg bg-club-blue/10 text-club-blue flex items-center justify-center shrink-0">
              <MapPin class="w-4 h-4" />
            </div>
            <div class="font-bold text-sm text-club-gray-900 leading-tight">{{ s.name }}</div>
          </div>
          <div class="text-[11px] text-club-gray-500">{{ s.space_type?.name || '' }}</div>
          <div class="mt-2 flex items-center justify-between text-xs">
            <span class="font-bold text-club-green">${{ Number(s.hourly_rate || 0).toLocaleString('es-CO') }}/h</span>
            <span v-if="s.requires_employee_approval" class="chip bg-club-amber/15 text-[#b45309] !text-[10px]">Requiere aprobación</span>
            <span v-else class="chip bg-club-green/15 text-club-green-dark !text-[10px]">Confirmación instantánea</span>
          </div>
        </button>
      </div>

      <template v-if="selectedSpace">
        <div class="section-title">2. Fecha</div>
        <input type="date" v-model="selectedDate" class="input" :min="minDate" />

        <SkeletonLoader v-if="loadingAvail" />
        <template v-else>
          <div class="section-title">3. Horario disponible</div>
          <EmptyState v-if="!availability.length" icon="Clock" title="Sin franjas disponibles" description="Intenta con otra fecha o espacio." />
          <div v-else class="grid grid-cols-3 sm:grid-cols-4 gap-2">
            <button
              v-for="slot in availability"
              :key="slot.start + slot.end"
              class="p-2.5 rounded-xl border text-xs font-semibold text-center transition-all"
              :class="selectedSlot?.start === slot.start && selectedSlot?.end === slot.end
                ? 'bg-club-blue text-white border-club-blue'
                : (slot.available ? 'border-club-gray-200 bg-white text-club-gray-800 hover:border-club-blue hover:text-club-blue'
                    : 'bg-club-gray-100 text-club-gray-400 line-through cursor-not-allowed')"
              :disabled="!slot.available"
              @click="selectedSlot = slot"
            >
              <div>{{ formatHour(slot.start) }}</div>
              <div class="opacity-70">a {{ formatHour(slot.end) }}</div>
            </button>
          </div>
        </template>

        <template v-if="selectedSlot">
          <div class="card mt-2 bg-gradient-to-br from-club-gray-50 to-white">
            <div class="section-title !mb-3">Resumen</div>
            <div class="space-y-2 text-sm">
              <Row label="Espacio" :value="selectedSpace.name" />
              <Row label="Fecha" :value="selectedDate" />
              <Row label="Horario" :value="`${formatHour(selectedSlot.start)} a ${formatHour(selectedSlot.end)}`" />
              <div class="flex items-center justify-between">
                <label class="label !mb-0">N° personas</label>
                <input type="number" v-model.number="guests" min="1" :max="selectedSpace.max_capacity || 999" class="input w-28 text-center !py-1.5" />
              </div>
              <Row label="Duración" :value="durationMin + ' minutos'" />
              <Row label="Valor total" :value="`$${total.toLocaleString('es-CO')}`" highlight />
            </div>
            <button
              class="btn-success w-full mt-4 !py-3"
              :disabled="loadingSubmit"
              @click="doReserve"
            >
              <Loader2 v-if="loadingSubmit" class="w-4 h-4 animate-spin" />
              Confirmar reserva
            </button>
          </div>
        </template>
      </template>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, MapPin, Clock, Loader2 } from 'lucide-vue-next'
import { useReservationsStore } from '@/stores/reservations'
import EmptyState from '@/components/EmptyState.vue'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import { showToast } from '@/utils/toast'

const Row = {
  props: ['label', 'value', 'highlight'],
  template: `
    <div class="flex items-center justify-between">
      <span class="text-club-gray-500">{{ label }}</span>
      <span :class="highlight ? 'font-black text-lg text-club-green' : 'font-semibold text-club-gray-900'">{{ value }}</span>
    </div>
  `,
}

const props = defineProps({ spaceId: [String, Number] })
const route = useRoute()
const router = useRouter()
const store = useReservationsStore()

const spaces = ref([])
const selectedSpace = ref(null)
const selectedDate = ref(new Date(Date.now() + 86400000).toISOString().slice(0, 10))
const availability = ref([])
const selectedSlot = ref(null)
const guests = ref(2)
const loadingSubmit = ref(false)

const loading = computed(() => store.loading && !spaces.value.length)
const loadingAvail = computed(() => store.loading)
const minDate = new Date().toISOString().slice(0, 10)

function formatHour(t) {
  if (!t) return ''
  if (t.includes('T')) return new Date(t).toTimeString().slice(0, 5)
  return t.slice(0, 5)
}

function toIso(date, hm) {
  return new Date(`${date}T${hm}:00`).toISOString()
}

const durationMin = computed(() => {
  if (!selectedSlot.value) return 0
  const [h1, m1] = selectedSlot.value.start.split(':').map(Number)
  const [h2, m2] = selectedSlot.value.end.split(':').map(Number)
  return (h2 * 60 + m2) - (h1 * 60 + m1)
})
const total = computed(() => Math.round(durationMin.value / 60 * Number(selectedSpace.value?.hourly_rate || 0)))

function selectSpace(s) {
  selectedSpace.value = s
  selectedSlot.value = null
  if (selectedDate.value) loadAvailability()
}

async function loadAvailability() {
  if (!selectedSpace.value?.id || !selectedDate.value) return
  try {
    const slots = await store.getAvailability(selectedSpace.value.id, selectedDate.value)
    availability.value = (Array.isArray(slots) ? slots : (slots?.available_slots || [])).map((x, i) => {
      if (typeof x === 'object') return { start: x.start || x.from || x.start_time, end: x.end || x.to || x.end_time, available: x.available !== false }
      return { start: x, end: addHour(x), available: true }
    })
  } catch (e) {
    const arr = []
    for (let h = 6; h < 22; h++) {
      arr.push({ start: `${String(h).padStart(2, '0')}:00`, end: `${String(h + 1).padStart(2, '0')}:00`, available: true })
    }
    availability.value = arr
  }
}
function addHour(h) {
  const [hh, mm] = h.split(':').map(Number)
  const d = new Date()
  d.setHours(hh + 1, mm || 0)
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

watch(selectedDate, () => {
  selectedSlot.value = null
  if (selectedSpace.value) loadAvailability()
})

async function doReserve() {
  if (!selectedSpace.value || !selectedSlot.value) return
  if (guests.value < 1) {
    showToast('Ingresa el número de personas.', 'warn')
    return
  }
  loadingSubmit.value = true
  try {
    const start_iso = toIso(selectedDate.value, selectedSlot.value.start)
    const end_iso = toIso(selectedDate.value, selectedSlot.value.end)
    await store.createReservation({
      space_id: selectedSpace.value.id,
      start_time: start_iso,
      end_time: end_iso,
      guests: guests.value,
      notes: '',
    })
    showToast('Reserva creada exitosamente!', 'success')
    router.replace({ name: 'client-reservations' })
  } catch (e) {
    showToast(e || 'No se pudo crear. Intente nuevamente.', 'error')
  } finally {
    loadingSubmit.value = false
  }
}

onMounted(async () => {
  const list = await store.listSpaces({ status: 'ACTIVE' })
  spaces.value = list
  const sid = props.spaceId || route.params.spaceId
  if (sid) {
    const found = list.find(x => x.id == sid)
    if (found) selectSpace(found)
  }
})
</script>
