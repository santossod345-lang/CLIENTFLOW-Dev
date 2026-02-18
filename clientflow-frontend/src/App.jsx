import React, { useEffect, useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import { CompanyProvider } from './context/CompanyContext'
import PrivateRoute from './routes/PrivateRoute'
import Login from './pages/Login'
import Sidebar from './components/layout/Sidebar'
import Header from './components/layout/Header'
import Dashboard from './pages/Dashboard'
import Company from './pages/Company'
import './App.css'

// Componente interna para usar useAuth
function DashboardLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const { logout } = useAuth()

  useEffect(() => {
    // Listener para logout automático (token expirado)
    const handleLogout = () => {
      logout()
    }

    window.addEventListener('auth:logout', handleLogout)
    return () => window.removeEventListener('auth:logout', handleLogout)
  }, [logout])

  return (
    <div className="flex h-screen bg-primary-900">
      <Sidebar isOpen={sidebarOpen} setIsOpen={setSidebarOpen} />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header onMenuClick={() => setSidebarOpen(!sidebarOpen)} />
        <main className="flex-1 overflow-auto">
          <Dashboard />
        </main>
      </div>
    </div>
  )
}

// Componente para layout com sidebar (Company page)
function MainLayout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const { logout } = useAuth()

  useEffect(() => {
    const handleLogout = () => {
      logout()
    }

    window.addEventListener('auth:logout', handleLogout)
    return () => window.removeEventListener('auth:logout', handleLogout)
  }, [logout])

  return (
    <div className="flex h-screen bg-primary-900">
      <Sidebar isOpen={sidebarOpen} setIsOpen={setSidebarOpen} />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header onMenuClick={() => setSidebarOpen(!sidebarOpen)} />
        <main className="flex-1 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  )
}

function AppRoutes() {
  return (
    <Routes>
      {/* Rota pública - Login */}
      <Route path="/login" element={<Login />} />

      {/* Rota protegida - Dashboard */}
      <Route
        path="/dashboard"
        element={
          <PrivateRoute>
            <DashboardLayout />
          </PrivateRoute>
        }
      />

      {/* Rota protegida - Perfil da Empresa */}
      <Route
        path="/empresa"
        element={
          <PrivateRoute>
            <MainLayout>
              <Company />
            </MainLayout>
          </PrivateRoute>
        }
      />

      {/* Rota raiz - Redirecionar para dashboard ou login */}
      <Route
        path="/"
        element={<Navigate to="/dashboard" replace />}
      />

      {/* Rota não encontrada */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <CompanyProvider>
          <AppRoutes />
        </CompanyProvider>
      </AuthProvider>
    </Router>
  )
}

export default App
