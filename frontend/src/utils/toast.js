import { reactive } from 'vue'

const state = reactive({
  toasts: [],
})
let nextId = 1

export function showToast(message, type = 'info', title = '', durationMs = 3500) {
  const id = nextId++
  state.toasts.push({ id, message, type, title })
  if (durationMs > 0) {
    setTimeout(() => removeToast(id), durationMs)
  }
  return id
}

export function removeToast(id) {
  const idx = state.toasts.findIndex(t => t.id === id)
  if (idx >= 0) state.toasts.splice(idx, 1)
}

export const toastState = state
