import { createRouter, createWebHashHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    name: 'root',
    redirect: () => {
      const auth = useAuthStore()
      if (!auth.isAuthenticated) return { name: 'login' }
      if (auth.isAdmin || auth.isEmployee) return { name: 'admin-dashboard' }
      return { name: 'client-home' }
    },
  },
  { path: '/login', name: 'login', component: () => import('@/views/auth/LoginView.vue'), meta: { public: true } },
  { path: '/registro', name: 'register', component: () => import('@/views/auth/RegisterView.vue'), meta: { public: true } },

  // === CLIENTE ===
  {
    path: '/cliente',
    component: () => import('@/layouts/MobileLayout.vue'),
    meta: { requiresAuth: true, role: 'CLIENT' },
    children: [
      { path: '', name: 'client-home', component: () => import('@/views/client/HomeView.vue') },
      { path: 'reservas', name: 'client-reservations', component: () => import('@/views/client/ReservationsView.vue') },
      { path: 'reservas/crear/:spaceId?', name: 'client-reserve-create', component: () => import('@/views/client/ReserveCreateView.vue'), props: true },
      { path: 'refrescos', name: 'client-refreshments', component: () => import('@/views/client/RefreshmentsView.vue') },
      { path: 'carrito', name: 'client-cart', component: () => import('@/views/client/CartView.vue') },
      { path: 'pedidos', name: 'client-orders', component: () => import('@/views/client/OrdersView.vue') },
      { path: 'recompensas', name: 'client-rewards', component: () => import('@/views/client/RewardsView.vue') },
      { path: 'fidelidad', name: 'client-loyalty', component: () => import('@/views/client/LoyaltyView.vue') },
      { path: 'gimnasio', name: 'client-gym', component: () => import('@/views/client/GymView.vue') },
      { path: 'gimnasio/rutina/:id', name: 'client-routine-detail', component: () => import('@/views/client/RoutineDetailView.vue'), props: true },
      { path: 'perfil', name: 'client-profile', component: () => import('@/views/client/ProfileView.vue') },
      { path: 'notificaciones', name: 'client-notifications', component: () => import('@/views/client/NotificationsView.vue') },
    ],
  },

  // === EMPLEADO / ADMIN comparten panel ===
  {
    path: '/panel',
    component: () => import('@/layouts/MobileLayout.vue'),
    meta: { requiresAuth: true, staff: true },
    children: [
      { path: '', name: 'admin-dashboard', component: () => import('@/views/staff/DashboardView.vue') },
      { path: 'reservas', name: 'staff-reservations', component: () => import('@/views/staff/ReservationsView.vue') },
      { path: 'pedidos', name: 'staff-orders', component: () => import('@/views/staff/OrdersView.vue') },
      { path: 'clientes', name: 'staff-clients', component: () => import('@/views/staff/ClientsView.vue') },
      { path: 'productos', name: 'staff-products', component: () => import('@/views/staff/ProductsView.vue') },
      { path: 'espacios', name: 'staff-spaces', component: () => import('@/views/staff/SpacesView.vue') },
      { path: 'reportes', name: 'staff-reports', component: () => import('@/views/staff/ReportsView.vue') },
      { path: 'perfil', name: 'staff-profile', component: () => import('@/views/staff/ProfileView.vue') },
    ],
  },

  { path: '/:pathMatch(.*)*', name: 'not-found', component: () => import('@/views/NotFoundView.vue'), meta: { public: true } },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  },
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (!auth.isAuthenticated && auth.accessToken) {
    try { await auth.restoreSession() } catch (_) {}
  }

  if (to.meta.public) {
    if (to.name === 'login' || to.name === 'register') {
      if (auth.isAuthenticated) {
        return { name: 'root' }
      }
    }
    return true
  }

  if (!auth.isAuthenticated) {
    return { name: 'login', query: { next: to.fullPath } }
  }

  if (to.meta.role === 'CLIENT' && !auth.isClient && !auth.isStaff) {
    return { name: 'root' }
  }
  if (to.meta.staff && !auth.isStaff) {
    return { name: 'client-home' }
  }
  return true
})

export default router
