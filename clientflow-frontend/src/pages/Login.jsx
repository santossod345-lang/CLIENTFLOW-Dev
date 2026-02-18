import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const Login = () => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [localError, setLocalError] = useState('')

  const navigate = useNavigate()
  const { login, isAuthenticated, error, clearError } = useAuth()

  // Se já está autenticado, redirecionar ao dashboard
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard')
    }
  }, [isAuthenticated, navigate])

  // Limpar erro quando o componente é desmontado
  useEffect(() => {
    return () => clearError()
  }, [clearError])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLocalError('')

    // Validação básica
    if (!email || !password) {
      setLocalError('Email e senha são obrigatórios')
      return
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setLocalError('Email inválido')
      return
    }

    setIsLoading(true)

    const result = await login(email, password)

    if (result.success) {
      // Sucesso - redirecionamento é automático via useEffect
      navigate('/dashboard')
    } else {
      setLocalError(result.error || 'Erro ao fazer login')
    }

    setIsLoading(false)
  }

  const displayError = localError || error

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-900 via-primary-800 to-primary-900 p-4">
      {/* Decorative background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-0 left-0 w-96 h-96 bg-accent-blue/10 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-0 w-96 h-96 bg-accent-cyan/10 rounded-full blur-3xl" />
      </div>

      {/* Main container */}
      <div className="relative z-10 w-full max-w-md">
        {/* Logo/Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <div className="w-16 h-16 bg-gradient-to-br from-accent-blue to-accent-cyan rounded-lg flex items-center justify-center">
              <svg
                className="w-8 h-8 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                />
              </svg>
            </div>
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">ClientFlow</h1>
          <p className="text-gray-400">Bem-vindo de volta</p>
        </div>

        {/* Glassmorphic Card */}
        <div className="bg-primary-800/40 backdrop-blur-xl border border-primary-700/50 rounded-2xl p-8 shadow-2xl">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Email field */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-300 mb-3">
                Email
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value)
                  setLocalError('')
                }}
                placeholder="seu@email.com"
                disabled={isLoading}
                className="w-full px-4 py-3 bg-primary-700/40 border border-primary-600/50 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-accent-blue focus:ring-2 focus:ring-accent-blue/30 transition-all disabled:opacity-50"
              />
            </div>

            {/* Password field */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-300 mb-3">
                Senha
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value)
                  setLocalError('')
                }}
                placeholder="••••••••"
                disabled={isLoading}
                className="w-full px-4 py-3 bg-primary-700/40 border border-primary-600/50 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-accent-blue focus:ring-2 focus:ring-accent-blue/30 transition-all disabled:opacity-50"
              />
            </div>

            {/* Error message */}
            {displayError && (
              <div className="p-4 bg-red-500/20 border border-red-500/50 rounded-lg">
                <p className="text-red-300 text-sm">⚠️ {displayError}</p>
              </div>
            )}

            {/* Submit button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3 px-4 bg-gradient-to-r from-accent-blue to-accent-cyan rounded-lg font-semibold text-primary-900 hover:shadow-lg hover:shadow-accent-blue/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-primary-900 border-t-transparent" />
                  Entrando...
                </>
              ) : (
                'Entrar'
              )}
            </button>
          </form>

          {/* Divider */}
          <div className="my-6 flex items-center gap-3">
            <div className="flex-1 h-px bg-primary-600/30" />
            <span className="text-xs text-gray-500 uppercase">ou</span>
            <div className="flex-1 h-px bg-primary-600/30" />
          </div>

          {/* Demo credentials */}
          <div className="bg-primary-900/50 border border-primary-600/30 rounded-lg p-4">
            <p className="text-xs text-gray-400 mb-3 font-semibold uppercase">Credenciais de teste:</p>
            <div className="space-y-1 text-xs text-gray-300">
              <p>
                <span className="text-gray-500">Email: </span>
                <code className="bg-primary-700/50 px-2 py-1 rounded text-accent-cyan">
                  teste@clientflow.com
                </code>
              </p>
              <p>
                <span className="text-gray-500">Senha: </span>
                <code className="bg-primary-700/50 px-2 py-1 rounded text-accent-cyan">
                  123456
                </code>
              </p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <p className="text-center text-gray-500 text-xs mt-6">
          © 2024 ClientFlow. Todos os direitos reservados.
        </p>
      </div>
    </div>
  )
}

export default Login
