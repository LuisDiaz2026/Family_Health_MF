<template>
  <div class="card flex gap-3">
    <div class="w-20 h-20 shrink-0 rounded-lg bg-club-gray-100 flex items-center justify-center text-2xl overflow-hidden">
      <span v-if="product.image"><img :src="product.image" class="w-full h-full object-cover" /></span>
      <component v-else :is="iconFor(product)" class="w-8 h-8 text-club-gray-400" />
    </div>
    <div class="flex-1 min-w-0 flex flex-col">
      <div class="flex items-start justify-between gap-2">
        <div class="min-w-0">
          <h4 class="font-bold text-sm text-club-gray-900 truncate">{{ product.name }}</h4>
          <div class="text-[11px] text-club-gray-500 mt-0.5 truncate">{{ product.sku || '' }} · {{ stockLabel }}</div>
        </div>
        <span class="chip bg-club-green/10 text-club-green-dark whitespace-nowrap">
          ${{ Number(product.price || 0).toLocaleString('es-CO') }}
        </span>
      </div>
      <p v-if="product.description" class="text-xs text-club-gray-600 line-clamp-2 mt-1">{{ product.description }}</p>
      <div class="mt-auto pt-2 flex items-center justify-between">
        <div v-if="allergensList.length" class="flex gap-1 flex-wrap">
          <span
            v-for="a in allergensList.slice(0, 3)"
            :key="a"
            class="text-[10px] px-1.5 py-0.5 rounded border border-club-gray-200 text-club-gray-600 bg-club-gray-50"
          >{{ a }}</span>
        </div>
        <div v-if="showAdd" class="flex items-center gap-1">
          <button
            v-if="quantity > 0"
            class="btn-ghost !p-1.5 !rounded-lg text-club-gray-700"
            @click="$emit('decrease')"
          ><Minus class="w-4 h-4" /></button>
          <span v-if="quantity > 0" class="w-7 text-center text-sm font-bold text-club-gray-900">{{ quantity }}</span>
          <button
            class="btn-primary !py-1.5 !px-2.5 text-xs"
            :disabled="(product.stock || 0) <= 0"
            @click="$emit('add')"
          >
            <Plus class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Plus, Minus, Coffee, Sandwich, Apple, Beer, Cookie, Utensils } from 'lucide-vue-next'

const props = defineProps({
  product: { type: Object, required: true },
  showAdd: { type: Boolean, default: true },
  quantity: { type: Number, default: 0 },
})

defineEmits(['add', 'decrease'])

function iconFor(p) {
  const c = (p.category?.name || p.category_name || '').toLowerCase()
  if (c.includes('bebida') || c.includes('jugo') || c.includes('agua')) return Coffee
  if (c.includes('snack') || c.includes('paquete')) return Cookie
  if (c.includes('comida') || c.includes('plato') || c.includes('hamburguesa')) return Utensils
  if (c.includes('fruta') || c.includes('saludable')) return Apple
  if (c.includes('alcohol') || c.includes('cerveza')) return Beer
  return Sandwich
}

const allergensList = computed(() => {
  const raw = props.product.allergens
  if (!raw) return []
  if (Array.isArray(raw)) return raw
  if (typeof raw === 'string') {
    try {
      const parsed = JSON.parse(raw)
      if (Array.isArray(parsed)) return parsed
    } catch (_) {}
    return raw.split(',').map(s => s.trim()).filter(Boolean)
  }
  return []
})

const stockLabel = computed(() => {
  const s = props.product.stock ?? 0
  if (s <= 0) return 'Agotado'
  if (s <= (props.product.min_stock || 5)) return `Stock bajo · ${s} und`
  return `${s} und disponibles`
})
</script>
