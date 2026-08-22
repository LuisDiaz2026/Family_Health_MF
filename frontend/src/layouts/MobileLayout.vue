<template>
  <div class="min-h-screen bg-club-gray-100 flex flex-col max-w-2xl mx-auto">
    <header class="sticky top-0 z-30 bg-white/90 backdrop-blur border-b border-club-gray-200 px-4 py-3">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2 min-w-0">
          <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-club-blue to-club-green flex items-center justify-center text-white font-black text-lg shadow-sm">
            CF
          </div>
          <div class="min-w-0">
            <div class="text-sm font-extrabold text-club-gray-900 truncate">Club Family Health</div>
            <div class="text-[11px] text-club-gray-500 truncate">{{ headerSubtitle }}</div>
          </div>
        </div>
        <div class="flex items-center gap-1.5">
          <button class="btn-ghost !p-2 !rounded-full relative" @click="$router.push(nameNotifications)">
            <Bell class="w-5 h-5 text-club-gray-700" />
            <span v-if="unreadCount > 0" class="absolute top-1 right-1 bg-club-red text-white text-[10px] font-bold rounded-full min-w-[18px] h-[18px] flex items-center justify-center px-1">
              {{ unreadCount > 99 ? '99+' : unreadCount }}
            </span>
          </button>
          <button class="btn-ghost !p-2 !rounded-full" @click="$router.push(nameProfile)">
            <User class="w-5 h-5 text-club-gray-700" />
          </button>
        </div>
      </div>
    </header>

    <main class="flex-1 overflow-x-hidden">
      <router-view v-slot="{ Component, route }">
        <transition name="fade-slide" mode="out-in">
          <component :is="Component" :key="route.fullPath" />
        </transition>
      </router-view>
    </main>

    <nav class="sticky bottom-0 z-30 bg-white border-t border-club-gray-200 shadow-nav pb-[env(safe-area-inset-bottom)]">
      <div class="grid grid-cols-5 max-w-2xl mx-auto">
        <button
          v-for="item in navItems"
          :key="item.to.name"
          @click="$router.push(item.to)"
          class="flex flex-col items-center justify-center py-2.5 px-1 gap-0.5 transition-colors"
          :class="activeRoute(item.to.name)
            ? 'text-club-blue'
            : 'text-club-gray-500 hover:text-club-gray-800'"
        >
          <component :is="item.icon" class="w-5 h-5" :stroke-width="activeRoute(item.to.name) ? 2.6 : 2" />
          <span class="text-[10px] font-semibold truncate max-w-full px-1">{{ item.label }}</span>
        </button>
      </div>
    </nav>

    <GlobalToast />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Home, Calendar, ShoppingBag, Award, Dumbbell, LayoutDashboard, UserPlus, Package, Bell, User } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { useReportsStore } from '@/stores/reports'
import GlobalToast from '@/components/GlobalToast.vue'
import { showToast } from '@/utils/toast'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const reports = useReportsStore()
const unreadCount = ref(0)

const clientNav = [
  { label: 'Inicio', icon: Home, to: { name: 'client-home' } },
  { label: 'Reservas', icon: Calendar, to: { name: 'client-reservations' } },
  { label: 'Refrescos', icon: ShoppingBag, to: { name: 'client-refreshments' } },
  { label: 'Puntos', icon: Award, to: { name: 'client-loyalty' } },
  { label: 'Gimnasio', icon: Dumbbell, to: { name: 'client-gym' } },
]

const staffNav = [
  { label: 'Panel', icon: LayoutDashboard, to: { name: 'admin-dashboard' } },
  { label: 'Reservas', icon: Calendar, to: { name: 'staff-reservations' } },
  { label: 'Pedidos', icon: Package, to: { name: 'staff-orders' } },
  { label: 'Clientes', icon: UserPlus, to: { name: 'staff-clients' } },
  { label: 'Reportes', icon: Award, to: { name: 'staff-reports' } },
]

const navItems = computed(() => auth.isStaff ? staffNav : clientNav)

const headerSubtitle = computed(() => {
  if (auth.isStaff) return auth.isAdmin ? 'Panel Administrador' : 'Panel Recepción'
  const parts = []
  if (auth.tierInfo?.name) parts.push(`${auth.tierInfo.name}`)
  if (auth.currentPoints != null) parts.push(`${auth.currentPoints} pts`)
  return parts.length ? parts.join(' · ') : 'Maicao · La Guajira'
})

const nameProfile = computed(() => auth.isStaff ? 'staff-profile' : 'client-profile')
const nameNotifications = computed(() => auth.isStaff ? 'admin-dashboard' : 'client-notifications')

function activeRoute(name) {
  if (!name) return false
  if (route.name === name) return true
  const staffMap = { 'admin-dashboard': true, 'staff-reservations': true, 'staff-orders': true, 'staff-clients': true, 'staff-reports': true }
  if (name in staffMap) return false
  if (name === 'client-home') return route.name === 'client-home'
  if (name === 'client-reservations') return ['client-reservations', 'client-reserve-create'].includes(route.name)
  if (name === 'client-refreshments') return ['client-refreshments', 'client-cart', 'client-orders'].includes(route.name)
  if (name === 'client-loyalty') return ['client-loyalty', 'client-rewards'].includes(route.name)
  if (name === 'client-gym') return ['client-gym', 'client-routine-detail'].includes(route.name)
  return false
}

onMounted(async () => {
  try {
    const list = await reports.listNotifications()
    unreadCount.value = (list || []).filter(x => !x.is_read).length
  } catch (_) {}
})

defineExpose({ showToast })
</script>

<style scoped>
.fade-slide-enter-active, .fade-slide-leave-active {
  transition: all .22s ease;
}
.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(10px);
}
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
</style>
