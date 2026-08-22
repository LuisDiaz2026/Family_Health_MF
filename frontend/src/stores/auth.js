import { defineStore } from 'pinia'
import api, { extractError } from '@/api/client'
import { computed, ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const accessToken = ref(localStorage.getItem('fh_access') || '')
  const refreshToken = ref(localStorage.getItem('fh_refresh') || '')
  const error = ref('')
  const loading = ref(false)

  const isAuthenticated = computed(() => !!accessToken.value && !!user.value)
  const role = computed(() => user.value?.role || null)
  const isAdmin = computed(() => role.value === 'ADMIN')
  const isEmployee = computed(() => role.value === 'EMPLOYEE')
  const isClient = computed(() => role.value === 'CLIENT')
  const isStaff = computed(() => isAdmin.value || isEmployee.value)
  const displayName = computed(() =>
    user.value?.full_name || user.value?.username || 'Usuario'
  )
  const tierInfo = computed(() => {
    if (user.value?.loyalty?.tier) return user.value.loyalty.tier
    const u = user.value
    if (u?.tier) return { name: u.tier }
    return null
  })
  const currentPoints = computed(() => {
    if (user.value?.loyalty?.current_points != null) return user.value.loyalty.current_points
    if (user.value?.points != null) return user.value.points
    return 0
  })

  function persistTokens(access, refresh) {
    accessToken.value = access
    refreshToken.value = refresh
    localStorage.setItem('fh_access', access)
    localStorage.setItem('fh_refresh', refresh)
  }

  function clearSession() {
    user.value = null
    accessToken.value = ''
    refreshToken.value = ''
    localStorage.removeItem('fh_access')
    localStorage.removeItem('fh_refresh')
  }

  async function login(username, password) {
    error.value = ''
    loading.value = true
    try {
      const resp = await api.post('/auth/login/', { username, password })
      const data = resp.data
      persistTokens(data.access, data.refresh)
      user.value = data.user
      return true
    } catch (e) {
      clearSession()
      error.value = extractError(e, 'Usuario o contraseña incorrectos.')
      throw error.value
    } finally {
      loading.value = false
    }
  }

  async function register(payload) {
    error.value = ''
    loading.value = true
    try {
      const resp = await api.post('/auth/register/', payload)
      if (resp.data && resp.data.access) {
        persistTokens(resp.data.access, resp.data.refresh)
        user.value = resp.data.user
      }
      return true
    } catch (e) {
      error.value = extractError(e, 'No se pudo completar el registro.')
      throw error.value
    } finally {
      loading.value = false
    }
  }

  async function refreshAccessToken() {
    if (!refreshToken.value) throw new Error('Sin refresh token.')
    const resp = await api.post('/auth/token/refresh/', {
      refresh: refreshToken.value,
    })
    const newAccess = resp.data.access
    accessToken.value = newAccess
    localStorage.setItem('fh_access', newAccess)
    if (resp.data.refresh) {
      refreshToken.value = resp.data.refresh
      localStorage.setItem('fh_refresh', resp.data.refresh)
    }
    return newAccess
  }

  async function fetchMe() {
    const resp = await api.get('/auth/me/')
    user.value = resp.data
    return resp.data
  }

  async function fetchMeLoyalty() {
    const resp = await api.get('/auth/me/loyalty/')
    user.value = { ...(user.value || {}), ...resp.data }
    return resp.data
  }

  async function restoreSession() {
    if (!accessToken.value) return false
    try {
      await fetchMe()
      return true
    } catch (e) {
      if (refreshToken.value) {
        try {
          await refreshAccessToken()
          await fetchMe()
          return true
        } catch (_) {}
      }
      clearSession()
      return false
    }
  }

  async function logout() {
    try {
      if (refreshToken.value) {
        await api.post('/auth/logout/', { refresh: refreshToken.value })
      }
    } catch (_) {}
    clearSession()
  }

  function logoutSilent() {
    clearSession()
  }

  function setError(msg) {
    error.value = msg
  }

  return {
    user,
    accessToken,
    refreshToken,
    error,
    loading,
    isAuthenticated,
    role,
    isAdmin,
    isEmployee,
    isClient,
    isStaff,
    displayName,
    tierInfo,
    currentPoints,
    login,
    register,
    refreshAccessToken,
    fetchMe,
    fetchMeLoyalty,
    restoreSession,
    logout,
    logoutSilent,
    persistTokens,
    clearSession,
    setError,
  }
})
