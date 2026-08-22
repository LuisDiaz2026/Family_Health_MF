<template>
  <div class="w-full h-full flex flex-col items-center justify-center py-14 text-center px-4">
    <div class="w-20 h-20 rounded-full bg-club-gray-100 flex items-center justify-center mb-4">
      <component :is="icon" class="w-9 h-9 text-club-gray-400" />
    </div>
    <h3 class="text-lg font-bold text-club-gray-800">{{ title }}</h3>
    <p v-if="description" class="mt-1 text-sm text-club-gray-500 max-w-xs">{{ description }}</p>
    <button
      v-if="ctaLabel"
      class="btn-primary mt-5"
      @click="$emit('cta')"
    >{{ ctaLabel }}</button>
  </div>
</template>

<script setup>
import { Package } from 'lucide-vue-next'

const props = defineProps({
  title: { type: String, default: 'Sin contenido' },
  description: { type: String, default: '' },
  icon: { type: Object, default: () => Package },
  ctaLabel: { type: String, default: '' },
})

defineEmits(['cta'])
</script>
