<template>
  <div class="page-padding space-y-4">
    <div>
      <h1 class="title-page">Catálogo de premios</h1>
      <p class="subtitle-page">Tus puntos: <span class="font-bold text-club-green">{{ auth.currentPoints }}</span></p>
    </div>

    <SkeletonLoader v-if="loading" />
    <EmptyState v-else-if="!items.length" icon="Gift" title="Catálogo vacío" description="Pronto tendremos nuevos premios." />
    <div v-else class="grid grid-cols-2 gap-3">
      <div v-for="it in items" :key="it.id" class="card !p-3 flex flex-col">
        <div class="aspect-square rounded-xl bg-gradient-to-br from-club-blue/10 to-club-green/10 flex items-center justify-center text-4xl mb-2.5">
          <Gift class="w-9 h-9 text-club-blue" />
        </div>
        <h4 class="font-bold text-sm text-club-gray-900 leading-tight mb-0.5">{{ it.name }}</h4>
        <p v-if="it.description" class="text-[11px] text-club-gray-500 line-clamp-2 mb-2">{{ it.description }}</p>
        <div class="mt-auto flex items-center justify-between">
          <span class="font-black text-club-amber">{{ it.points_cost }} pts</span>
          <button
            class="btn-primary !py-1.5 !px-2.5 !text-xs"
            :disabled="(auth.currentPoints || 0) < it.points_cost || loadingRedeem"
            @click="redeem(it)"
          >
            {{ (auth.currentPoints || 0) < it.points_cost ? 'Sin puntos' : (loadingRedeem ? '...' : 'Canjear') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { Gift } from 'lucide-vue-next'
import { useRewardsStore } from '@/stores/rewards'
import { useAuthStore } from '@/stores/auth'
import EmptyState from '@/components/EmptyState.vue'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import { showToast } from '@/utils/toast'

const store = useRewardsStore()
const auth = useAuthStore()
const items = computed(() => store.catalog || [])
const loading = computed(() => store.loading)
const loadingRedeem = ref(false)

async function redeem(it) {
  loadingRedeem.value = true
  try {
    await store.redeem(it.id)
    await Promise.all([
      auth.fetchMeLoyalty(),
      store.listCatalog().catch(() => {}),
    ])
    showToast(`¡Canjeaste ${it.name}! Por favor dirígete a recepción.`, 'success', '¡Canje exitoso!')
  } catch (e) {
    showToast(e || 'No se pudo canjear.', 'error')
  } finally {
    loadingRedeem.value = false
  }
}

onMounted(() => store.listCatalog().catch(() => {}))
</script>
