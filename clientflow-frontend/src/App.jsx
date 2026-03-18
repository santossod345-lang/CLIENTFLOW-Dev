import { lazy, Suspense, useContext, useEffect } from 'react'
import { Navigate, Outlet, Route, Routes, useLocation } from 'react-router-dom'
import PrivateRoute from './routes/PrivateRoute'
import DashboardLayout from './layouts/DashboardLayout'
import AuthContext from './context/AuthContext'
import { useLoading } from './context/LoadingContext'

const Login = lazy(() => import('./pages/Login'))
const Cadastro = lazy(() => import('./pages/Cadastro'))
const Painel = lazy(() => import('./pages/Painel'))
const Clientes = lazy(() => import('./pages/Clientes'))
const Planos = lazy(() => import('./pages/Planos'))
const Whatsapp = lazy(() => import('./pages/WhatsApp'))
const Marketing = lazy(() => import('./pages/Marketing'))
const Atendimentos = lazy(() => import('./pages/Atendimentos'))
const Financeiro = lazy(() => import('./pages/Financeiro'))
const Relatorios = lazy(() => import('./pages/Relatorios'))
const Agenda = lazy(() => import('./pages/Agenda'))
const Configuracoes = lazy(() => import('./pages/Configuracoes'))
const Suporte = lazy(() => import('./pages/Suporte'))
const Documentacao = lazy(() => import('./pages/Documentacao'))

function RouteDebugLogger() {
  const location = useLocation()
  const { startLoading, stopLoading } = useLoading()

  useEffect(() => {
    console.log('[Routing] Route changed:', location.pathname)
    startLoading('route-change')

    const t = window.setTimeout(() => {
      stopLoading('route-change')
    }, 120)

    return () => window.clearTimeout(t)
  }, [location.pathname, startLoading, stopLoading])

  return null
}

function GlobalSuspense({ children }) {
  return (
    <Suspense
      fallback={<div className="flex min-h-screen items-center justify-center text-slate-200">Carregando pagina...</div>}
    >
      {children}
    </Suspense>
  )
}

function ProtectedShell() {
  return (
    <PrivateRoute>
      <DashboardLayout>
        <Outlet />
      </DashboardLayout>
    </PrivateRoute>
  )
}

function App() {
  const { isAuthenticated, isLoading } = useContext(AuthContext)

  if (isLoading) {
    return <div className="flex min-h-screen items-center justify-center text-slate-200">Validando sessao...</div>
  }

  return (
    <>
      <RouteDebugLogger />
      <GlobalSuspense>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/cadastro" element={<Cadastro />} />
          <Route path="/" element={<Navigate to={isAuthenticated ? '/painel' : '/login'} replace />} />

          <Route element={<ProtectedShell />}>
            <Route path="/painel" element={<Painel />} />
            <Route path="/clientes" element={<Clientes />} />
            <Route path="/planos" element={<Planos />} />
            <Route path="/whatsapp" element={<Whatsapp />} />
            <Route path="/marketing" element={<Marketing />} />
            <Route path="/atendimentos" element={<Atendimentos />} />
            <Route path="/financeiro" element={<Financeiro />} />
            <Route path="/relatorios" element={<Relatorios />} />
            <Route path="/agenda" element={<Agenda />} />
            <Route path="/configuracoes" element={<Configuracoes />} />
            <Route path="/suporte" element={<Suporte />} />
            <Route path="/documentacao" element={<Documentacao />} />
          </Route>

          <Route path="/dashboard" element={<Navigate to="/painel" replace />} />
          <Route path="/crm" element={<Navigate to="/clientes" replace />} />
          <Route path="*" element={<Navigate to={isAuthenticated ? '/painel' : '/login'} replace />} />
        </Routes>
      </GlobalSuspense>
    </>
  )
}

export default App
