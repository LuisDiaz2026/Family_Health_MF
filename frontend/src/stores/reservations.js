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
      const data = resp.data || {}
      const ocupados = (data.occupied_slots || []).map((o) => ({
        ini: new Date(o.start_time).getTime(),
        fin: new Date(o.end_time).getTime(),
      }))
      const base = data.thirty_minute_slots || []
      availability.value = base.map((s) => {
        const inicio = new Date(s.datetime).getTime()
        const fin = inicio + 30 * 60000
        const ocupado = ocupados.some((o) => inicio < o.fin && fin > o.ini)
        return {
          start: s.time || horaDe(s.datetime),
          end: sumarMinutos(s.time || horaDe(s.datetime), 30),
          available: !ocupado,
        }
      })
      return availability.value
    } catch (e) {
      error.value = extractError(e)
      throw error.value
    } finally {
      loading.value = false
    }
  }

  function horaDe(iso) {
    if (!iso) return ''
    return new Date(iso).toTimeString().slice(0, 5)
  }

  function sumarMinutos(hhmm, minutos) {
    const [h, m] = hhmm.split(':').map(Number)
    const total = h * 60 + m + minutos
    const hh = String(Math.floor(total / 60) % 24).padStart(2, '0')
    const mm = String(total % 60).padStart(2, '0')
    return `${hh}:${mm}`
  }

  async function listMyReservations() {
    loading.value = true
    error.value = ''
    try {
      const resp = await api.get('/reservations/reservations/mis-reservas/')
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
