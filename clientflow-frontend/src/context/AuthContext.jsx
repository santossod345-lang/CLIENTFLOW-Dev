import { createContext, useState, useEffect, useCallback } from 'react'

const AuthContext = createContext({
  auth: null,
  setAuth: () => {},
  logout: () => {},
  isAuthenticated: false,
  token: null
})

/**
 * Provider para o AuthContext
 * Gerencia o estado de autenticação da aplicação
 * Sincroniza com localStorage para persistência
 */
export function AuthProvider({ children }) {
  const [auth, setAuth] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  // Carregar token do localStorage ao montar
  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (token && token !== 'null' && token !== 'undefined' && token.trim() !== '') {
      console.log('[AuthContext] Token encontrado ao carregar, restaurando sessão')
      setAuth({ token })
    }
    setIsLoading(false)
  }, [])

  // Função para fazer logout
  const logout = useCallback(() => {
    console.log('[AuthContext] Fazendo logout')
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setAuth(null)
    window.location.hash = '#/login'
  }, [])

  // Atualizar localStorage quando auth muda
  useEffect(() => {
    if (auth && auth.token) {
      localStorage.setItem('access_token', auth.token)
      console.log('[AuthContext] Token salvo em localStorage')
    }
  }, [auth])

  const value = {
    auth,
    setAuth,
    logout,
    isAuthenticated: !!auth?.token,
    token: auth?.token || null,
    isLoading
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export default AuthContext
