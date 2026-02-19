import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom'
import { useState, useEffect, useCallback } from 'react'
import axios from 'axios'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Planos from './pages/Planos'
import PrivateRoute from './routes/PrivateRoute'
import AuthContext from './context/AuthContext'

const PLAN_LIMIT_MESSAGE = 'Você atingiu o limite do plano FREE.'

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
        <p className="text-sm text-gray-600 mb-6">
          Você atingiu o limite do plano FREE. Faça upgrade para continuar.
        </p>
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

function AxiosPlanLimitBridge({ onPlanLimit }) {
  useEffect(() => {
    const interceptor = axios.interceptors.response.use(
      (response) => response,
      (error) => {
        const status = error?.response?.status
        const detail = error?.response?.data?.detail
        if (status === 403 && String(detail || '').trim() === PLAN_LIMIT_MESSAGE) {
          onPlanLimit()
        }
        return Promise.reject(error)
      }
    )
    return () => axios.interceptors.response.eject(interceptor)
  }, [onPlanLimit])

  return null
}

function App() {
  const [auth, setAuth] = useState(null)
  const [loading, setLoading] = useState(true)
  const [planLimitOpen, setPlanLimitOpen] = useState(false)

  const openPlanLimitModal = useCallback(() => setPlanLimitOpen(true), [])
  const closePlanLimitModal = useCallback(() => setPlanLimitOpen(false), [])

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem('access_token')
    if (token) {
      setAuth({ token })
    }
    setLoading(false)
  }, [])

  if (loading) {
    return <div className="flex items-center justify-center h-screen">Loading...</div>
  }

  return (
    <AuthContext.Provider value={{ auth, setAuth }}>
      <BrowserRouter>
        <AxiosPlanLimitBridge onPlanLimit={openPlanLimitModal} />
        <PlanLimitModal open={planLimitOpen} onClose={closePlanLimitModal} />
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/dashboard"
            element={
              <PrivateRoute>
                <Dashboard />
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
          <Route path="/" element={<Navigate to={auth ? '/dashboard' : '/login'} />} />
        </Routes>
      </BrowserRouter>
    </AuthContext.Provider>
  )
}

export default App
