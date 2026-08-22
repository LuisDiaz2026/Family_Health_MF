import { defineStore } from 'pinia'
import api, { extractError } from '@/api/client'
import { ref } from 'vue'

export const useGymStore = defineStore('gym', () => {
  const routines = ref([])
  const exercises = ref([])
  const routineDetail = ref(null)
  const loading = ref(false)
  const error = ref('')

  async function listMyRoutines() {
    loading.value = true
    error.value = ''
    try {
      const resp = await api.get('/gym/routines/my-routines/')
      routines.value = resp.data?.results || resp.data || []
      return routines.value
    } catch (e) {
      error.value = extractError(e)
      throw error.value
    } finally {
      loading.value = false
    }
  }

  async function getRoutine(id) {
    loading.value = true
    error.value = ''
    try {
      const resp = await api.get(`/gym/routines/${id}/`)
      routineDetail.value = resp.data
      return resp.data
    } catch (e) {
      error.value = extractError(e)
      throw error.value
    } finally {
      loading.value = false
    }
  }

  async function listExercises(params) {
    loading.value = true
    error.value = ''
    try {
      const resp = await api.get('/gym/exercises/', { params })
      exercises.value = resp.data?.results || resp.data || []
      return exercises.value
    } catch (e) {
      error.value = extractError(e)
      throw error.value
    } finally {
      loading.value = false
    }
  }

  return {
    routines, exercises, routineDetail, loading, error,
    listMyRoutines, getRoutine, listExercises,
  }
})
