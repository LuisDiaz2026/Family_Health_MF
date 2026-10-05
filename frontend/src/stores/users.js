import { defineStore } from 'pinia'
import api, { extractError } from '@/api/client'
import { ref } from 'vue'

export const useUsersStore = defineStore('users', () => {
  const list = ref([])
  const loading = ref(false)
  const error = ref('')

  async function fetchClients(params = {}) {
    loading.value = true
    error.value = ''
    try {
      const resp = await api.get('/auth/admin/users/', {
        params: { role: 'client', page_size: 500, ...params },
      })
      list.value = resp.data?.results || resp.data || []
      return list.value
    } catch (e) {
      error.value = extractError(e)
      throw error.value
    } finally {
      loading.value = false
    }
  }

  async function createClient(payload) {
    loading.value = true
    error.value = ''
    try {
      const resp = await api.post('/auth/admin/users/', {
        ...payload,
        role: 'client',
        is_active: payload.is_active !== false,
      })
      return resp.data
    } catch (e) {
      error.value = extractError(e)
      throw error.value
    } finally {
      loading.value = false
    }
  }

  async function updateClient(id, payload) {
    loading.value = true
    error.value = ''
    try {
      const resp = await api.patch(`/auth/admin/users/${id}/`, payload)
      return resp.data
    } catch (e) {
      error.value = extractError(e)
      throw error.value
    } finally {
      loading.value = false
    }
  }

  async function setClientPassword(id, newPassword) {
    loading.value = true
    error.value = ''
    try {
      const resp = await api.post(`/auth/admin/users/${id}/set-password/`, {
        new_password: newPassword,
      })
      return resp.data
    } catch (e) {
      error.value = extractError(e)
      throw error.value
    } finally {
      loading.value = false
    }
  }

  async function toggleClientActive(id) {
    loading.value = true
    error.value = ''
    try {
      const resp = await api.post(`/auth/admin/users/${id}/toggle-active/`)
      return resp.data
    } catch (e) {
      error.value = extractError(e)
      throw error.value
    } finally {
      loading.value = false
    }
  }

  async function deleteClient(id) {
    loading.value = true
    error.value = ''
    try {
      await api.delete(`/auth/admin/users/${id}/`)
      return true
    } catch (e) {
      error.value = extractError(e)
      throw error.value
    } finally {
      loading.value = false
    }
  }

  return {
    list,
    loading,
    error,
    fetchClients,
    createClient,
    updateClient,
    setClientPassword,
    toggleClientActive,
    deleteClient,
  }
})
