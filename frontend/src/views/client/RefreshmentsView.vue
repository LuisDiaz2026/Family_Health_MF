<template>
  <div class="page-padding space-y-4">
    <div class="flex items-center justify-between flex-wrap gap-2">
      <div>
        <h1 class="title-page">Refresquería</h1>
        <p class="subtitle-page">Pide y retira en barra</p>
      </div>
      <button class="btn-secondary relative" @click="$router.push({ name: 'client-cart' })">
        <ShoppingCart class="w-4 h-4" /> Carrito
        <span v-if="rf.cartCount > 0" class="badge-dot"></span>
        <span v-if="rf.cartCount > 0" class="ml-2 chip bg-club-red text-white !text-[10px]">{{ rf.cartCount }}</span>
      </button>
    </div>

    <div class="flex gap-2 overflow-x-auto pb-2 -mx-4 px-4">
      <button
        v-for="c in categories"
        :key="c.id || c.name"
        class="chip whitespace-nowrap !px-3 !py-1.5 !text-xs"
        :class="cat === c.name ? 'bg-club-green text-white' : 'bg-white border border-club-gray-200 text-club-gray-700'"
        @click="cat = c.name"
      >{{ c.name }}</button>
    </div>

    <div class="relative">
      <Search class="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-club-gray-400" />
      <input v-model="query" class="input pl-9" placeholder="Buscar producto..." />
    </div>

    <SkeletonLoader v-if="loading" />
    <EmptyState v-else-if="!productsList.length" icon="Package" title="Sin productos" description="Intenta con otra categoría o busqueda." />
    <div v-else class="space-y-3">
      <ProductCard
        v-for="p in productsList"
        :key="p.id"
        :product="p"
        :quantity="(rf.findInCart(p.id) || {}).quantity || 0"
        @add="rf.addToCart(p, 1); showToast(`${p.name} añadido`, 'success')"
        @decrease="rf.updateQuantity(p.id, ((rf.findInCart(p.id) || {}).quantity || 0) - 1); showToast('Carrito actualizado', 'info')"
      />
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ShoppingCart, Search, Package } from 'lucide-vue-next'
import { useRefreshmentsStore } from '@/stores/refreshments'
import ProductCard from '@/components/ProductCard.vue'
import EmptyState from '@/components/EmptyState.vue'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import { showToast } from '@/utils/toast'

const rf = useRefreshmentsStore()
const loading = computed(() => rf.loading)
const query = ref('')
const cat = ref('Todos')

const categories = computed(() => {
  const cats = (rf.catalog || []).map(c => ({ id: c.id, name: c.name, products: c.products || [] }))
  return [{ id: null, name: 'Todos' }, ...cats]
})

const productsList = computed(() => {
  let list = []
  const raw = rf.catalog || []
  if (cat.value === 'Todos') {
    for (const c of raw) list.push(...(c.products || []))
  } else {
    const found = raw.find(c => c.name === cat.value)
    if (found) list = found.products || []
  }
  const q = query.value.trim().toLowerCase()
  if (q) list = list.filter(p => String(p.name || '').toLowerCase().includes(q) || String(p.sku || '').toLowerCase().includes(q))
  return list
})

onMounted(() => rf.listCatalog().catch(() => {}))
</script>
