<template>
  <div class="page-padding space-y-4">
    <div class="flex items-center justify-between flex-wrap gap-3">
      <div>
        <h1 class="title-page">Ofertas refresquería</h1>
        <p class="subtitle-page">Promociones basadas en productos reales del inventario</p>
      </div>
      <button class="btn-primary" @click="openCreate">
        <Plus class="w-4 h-4" /> Nueva oferta
      </button>
    </div>

    <div class="grid grid-cols-3 gap-2 text-center text-sm">
      <div class="card !p-3">
        <div class="text-xs uppercase text-club-gray-500 font-bold">Total</div>
        <div class="text-2xl font-black text-club-forest">{{ offers.length }}</div>
      </div>
      <div class="card !p-3">
        <div class="text-xs uppercase text-club-gray-500 font-bold">Vigentes</div>
        <div class="text-2xl font-black text-club-wellness-dark">{{ activeCount }}</div>
      </div>
      <div class="card !p-3">
        <div class="text-xs uppercase text-club-gray-500 font-bold">Inactivas</div>
        <div class="text-2xl font-black text-club-gray-500">{{ inactiveCount }}</div>
      </div>
    </div>

    <div class="flex flex-col md:flex-row gap-2">
      <div class="relative flex-1">
        <Search class="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-club-gray-400" />
        <input v-model="q" class="input pl-9" placeholder="Buscar oferta por nombre..." />
      </div>
      <select v-model="filterTag" class="input md:w-48">
        <option value="">Todas las etiquetas</option>
        <option value="COMBO">Combo</option>
        <option value="2X1">2x1</option>
        <option value="DESCUENTO">Descuento</option>
        <option value="ENERGIA">Energía</option>
        <option value="PROMO">Promoción</option>
      </select>
    </div>

    <SkeletonLoader v-if="loading" />
    <EmptyState v-else-if="!filtered.length" icon="Tag" title="Sin ofertas" description="Crea tu primera oferta para mostrarla a los clientes." />
    <div v-else class="space-y-3">
      <div v-for="o in filtered" :key="o.id" class="card !p-3">
        <div class="flex items-start justify-between gap-3">
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 flex-wrap">
              <span class="text-[10px] font-bold uppercase chip bg-club-red/15 text-club-red">{{ o.tag_display || o.tag }}</span>
              <span
                v-if="o.is_valid_now"
                class="chip bg-club-wellness/15 text-club-wellness-dark !text-[10px]"
              >Vigente</span>
              <span v-else class="chip bg-club-gray-100 text-club-gray-500 !text-[10px]">No vigente</span>
              <span v-if="!o.is_active" class="chip bg-club-gray-100 text-club-gray-500 !text-[10px]">Inactiva</span>
            </div>
            <h3 class="font-bold text-sm text-club-graphite mt-1.5">{{ o.name }}</h3>
            <p v-if="o.description" class="text-xs text-club-gray-500 mt-0.5 line-clamp-2">{{ o.description }}</p>

            <div class="flex items-center gap-3 mt-2 text-xs flex-wrap">
              <div>
                <span class="text-club-gray-500 line-through">${{ formatMoney(o.regular_price) }}</span>
                <span class="ml-2 text-club-gold-dark font-black text-base">${{ formatMoney(o.offer_price) }}</span>
                <span v-if="o.discount_percent" class="ml-1 text-club-red font-bold">-{{ o.discount_percent }}%</span>
              </div>
            </div>

            <div class="flex items-center gap-3 mt-1.5 text-[11px] text-club-gray-500 flex-wrap">
              <span v-if="o.start_date || o.end_date">
                <Calendar class="w-3 h-3 inline" />
                {{ formatDate(o.start_date) }} → {{ formatDate(o.end_date) || 'sin fin' }}
              </span>
              <span>
                <Package class="w-3 h-3 inline" />
                {{ o.products?.length || o.product_count || 0 }} producto(s)
              </span>
              <span v-if="o.stock > 0">
                Stock: {{ o.stock }}
              </span>
            </div>
          </div>

          <div class="flex gap-1.5 items-start shrink-0">
            <button class="btn-secondary !px-2.5 !py-1.5 text-xs" @click="openEdit(o)" title="Editar oferta">
              <Pencil class="w-3.5 h-3.5" />
            </button>
            <button class="btn-secondary !px-2.5 !py-1.5 text-xs text-club-red hover:bg-club-red/10" @click="confirmDelete(o)" title="Eliminar oferta">
              <Trash2 class="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal Crear / Editar oferta -->
    <Teleport to="body">
      <div v-if="showForm" class="fixed inset-0 bg-black/50 z-50 flex items-start md:items-center justify-center p-3 md:p-6 overflow-y-auto" @click.self="closeForm">
        <div class="bg-white rounded-2xl w-full max-w-lg shadow-2xl my-4">
          <div class="p-5 border-b border-club-gray-100 flex items-center justify-between">
            <div>
              <h2 class="text-lg font-black text-club-graphite">
                {{ editing ? 'Editar oferta' : 'Nueva oferta' }}
              </h2>
              <p class="text-xs text-club-gray-500 mt-0.5">
                {{ editing ? 'Actualiza los datos de la oferta.' : 'Define la promoción y su vigencia.' }}
              </p>
            </div>
            <button class="btn-secondary !p-1.5" @click="closeForm"><X class="w-4 h-4" /></button>
          </div>

          <div class="p-5 space-y-3">
            <div>
              <label class="label">Nombre de la oferta *</label>
              <input v-model.trim="form.name" class="input" placeholder="Ej: Combo Hamburguesa + Gaseosa" />
            </div>

            <div class="grid grid-cols-2 gap-2.5">
              <div>
                <label class="label">Etiqueta *</label>
                <select v-model="form.tag" class="input">
                  <option value="PROMO">Promoción</option>
                  <option value="COMBO">Combo</option>
                  <option value="2X1">2x1</option>
                  <option value="DESCUENTO">Descuento</option>
                  <option value="ENERGIA">Energía</option>
                </select>
              </div>
              <div>
                <label class="label">Stock (0 = sin límite)</label>
                <input v-model.number="form.stock" type="number" min="0" step="1" class="input" placeholder="0" />
              </div>
            </div>

            <div>
              <label class="label">Productos incluidos</label>
              <div class="grid grid-cols-1 gap-1.5 max-h-44 overflow-y-auto border border-club-gray-200 rounded-lg p-2">
                <label
                  v-for="p in productList"
                  :key="p.id"
                  class="flex items-center gap-2 text-sm cursor-pointer hover:bg-club-gray-50 p-1.5 rounded"
                >
                  <input type="checkbox" :value="p.id" v-model="form.product_ids" class="w-4 h-4 accent-club-forest" />
                  <span class="flex-1 truncate">{{ p.name }}</span>
                  <span class="text-xs text-club-gray-500 shrink-0">${{ formatMoney(p.price) }}</span>
                </label>
                <div v-if="!productList.length" class="text-xs text-club-gray-400 text-center py-3">
                  No hay productos disponibles
                </div>
              </div>
              <button type="button" class="text-xs text-club-forest font-bold mt-1" @click="autoFillRegularPrice">
                Usar suma de productos como precio regular
              </button>
            </div>

            <div class="grid grid-cols-2 gap-2.5">
              <div>
                <label class="label">Precio regular (COP) *</label>
                <input v-model.number="form.regular_price" type="number" min="0" step="1" class="input" placeholder="0" />
              </div>
              <div>
                <label class="label">Precio oferta (COP) *</label>
                <input v-model.number="form.offer_price" type="number" min="0" step="1" class="input" placeholder="0" />
              </div>
            </div>
            <div v-if="form.regular_price && form.offer_price" class="text-xs text-club-gray-500">
              Descuento aplicado: <b class="text-club-red">{{ calcDiscount }}%</b>
            </div>

            <div class="grid grid-cols-2 gap-2.5">
              <div>
                <label class="label">Inicio vigencia</label>
                <input v-model="form.start_date" type="datetime-local" class="input" />
                <div class="text-[10px] text-club-gray-400 mt-0.5">Vacío = inmediato</div>
              </div>
              <div>
                <label class="label">Fin vigencia</label>
                <input v-model="form.end_date" type="datetime-local" class="input" />
                <div class="text-[10px] text-club-gray-400 mt-0.5">Vacío = sin caducidad</div>
              </div>
            </div>

            <div class="flex items-center gap-2">
              <input type="checkbox" id="is_active_cb" v-model="form.is_active" class="w-4 h-4 accent-club-forest" />
              <label for="is_active_cb" class="text-sm font-semibold text-club-graphite cursor-pointer">
                {{ form.is_active ? 'Oferta activa' : 'Oferta inactiva' }}
              </label>
            </div>

            <div>
              <label class="label">Descripción</label>
              <textarea v-model.trim="form.description" class="input" rows="2" placeholder="Detalles de la oferta (opcional)"></textarea>
            </div>
          </div>

          <div class="p-4 bg-club-gray-50 rounded-b-2xl flex justify-end gap-2 border-t border-club-gray-100">
            <button class="btn-secondary" @click="closeForm">Cancelar</button>
            <button class="btn-primary" :disabled="submitting" @click="submitForm">
              <Loader2 v-if="submitting" class="w-4 h-4 animate-spin" />
              {{ submitting ? 'Guardando...' : (editing ? 'Guardar cambios' : 'Crear oferta') }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Modal confirmar eliminación -->
    <Teleport to="body">
      <div v-if="confirmDeleteTarget" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" @click.self="confirmDeleteTarget = null">
        <div class="bg-white rounded-2xl w-full max-w-md shadow-2xl">
          <div class="p-5">
            <div class="flex items-start gap-3">
              <div class="w-11 h-11 rounded-xl bg-club-red/15 text-club-red flex items-center justify-center shrink-0">
                <AlertTriangle class="w-5 h-5" />
              </div>
              <div class="flex-1">
                <h3 class="font-black text-club-graphite">¿Eliminar oferta?</h3>
                <p class="text-sm text-club-gray-600 mt-1">
                  Esta acción es irreversible. Se eliminará permanentemente la oferta
                  <b class="text-club-red">"{{ confirmDeleteTarget.name }}"</b>.
                </p>
              </div>
            </div>
          </div>
          <div class="p-4 bg-club-gray-50 rounded-b-2xl flex justify-end gap-2 border-t border-club-gray-100">
            <button class="btn-secondary" @click="confirmDeleteTarget = null">Cancelar</button>
            <button
              class="btn-primary !bg-club-red hover:!bg-club-red/90"
              :disabled="submitting"
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
  Plus, Search, Pencil, Trash2, X, Loader2, AlertTriangle, Calendar, Package
} from 'lucide-vue-next'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import EmptyState from '@/components/EmptyState.vue'
import { showToast } from '@/utils/toast'
import api, { extractError } from '@/api/client'
import { useRefreshmentsStore } from '@/stores/refreshments'

