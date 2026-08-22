<template>
  <div class="w-full py-16 flex flex-col items-center justify-center">
    <div class="animate-pulse flex flex-col items-center gap-3 w-full max-w-md px-8">
      <div class="h-3 w-32 bg-club-gray-200 rounded-full"></div>
      <div class="h-3 w-40 bg-club-gray-200 rounded-full"></div>
      <div class="grid grid-cols-2 gap-3 w-full pt-3">
        <div v-for="i in 4" :key="i" class="h-24 bg-club-gray-200 rounded-xl"></div>
      </div>
    </div>
    <p v-if="text" class="mt-5 text-sm text-club-gray-500">{{ text }}</p>
  </div>
</template>

<script setup>
defineProps({
  text: { type: String, default: 'Cargando...' },
})
</script>
