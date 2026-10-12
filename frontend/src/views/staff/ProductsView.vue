<template>
  <div class="page-padding space-y-4">
    <div class="flex items-center justify-between flex-wrap gap-3">
      <div>
        <h1 class="title-page">Inventario productos</h1>
        <p class="subtitle-page">SKU, stock y precios de refresquería</p>
      </div>
      <button class="btn-primary" @click="openCreate">
        <Plus class="w-4 h-4" /> Crear producto
      </button>
    </div>

    <div class="grid grid-cols-3 gap-2 text-center text-sm">
      <div class="card !p-3">
        <div class="text-xs uppercase text-club-gray-500 font-bold">Total</div>
        <div class="text-2xl font-black text-club-forest">{{ totalProducts }}</div>
      </div>
      <div class="card !p-3">
        <div class="text-xs uppercase text-club-gray-500 font-bold">Stock bajo</div>
        <div class="text-2xl font-black text-club-coral">{{ lowStock }}</div>
      </div>
      <div class="card !p-3">
        <div class="text-xs uppercase text-club-gray-500 font-bold">Agotados</div>
        <div class="text-2xl font-black text-club-red">{{ outOfStock }}</div>
      </div>
    </div>

    <div class="flex flex-col md:flex-row gap-2">
      <div class="relative flex-1">
        <Search class="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-club-gray-400" />
        <input v-model="q" class="input pl-9" placeholder="Buscar producto por nombre o SKU..." />
      </div>
      <select v-model="filterCategory" class="input md:w-48">
        <option value="">Todas las categorías</option>
        <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
      </select>
    </div>

    <SkeletonLoader v-if="loading" />
    <EmptyState v-else-if="!filtered.length" icon="Package" title="Sin productos" description="Ajusta la búsqueda o crea un producto nuevo." />
    <div v-else class="space-y-3">
      <div v-for="p in filtered" :key="p.id" class="card !p-3 flex gap-3">
        <div class="w-14 h-14 rounded-lg bg-club-ivory-dark flex items-center justify-center shrink-0">
          <Package class="w-7 h-7 text-club-gray-400" />
        </div>
        <div class="flex-1 min-w-0">
          <div class="flex items-start justify-between gap-2 flex-wrap">
            <div class="min-w-0 flex-1">
              <div class="font-bold text-sm text-club-graphite truncate">{{ p.name }}</div>
              <div class="text-[11px] text-club-gray-500 mt-0.5">SKU: {{ p.sku || '-' }} · {{ p.category?.name || 'Sin categoría' }}</div>
            </div>
            <div class="flex gap-1.5 items-center shrink-0">
              <button class="btn-secondary !px-2.5 !py-1.5 text-xs" @click="openRestock(p)" title="Surtir inventario">
                <PackagePlus class="w-3.5 h-3.5" />
              </button>
              <button class="btn-secondary !px-2.5 !py-1.5 text-xs" @click="openEdit(p)" title="Editar producto">
                <Pencil class="w-3.5 h-3.5" />
              </button>
              <button class="btn-secondary !px-2.5 !py-1.5 text-xs text-club-red hover:bg-club-red/10" @click="confirmDelete(p)" title="Eliminar producto">
                <Trash2 class="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
          <div class="mt-2 flex items-center justify-between text-xs flex-wrap gap-2">
            <div class="text-club-gray-600">
              Stock: <b class="text-club-graphite">{{ p.stock }}</b>
              <span v-if="(p.stock || 0) <= 0" class="chip bg-club-red/15 text-club-red !text-[10px] ml-1">Agotado</span>
              <span v-else-if="(p.stock || 0) <= (p.min_stock || 5)" class="chip bg-club-coral/15 text-club-coral-dark !text-[10px] ml-1">Stock bajo</span>
              <span v-else class="chip bg-club-wellness/15 text-club-wellness-dark !text-[10px] ml-1">OK</span>
              <span class="ml-2 text-club-gray-400">Min: {{ p.min_stock || 0 }}</span>
            </div>
            <div class="font-black text-club-gold-dark">${{ formatMoney(p.price) }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal Crear / Editar producto -->
    <Teleport to="body">
      <div v-if="showForm" class="fixed inset-0 bg-black/50 z-50 flex items-start md:items-center justify-center p-3 md:p-6 overflow-y-auto" @click.self="closeForm">
        <div class="bg-white rounded-2xl w-full max-w-lg shadow-2xl">
          <div class="p-5 border-b border-club-gray-100 flex items-center justify-between">
            <div>
              <h2 class="text-lg font-black text-club-graphite">
                {{ editing ? 'Editar producto' : 'Nuevo producto' }}
              </h2>
              <p class="text-xs text-club-gray-500 mt-0.5">
                {{ editing ? 'Actualiza los datos del producto.' : 'Ingresa la información para crear el producto.' }}
              </p>
            </div>
            <button class="btn-secondary !p-1.5" @click="closeForm"><X class="w-4 h-4" /></button>
          </div>

          <div class="p-5 space-y-3">
            <div>
              <label class="label">Nombre del producto *</label>
              <input v-model.trim="form.name" class="input" placeholder="Ej: Gatorade 500 ML" />
            </div>

            <div class="grid grid-cols-2 gap-2.5">
              <div>
                <label class="label">Categoría *</label>
                <select v-model="form.category_id" class="input">
                  <option value="" disabled>Selecciona...</option>
                  <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
                </select>
              </div>
              <div>
                <label class="label">SKU</label>
                <input v-model.trim="form.sku" class="input" placeholder="Código de barras" />
              </div>
            </div>

            <div class="grid grid-cols-2 gap-2.5">
              <div>
                <label class="label">Precio de venta (COP) *</label>
                <input v-model.number="form.price" type="number" min="0" step="1" class="input" placeholder="0" />
              </div>
              <div>
                <label class="label">Costo unitario (COP)</label>
                <input v-model.number="form.cost" type="number" min="0" step="1" class="input" placeholder="0" />
              </div>
            </div>

            <div class="grid grid-cols-3 gap-2.5">
              <div>
                <label class="label">Stock inicial *</label>
                <input v-model.number="form.stock" type="number" min="0" step="1" class="input" placeholder="0" />
              </div>
              <div>
                <label class="label">Stock mínimo</label>
                <input v-model.number="form.min_stock" type="number" min="0" step="1" class="input" placeholder="5" />
              </div>
              <div>
                <label class="label">Unidad de medida</label>
                <select v-model="form.unit_measure" class="input">
                  <option value="UNIT">Unidad</option>
                  <option value="LITER">Litro</option>
                  <option value="KILO">Kilo</option>
                  <option value="ML">Mililitro</option>
                </select>
              </div>
            </div>

            <div class="flex items-center gap-2">
              <input type="checkbox" id="is_available_cb" v-model="form.is_available" class="w-4 h-4 accent-club-forest" />
              <label for="is_available_cb" class="text-sm font-semibold text-club-graphite cursor-pointer">{{ form.is_available ? 'Disponible para pedidos' : 'No disponible para pedidos' }}</label>
            </div>

            <div>
              <label class="label">Descripción</label>
              <textarea v-model.trim="form.description" class="input" rows="2" placeholder="Descripción del producto (opcional)"></textarea>
            </div>
          </div>

          <div class="p-4 bg-club-gray-50 rounded-b-2xl flex justify-end gap-2 border-t border-club-gray-100">
            <button class="btn-secondary" @click="closeForm">Cancelar</button>
            <button class="btn-primary" :disabled="submitting" @click="submitForm">
              <Loader2 v-if="submitting" class="w-4 h-4 animate-spin" />
              {{ submitting ? 'Guardando...' : (editing ? 'Guardar cambios' : 'Crear producto') }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Modal Surtir inventario -->
    <Teleport to="body">
      <div v-if="restockTarget" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" @click.self="restockTarget = null">
        <div class="bg-white rounded-2xl w-full max-w-md shadow-2xl">
          <div class="p-5 border-b border-club-gray-100 flex items-center justify-between">
            <div>
              <h2 class="text-lg font-black text-club-graphite">Surtir inventario</h2>
              <p class="text-xs text-club-gray-500 mt-0.5">Ingresa la cantidad a adicionar al stock actual.</p>
            </div>
            <button class="btn-secondary !p-1.5" @click="restockTarget = null"><X class="w-4 h-4" /></button>
          </div>

          <div class="p-5 space-y-3">
            <div class="bg-club-ivory-dark rounded-xl p-3">
              <div class="font-bold text-sm text-club-graphite truncate">{{ restockTarget.name }}</div>
              <div class="text-xs text-club-gray-500 mt-0.5">SKU: {{ restockTarget.sku || '-' }}</div>
              <div class="mt-2 text-sm">
                Stock actual: <b class="text-club-forest">{{ restockTarget.stock }}</b> unidades
              </div>
            </div>

            <div>
              <label class="label">Cantidad a adicionar *</label>
              <input v-model.number="restockAmount" type="number" min="1" step="1" class="input" placeholder="Ej: 50" />
              <div v-if="restockAmount > 0" class="text-xs text-club-gray-500 mt-1.5">
                Nuevo stock: <b class="text-club-graphite">{{ Number(restockTarget.stock) + Number(restockAmount) }}</b> unidades
              </div>
            </div>
          </div>

          <div class="p-4 bg-club-gray-50 rounded-b-2xl flex justify-end gap-2 border-t border-club-gray-100">
            <button class="btn-secondary" @click="restockTarget = null">Cancelar</button>
            <button class="btn-primary" :disabled="submitting || !restockAmount || restockAmount < 1" @click="executeRestock">
              <Loader2 v-if="submitting" class="w-4 h-4 animate-spin" />
              Surtir
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
                <h3 class="font-black text-club-graphite">¿Eliminar producto?</h3>
                <p class="text-sm text-club-gray-600 mt-1">
                  Esta acción es irreversible. Se eliminará permanentemente el producto
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
  Plus, Search, Package, Pencil, Trash2, X, Loader2, AlertTriangle, PackagePlus
} from 'lucide-vue-next'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import EmptyState from '@/components/EmptyState.vue'
import { showToast } from '@/utils/toast'
import api, { extractError } from '@/api/client'

const products = ref([])
const categories = ref([])
const totalProducts = ref(0)
const loading = ref(true)
const submitting = ref(false)
const q = ref('')
const filterCategory = ref('')

const showForm = ref(false)
const editing = ref(false)
const defaultForm = () => ({
  id: null,
  name: '',
  category_id: '',
  sku: '',
  price: '',
  cost: '',
  stock: 0,
  min_stock: 5,
  unit_measure: 'UNIT',
  is_available: true,
  description: '',
})
const form = reactive(defaultForm())

const restockTarget = ref(null)
const restockAmount = ref('')
const confirmDeleteTarget = ref(null)

const lowStock = computed(() => products.value.filter(p => p.stock > 0 && p.stock <= (p.min_stock || 5)).length)
const outOfStock = computed(() => products.value.filter(p => (p.stock || 0) <= 0).length)

const filtered = computed(() => {
  let data = products.value.slice()
  if (filterCategory.value) data = data.filter(p => p.category?.id === Number(filterCategory.value))
  const s = q.value.trim().toLowerCase()
  if (!s) return data
  return data.filter(p =>
    String(p.name || '').toLowerCase().includes(s) ||
    String(p.sku || '').toLowerCase().includes(s)
  )
})

function formatMoney(n) { return Number(n || 0).toLocaleString('es-CO') }

async function fetchAllProducts() {
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
  return all
}

async function load() {
  loading.value = true
  try {
    const [catsResp, prodResp] = await Promise.all([
      api.get('/refreshments/categories/?page_size=100'),
      api.get('/refreshments/products/?page_size=100'),
    ])
    categories.value = catsResp.data?.results || catsResp.data || []
    totalProducts.value = prodResp.data?.count || 0
    products.value = await fetchAllProducts()
  } catch (e) {
    const status = e?.response?.status
    if (status === 401 || status === 403) {
      try {
        const { useAuthStore } = await import('@/stores/auth')
        const auth = useAuthStore()
        auth.clearSession()
        if (window?.location) window.location.href = '/#/login'
      } catch (_) {}
      const msg = status === 403
        ? 'No tienes permisos para gestionar el inventario. Inicia sesión con cuenta Admin.'
        : 'Tu sesión venció. Por favor vuelve a iniciar sesión.'
      showToast(msg, 'error')
    } else {
      showToast(extractError(e, 'No se pudo cargar el inventario.'), 'error')
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

function openEdit(p) {
  Object.assign(form, defaultForm(), {
    id: p.id,
    name: p.name || '',
    category_id: p.category?.id || '',
    sku: p.sku || '',
    price: p.price ?? '',
    cost: p.cost ?? '',
    stock: p.stock ?? 0,
    min_stock: p.min_stock ?? 5,
    unit_measure: p.unit_measure || 'UNIT',
    is_available: !!p.is_available,
    description: p.description || '',
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
  if (!form.name.trim()) { showToast('Debes ingresar el nombre del producto.', 'error'); return }
  if (!form.category_id) { showToast('Debes seleccionar una categoría.', 'error'); return }
  if (form.price === '' || form.price === null || Number(form.price) < 0) { showToast('Debes ingresar un precio válido.', 'error'); return }

  submitting.value = true
  try {
    const payload = {
      name: form.name.trim(),
      category_id: Number(form.category_id),
      sku: form.sku.trim() || null,
      price: Number(form.price),
      cost: form.cost !== '' ? Number(form.cost) : 0,
      stock: Number(form.stock) || 0,
      min_stock: Number(form.min_stock) || 0,
      unit_measure: form.unit_measure,
      is_available: !!form.is_available,
      description: form.description.trim() || null,
    }
    if (editing.value) {
      await api.patch(`/refreshments/products/${form.id}/`, payload)
      showToast('Producto actualizado exitosamente.', 'success')
    } else {
      await api.post('/refreshments/products/', payload)
      showToast('Producto creado exitosamente.', 'success')
    }
    closeForm()
    await load()
  } catch (err) {
    showToast(extractError(err, 'Ocurrió un error al guardar el producto.'), 'error')
  } finally {
    submitting.value = false
  }
}

function openRestock(p) {
  restockTarget.value = p
  restockAmount.value = ''
}

async function executeRestock() {
  const p = restockTarget.value
  if (!p || !restockAmount.value || restockAmount.value < 1) return
  submitting.value = true
  try {
    const newStock = Number(p.stock) + Number(restockAmount.value)
    await api.patch(`/refreshments/products/${p.id}/`, { stock: newStock })
    showToast(`Stock actualizado a ${newStock} unidades.`, 'success')
    restockTarget.value = null
    restockAmount.value = ''
    await load()
  } catch (err) {
    showToast(extractError(err, 'No se pudo actualizar el stock.'), 'error')
  } finally {
    submitting.value = false
  }
}

function confirmDelete(p) {
  confirmDeleteTarget.value = p
}

async function executeDelete() {
  const p = confirmDeleteTarget.value
  if (!p) return
  submitting.value = true
  try {
    await api.delete(`/refreshments/products/${p.id}/`)
    showToast('Producto eliminado permanentemente.', 'success')
    confirmDeleteTarget.value = null
    await load()
  } catch (err) {
    showToast(extractError(err, 'No se pudo eliminar el producto.'), 'error')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  load()
})
</script>
