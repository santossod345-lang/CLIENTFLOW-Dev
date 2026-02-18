📋 SNIPPETS DE CÓDIGO - COPY & PASTE PRONTOS

═══════════════════════════════════════════════════════════════════════════════

1️⃣ COMPONENTE: Hook useAsync (gerenciar estado de chamadas API)

Crie arquivo: src/hooks/useAsync.js

────────────────────────────────────────────────────────────────────────────────

import { useState, useEffect } from 'react'

export function useAsync(asyncFunction, immediate = true) {
  const [status, setStatus] = useState('idle')
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  const execute = async () => {
    setStatus('pending')
    setData(null)
    setError(null)
    try {
      const response = await asyncFunction()
      setData(response.data)
      setStatus('success')
    } catch (err) {
      setError(err)
      setStatus('error')
    }
  }

  useEffect(() => {
    if (immediate) {
      execute()
    }
  }, [])

  return { execute, status, data, error }
}

COMO USAR:

import { useAsync } from '../hooks/useAsync'
import { clientsService } from '../services/api'

const { status, data: clients, error } = useAsync(() => clientsService.list())

{status === 'pending' && <div>Carregando...</div>}
{status === 'success' && <div>{clients.length} clientes</div>}
{status === 'error' && <div>Erro: {error.message}</div>}

════════════════════════════════════════════════════════════════════════════════

2️⃣ COMPONENTE: Loading Skeleton

Crie arquivo: src/components/common/Skeleton.jsx

────────────────────────────────────────────────────────────────────────────────

export function Skeleton({ width = 'w-full', height = 'h-4', className = '' }) {
  return (
    <div className={`${width} ${height} bg-primary-700/30 rounded-lg animate-pulse ${className}`} />
  )
}

COMO USAR:

{loading ? (
  <div className="space-y-3">
    <Skeleton height="h-12" />
    <Skeleton height="h-4" width="w-3/4" />
    <Skeleton height="h-4" width="w-1/2" />
  </div>
) : (
  <ClientsTable />
)}

════════════════════════════════════════════════════════════════════════════════

3️⃣ COMPONENTE: Toast Notification

Crie arquivo: src/components/common/Toast.jsx

────────────────────────────────────────────────────────────────────────────────

import { useState, useEffect } from 'react'

export function Toast({ message, type = 'success', duration = 3000 }) {
  const [visible, setVisible] = useState(true)

  useEffect(() => {
    const timer = setTimeout(() => setVisible(false), duration)
    return () => clearTimeout(timer)
  }, [duration])

  if (!visible) return null

  const bgColor = {
    success: 'bg-green-500',
    error: 'bg-red-500',
    warning: 'bg-orange-500',
    info: 'bg-blue-500',
  }[type]

  return (
    <div className={`fixed top-4 right-4 px-4 py-3 rounded-lg text-white ${bgColor} z-50`}>
      {message}
    </div>
  )
}

COMO USAR:

const [toast, setToast] = useState(null)

const handleCreate = async () => {
  try {
    await clientsService.create(data)
    setToast({ message: 'Cliente criado!', type: 'success' })
  } catch (error) {
    setToast({ message: 'Erro ao criar', type: 'error' })
  }
}

return (
  <>
    {toast && <Toast {...toast} />}
    <button onClick={handleCreate}>Criar</button>
  </>
)

════════════════════════════════════════════════════════════════════════════════

4️⃣ PAGINA: Login Completo

Crie arquivo: src/pages/Login.jsx

────────────────────────────────────────────────────────────────────────────────

import { useState } from 'react'
import { authService } from '../services/api'

export function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const response = await authService.login(email, password)
      localStorage.setItem('token', response.data.token)
      window.location.href = '/dashboard'
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao fazer login')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-primary-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="card-base">
          <div className="mb-8 text-center">
            <div className="w-16 h-16 bg-gradient-to-br from-accent-blue to-accent-purple rounded-lg flex items-center justify-center mx-auto mb-4">
              <span className="text-white font-bold text-2xl">CF</span>
            </div>
            <h1 className="text-2xl font-bold text-white">ClientFlow</h1>
            <p className="text-gray-400 text-sm mt-1">Intelligence Platform</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="bg-red-500/20 text-red-300 p-3 rounded-lg text-sm">
                {error}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-primary-700 text-white rounded-lg px-4 py-2 outline-none focus:ring-2 focus:ring-accent-blue"
                placeholder="seu@email.com"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Senha
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-primary-700 text-white rounded-lg px-4 py-2 outline-none focus:ring-2 focus:ring-accent-blue"
                placeholder="••••••••"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-accent-blue hover:bg-opacity-90 text-white font-medium py-2 rounded-lg transition disabled:opacity-50"
            >
              {loading ? 'Entrando...' : 'Entrar'}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}

