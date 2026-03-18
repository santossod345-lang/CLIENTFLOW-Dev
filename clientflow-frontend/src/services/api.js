import axios from 'axios'
import { captureException } from '../utils/monitoring'

function resolveApiBase() {
  const rawApiUrl = import.meta.env.VITE_API_URL
  if (!rawApiUrl) {
    console.warn('[API] VITE_API_URL not set, using /api fallback')
    return '/api'
  }

  const sanitized = rawApiUrl.replace(/\/$/, '')
  return sanitized.endsWith('/api') ? sanitized : `${sanitized}/api`
}

export const API_BASE = resolveApiBase()
console.log('[API] Base URL ->', API_BASE)

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' }
})

let refreshPromise = null
let authHandlers = {
  onAuthFailure: null,
  onTokenRefreshed: null
}
let loadingHandlers = {
  onRequestStart: null,
  onRequestEnd: null
}

const requestCache = new Map()
const DEFAULT_CACHE_TTL_MS = 30000

export function setApiAuthHandlers(nextHandlers) {
  authHandlers = { ...authHandlers, ...nextHandlers }
}

export function setApiLoadingHandlers(nextHandlers) {
  loadingHandlers = { ...loadingHandlers, ...nextHandlers }
}

function startLoadFor(config) {
  const key = `${config?.method || 'get'}:${config?.url || 'unknown'}:${Date.now()}`
  config.__loadingToken = key
  if (loadingHandlers.onRequestStart) {
    loadingHandlers.onRequestStart(key)
  }
}

function stopLoadFor(config) {
  const key = config?.__loadingToken
  if (key && loadingHandlers.onRequestEnd) {
    loadingHandlers.onRequestEnd(key)
  }
}

function shouldSkipRefresh(config) {
  const url = String(config?.url || '')
  return (
    url.includes('/auth/login') ||
    url.includes('/auth/register') ||
    url.includes('/auth/refresh') ||
    url.includes('/empresas/login') ||
    url.includes('/empresas/cadastrar') ||
    url.includes('/empresas/refresh')
  )
}

async function requestTokenRefresh() {
  if (refreshPromise) return refreshPromise

  refreshPromise = (async () => {
    const refreshToken = localStorage.getItem('refresh_token')
    if (!refreshToken) {
      throw new Error('Refresh token missing')
    }

    try {
      const response = await axios.post(`${API_BASE}/auth/refresh`, { refresh_token: refreshToken })
      return response.data
    } catch {
      const legacyResponse = await axios.post(`${API_BASE}/empresas/refresh`, { refresh_token: refreshToken })
      return legacyResponse.data
    }
  })()

  try {
    return await refreshPromise
  } finally {
    refreshPromise = null
  }
}

api.interceptors.request.use(
  (config) => {
    startLoadFor(config)

    const token = localStorage.getItem('access_token')
    if (token && token !== 'null' && token !== 'undefined') {
      config.headers = config.headers || {}
      config.headers.Authorization = `Bearer ${token}`
    }

    const method = String(config.method || 'GET').toUpperCase()
    console.log(`API REQUEST -> ${method} ${config.url}`)
    return config
  },
  (error) => {
    stopLoadFor(error?.config)
    console.error('API REQUEST ERROR ->', error?.message)
    return Promise.reject(error)
  }
)

api.interceptors.response.use(
  (response) => {
    stopLoadFor(response.config)
    console.log(`API RESPONSE -> ${response.status} ${response.config?.url || ''}`)
    return response
  },
  async (error) => {
    const originalRequest = error?.config || {}
    stopLoadFor(originalRequest)

    const status = error?.response?.status
    console.error('API RESPONSE ERROR ->', status, originalRequest?.url, error?.message)
    captureException(error, {
      status,
      path: originalRequest?.url || '',
      method: originalRequest?.method || ''
    })

    if (status === 401 && !originalRequest._retry && !shouldSkipRefresh(originalRequest)) {
      originalRequest._retry = true

      try {
        const refreshed = await requestTokenRefresh()
        const newAccessToken = refreshed?.access_token
        const newRefreshToken = refreshed?.refresh_token

        if (!newAccessToken) {
          throw new Error('Invalid refresh response')
        }

        localStorage.setItem('access_token', newAccessToken)
        if (newRefreshToken) {
          localStorage.setItem('refresh_token', newRefreshToken)
        }

        if (authHandlers.onTokenRefreshed) {
          authHandlers.onTokenRefreshed(newAccessToken)
        }

        originalRequest.headers = originalRequest.headers || {}
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`
        return api(originalRequest)
      } catch (refreshError) {
        if (authHandlers.onAuthFailure) {
          authHandlers.onAuthFailure()
        }
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

function buildCacheKey(url, config) {
  return JSON.stringify({
    url,
    params: config?.params || null
  })
}

export async function cachedGet(url, config = {}, ttlMs = DEFAULT_CACHE_TTL_MS) {
  const key = buildCacheKey(url, config)
  const now = Date.now()
  const cached = requestCache.get(key)

  if (cached && cached.expiresAt > now) {
    return cached.value
  }

  const response = await api.get(url, config)
  requestCache.set(key, { value: response, expiresAt: now + ttlMs })
  return response
}

export function clearApiCache() {
  requestCache.clear()
}

export default api