const refreshments = useRefreshmentsStore()
const offers = ref([])
const productList = ref([])
const loading = ref(true)
const submitting = ref(false)
const q = ref('')
const filterTag = ref('')

const showForm = ref(false)
const editing = ref(false)
const defaultForm = () => ({
  id: null,
  name: '',
  tag: 'PROMO',
  description: '',
  product_ids: [],
  regular_price: '',
  offer_price: '',
  start_date: '',
  end_date: '',
  is_active: true,
  stock: 0,
})
const form = reactive(defaultForm())

const confirmDeleteTarget = ref(null)

const activeCount = computed(() => offers.value.filter(o => o.is_valid_now).length)
const inactiveCount = computed(() => offers.value.filter(o => !o.is_active || !o.is_valid_now).length)

const calcDiscount = computed(() => {
  if (!form.regular_price || !form.offer_price) return 0
  const diff = Number(form.regular_price) - Number(form.offer_price)
  if (diff <= 0) return 0
  return Math.round(diff * 100 / Number(form.regular_price))
})

const filtered = computed(() => {
  let data = offers.value.slice()
  if (filterTag.value) data = data.filter(o => o.tag === filterTag.value)
  const s = q.value.trim().toLowerCase()
  if (!s) return data
  return data.filter(o => String(o.name || '').toLowerCase().includes(s))
})