════════════════════════════════════════════════════════════════════════════════

5️⃣ HOOK: useForm (Gerenciar formulários)

Crie arquivo: src/hooks/useForm.js

────────────────────────────────────────────────────────────────────────────────

import { useState, useCallback } from 'react'

export function useForm(initialValues, onSubmit) {
  const [values, setValues] = useState(initialValues)
  const [errors, setErrors] = useState({})
  const [touched, setTouched] = useState({})
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleChange = useCallback((e) => {
    const { name, value, type, checked } = e.target
    setValues(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }, [])

  const handleBlur = useCallback((e) => {
    const { name } = e.target
    setTouched(prev => ({ ...prev, [name]: true }))
  }, [])

  const handleSubmit = useCallback(async (e) => {
    e.preventDefault()
    setIsSubmitting(true)
    try {
      await onSubmit(values)
    } finally {
      setIsSubmitting(false)
    }
  }, [values, onSubmit])

  const reset = useCallback(() => {
    setValues(initialValues)
    setErrors({})
    setTouched({})
  }, [initialValues])

  return {
    values,
    errors,
    touched,
    isSubmitting,
    handleChange,
    handleBlur,
    handleSubmit,
    reset,
    setValues,
    setErrors
  }
}

COMO USAR:

const form = useForm(
  { name: '', email: '' },
  async (values) => {
    await clientsService.create(values)
  }
)

<form onSubmit={form.handleSubmit}>
  <input
    name="name"
    value={form.values.name}
    onChange={form.handleChange}
    onBlur={form.handleBlur}
  />
  <button type="submit" disabled={form.isSubmitting}>
    Enviar
  </button>
</form>

════════════════════════════════════════════════════════════════════════════════

6️⃣ CONTEXTO: AuthContext (Autenticação Global)

Crie arquivo: src/context/AuthContext.jsx

────────────────────────────────────────────────────────────────────────────────

import { createContext, useState, useContext, useCallback } from 'react'
import { authService } from '../services/api'

const AuthContext = createContext()

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(false)

  const login = useCallback(async (email, password) => {
    setLoading(true)
    try {
      const response = await authService.login(email, password)
      localStorage.setItem('token', response.data.token)
      setUser(response.data.user)
      return true
    } catch (error) {
      throw error
    } finally {
      setLoading(false)
    }
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('token')
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}

COMO USAR NO App.jsx:

import { AuthProvider } from './context/AuthContext'

<AuthProvider>
  <App />
</AuthProvider>

E em qualquer componente:

const { user, login, logout } = useAuth()

════════════════════════════════════════════════════════════════════════════════

7️⃣ COMPONENTE: Modal Reutilizável

Crie arquivo: src/components/common/Modal.jsx

────────────────────────────────────────────────────────────────────────────────

export function Modal({ isOpen, onClose, title, children }) {
  if (!isOpen) return null

  return (
    <>
      <div
        className="fixed inset-0 bg-black/50 z-40"
        onClick={onClose}
      />
      <div className="fixed inset-0 flex items-center justify-center z-50 p-4">
        <div className="bg-primary-800 rounded-2xl max-w-md w-full card-base">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-white">{title}</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-white transition"
            >
              ✕
            </button>
          </div>
          <div className="max-h-96 overflow-y-auto">
            {children}
          </div>
        </div>
      </div>
    </>
  )
}

COMO USAR:

const [open, setOpen] = useState(false)

<button onClick={() => setOpen(true)}>Abrir Modal</button>
<Modal isOpen={open} onClose={() => setOpen(false)} title="Editar Cliente">
  {/* conteúdo */}
</Modal>

════════════════════════════════════════════════════════════════════════════════

8️⃣ COMPONENTE: Tabela com Paginação

Crie arquivo: src/components/common/Table.jsx

────────────────────────────────────────────────────────────────────────────────

import { useState } from 'react'

export function Table({ data, columns, itemsPerPage = 10 }) {
  const [currentPage, setCurrentPage] = useState(1)

  const totalPages = Math.ceil(data.length / itemsPerPage)
  const start = (currentPage - 1) * itemsPerPage
  const paginatedData = data.slice(start, start + itemsPerPage)

  return (
    <div className="card-base">
      <div className="overflow-x-auto mb-4">
        <table className="w-full">
          <thead>
            <tr className="border-b border-primary-700">
              {columns.map((col) => (
                <th key={col.key} className="text-left py-3 px-4 font-semibold text-gray-400">
                  {col.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {paginatedData.map((row, idx) => (
              <tr key={idx} className="border-b border-primary-700 hover:bg-primary-700/30">
                {columns.map((col) => (
                  <td key={col.key} className="py-4 px-4 text-gray-300">
                    {col.render ? col.render(row) : row[col.key]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex items-center justify-between text-sm">
        <p className="text-gray-400">
          Página {currentPage} de {totalPages}
        </p>
        <div className="flex gap-2">
          <button
            onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
            disabled={currentPage === 1}
            className="px-3 py-1 bg-primary-700 rounded disabled:opacity-50"
          >
            ← Anterior
          </button>
          <button
            onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
            disabled={currentPage === totalPages}
            className="px-3 py-1 bg-primary-700 rounded disabled:opacity-50"
          >
            Próxima →
          </button>
        </div>
      </div>
    </div>
  )
}

════════════════════════════════════════════════════════════════════════════════

9️⃣ COMPONENTE: Badge Status

Crie arquivo: src/components/common/Badge.jsx

────────────────────────────────────────────────────────────────────────────────

const statusConfig = {
  pending: { bg: 'bg-orange-500/20', text: 'text-orange-300', label: 'Pendente' },
  progress: { bg: 'bg-blue-500/20', text: 'text-blue-300', label: 'Em Progresso' },
  completed: { bg: 'bg-green-500/20', text: 'text-green-300', label: 'Concluído' },
  cancelled: { bg: 'bg-red-500/20', text: 'text-red-300', label: 'Cancelado' },
}

export function Badge({ status, children }) {
  const config = statusConfig[status] || statusConfig.pending

  return (
    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${config.bg} ${config.text}`}>
      {children || config.label}
    </span>
  )
}

COMO USAR:

<Badge status="completed">Entregue</Badge>
<Badge status="pending" />

════════════════════════════════════════════════════════════════════════════════

🔟 COMPONENTE: Confirmação (Delete)

Crie arquivo: src/components/common/ConfirmDialog.jsx

────────────────────────────────────────────────────────────────────────────────

export function ConfirmDialog({ isOpen, title, message, onConfirm, onCancel, loading = false }) {
  if (!isOpen) return null

  return (
    <>
      <div className="fixed inset-0 bg-black/50 z-40" onClick={onCancel} />
      <div className="fixed inset-0 flex items-center justify-center z-50 p-4">
        <div className="bg-primary-800 rounded-2xl max-w-sm w-full p-6 card-base">
          <h2 className="text-lg font-bold text-white mb-2">{title}</h2>
          <p className="text-gray-400 mb-6">{message}</p>
          <div className="flex gap-3">
            <button
              onClick={onCancel}
              disabled={loading}
              className="flex-1 btn-secondary"
            >
              Cancelar
            </button>
            <button
              onClick={onConfirm}
              disabled={loading}
              className="flex-1 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition disabled:opacity-50"
            >
              {loading ? 'Deletando...' : 'Deletar'}
            </button>
          </div>
        </div>
      </div>
    </>
  )
}

COMO USAR:

const [confirmOpen, setConfirmOpen] = useState(false)

<button onClick={() => setConfirmOpen(true)}>Deletar</button>
<ConfirmDialog
  isOpen={confirmOpen}
  title="Deletar Cliente?"
  message="Esta ação não pode ser desfeita."
  onConfirm={async () => {
    await clientsService.delete(id)
    setConfirmOpen(false)
  }}
  onCancel={() => setConfirmOpen(false)}
/>

════════════════════════════════════════════════════════════════════════════════

🎉 MAIS 10 SNIPPETS PRONTOS PARA USAR!

Copie e cola esses códigos no seu projeto React para acelerar ainda mais! ⚡

═══════════════════════════════════════════════════════════════════════════════
