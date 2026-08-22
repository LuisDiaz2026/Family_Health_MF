<template>
  <div class="min-h-screen w-full bg-gradient-to-b from-club-blue via-sky-600 to-club-green px-4 py-8">
    <div class="w-full max-w-md mx-auto">
      <button class="mb-4 inline-flex items-center gap-1 text-white/90 text-sm font-semibold hover:underline" @click="$router.back()">
        <ArrowLeft class="w-4 h-4" /> Volver
      </button>

      <div class="bg-white rounded-2xl shadow-2xl p-5 sm:p-6">
        <div class="mb-5">
          <h1 class="text-xl font-extrabold text-club-gray-900">Crear cuenta de cliente</h1>
          <p class="text-sm text-club-gray-500 mt-1">Únete a Club Family Health Maicao y empieza a ganar puntos.</p>
        </div>

        <div v-if="error" class="mb-4 p-3 rounded-xl bg-club-red/10 border border-club-red/20 text-club-red text-sm font-semibold">
          {{ error }}
        </div>

        <form @submit.prevent="submit" class="flex flex-col gap-3.5">
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="label">Nombres</label>
              <input v-model="form.first_name" class="input" placeholder="Juan" required />
            </div>
            <div>
              <label class="label">Apellidos</label>
              <input v-model="form.last_name" class="input" placeholder="Pérez" required />
            </div>
          </div>

          <div>
            <label class="label">Usuario (ingreso)</label>
            <input v-model="form.username" class="input" placeholder="juan_perez" required minlength="4" />
          </div>
          <div>
            <label class="label">Correo electrónico</label>
            <input v-model="form.email" type="email" class="input" placeholder="tu@correo.com" required />
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="label">Tipo doc.</label>
              <select v-model="form.document_type" class="input">
                <option value="CC">Cédula</option>
                <option value="TI">Tarjeta identidad</option>
                <option value="CE">Cédula extranjera</option>
                <option value="PAS">Pasaporte</option>
              </select>
            </div>
            <div>
              <label class="label">N° documento</label>
              <input v-model="form.document_number" class="input" placeholder="12345678" required />
            </div>
          </div>

          <div>
            <label class="label">Celular</label>
            <input v-model="form.phone" class="input" placeholder="+57 300 123 4567" required />
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="label">Contraseña</label>
              <input v-model="form.password" type="password" class="input" required minlength="8" />
            </div>
            <div>
              <label class="label">Confirmar</label>
              <input v-model="form.password_confirm" type="password" class="input" required minlength="8" />
            </div>
          </div>

          <label class="flex items-start gap-2 p-3 rounded-xl bg-club-blue/5 border border-club-blue/20 text-sm text-club-gray-800 cursor-pointer">
            <input v-model="form.privacy_policy_accepted" type="checkbox" class="mt-0.5 w-4 h-4 rounded text-club-blue" required />
            <span>
              Acepto la <a class="text-club-blue font-bold hover:underline" href="#">Política de Tratamiento de Datos Personales (Ley 1581/2012)</a>
              y los términos y condiciones del club.
            </span>
          </label>

          <button class="btn-primary w-full !py-3 !text-base" :disabled="loading">
            <Loader2 v-if="loading" class="w-4 h-4 animate-spin" />
            Crear cuenta y acceder
          </button>
        </form>

        <div class="mt-5 pt-4 border-t text-sm text-center text-club-gray-600">
          ¿Ya tienes cuenta?
          <button class="font-bold text-club-blue hover:underline ml-1" @click="$router.push({ name: 'login' })">
            Ingresa aquí
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, Loader2 } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { showToast } from '@/utils/toast'

const auth = useAuthStore()
const router = useRouter()

const form = reactive({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  document_type: 'CC',
  document_number: '',
  phone: '',
  password: '',
  password_confirm: '',
  privacy_policy_accepted: false,
})
const loading = ref(false)
const error = ref('')

watch(() => auth.error, (v) => { error.value = v || '' })

async function submit() {
  error.value = ''
  if (form.password !== form.password_confirm) {
    error.value = 'Las contraseñas no coinciden.'
    return
  }
  if (!form.privacy_policy_accepted) {
    error.value = 'Debes aceptar la política de privacidad.'
    return
  }
  loading.value = true
  try {
    await auth.register({ ...form })
    showToast('Cuenta creada exitosamente. Bienvenido/a!', 'success')
    router.replace({ name: 'client-home' })
  } catch (e) {
    error.value = e
  } finally {
    loading.value = false
  }
}
</script>
