import { HashRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom'
import { useCallback, useContext, useRef, useEffect, useState } from 'react'
import api, { API_BASE } from './services/api'
import Login from './pages/Login'
import Cadastro from './pages/Cadastro'
import Planos from './pages/Planos'
import DashboardLayout from './layouts/DashboardLayout'
import Painel from './pages/Painel'
import CRM from './pages/CRM'
import Atendimentos from './pages/Atendimentos'
import Financeiro from './pages/Financeiro'
import Relatorios from './pages/Relatorios'
import WhatsApp from './pages/WhatsApp'
import Agenda from './pages/Agenda'
import Marketing from './pages/Marketing'
import Configuracoes from './pages/Configuracoes'
import Suporte from './pages/Suporte'
import Documentacao from './pages/Documentacao'
import PrivateRoute from './routes/PrivateRoute'
import AuthContext, { AuthProvider } from './context/AuthContext'

const PLAN_LIMIT_MESSAGE = 'Voc\u00ea atingiu o limite do plano FREE.'

function PlanLimitModal({ open, onClose }) {
  const navigate = useNavigate()

  if (!open) return null

  const handleVerPlanos = () => {
    onClose()
    navigate('/planos')
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center px-4">
      <div className="absolute inset-0 bg-gray-900/60" />
      <div className="relative w-full max-w-lg bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-dark mb-2">Limite do plano atingido</h2>
        <p className="text-sm text-gray-600 mb-6">Voce atingiu o limite do plano FREE. Faca upgrade para continuar.</p>
        <div className="flex items-center justify-end gap-3">
          <button
            type="button"
            onClick={handleVerPlanos}
            className="bg-primary text-white px-4 py-2 rounded-lg hover:opacity-95"
          >
            Ver planos
          </button>
          <button
            type="button"
            onClick={onClose}
            className="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200"
          >
            Fechar
          </button>
        </div>
      </div>
    </div>
  )
}

function AxiosBridge() {
  const stateRef = useRef({ isRefreshing: false, queue: [] })
  const { setAuth, logout } = useContext(AuthContext)

  const processQueue = (error, token = null) => {
    const queue = stateRef.current.queue
    queue.forEach(({ resolve, reject }) => {
      if (error) reject(error)
      else resolve(token)
    })
    stateRef.current.queue = []
  }

  useEffect(() => {
    const interceptor = api.interceptors.response.use(
      (response) => response,
      async (error) => {
        const status = error?.response?.status
        const detail = error?.response?.data?.detail
        const originalRequest = error?.config || {}

        if (status === 403 && String(detail || '').trim() === PLAN_LIMIT_MESSAGE) {
          // Plan limit is handled separately (via event or state)
          return Promise.reject(error)
        }

        if (status !== 401) return Promise.reject(error)

        const isRefreshRoute = String(originalRequest?.url || '').includes('/empresas/refresh')
        if (isRefreshRoute || originalRequest._retry) {
          console.warn('[AxiosBridge] Refresh token falhou. Fazendo logout.')
          logout()
          return Promise.reject(error)
        }

        if (stateRef.current.isRefreshing) {
          return new Promise((resolve, reject) => {
            stateRef.current.queue.push({ resolve, reject })
          }).then((newAccessToken) => {
            originalRequest.headers = originalRequest.headers || {}
            originalRequest.headers.Authorization = `Bearer ${newAccessToken}`
            return api(originalRequest)
          })
        }

        originalRequest._retry = true
        stateRef.current.isRefreshing = true
        const refreshToken = localStorage.getItem('refresh_token')

        if (!refreshToken) {
          stateRef.current.isRefreshing = false
          console.warn('[AxiosBridge] Refresh token não encontrado. Fazendo logout.')
          logout()
          return Promise.reject(error)
        }

        try {
          console.log('[AxiosBridge] Tentando renovar token...')
          const refreshResponse = await api.post('/empresas/refresh', {
            refresh_token: refreshToken
          })
          const newAccessToken = refreshResponse?.data?.access_token
          const newRefreshToken = refreshResponse?.data?.refresh_token

          if (!newAccessToken || !newRefreshToken) {
            throw new Error('Refresh retornou tokens invalidos')
          }

          console.log('[AxiosBridge] Token renovado com sucesso!')
          localStorage.setItem('access_token', newAccessToken)
          localStorage.setItem('refresh_token', newRefreshToken)
          setAuth({ token: newAccessToken })

          processQueue(null, newAccessToken)
          originalRequest.headers = originalRequest.headers || {}
          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`
          return api(originalRequest)
        } catch (refreshError) {
          console.error('[AxiosBridge] Erro ao renovar token:', refreshError)
          processQueue(refreshError)
          logout()
          return Promise.reject(refreshError)
        } finally {
          stateRef.current.isRefreshing = false
        }
      }
    )

    return () => api.interceptors.response.eject(interceptor)
  }, [setAuth, logout])

  return null
}

/**
 * Componente interno que usa AuthContext para decidir rotas.
 * Deve estar DENTRO de AuthProvider para acessar o contexto.
 */
function AppRoutes() {
  const { isAuthenticated, isLoading } = useContext(AuthContext)
  const [planLimitOpen, setPlanLimitOpen] = useState(false)

  if (isLoading) {
    return <div className="flex items-center justify-center h-screen">Loading...</div>
  }

  return (
    <>
      <AxiosBridge />
      <PlanLimitModal open={planLimitOpen} onClose={() => setPlanLimitOpen(false)} />
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/cadastro" element={<Cadastro />} />
        <Route path="/" element={<Navigate to={isAuthenticated ? '/dashboard' : '/login'} />} />
        
        {/* Dashboard Routes with Sidebar Layout */}
        <Route
          path="/dashboard"
          element={
            <PrivateRoute>
              <DashboardLayout><Painel /></DashboardLayout>
            </PrivateRoute>
          }
        />
        <Route
          path="/crm"
          element={
            <PrivateRoute>
              <DashboardLayout><CRM /></DashboardLayout>
            </PrivateRoute>
          }
        />
        <Route
          path="/atendimentos"
          element={
            <PrivateRoute>
              <DashboardLayout><Atendimentos /></DashboardLayout>
            </PrivateRoute>
          }
        />
        <Route
          path="/financeiro"
          element={
            <PrivateRoute>
              <DashboardLayout><Financeiro /></DashboardLayout>
            </PrivateRoute>
          }
        />
        <Route
          path="/relatorios"
          element={
            <PrivateRoute>
              <DashboardLayout><Relatorios /></DashboardLayout>
            </PrivateRoute>
          }
        />
        <Route
          path="/whatsapp"
          element={
            <PrivateRoute>
              <DashboardLayout><WhatsApp /></DashboardLayout>
            </PrivateRoute>
          }
        />
        <Route
          path="/agenda"
          element={
            <PrivateRoute>
              <DashboardLayout><Agenda /></DashboardLayout>
            </PrivateRoute>
          }
        />
        <Route
          path="/marketing"
          element={
            <PrivateRoute>
              <DashboardLayout><Marketing /></DashboardLayout>
            </PrivateRoute>
          }
        />
        <Route
          path="/configuracoes"
          element={
            <PrivateRoute>
              <DashboardLayout><Configuracoes /></DashboardLayout>
            </PrivateRoute>
          }
        />
        <Route
          path="/suporte"
          element={
            <PrivateRoute>
              <DashboardLayout><Suporte /></DashboardLayout>
            </PrivateRoute>
          }
        />
        <Route
          path="/documentacao"
          element={
            <PrivateRoute>
              <DashboardLayout><Documentacao /></DashboardLayout>
            </PrivateRoute>
          }
        />
        <Route
          path="/planos"
          element={
            <PrivateRoute>
              <Planos />
            </PrivateRoute>
          }
        />
        
        <Route path="*" element={<Navigate to={isAuthenticated ? '/dashboard' : '/login'} replace />} />
      </Routes>
    </>
  )
}

function App() {
  return (
    <AuthProvider>
      <HashRouter>
        <AppRoutes />
      </HashRouter>
    </AuthProvider>
  )
}

export default App
