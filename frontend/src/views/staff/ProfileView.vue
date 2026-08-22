<template>
  <div class="page-padding space-y-4">
    <div>
      <h1 class="title-page">Mi cuenta</h1>
      <p class="subtitle-page">Panel administración y recepción</p>
    </div>

    <section class="card flex items-center gap-3">
      <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-club-blue to-sky-700 text-white text-2xl font-black flex items-center justify-center shadow-md">
        {{ initials }}
      </div>
      <div class="flex-1 min-w-0">
        <div class="font-extrabold text-club-gray-900 truncate">{{ auth.displayName }}</div>
        <div class="text-xs text-club-gray-500 mt-0.5 truncate">{{ auth.user?.email || auth.user?.username }}</div>
        <div class="mt-2 flex flex-wrap gap-1.5">
          <span class="chip bg-club-blue/15 text-club-blue-dark">{{ roleLabel }}</span>
          <span v-if="auth.user?.is_staff || auth.isAdmin" class="chip bg-club-amber/15 text-[#b45309]">Staff</span>
          <span v-if="auth.user?.is_verified" class="chip bg-club-green/15 text-club-green-dark">Verificado</span>
        </div>
      </div>
    </section>

    <section class="card space-y-3">
      <div class="section-title"><User class="w-4 h-4 text-club-blue" /> Datos de acceso</div>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <Field label="Usuario" :value="auth.user?.username || '-'" />
        <Field label="Rol" :value="roleLabel" />
        <Field label="Documento" :value="docLabel" />
        <Field label="Celular" :value="auth.user?.phone || '-'" />
        <Field label="Correo" :value="auth.user?.email || '-'" />
      </div>
    </section>

    <section class="card space-y-3">
      <div class="section-title"><ShieldCheck class="w-4 h-4 text-club-green" /> Seguridad</div>
      <p class="text-xs text-club-gray-600 bg-club-gray-50 p-3 rounded-xl border border-club-gray-200">
        El panel administrativo solo permite acceso a personal autorizado (ADMIN / EMPLOYEE).
        Todas las acciones se registran en el sistema de auditoría del club.
      </p>
      <button class="btn-outline w-full" @click="openAdminDjango">
        <ExternalLink class="w-4 h-4" /> Abrir panel Django Admin
      </button>
    </section>

    <section class="card space-y-3">
      <div class="section-title"><LogOut class="w-4 h-4 text-club-red" /> Cerrar sesión</div>
      <button class="btn-danger w-full" @click="logout">
        Salir de la cuenta
      </button>
    </section>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { User, ShieldCheck, LogOut, ExternalLink } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { showToast } from '@/utils/toast'

const auth = useAuthStore()
const router = useRouter()

const Field = {
  props: ['label', 'value'],
  template: `
    <div>
      <div class="text-[11px] uppercase tracking-wide font-bold text-club-gray-500">{{ label }}</div>
      <div class="text-sm font-semibold text-club-gray-900 mt-0.5">{{ value }}</div>
    </div>
  `,
}

const initials = computed(() => {
  const fn = auth.user?.first_name?.[0] || auth.displayName?.[0] || 'S'
  const ln = auth.user?.last_name?.[0] || auth.displayName?.split(' ')[1]?.[0] || ''
  return (fn + ln).toUpperCase()
})
const roleLabel = computed(() => ({ ADMIN: 'Administrador', EMPLOYEE: 'Recepción / Empleado', CLIENT: 'Cliente' }[auth.role] || auth.role || '-'))
const docLabel = computed(() => `${auth.user?.document_type || 'CC'} · ${auth.user?.document_number || '-'}`)

function openAdminDjango() {
  window.open('/admin/', '_blank', 'noopener,noreferrer')
}

async function logout() {
  await auth.logout()
  showToast('Sesión cerrada.', 'info')
  router.replace({ name: 'login' })
}
</script>
