import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor para adicionar token de autenticação
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Interceptor para tratar erros de autenticação
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expirado ou inválido
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      // Redirecionar para login será feito pela app via evento
      window.dispatchEvent(new CustomEvent('auth:logout'))
    }
    return Promise.reject(error)
  }
)

// Serviços de Clientes
export const clientsService = {
  list: () => api.get('/clientes'),
  get: (id) => api.get(`/clientes/${id}`),
  create: (data) => api.post('/clientes', data),
  update: (id, data) => api.put(`/clientes/${id}`, data),
  delete: (id) => api.delete(`/clientes/${id}`),
}

// Serviços de Atendimentos
export const appointmentsService = {
  list: () => api.get('/atendimentos'),
  get: (id) => api.get(`/atendimentos/${id}`),
  create: (data) => api.post('/atendimentos', data),
  update: (id, data) => api.put(`/atendimentos/${id}`, data),
  delete: (id) => api.delete(`/atendimentos/${id}`),
}

// Serviços de Dashboard
export const dashboardService = {
  getMetrics: () => api.get('/dashboard/metrics'),
  getRevenue: () => api.get('/dashboard/revenue'),
  getAppointmentsStatus: () => api.get('/dashboard/appointments-status'),
  getStats: () => api.get('/dashboard/stats'),
  getTodayAppointments: () => api.get('/atendimentos/today'),
}

// Serviços de Autenticação
export const authService = {
  login: (email, password) => api.post('/empresas/login', { email_login: email, senha: password }),
  register: (data) => api.post('/empresas/cadastrar', data),
  logout: () => {
    localStorage.removeItem('token')
  },
}

// Serviços de Empresa
export const companyService = {
  getProfile: () => api.get('/empresas/me'),
  updateProfile: (data) => api.put('/empresas/me', data),
  uploadLogo: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/empresas/logo', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },
  getLogo: () => api.get('/empresas/me/logo'),
}

// Helper para tratamento de erros e dados
export const apiCall = async (fn, defaultValue = null) => {
  try {
    const response = await fn()
    return { data: response.data, error: null }
  } catch (error) {
    console.error('API Error:', error)
    return { data: defaultValue, error: error.message }
  }
}

export default api
