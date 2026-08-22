<template>
  <div class="min-h-screen w-full bg-gradient-to-b from-club-blue via-sky-600 to-club-green flex items-center justify-center px-5 py-10">
    <div class="w-full max-w-md">
      <div class="text-center mb-7 text-white">
        <div class="mx-auto w-20 h-20 rounded-3xl bg-white/15 backdrop-blur flex items-center justify-center text-3xl font-black border border-white/30 shadow-xl">
          CF
        </div>
        <h1 class="mt-4 text-3xl font-black tracking-tight">Club Family Health</h1>
        <p class="mt-1 text-white/80 text-sm">Maicao · La Guajira · Iniciar sesión</p>
      </div>

      <div class="bg-white rounded-2xl shadow-2xl p-5 sm:p-7">
        <div v-if="error" class="mb-4 p-3 rounded-xl bg-club-red/10 border border-club-red/20 text-club-red text-sm font-semibold">
          {{ error }}
        </div>
        <form @submit.prevent="submit" class="flex flex-col gap-4">
          <div>
            <label class="label">Usuario</label>
            <div class="relative">
              <User class="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-club-gray-400" />
              <input
                v-model="form.username"
                type="text"
                placeholder="ej. cliente1_fh"
                class="input pl-9"
                autocomplete="username"
                required
              />
            </div>
          </div>
          <div>
            <label class="label">Contraseña</label>
            <div class="relative">
              <Lock class="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-club-gray-400" />
              <input
                v-model="form.password"
                :type="showPass ? 'text' : 'password'"
                placeholder="••••••••"
                class="input pl-9 pr-10"
                autocomplete="current-password"
                required
                minlength="6"
              />
              <button type="button" class="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 text-club-gray-400 hover:text-club-blue" @click="showPass = !showPass">
                <Eye v-if="!showPass" class="w-4 h-4" />
                <EyeOff v-else class="w-4 h-4" />
              </button>
            </div>
          </div>
          <label class="flex items-center gap-2 text-sm text-club-gray-700 select-none cursor-pointer">
            <input type="checkbox" v-model="remember" class="w-4 h-4 rounded border-club-gray-300 text-club-blue focus:ring-club-blue" />
            Recordarme en este equipo
          </label>
          <button class="btn-success w-full !py-3 !text-base" :disabled="loading">
            <Loader2 v-if="loading" class="w-4 h-4 animate-spin" />
            Ingresar
          </button>
        </form>

        <div class="mt-6 pt-5 border-t border-club-gray-100 flex flex-col gap-2 text-sm">
          <div class="flex items-center justify-between">
            <span class="text-club-gray-500">¿Eres nuevo?</span>
            <button class="text-club-blue font-bold hover:underline" @click="$router.push({ name: 'register' })">
              Crear cuenta
            </button>
          </div>
          <div class="rounded-xl bg-club-gray-50 border border-club-gray-200 p-3 text-xs">
            <div class="font-bold text-club-gray-700 mb-1">Accesos de demo:</div>
            <div class="grid grid-cols-1 gap-0.5 text-club-gray-600">
              <div><b>Admin:</b> admin_fh / AdminFH2026*!</div>
              <div><b>Recepción:</b> recepcion_fh / RecepcionFH2026*!</div>
              <div><b>Cliente:</b> cliente1_fh / Cliente1FH*!</div>
            </div>
          </div>
        </div>
      </div>

      <div class="text-center text-white/75 text-xs mt-6">
        Club Family Health MF · NIT 32739028-5
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { User, Lock, Eye, EyeOff, Loader2 } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { showToast } from '@/utils/toast'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const form = reactive({ username: '', password: '' })
const showPass = ref(false)
const remember = ref(true)
const loading = ref(false)
const error = ref('')

watch(() => auth.error, (v) => { error.value = v || '' })

async function submit() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(form.username.trim(), form.password)
    showToast(`Bienvenido/a, ${auth.displayName}`, 'success', 'Sesión iniciada')
    const next = route.query.next
    if (typeof next === 'string' && next.startsWith('/')) {
      router.replace(next)
    } else {
      router.replace({ name: 'root' })
    }
  } catch (e) {
    error.value = e
  } finally {
    loading.value = false
  }
}
</script>
