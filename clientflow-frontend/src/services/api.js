import axios from 'axios'

/**
 * Resolve the API base URL from environment variables
 * @returns {string} The API base URL
 */
function resolveApiBase() {
  const rawApiUrl = import.meta.env.VITE_API_URL
  if (!rawApiUrl) return '/api'
  const sanitized = rawApiUrl.replace(/\/$/, '')
  return sanitized.endsWith('/api') ? sanitized : `${sanitized}/api`
}

// API base URL
export const API_BASE = resolveApiBase()

/**
 * Configured Axios instance for API calls
 * Automatically includes authentication headers from localStorage
 * Token refresh is handled by AxiosBridge in App.jsx
 */
const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

/**
 * Request interceptor to add authentication token
 */
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    
    if (token && token !== 'null' && token !== 'undefined' && token.trim() !== '') {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    return config
  },
  (error) => {
    console.error('[API] Request error:', error)
    return Promise.reject(error)
  }
)

// Note: Response interceptor for token refresh is handled in App.jsx AxiosBridge
// to avoid duplicate logic and ensure proper state management

export default api
