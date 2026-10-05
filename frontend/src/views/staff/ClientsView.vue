<template>
  <div class="page-padding space-y-4">
    <div class="flex items-center justify-between flex-wrap gap-3">
      <div>
        <h1 class="title-page">Gestión de clientes</h1>
        <p class="subtitle-page">Afiliados, membresías y administración</p>
      </div>
      <button class="btn-primary" @click="openCreate">
        <Plus class="w-4 h-4" /> Nuevo cliente
      </button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-2 text-center text-sm">
      <div class="card !p-3">
        <div class="text-xs uppercase text-club-gray-500 font-bold">Total</div>
        <div class="text-2xl font-black text-club-forest">{{ list.length }}</div>
      </div>
      <div class="card !p-3">
        <div class="text-xs uppercase text-club-gray-500 font-bold">Activos</div>
        <div class="text-2xl font-black text-club-wellness-dark">{{ activeCount }}</div>
      </div>
      <div class="card !p-3">
        <div class="text-xs uppercase text-club-gray-500 font-bold">Inactivos</div>
        <div class="text-2xl font-black text-club-red">{{ inactiveCount }}</div>
      </div>
    </div>

    <div class="flex flex-col md:flex-row gap-2">
      <div class="relative flex-1">
        <Search class="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-club-gray-400" />
        <input v-model="q" class="input pl-9" placeholder="Buscar por nombre, documento, email o teléfono..." />
      </div>
      <select v-model="filterStatus" class="input md:w-40">
        <option value="">Todos</option>
        <option value="active">Activos</option>
        <option value="inactive">Inactivos</option>
      </select>
    </div>

    <SkeletonLoader v-if="loading" />
    <EmptyState v-else-if="errorMsg && !list.length" icon="AlertTriangle" title="Error al cargar clientes" :description="errorMsg">
      <button class="btn-primary mt-3" @click="load">
        <RefreshCw class="w-4 h-4" /> Reintentar
      </button>
    </EmptyState>
    <EmptyState v-else-if="!filtered.length" icon="Users" title="Sin clientes" description="Invita a nuevos clientes a registrarse o crea uno nuevo." />
    <div v-else class="space-y-2">
      <div v-for="c in filtered" :key="c.id" class="card !p-3 flex items-start gap-3">
        <div class="w-11 h-11 rounded-xl bg-gradient-to-br from-club-forest to-club-gold text-white font-black flex items-center justify-center text-sm shrink-0">
          {{ initials(c) }}
        </div>
        <div class="flex-1 min-w-0">
          <div class="flex items-start justify-between gap-2 flex-wrap">
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 flex-wrap">
                <div class="font-bold text-sm text-club-graphite truncate">{{ c.first_name }} {{ c.last_name }}</div>
                <span class="chip" :class="c.is_active ? 'bg-club-wellness/15 text-club-wellness-dark' : 'bg-club-red/15 text-club-red'">
                  {{ c.is_active ? 'Activo' : 'Inactivo' }}
                </span>
                <span class="chip bg-club-forest/10 text-club-forest-dark">{{ c.membership_type || 'Básica' }}</span>
              </div>
              <div class="text-xs text-club-gray-500 mt-0.5 truncate">
                @{{ c.username }} · {{ c.document_type || '' }} {{ c.document_number || '' }}
              </div>
              <div class="text-xs text-club-gray-600 mt-1 flex flex-wrap gap-1.5">
                <span class="chip bg-club-ivory-dark text-club-gray-700">{{ c.phone || c.email }}</span>
                <span v-if="c.loyalty_profile?.tier" class="chip bg-club-gold/15 text-club-gold-dark">
                  {{ c.loyalty_profile.tier?.name || c.loyalty_profile.tier }}
                </span>
              </div>
            </div>
            <div class="flex gap-1.5 items-center shrink-0">
              <button class="btn-secondary !px-2.5 !py-1.5 text-xs" @click="openEdit(c)" title="Editar cliente">
                <Pencil class="w-3.5 h-3.5" />
              </button>
              <button
                class="btn-secondary !px-2.5 !py-1.5 text-xs"
                :class="c.is_active ? 'text-club-coral-dark hover:bg-club-coral/10' : 'text-club-wellness-dark hover:bg-club-wellness/10'"
                @click="confirmToggleActive(c)"
                :title="c.is_active ? 'Inactivar' : 'Activar'"
              >
                <PowerOff v-if="c.is_active" class="w-3.5 h-3.5" />
                <Play v-else class="w-3.5 h-3.5" />
              </button>
              <button class="btn-secondary !px-2.5 !py-1.5 text-xs text-club-red hover:bg-club-red/10" @click="confirmDelete(c)" title="Eliminar cliente">
                <Trash2 class="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="showForm" class="fixed inset-0 bg-black/50 z-50 flex items-start md:items-center justify-center p-3 md:p-6 overflow-y-auto" @click.self="closeForm">
        <div class="bg-white rounded-2xl w-full max-w-lg shadow-2xl">
          <div class="p-5 border-b border-club-gray-100 flex items-center justify-between">
            <div>
              <h2 class="text-lg font-black text-club-graphite">
                {{ editing ? 'Editar cliente' : 'Nuevo cliente' }}
              </h2>
              <p class="text-xs text-club-gray-500 mt-0.5">
                {{ editing ? 'Actualiza los datos del afiliado.' : 'Ingresa la información para crear el nuevo cliente.' }}
              </p>
            </div>
            <button class="btn-secondary !p-1.5" @click="closeForm"><X class="w-4 h-4" /></button>
          </div>

          <div class="p-5 space-y-3">
            <div class="grid grid-cols-2 gap-2.5">
              <div>
                <label class="label">Nombres</label>
                <input v-model.trim="form.first_name" class="input" placeholder="Ej: Juan Carlos" />
              </div>
              <div>
                <label class="label">Apellidos</label>
                <input v-model.trim="form.last_name" class="input" placeholder="Ej: Pérez Gómez" />
              </div>
            </div>

            <div class="grid grid-cols-2 gap-2.5">
              <div>
                <label class="label">Usuario</label>
                <input v-model.trim="form.username" class="input" placeholder="Ej: juanperez" />
              </div>
              <div>
                <label class="label">Email</label>
                <input v-model.trim="form.email" type="email" class="input" placeholder="juan@email.com" />
              </div>
            </div>

            <div class="grid grid-cols-3 gap-2.5">
              <div class="col-span-1">
                <label class="label">Tipo Doc.</label>
                <select v-model="form.document_type" class="input">
                  <option value="">-</option>
                  <option value="CC">CC</option>
                  <option value="CE">CE</option>
                  <option value="TI">TI</option>
                  <option value="Pasaporte">Pasaporte</option>
                </select>
              </div>
              <div class="col-span-2">
                <label class="label">Número</label>
                <input v-model.trim="form.document_number" class="input" placeholder="Ej: 123456789" />
              </div>
            </div>

            <div class="grid grid-cols-2 gap-2.5">
              <div>
                <label class="label">Teléfono</label>
                <input v-model.trim="form.phone" class="input" placeholder="Ej: 3001234567" />
              </div>
              <div>
                <label class="label">Membresía</label>
                <select v-model="form.membership_type" class="input">
                  <option value="">Básica</option>
                  <option value="Familiar">Familiar</option>
                  <option value="Premium">Premium</option>
                  <option value="Gold">Gold</option>
                </select>
              </div>
            </div>

            <div class="grid grid-cols-2 gap-2.5">
              <div>
                <label class="label">{{ editing ? 'Nueva contraseña (opcional)' : 'Contraseña *' }}</label>
                <input v-model="form.password" type="password" class="input" placeholder="Mínimo 8 caracteres" />
              </div>
              <div v-if="!editing">
                <label class="label">Confirmar *</label>
                <input v-model="form.password_confirm" type="password" class="input" placeholder="Repite la contraseña" />
              </div>
              <div v-else class="flex items-end gap-2">
                <label class="label w-full">Estado
                  <div class="mt-1.5 flex items-center gap-2">
                    <input type="checkbox" id="is_active_cb" v-model="form.is_active" class="w-4 h-4 accent-club-forest" />
                    <label for="is_active_cb" class="text-xs font-semibold text-club-graphite cursor-pointer">{{ form.is_active ? 'Activo' : 'Inactivo' }}</label>
                  </div>
                </label>
              </div>
            </div>
          </div>

          <div class="p-4 bg-club-gray-50 rounded-b-2xl flex justify-end gap-2 border-t border-club-gray-100">
            <button class="btn-secondary" @click="closeForm">Cancelar</button>
            <button class="btn-primary" :disabled="submitting" @click="submitForm">
              <Loader2 v-if="submitting" class="w-4 h-4 animate-spin" />
              {{ submitting ? 'Guardando...' : (editing ? 'Guardar cambios' : 'Crear cliente') }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <Teleport to="body">
      <div v-if="confirmToggle" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" @click.self="confirmToggle = null">
        <div class="bg-white rounded-2xl w-full max-w-md shadow-2xl">
          <div class="p-5">
            <div class="flex items-start gap-3">
              <div class="w-11 h-11 rounded-xl flex items-center justify-center shrink-0"
                   :class="confirmToggle.is_active ? 'bg-club-coral/15 text-club-coral-dark' : 'bg-club-wellness/15 text-club-wellness-dark'">
                <PowerOff v-if="confirmToggle.is_active" class="w-5 h-5" />
                <Play v-else class="w-5 h-5" />
              </div>
              <div class="flex-1">
                <h3 class="font-black text-club-graphite">
                  {{ confirmToggle.is_active ? '¿Inactivar cliente?' : '¿Activar cliente?' }}
                </h3>
                <p class="text-sm text-club-gray-600 mt-1">
                  {{ confirmToggle.is_active
                    ? `El cliente "${confirmToggle.first_name} ${confirmToggle.last_name}" no podrá iniciar sesión ni acceder a servicios mientras esté inactivo.`
                    : `Se habilitará nuevamente el acceso para "${confirmToggle.first_name} ${confirmToggle.last_name}".` }}
                </p>
              </div>
            </div>
          </div>
          <div class="p-4 bg-club-gray-50 rounded-b-2xl flex justify-end gap-2 border-t border-club-gray-100">
            <button class="btn-secondary" @click="confirmToggle = null">Cancelar</button>
            <button class="btn-primary" :class="confirmToggle.is_active ? '!bg-club-coral-dark' : '!bg-club-wellness-dark'" :disabled="submitting" @click="executeToggleActive">
              <Loader2 v-if="submitting" class="w-4 h-4 animate-spin" />
              {{ confirmToggle.is_active ? 'Sí, inactivar' : 'Sí, activar' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <Teleport to="body">
      <div v-if="confirmDeleteTarget" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" @click.self="confirmDeleteTarget = null">
        <div class="bg-white rounded-2xl w-full max-w-md shadow-2xl">
          <div class="p-5">
            <div class="flex items-start gap-3">
              <div class="w-11 h-11 rounded-xl bg-club-red/15 text-club-red flex items-center justify-center shrink-0">
                <AlertTriangle class="w-5 h-5" />
              </div>
              <div class="flex-1">
                <h3 class="font-black text-club-graphite">¿Eliminar cliente?</h3>
                <p class="text-sm text-club-gray-600 mt-1">
                  Esta acción es irreversible. Se eliminarán todos los datos asociados a
                  <b class="text-club-red">"{{ confirmDeleteTarget.first_name }} {{ confirmDeleteTarget.last_name }}"</b>
                  (reservas, recompensas, membresía, historial).
                </p>
                <div class="mt-3 bg-club-red/5 border border-club-red/20 rounded-xl p-3 text-xs text-club-red font-semibold">
                  Escribe el <b>usuario</b> para confirmar: <kbd class="px-1.5 py-0.5 bg-white rounded border">{{ confirmDeleteTarget.username }}</kbd>
                  <input v-model="deleteConfirmText" class="input mt-2 !text-sm" placeholder="Escribe aquí..." />
                </div>
              </div>
            </div>
          </div>
          <div class="p-4 bg-club-gray-50 rounded-b-2xl flex justify-end gap-2 border-t border-club-gray-100">
            <button class="btn-secondary" @click="confirmDeleteTarget = null">Cancelar</button>
            <button
              class="btn-primary !bg-club-red hover:!bg-club-red/90"
              :disabled="submitting || deleteConfirmText.trim() !== confirmDeleteTarget.username"
              @click="executeDelete"
            >
              <Loader2 v-if="submitting" class="w-4 h-4 animate-spin" />
              Eliminar permanentemente
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import {
  Plus, Search, Users, Pencil, PowerOff, Play, Trash2, X, Loader2, AlertTriangle, RefreshCw
} from 'lucide-vue-next'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import EmptyState from '@/components/EmptyState.vue'
import { showToast } from '@/utils/toast'
import api, { extractError } from '@/api/client'

const API_BASE = '/auth/admin/users'

const list = ref([])
const loading = ref(false)
const submitting = ref(false)
const errorMsg = ref('')
const q = ref('')
const filterStatus = ref('')

const showForm = ref(false)
const editing = ref(false)
const defaultForm = () => ({
  id: null,
  first_name: '',
  last_name: '',
  username: '',
  email: '',
  document_type: '',
  document_number: '',
  phone: '',
  membership_type: '',
  password: '',
  password_confirm: '',
  is_active: true,
})
const form = reactive(defaultForm())

const confirmToggle = ref(null)
const confirmDeleteTarget = ref(null)
const deleteConfirmText = ref('')

const activeCount = computed(() => (list.value || []).filter(c => c.is_active).length)
const inactiveCount = computed(() => (list.value || []).filter(c => !c.is_active).length)

const filtered = computed(() => {
  let data = (list.value || []).slice()
  if (filterStatus.value === 'active') data = data.filter(c => c.is_active)
  if (filterStatus.value === 'inactive') data = data.filter(c => !c.is_active)
  const s = q.value.trim().toLowerCase()
  if (!s) return data
  return data.filter(c =>
    String(c.username || '').toLowerCase().includes(s) ||
    String(c.first_name || '').toLowerCase().includes(s) ||
    String(c.last_name || '').toLowerCase().includes(s) ||
    String(c.document_number || '').includes(s) ||
    String(c.email || '').toLowerCase().includes(s) ||
    String(c.phone || '').includes(s)
  )
})

function initials(c) {
  return ((c.first_name?.[0] || 'U') + (c.last_name?.[0] || '')).toUpperCase()
}

async function load() {
  loading.value = true
  errorMsg.value = ''
  try {
    const resp = await api.get(API_BASE + '/', {
      params: { role: 'CLIENT', page_size: 500 },
    })
    const raw = resp.data?.results || resp.data
    const data = Array.isArray(raw) ? raw : (Array.isArray(raw?.items) ? raw.items : [])
    list.value = data.filter(x => !!x && typeof x === 'object')
    return list.value
  } catch (e) {
    const status = e?.response?.status
    if (status === 401 || status === 403) {
      try {
        const { useAuthStore } = await import('@/stores/auth')
        const auth = useAuthStore()
        auth.clearSession()
        if (window?.location) {
          window.location.href = '/#/login'
        }
      } catch (_) {}
      const msg = status === 403
        ? 'No tienes permisos de Administrador para gestionar clientes. Por favor inicia sesión con cuenta Admin.'
        : 'Tu sesión venció. Por favor vuelve a iniciar sesión.'
      errorMsg.value = msg
      showToast(msg, 'error')
      list.value = []
      return []
    }
    const msg = extractError(e, 'No se pudo cargar el listado de clientes.')
    errorMsg.value = msg
    showToast(msg, 'error')
    list.value = []
    return []
  } finally {
    loading.value = false
  }
}

function openCreate() {
  Object.assign(form, defaultForm())
  editing.value = false
  showForm.value = true
}

function openEdit(c) {
  Object.assign(form, defaultForm(), {
    id: c.id,
    first_name: c.first_name || '',
    last_name: c.last_name || '',
    username: c.username || '',
    email: c.email || '',
    document_type: c.document_type || '',
    document_number: c.document_number || '',
    phone: c.phone || '',
    membership_type: c.membership_type || '',
    is_active: !!c.is_active,
  })
  editing.value = true
  showForm.value = true
}

function closeForm() {
  if (submitting.value) return
  showForm.value = false
  Object.assign(form, defaultForm())
}

async function submitForm() {
  if (!form.first_name.trim() || !form.last_name.trim()) {
    showToast('Debes ingresar nombres y apellidos.', 'error'); return
  }
  if (!form.username.trim()) {
    showToast('Debes ingresar un nombre de usuario.', 'error'); return
  }
  if (!form.email.trim()) {
    showToast('Debes ingresar un correo electrónico.', 'error'); return
  }
  if (!editing.value) {
    if (!form.password) {
      showToast('Debes ingresar una contraseña (mínimo 8 caracteres).', 'error'); return
    }
    if (form.password.length < 8) {
      showToast('La contraseña debe tener al menos 8 caracteres.', 'error'); return
    }
    if (form.password !== form.password_confirm) {
      showToast('Las contraseñas no coinciden.', 'error'); return
    }
  }

  submitting.value = true
  try {
    if (editing.value) {
      const payload = {
        first_name: form.first_name.trim(),
        last_name: form.last_name.trim(),
        username: form.username.trim(),
        email: form.email.trim(),
        document_type: form.document_type || '',
        document_number: form.document_number.trim() || '',
        phone: form.phone.trim() || '',
        membership_type: form.membership_type || '',
        is_active: !!form.is_active,
      }
      await api.patch(`${API_BASE}/${form.id}/`, payload)
      if (form.password.trim()) {
        if (form.password.length < 8) {
          showToast('La nueva contraseña debe tener mínimo 8 caracteres.', 'error'); return
        }
        await api.post(`${API_BASE}/${form.id}/set-password/`, { new_password: form.password.trim() })
      }
      showToast('Cliente actualizado exitosamente.', 'success')
    } else {
      await api.post(API_BASE + '/', {
        first_name: form.first_name.trim(),
        last_name: form.last_name.trim(),
        username: form.username.trim(),
        email: form.email.trim(),
        document_type: form.document_type || '',
        document_number: form.document_number.trim() || '',
        phone: form.phone.trim() || '',
        membership_type: form.membership_type || '',
        password: form.password,
        role: 'CLIENT',
        is_active: true,
      })
      showToast('Cliente creado exitosamente.', 'success')
    }
    closeForm()
    await load()
  } catch (err) {
    const msg = extractError(err, 'Ocurrió un error al guardar el cliente.')
    showToast(msg, 'error')
  } finally {
    submitting.value = false
  }
}

function confirmToggleActive(c) {
  confirmToggle.value = c
}

async function executeToggleActive() {
  const c = confirmToggle.value
  if (!c) return
  submitting.value = true
  try {
    await api.post(`${API_BASE}/${c.id}/toggle-active/`)
    showToast(c.is_active ? 'Cliente inactivado exitosamente.' : 'Cliente activado exitosamente.', 'success')
    confirmToggle.value = null
    await load()
  } catch (err) {
    const msg = extractError(err, 'No se pudo actualizar el estado del cliente.')
    showToast(msg, 'error')
  } finally {
    submitting.value = false
  }
}

function confirmDelete(c) {
  confirmDeleteTarget.value = c
  deleteConfirmText.value = ''
}

async function executeDelete() {
  const c = confirmDeleteTarget.value
  if (!c) return
  submitting.value = true
  try {
    await api.delete(`${API_BASE}/${c.id}/`)
    showToast('Cliente eliminado permanentemente.', 'success')
    confirmDeleteTarget.value = null
    deleteConfirmText.value = ''
    await load()
  } catch (err) {
    const msg = extractError(err, 'No se pudo eliminar el cliente.')
    showToast(msg, 'error')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  load()
})
</script>
