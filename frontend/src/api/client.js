import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
  },
  withCredentials: true,
})

let isRefreshing = false
let failedQueue = []

const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

api.interceptors.request.use((config) => {
  try {
    const auth = useAuthStore()
    if (auth.accessToken) {
      config.headers.Authorization = `Bearer ${auth.accessToken}`
    }
  } catch (e) {}
  return config
}, Promise.reject)

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      !originalRequest.url?.includes('/auth/login/') &&
      !originalRequest.url?.includes('/auth/token/refresh/')
    ) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            return api(originalRequest)
          })
          .catch(Promise.reject)
      }
      originalRequest._retry = true
      isRefreshing = true
      try {
        const auth = useAuthStore()
        const newToken = await auth.refreshAccessToken()
        processQueue(null, newToken)
        originalRequest.headers.Authorization = `Bearer ${newToken}`
        return api(originalRequest)
      } catch (refreshErr) {
        processQueue(refreshErr, null)
        try { useAuthStore().logoutSilent() } catch (_) {}
        return Promise.reject(refreshErr)
      } finally {
        isRefreshing = false
      }
    }
    return Promise.reject(error)
  }
)

export function extractError(err, fallback = 'Ha ocurrido un error inesperado.') {
  try {
    if (!err) return fallback
    if (typeof err === 'string') return err
    if (err.response?.data) {
      const d = err.response.data
      if (typeof d === 'string') return d
      if (d.detail) return d.detail
      if (d.message) return d.message
      if (d.errors && typeof d.errors === 'object') {
        const [firstKey] = Object.keys(d.errors)
        const firstVal = d.errors[firstKey]
        const msg = Array.isArray(firstVal) ? firstVal[0] : firstVal
        return `${firstKey}: ${msg}`
      }
      const [f] = Object.keys(d)
      if (f) {
        const v = d[f]
        const msg = Array.isArray(v) ? v[0] : v
        if (typeof msg === 'string') return `${f}: ${msg}`
      }
    }
    if (err.message) return err.message
  } catch (_) {}
  return fallback
}

export default api
