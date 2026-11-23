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
    const firstMessage = (value) => {
      if (typeof value === 'string') return value
      if (Array.isArray(value)) {
        for (const item of value) {
          const message = firstMessage(item)
          if (message) return message
        }
      } else if (value && typeof value === 'object') {
        for (const key of ['detail', 'message']) {
          const message = firstMessage(value[key])
          if (message) return message
        }
        for (const item of Object.values(value)) {
          const message = firstMessage(item)
          if (message) return message
        }
      }
      return ''
    }
    if (err.response?.data) {
      const d = err.response.data
      if (typeof d === 'string') return d
      if (d.detail) return firstMessage(d.detail)
      if (d.message) return firstMessage(d.message)
      if (d.errors && typeof d.errors === 'object') {
        const [firstKey] = Object.keys(d.errors)
        const msg = firstMessage(d.errors[firstKey])
        return firstKey === '__all__' ? msg : `${firstKey}: ${msg}`
      }
      const [f] = Object.keys(d)
      if (f) {
        const msg = firstMessage(d[f])
        if (msg) return f === '__all__' ? msg : `${f}: ${msg}`
      }
    }
    if (err.message) return err.message
  } catch (_) {}
  return fallback
}

export default api