function formatMoney(n) { return Number(n || 0).toLocaleString('es-CO') }

function formatDate(iso) {
  if (!iso) return ''
  try {
    const d = new Date(iso)
    return d.toLocaleString('es-CO', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
  } catch (_) { return iso }
}

function toLocalInput(iso) {
  if (!iso) return ''
  try {
    const d = new Date(iso)
    const pad = (n) => String(n).padStart(2, '0')
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`
  } catch (_) { return '' }
}

async function loadProducts() {
  try {
    const all = []
    let page = 1
    while (true) {
      const resp = await api.get(`/refreshments/products/?page=${page}&page_size=100`)
      const data = resp.data
      const items = data?.results || data || []
      all.push(...items)
      if (!data?.next) break
      page++
    }
    productList.value = all
  } catch (_) {
    productList.value = []
  }
}

async function load() {
  loading.value = true
  try {
    offers.value = await refreshments.listOffers()
  } catch (e) {
    const status = e?.response?.status
    if (status === 401 || status === 403) {
      try {
        const { useAuthStore } = await import('@/stores/auth')
        const auth = useAuthStore()
        auth.clearSession()
        if (window?.location) window.location.href = '/#/login'
      } catch (_) {}
      showToast('No tienes permisos para gestionar ofertas.', 'error')
    } else {
      showToast(extractError(e, 'No se pudieron cargar las ofertas.'), 'error')
    }
  } finally {
    loading.value = false
  }
}

function openCreate() {
  Object.assign(form, defaultForm())
  editing.value = false
  showForm.value = true
}

function openEdit(o) {
  Object.assign(form, defaultForm(), {
    id: o.id,
    name: o.name || '',
    tag: o.tag || 'PROMO',
    description: o.description || '',
    product_ids: (o.products || []).map(p => p.id),
    regular_price: o.regular_price ?? '',
    offer_price: o.offer_price ?? '',
    start_date: toLocalInput(o.start_date),
    end_date: toLocalInput(o.end_date),
    is_active: !!o.is_active,
    stock: o.stock ?? 0,
  })
  editing.value = true
  showForm.value = true
}

function closeForm() {
  if (submitting.value) return
  showForm.value = false
  Object.assign(form, defaultForm())
}

function autoFillRegularPrice() {
  const ids = form.product_ids || []
  const total = ids.reduce((sum, id) => {
    const p = productList.value.find(x => x.id === id)
    return sum + (p ? Number(p.price) : 0)
  }, 0)
  if (total > 0) form.regular_price = total
}

async function submitForm() {
  if (!form.name.trim()) { showToast('Debes ingresar el nombre de la oferta.', 'error'); return }
  if (form.regular_price === '' || form.regular_price === null || Number(form.regular_price) < 0) {
    showToast('Debes ingresar un precio regular válido.', 'error'); return
  }
  if (form.offer_price === '' || form.offer_price === null || Number(form.offer_price) < 0) {
    showToast('Debes ingresar un precio de oferta válido.', 'error'); return
  }
  if (Number(form.offer_price) > Number(form.regular_price)) {
    showToast('El precio de oferta no puede ser mayor al precio regular.', 'error'); return
  }

  submitting.value = true
  try {
    const payload = {
      name: form.name.trim(),
      tag: form.tag,
      description: form.description.trim() || null,
      product_ids: form.product_ids,
      regular_price: Number(form.regular_price),
      offer_price: Number(form.offer_price),
      start_date: form.start_date || null,
      end_date: form.end_date || null,
      is_active: !!form.is_active,
      stock: Number(form.stock) || 0,
    }
    if (editing.value) {
      await refreshments.updateOffer(form.id, payload)
      showToast('Oferta actualizada exitosamente.', 'success')
    } else {
      await refreshments.createOffer(payload)
      showToast('Oferta creada exitosamente.', 'success')
    }
    closeForm()
    await load()
  } catch (err) {
    showToast(extractError(err, 'Ocurrió un error al guardar la oferta.'), 'error')
  } finally {
    submitting.value = false
  }
}

function confirmDelete(o) {
  confirmDeleteTarget.value = o
}

async function executeDelete() {
  const o = confirmDeleteTarget.value
  if (!o) return
  submitting.value = true
  try {
    await refreshments.deleteOffer(o.id)
    showToast('Oferta eliminada permanentemente.', 'success')
    confirmDeleteTarget.value = null
    await load()
  } catch (err) {
    showToast(extractError(err, 'No se pudo eliminar la oferta.'), 'error')
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  await Promise.all([load(), loadProducts()])
})
</script>
