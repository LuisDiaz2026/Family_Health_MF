<template>
  <div class="page-padding space-y-4">
    <button class="inline-flex items-center gap-1 text-club-forest font-bold text-sm hover:underline" @click="$router.back()">
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
            ? 'ring-2 ring-club-forest bg-club-forest/5'
            : 'hover:bg-club-ivory'"
          @click="selectSpace(s)"
        >
          <div class="flex items-center gap-2 mb-1.5">
            <div class="w-9 h-9 rounded-lg bg-club-forest/10 text-club-forest flex items-center justify-center shrink-0">
              <MapPin class="w-4 h-4" />
            </div>
            <div class="font-bold text-sm text-club-graphite leading-tight">{{ s.name }}</div>
          </div>
          <div class="text-[11px] text-club-gray-500">{{ s.space_type?.name || '' }}</div>
          <div class="mt-2 flex items-center justify-between text-xs">
            <span class="font-bold text-club-gold-dark">${{ Number(s.hourly_rate || 0).toLocaleString('es-CO') }}/h</span>
            <span v-if="s.requires_employee_approval" class="chip bg-club-coral/15 text-club-coral-dark !text-[10px]">Requiere aprobación</span>
            <span v-else class="chip bg-club-wellness/15 text-club-wellness-dark !text-[10px]">Confirmación instantánea</span>
          </div>
        </button>
      </div>

      <template v-if="selectedSpace">
        <div class="section-title">2. Fecha</div>
        <input type="date" v-model="selectedDate" class="input" :min="minDate" />

        <SkeletonLoader v-if="loadingAvail" />
        <template v-else>
          <div class="section-title">3. Hora de inicio</div>
          <p class="text-sm text-club-gray-500 -mt-2 mb-3">
            Selecciona la hora en que quieres iniciar. La duración se elige en el siguiente paso.
          </p>
          <EmptyState v-if="!availability.length" icon="Clock" title="Sin franjas disponibles" description="Intenta con otra fecha o espacio." />
          <div v-else class="grid grid-cols-3 sm:grid-cols-4 gap-2">
            <button
              v-for="slot in availability"
              :key="slot.start"
              class="p-2.5 rounded-xl border text-xs font-semibold text-center transition-all"
              :class="selectedSlot?.start === slot.start
                ? 'bg-club-forest text-white border-club-forest'
                : (canStartAt(slot) ? 'border-club-gray-200 bg-white text-club-graphite-light hover:border-club-forest hover:text-club-forest'
                    : 'bg-club-ivory-dark text-club-gray-400 line-through cursor-not-allowed')"
              :disabled="!canStartAt(slot)"
              @click="selectStart(slot)"
            >
              <div>{{ formatHour(slot.start) }}</div>
              <div class="opacity-70">Inicio</div>
            </button>
          </div>
        </template>

        <template v-if="selectedSlot">
          <div class="section-title">4. Duración</div>
          <label for="reservation-duration" class="label">Tiempo de reserva</label>
          <select
            id="reservation-duration"
            v-model.number="selectedDuration"
            class="input"
            :disabled="!durationOptions.length"
          >
            <option v-for="minutes in durationOptions" :key="minutes" :value="minutes">
              {{ durationLabel(minutes) }}
            </option>
          </select>
          <p v-if="!durationOptions.length" class="text-sm text-club-coral-dark">
            No hay tiempo continuo disponible desde esta hora. Selecciona otra hora de inicio.
          </p>

          <div class="card mt-2 bg-gradient-to-br from-club-ivory-light to-white">
            <div class="section-title !mb-3">Resumen</div>
            <div class="space-y-2 text-sm">
              <Row label="Espacio" :value="selectedSpace.name" />
              <Row label="Fecha" :value="selectedDate" />
              <Row label="Horario" :value="`${formatHour(selectedSlot.start)} a ${formatHour(selectedEndTime)}`" />
              <div class="flex items-center justify-between">
                <label class="label !mb-0">N° personas</label>
                <input type="number" v-model.number="guests" min="1" :max="selectedSpace.capacity || 999" class="input w-28 text-center !py-1.5" />
              </div>
              <Row label="Duración" :value="durationMin + ' minutos'" />
              <Row label="Valor total" :value="`$${total.toLocaleString('es-CO')}`" highlight />
            </div>
            <button
              class="btn-primary w-full mt-4 !py-3"
              :disabled="loadingSubmit || !selectedDuration"
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
      <span :class="highlight ? 'font-black text-lg text-club-gold-dark' : 'font-semibold text-club-graphite'">{{ value }}</span>
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
const selectedDuration = ref(null)
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

function addMinutes(hm, minutes) {
  const [hour, minute] = hm.split(':').map(Number)
  const total = hour * 60 + minute + minutes
  return `${String(Math.floor(total / 60) % 24).padStart(2, '0')}:${String(total % 60).padStart(2, '0')}`
}

function availableDurationsFor(startSlot) {
  if (!startSlot?.available || !selectedSpace.value) return []
  const min = Math.max(1, Number(selectedSpace.value.min_reservation_minutes || 60))
  const max = Number(selectedSpace.value.max_reservation_minutes || 180)
  const options = []

  for (let minutes = Math.ceil(min / 30) * 30; minutes <= max; minutes += 30) {
    const segments = minutes / 30
    const isAvailable = Array.from({ length: segments }, (_, index) => {
      const start = addMinutes(startSlot.start, index * 30)
      const slot = availability.value.find(item => item.start === start)
      return slot?.available && slot.end === addMinutes(start, 30)
    }).every(Boolean)
    if (isAvailable) options.push(minutes)
  }
  return options
}

function canStartAt(slot) {
  return availableDurationsFor(slot).length > 0
}

function selectStart(slot) {
  selectedSlot.value = slot
  selectedDuration.value = availableDurationsFor(slot)[0] || null
}

function durationLabel(minutes) {
  const hours = Math.floor(minutes / 60)
  const remainder = minutes % 60
  const parts = []
  if (hours) parts.push(`${hours} ${hours === 1 ? 'hora' : 'horas'}`)
  if (remainder) parts.push(`${remainder} minutos`)
  return `${minutes} minutos (${parts.join(' y ')})`
}

const durationOptions = computed(() => availableDurationsFor(selectedSlot.value))
const selectedEndTime = computed(() => (
  selectedSlot.value && selectedDuration.value
    ? addMinutes(selectedSlot.value.start, selectedDuration.value)
    : ''
))
const durationMin = computed(() => {
  return selectedDuration.value || 0
})
const total = computed(() => Math.round(durationMin.value / 60 * Number(selectedSpace.value?.hourly_rate || 0)))

function selectSpace(s) {
  selectedSpace.value = s
  selectedSlot.value = null
  selectedDuration.value = null
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
    availability.value = []
    showToast(typeof e === 'string' ? e : 'No fue posible consultar la disponibilidad. Intenta de nuevo.', 'error')
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
  selectedDuration.value = null
  if (selectedSpace.value) loadAvailability()
})

async function doReserve() {
  if (!selectedSpace.value || !selectedSlot.value || !selectedDuration.value) return
  if (guests.value < 1) {
    showToast('Ingresa el número de personas.', 'warn')
    return
  }
  loadingSubmit.value = true
  try {
    const start_iso = toIso(selectedDate.value, selectedSlot.value.start)
    const end_iso = toIso(selectedDate.value, selectedEndTime.value)
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
