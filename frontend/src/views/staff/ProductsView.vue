<template>
  <div class="page-padding space-y-4">
    <div class="flex items-center justify-between flex-wrap gap-3">
      <div>
        <h1 class="title-page">Inventario productos</h1>
        <p class="subtitle-page">SKU, stock y precios de refresquería</p>
      </div>
      <button class="btn-success" @click="showToast('Función de creación implementada en Admin Django')">
        <Plus class="w-4 h-4" /> Crear producto
      </button>
    </div>

    <div class="relative">
      <Search class="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-club-gray-400" />
      <input v-model="q" class="input pl-9" placeholder="Buscar producto..." />
    </div>

    <div class="grid grid-cols-3 gap-2 text-center text-sm">
      <div class="card !p-3">
        <div class="text-xs uppercase text-club-gray-500 font-bold">Total</div>
        <div class="text-2xl font-black text-club-blue">{{ products.length }}</div>
      </div>
      <div class="card !p-3">
        <div class="text-xs uppercase text-club-gray-500 font-bold">Stock bajo</div>
        <div class="text-2xl font-black text-club-amber">{{ lowStock }}</div>
      </div>
      <div class="card !p-3">
        <div class="text-xs uppercase text-club-gray-500 font-bold">Agotados</div>
        <div class="text-2xl font-black text-club-red">{{ outOfStock }}</div>
      </div>
    </div>

    <SkeletonLoader v-if="loading" />
    <EmptyState v-else-if="!filtered.length" icon="Package" title="Sin productos" description="Ajusta la búsqueda." />
    <div v-else class="space-y-3">
      <div v-for="p in filtered" :key="p.id" class="card !p-3 flex gap-3">
        <div class="w-14 h-14 rounded-lg bg-club-gray-100 flex items-center justify-center shrink-0">
          <Package class="w-7 h-7 text-club-gray-400" />
        </div>
        <div class="flex-1 min-w-0">
          <div class="flex items-start justify-between gap-2">
            <div class="min-w-0">
              <div class="font-bold text-sm text-club-gray-900 truncate">{{ p.name }}</div>
              <div class="text-[11px] text-club-gray-500 mt-0.5">SKU: {{ p.sku || '-' }} · {{ p.category?.name || p.category_name || 'Sin categoría' }}</div>
            </div>
            <span v-if="(p.stock || 0) <= 0" class="chip bg-club-red/15 text-club-red !text-[10px]">Agotado</span>
            <span v-else-if="(p.stock || 0) <= (p.min_stock || 5)" class="chip bg-club-amber/15 text-[#b45309] !text-[10px]">Stock bajo</span>
            <span v-else class="chip bg-club-green/15 text-club-green-dark !text-[10px]">OK</span>
          </div>
          <div class="mt-2 flex items-center justify-between text-xs">
            <div class="text-club-gray-600">Stock: <b class="text-club-gray-900">{{ p.stock }}</b> / Min: <b class="text-club-gray-900">{{ p.min_stock || 0 }}</b></div>
            <div class="font-black text-club-green">${{ formatMoney(p.price) }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { Plus, Search, Package } from 'lucide-vue-next'
import api from '@/api/client'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import EmptyState from '@/components/EmptyState.vue'
import { showToast } from '@/utils/toast'

const products = ref([])
const loading = ref(true)
const q = ref('')

const filtered = computed(() => {
  const s = q.value.trim().toLowerCase()
  if (!s) return products.value
  return products.value.filter(p =>
    String(p.name || '').toLowerCase().includes(s) ||
    String(p.sku || '').toLowerCase().includes(s)
  )
})
const lowStock = computed(() => products.value.filter(p => p.stock > 0 && p.stock <= (p.min_stock || 5)).length)
const outOfStock = computed(() => products.value.filter(p => (p.stock || 0) <= 0).length)

function formatMoney(n) { return Number(n || 0).toLocaleString('es-CO') }

onMounted(async () => {
  loading.value = true
  try {
    const resp = await api.get('/refreshments/products/?page_size=300')
    products.value = resp.data?.results || resp.data || []
  } finally { loading.value = false }
})
</script>
