import { defineStore } from 'pinia'
import api, { extractError } from '@/api/client'
import { ref } from 'vue'

export const useReportsStore = defineStore('reports', () => {
  const summary = ref(null)
  const topClients = ref([])
  const notifications = ref([])
  const loading = ref(false)
  const error = ref('')

  async function getDashboardSummary() {
    loading.value = true
    error.value = ''
    try {
      const resp = await api.get('/reports/dashboard/summary/')
      summary.value = resp.data
      return resp.data
    } catch (e) {
      error.value = extractError(e)
      throw error.value
    } finally {
      loading.value = false
    }
  }

  async function getTopClients(n = 5) {
    try {
      const resp = await api.get(`/reports/top-clients/?n=${n}`)
      topClients.value = resp.data?.results || resp.data || []
      return topClients.value
    } catch (_) { return topClients.value }
  }

  async function listNotifications() {
    try {
      const resp = await api.get('/reports/notifications/?is_read=false')
      notifications.value = resp.data?.results || resp.data || []
      return notifications.value
    } catch (_) { return notifications.value }
  }

  async function markNotificationRead(id) {
    try {
      await api.patch(`/reports/notifications/${id}/`, { is_read: true })
      const n = notifications.value.find(x => x.id === id)
      if (n) n.is_read = true
    } catch (_) {}
  }

  return {
    summary, topClients, notifications, loading, error,
    getDashboardSummary, getTopClients, listNotifications, markNotificationRead,
  }
})
