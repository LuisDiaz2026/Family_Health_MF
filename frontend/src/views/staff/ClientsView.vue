<template>
  <div class="page-padding space-y-4">
    <div>
      <h1 class="title-page">Gestión de clientes</h1>
      <p class="subtitle-page">Afiliados, membresías y datos</p>
    </div>

    <div class="relative">
      <Search class="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-club-gray-400" />
      <input v-model="q" class="input pl-9" placeholder="Buscar por nombre, cédula o usuario..." />
    </div>

    <SkeletonLoader v-if="loading" />
    <EmptyState v-else-if="!filtered.length" icon="Users" title="Sin clientes" description="Invita a nuevos clientes a registrarse." />
    <div v-else class="space-y-2">
      <div v-for="c in filtered" :key="c.id" class="card !p-3 flex items-center gap-3">
        <div class="w-11 h-11 rounded-xl bg-gradient-to-br from-club-blue to-club-green text-white font-black flex items-center justify-center text-sm shrink-0">
          {{ initials(c) }}
        </div>
        <div class="flex-1 min-w-0">
          <div class="flex items-center justify-between gap-2">
            <div class="font-bold text-sm text-club-gray-900 truncate">{{ c.first_name }} {{ c.last_name }}</div>
            <span class="chip" :class="c.is_active ? 'bg-club-green/15 text-club-green-dark' : 'bg-club-red/15 text-club-red'">
              {{ c.is_active ? 'Activo' : 'Inactivo' }}
            </span>
          </div>
          <div class="text-xs text-club-gray-500 mt-0.5 truncate">
            @{{ c.username }} · {{ c.document_type || '' }} {{ c.document_number || '' }}
          </div>
          <div class="text-xs text-club-gray-600 mt-1 flex flex-wrap gap-1.5">
            <span class="chip bg-club-blue/10 text-club-blue-dark">{{ c.membership_type || 'Básica' }}</span>
            <span v-if="c.loyalty_profile?.tier" class="chip bg-club-amber/15 text-[#b45309]">
              {{ c.loyalty_profile.tier.name || c.loyalty_profile.tier }}
            </span>
            <span class="chip bg-club-gray-100 text-club-gray-700">{{ c.phone || c.email }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { Search, Users } from 'lucide-vue-next'
import api from '@/api/client'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import EmptyState from '@/components/EmptyState.vue'

const list = ref([])
const loading = ref(true)
const q = ref('')

const filtered = computed(() => {
  const s = q.value.trim().toLowerCase()
  if (!s) return list.value
  return list.value.filter(c =>
    String(c.username || '').toLowerCase().includes(s) ||
    String(c.first_name || '').toLowerCase().includes(s) ||
    String(c.last_name || '').toLowerCase().includes(s) ||
    String(c.document_number || '').includes(s) ||
    String(c.email || '').toLowerCase().includes(s)
  )
})

function initials(c) {
  return ((c.first_name?.[0] || 'U') + (c.last_name?.[0] || '')).toUpperCase()
}

onMounted(async () => {
  loading.value = true
  try {
    const resp = await api.get('/auth/clients/?page_size=200')
    list.value = resp.data?.results || resp.data || []
  } finally { loading.value = false }
})
</script>
