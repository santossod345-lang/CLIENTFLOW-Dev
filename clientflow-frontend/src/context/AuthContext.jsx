import { createContext, useCallback, useEffect, useMemo, useState } from 'react'
import api, { setApiAuthHandlers } from '../services/api'

const AuthContext = createContext({
  user: null,
  isAuthenticated: false,
  isLoading: true,
  token: null,
  login: () => {},
  logout: () => {},
  refreshUser: async () => null,
  setAuth: () => {}
})

function parseUserFromToken(token) {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    return {
      id: payload?.sub || null,
      email: payload?.email || null
    }
  } catch {
    return null
  }
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  const logout = useCallback(() => {
    console.log('[Auth] logout')
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setToken(null)
    setUser(null)
  }, [])

  const login = useCallback(({ accessToken, refreshToken, user: incomingUser }) => {
    if (!accessToken) return
    localStorage.setItem('access_token', accessToken)
    if (refreshToken) {
      localStorage.setItem('refresh_token', refreshToken)
    }
    setToken(accessToken)
    setUser(incomingUser || parseUserFromToken(accessToken))
  }, [])

  const setAuth = useCallback(
    (nextAuth) => {
      const nextToken = nextAuth?.token || nextAuth?.access_token || null
      if (!nextToken) {
        logout()
        return
      }
      login({ accessToken: nextToken, user: nextAuth?.user })
    },
    [login, logout]
  )

  const refreshUser = useCallback(async () => {
    try {
      const resp = await api.get('/auth/me')
      setUser(resp.data)
      return resp.data
    } catch {
      try {
        const legacyResp = await api.get('/empresas/me')
        setUser(legacyResp.data)
        return legacyResp.data
      } catch {
        return null
      }
    }
  }, [])

  useEffect(() => {
    setApiAuthHandlers({
      onAuthFailure: logout,
      onTokenRefreshed: (newToken) => {
        setToken(newToken)
      }
    })
  }, [logout])

  useEffect(() => {
    const bootstrapAuth = async () => {
      const savedToken = localStorage.getItem('access_token')

      if (!savedToken || savedToken === 'null' || savedToken === 'undefined') {
        setIsLoading(false)
        return
      }

      setToken(savedToken)
      const currentUser = await refreshUser()

      if (!currentUser) {
        logout()
      }

      setIsLoading(false)
    }

    bootstrapAuth()
  }, [logout, refreshUser])

  const value = useMemo(
    () => ({
      user,
      token,
      isAuthenticated: Boolean(token),
      isLoading,
      login,
      logout,
      refreshUser,
      setAuth
    }),
    [user, token, isLoading, login, logout, refreshUser, setAuth]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export default AuthContext
