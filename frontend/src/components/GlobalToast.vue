<template>
  <Teleport to="body">
    <div class="pointer-events-none fixed inset-x-0 top-4 z-[999] flex flex-col items-center gap-2 px-4">
      <transition-group name="toast" tag="div" class="flex flex-col items-center gap-2 w-full max-w-md">
        <div
          v-for="t in toasts"
          :key="t.id"
          class="pointer-events-auto w-full rounded-xl shadow-card px-4 py-3 flex items-start gap-3 text-sm"
          :class="styleFor(t.type)"
        >
          <component :is="iconFor(t.type)" class="w-5 h-5 shrink-0 mt-0.5" />
          <div class="flex-1 min-w-0">
            <div v-if="t.title" class="font-bold">{{ t.title }}</div>
            <div class="opacity-90">{{ t.message }}</div>
          </div>
          <button @click="remove(t.id)" class="opacity-70 hover:opacity-100">
            <X class="w-4 h-4" />
          </button>
        </div>
      </transition-group>
    </div>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'
import { CheckCircle2, AlertTriangle, Info, X, XCircle } from 'lucide-vue-next'
import { toastState, removeToast as removeT } from '@/utils/toast'

const toasts = computed(() => toastState.toasts)

function styleFor(type) {
  switch (type) {
    case 'success':
      return 'bg-club-green text-white'
    case 'error':
      return 'bg-club-red text-white'
    case 'warn':
      return 'bg-club-amber text-white'
    default:
      return 'bg-club-gray-800 text-white'
  }
}

function iconFor(type) {
  switch (type) {
    case 'success': return CheckCircle2
    case 'error': return XCircle
    case 'warn': return AlertTriangle
    default: return Info
  }
}

function remove(id) { removeT(id) }
</script>

<style scoped>
.toast-enter-active, .toast-leave-active {
  transition: all .28s cubic-bezier(.2,.8,.2,1);
}
.toast-enter-from {
  opacity: 0;
  transform: translateY(-24px) scale(.96);
}
.toast-leave-to {
  opacity: 0;
  transform: translateY(-10px) scale(.96);
}
.toast-move {
  transition: transform .28s ease;
}
</style>
