import React, { createContext, useState, useEffect, useCallback } from 'react'
import { authService } from '../services/api'

export const AuthContext = createContext(null)

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Restaurar sessão ao carregar a aplicação
  useEffect(() => {
    const storedToken = localStorage.getItem('token')
    const storedUser = localStorage.getItem('user')

    if (storedToken && storedUser) {
      setToken(storedToken)
      setUser(JSON.parse(storedUser))
    }

    setLoading(false)
  }, [])

  // Login
  const login = useCallback(async (email, password) => {
    setLoading(true)
    setError(null)

    try {
      const response = await authService.login(email, password)

      if (response.data && response.data.access_token) {
        const accessToken = response.data.access_token
        const userData = response.data.data || response.data

        // Salvar token e usuário
        localStorage.setItem('token', accessToken)
        localStorage.setItem('user', JSON.stringify(userData))

        // Atualizar estado
        setToken(accessToken)
        setUser(userData)

        return { success: true, data: userData }
      } else {
        throw new Error('Resposta inválida do servidor')
      }
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.message || 
                          error.message || 
                          'Erro ao fazer login'
      setError(errorMessage)
      console.error('Erro no login:', errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      setLoading(false)
    }
  }, [])

  // Logout
  const logout = useCallback(() => {
    setToken(null)
    setUser(null)
    setError(null)

    // Limpar localStorage
    localStorage.removeItem('token')
    localStorage.removeItem('user')

    // Redirecionar para login é responsabilidade da aplicação
    return true
  }, [])

  // Limpar erro
  const clearError = useCallback(() => {
    setError(null)
  }, [])

  const value = {
    user,
    token,
    loading,
    error,
    login,
    logout,
    clearError,
    isAuthenticated: !!token,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

// Hook para usar o contexto
export const useAuth = () => {
  const context = React.useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth deve ser usado dentro de um AuthProvider')
  }
  return context
}
