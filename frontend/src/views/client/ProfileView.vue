<template>
  <div class="page-padding space-y-4">
    <div>
      <h1 class="title-page">Mi perfil</h1>
      <p class="subtitle-page">Información personal y seguridad</p>
    </div>

    <section class="card flex items-center gap-3">
      <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-club-blue to-club-green text-white text-2xl font-black flex items-center justify-center shadow-md">
        {{ initials }}
      </div>
      <div class="flex-1 min-w-0">
        <div class="font-extrabold text-club-gray-900 truncate">{{ auth.displayName }}</div>
        <div class="text-xs text-club-gray-500 mt-0.5">{{ emailOrUser }}</div>
        <div class="mt-2 flex flex-wrap gap-1.5">
          <span class="chip bg-club-blue/15 text-club-blue-dark">{{ auth.role }}</span>
          <span v-if="auth.user?.membership_active" class="chip bg-club-green/15 text-club-green-dark">Membresía activa</span>
          <span v-if="tierName" class="chip text-white" :style="{ background: tierColor }">{{ tierName }}</span>
        </div>
      </div>
    </section>

    <section class="card space-y-3">
      <div class="section-title"><User class="w-4 h-4 text-club-blue" /> Datos personales</div>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <Field label="Nombres" :value="auth.user?.first_name || '-'"/>
        <Field label="Apellidos" :value="auth.user?.last_name || '-'"/>
        <Field label="Documento" :value="docLabel" />
        <Field label="Celular" :value="auth.user?.phone || '-'"/>
        <Field label="Correo" :value="auth.user?.email || '-'" />
        <Field label="Ciudad / Dpto" :value="cityLabel" />
        <Field label="Género" :value="genderLabel" />
        <Field label="Fecha nacimiento" :value="auth.user?.birth_date || '-'" />
      </div>
    </section>

    <section class="card space-y-3">
      <div class="section-title"><Crown class="w-4 h-4 text-club-amber" /> Membresía</div>
      <div class="grid grid-cols-2 gap-3">
        <Field label="Plan actual" :value="auth.user?.membership_type || 'Básica'" />
        <Field label="Activa hasta" :value="auth.user?.membership_expires_at ? (new Date(auth.user.membership_expires_at).toLocaleDateString('es-CO')) : 'Indefinida'" />
      </div>
      <div v-if="auth.isClient" class="rounded-xl bg-gradient-to-br from-club-amber/10 to-club-green/10 p-3 border border-club-amber/20 flex items-center gap-3">
        <Award class="w-9 h-9 text-club-amber shrink-0" />
        <div class="text-sm">
          <div class="font-bold text-club-gray-900">{{ auth.currentPoints }} puntos acumulados</div>
          <button class="text-club-blue font-bold text-xs mt-0.5 hover:underline" @click="$router.push({ name: 'client-loyalty' })">
            Ver programa de fidelidad →
          </button>
        </div>
      </div>
    </section>

    <section class="card space-y-3">
      <div class="section-title"><ShieldCheck class="w-4 h-4 text-club-green" /> Seguridad</div>
      <div class="rounded-xl bg-club-blue/5 border border-club-blue/15 p-3 text-xs text-club-gray-700 space-y-1">
        <p>✓ Tus datos son tratados según la Ley 1581/2012 (Habeas Data).</p>
        <p>✓ Las contraseñas se almacenan cifradas con Argon2id.</p>
        <p>✓ Tokens JWT rotables y con expiración corta.</p>
      </div>
      <button class="btn-outline w-full" @click="$router.push({ name: 'client-notifications' })">
        <Bell class="w-4 h-4" /> Mis notificaciones
      </button>
    </section>

    <section class="card space-y-3">
      <div class="section-title"><Settings class="w-4 h-4 text-club-gray-600" /> Sesión</div>
      <button class="btn-danger w-full" @click="logout">
        <LogOut class="w-4 h-4" /> Cerrar sesión
      </button>
    </section>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { User, Crown, Award, ShieldCheck, Bell, Settings, LogOut } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { showToast } from '@/utils/toast'

const auth = useAuthStore()
const router = useRouter()

const Field = {
  props: ['label', 'value'],
  template: `
    <div>
      <div class="text-[11px] uppercase tracking-wide font-bold text-club-gray-500">{{ label }}</div>
      <div class="text-sm font-semibold text-club-gray-900 mt-0.5 break-all">{{ value }}</div>
    </div>
  `,
}

const initials = computed(() => {
  const fn = auth.user?.first_name?.[0] || auth.displayName?.[0] || 'U'
  const ln = auth.user?.last_name?.[0] || auth.displayName?.split(' ')[1]?.[0] || ''
  return (fn + ln).toUpperCase()
})
const emailOrUser = computed(() => auth.user?.email || auth.user?.username || '')
const docLabel = computed(() => `${auth.user?.document_type || 'CC'} · ${auth.user?.document_number || '-'}`)
const cityLabel = computed(() => [auth.user?.city, auth.user?.department].filter(Boolean).join(' / ') || '-')
const genderLabel = computed(() => ({ M: 'Masculino', F: 'Femenino', O: 'Otro', NB: 'No binario' }[auth.user?.gender] || auth.user?.gender || '-'))
const tierName = computed(() => auth.tierInfo?.name)
const tierColor = computed(() => {
  const n = (tierName.value || '').toLowerCase()
  if (n === 'plata') return '#94a3b8'
  if (n === 'oro') return '#eab308'
  if (n === 'diamante') return '#22d3ee'
  return '#cd7f32'
})

async function logout() {
  await auth.logout()
  showToast('Sesión cerrada.', 'info')
  router.replace({ name: 'login' })
}
</script>
