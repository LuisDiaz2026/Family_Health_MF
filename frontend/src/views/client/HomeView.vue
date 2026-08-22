<template>
  <div class="page-padding space-y-5">
    <section class="rounded-2xl p-5 text-white relative overflow-hidden bg-gradient-to-br from-club-blue via-sky-600 to-club-green">
      <div class="absolute -right-10 -top-10 w-40 h-40 rounded-full bg-white/10" />
      <div class="absolute right-10 bottom-0 w-20 h-20 rounded-full bg-white/10" />
      <div class="relative">
        <div class="text-sm/6 font-semibold opacity-90">¡Hola de nuevo! 👋</div>
        <div class="mt-0.5 text-2xl font-black tracking-tight">{{ auth.displayName }}</div>
        <div class="mt-3 grid grid-cols-3 gap-2 text-center">
          <div class="rounded-xl bg-white/15 backdrop-blur px-2 py-2.5">
            <div class="text-[10px] uppercase font-bold opacity-80">Puntos</div>
            <div class="text-lg font-black">{{ auth.currentPoints }}</div>
          </div>
          <div class="rounded-xl bg-white/15 backdrop-blur px-2 py-2.5">
            <div class="text-[10px] uppercase font-bold opacity-80">Nivel</div>
            <div class="text-lg font-black">{{ tierName }}</div>
          </div>
          <div class="rounded-xl bg-white/15 backdrop-blur px-2 py-2.5">
            <div class="text-[10px] uppercase font-bold opacity-80">Membresía</div>
            <div class="text-lg font-black">{{ membershipShort }}</div>
          </div>
        </div>
      </div>
    </section>

    <section>
      <div class="section-title">Acciones rápidas</div>
      <div class="grid grid-cols-4 gap-3">
        <button v-for="s in shortcuts" :key="s.label" class="flex flex-col items-center gap-1.5 p-3 rounded-xl bg-white shadow-card hover:-translate-y-0.5 transition-all" @click="$router.push(s.to)">
          <div class="w-10 h-10 rounded-xl flex items-center justify-center text-white" :style="{ background: s.color }">
            <component :is="s.icon" class="w-5 h-5" />
          </div>
          <span class="text-[11px] font-semibold text-club-gray-800 text-center leading-tight">{{ s.label }}</span>
        </button>
      </div>
    </section>

    <section>
      <div class="flex items-center justify-between mb-3">
        <div class="section-title !mb-0">Reservas recientes</div>
        <button class="text-xs font-bold text-club-blue hover:underline" @click="$router.push({ name: 'client-reservations' })">Ver todas</button>
      </div>
      <template v-if="loadingReservations"><SkeletonLoader text="Cargando reservas..." /></template>
      <EmptyState
        v-else-if="!recent.length"
        icon="Calendar"
        title="Aún no tienes reservas"
        description="Reserva canchas, salones, piscina o gimnasio en segundos."
        cta-label="Reservar ahora"
        @cta="$router.push({ name: 'client-reservations' })"
      />
      <div v-else class="space-y-3">
        <ReservationCard
          v-for="r in recent"
          :key="r.id"
          v-bind="r"
          :show-details="true"
          @details="$router.push({ name: 'client-reserve-create', params: { spaceId: r.space?.id } })"
        />
      </div>
    </section>

    <section>
      <div class="flex items-center justify-between mb-3">
        <div class="section-title !mb-0">Ofertas refresquería</div>
        <button class="text-xs font-bold text-club-blue hover:underline" @click="$router.push({ name: 'client-refreshments' })">Ver catálogo</button>
      </div>
      <div class="flex gap-3 overflow-x-auto pb-2 -mx-4 px-4 snap-x snap-mandatory">
        <div
          v-for="offer in featuredOffers"
          :key="offer.id"
          class="card min-w-[220px] snap-start cursor-pointer hover:-translate-y-0.5 transition-all"
          @click="$router.push({ name: 'client-refreshments' })"
        >
          <div class="text-[10px] font-bold uppercase chip bg-club-red/15 text-club-red">{{ offer.tag }}</div>
          <h4 class="font-extrabold text-club-gray-900 mt-2">{{ offer.name }}</h4>
          <div class="flex items-end justify-between mt-3">
            <div>
              <div class="text-xs text-club-gray-500 line-through">${{ offer.oldPrice.toLocaleString('es-CO') }}</div>
              <div class="text-xl font-black text-club-green">${{ offer.price.toLocaleString('es-CO') }}</div>
            </div>
            <ShoppingBag class="w-7 h-7 text-club-blue" />
          </div>
        </div>
      </div>
    </section>

    <section>
      <div class="section-title">Rutina recomendada de hoy</div>
      <template v-if="loadingRoutines"><SkeletonLoader text="Cargando rutinas..." /></template>
      <RoutineCard v-else-if="featuredRoutine" :routine="featuredRoutine" @click="$router.push({ name: 'client-routine-detail', params: { id: featuredRoutine.id } })" />
      <EmptyState v-else icon="Dumbbell" title="Sin rutinas" description="Consulta el módulo Gimnasio para ver tus planes." />
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Calendar, ShoppingBag, Award, Dumbbell, Bell, User, MapPin, Droplets, Trophy } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { useReservationsStore } from '@/stores/reservations'
import { useGymStore } from '@/stores/gym'
import ReservationCard from '@/components/ReservationCard.vue'
import RoutineCard from '@/components/RoutineCard.vue'
import EmptyState from '@/components/EmptyState.vue'
import SkeletonLoader from '@/components/SkeletonLoader.vue'

const router = useRouter()
const auth = useAuthStore()
const reservations = useReservationsStore()
const gym = useGymStore()

const loadingReservations = ref(true)
const loadingRoutines = ref(true)
const recent = ref([])
const featuredRoutine = ref(null)

const tierName = computed(() => auth.tierInfo?.name || 'Bronce')
const membershipShort = computed(() => {
  const t = auth.user?.membership_type
  if (!t) return '-'
  if (String(t).toLowerCase().includes('premium')) return 'Premium'
  return 'Básica'
})

const shortcuts = [
  { label: 'Reservar', icon: Calendar, to: { name: 'client-reservations' }, color: '#0ea5e9' },
  { label: 'Refrescos', icon: ShoppingBag, to: { name: 'client-refreshments' }, color: '#10b981' },
  { label: 'Puntos', icon: Award, to: { name: 'client-loyalty' }, color: '#f59e0b' },
  { label: 'Gimnasio', icon: Dumbbell, to: { name: 'client-gym' }, color: '#8b5cf6' },
]

const featuredOffers = [
  { id: 1, tag: 'Combo', name: 'Hamburguesa + Gaseosa 1.5L', oldPrice: 28000, price: 22000 },
  { id: 2, tag: '2x1', name: 'Jarra de limonada x2', oldPrice: 16000, price: 10000 },
  { id: 3, tag: 'Energía', name: 'Protein Shake Whey 500ml', oldPrice: 18000, price: 14000 },
]

onMounted(async () => {
  try {
    const list = await reservations.listMyReservations()
    recent.value = (list || []).slice(0, 3)
  } finally {
    loadingReservations.value = false
  }
  try {
    const routines = await gym.listMyRoutines()
    featuredRoutine.value = (routines || [])[0] || null
  } finally {
    loadingRoutines.value = false
  }
})
</script>
