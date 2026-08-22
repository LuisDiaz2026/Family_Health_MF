import { defineStore } from 'pinia'
import api, { extractError } from '@/api/client'
import { ref } from 'vue'

export const useReservationsStore = defineStore('reservations', () => {
  const spaces = ref([])
  const space = ref(null)
  const availability = ref([])
  const myReservations = ref([])
  const loading = ref(false)
  const error = ref('')

  async function listSpaces(params = {}) {
    loading.value = true
    error.value = ''
    try {
      const resp = await api.get('/reservations/spaces/', { params })
      spaces.value = resp.data?.results || resp.data || []
      return spaces.value
    } catch (e) {
      error.value = extractError(e)
      throw error.value
    } finally {
      loading.value = false
    }
  }

  async function getSpace(id) {
    const resp = await api.get(`/reservations/spaces/${id}/`)
    space.value = resp.data
    return resp.data
  }

  async function getAvailability(spaceId, date) {
    loading.value = true
    error.value = ''
    try {
      const resp = await api.get(
        `/reservations/spaces/${spaceId}/availability/?date=${date}`
      )
      availability.value = resp.data?.available_slots || resp.data || []
      return availability.value
    } catch (e) {
      error.value = extractError(e)
      throw error.value
    } finally {
      loading.value = false
    }
  }

  async function listMyReservations() {
    loading.value = true
    error.value = ''
    try {
      const resp = await api.get('/reservations/reservations/')
      myReservations.value = resp.data?.results || resp.data || []
      return myReservations.value
    } catch (e) {
      error.value = extractError(e)
      throw error.value
    } finally {
      loading.value = false
    }
  }

  async function createReservation(payload) {
    loading.value = true
    error.value = ''
    try {
      const resp = await api.post('/reservations/reservations/', payload)
      return resp.data
    } catch (e) {
      error.value = extractError(e)
      throw error.value
    } finally {
      loading.value = false
    }
  }

  async function cancelReservation(id) {
    loading.value = true
    error.value = ''
    try {
      await api.post(`/reservations/reservations/${id}/cancel/`)
      return true
    } catch (e) {
      error.value = extractError(e)
      throw error.value
    } finally {
      loading.value = false
    }
  }

  return {
    spaces, space, availability, myReservations, loading, error,
    listSpaces, getSpace, getAvailability, listMyReservations,
    createReservation, cancelReservation,
  }
})
