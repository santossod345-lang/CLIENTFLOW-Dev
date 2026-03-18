import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { setApiLoadingHandlers } from '../services/api'

const LoadingContext = createContext({
  isGlobalLoading: false,
  startLoading: () => {},
  stopLoading: () => {}
})

export function LoadingProvider({ children }) {
  const [tokens, setTokens] = useState([])

  const startLoading = useCallback((token = `loading-${Date.now()}`) => {
    setTokens((current) => (current.includes(token) ? current : [...current, token]))
    return token
  }, [])

  const stopLoading = useCallback((token) => {
    if (!token) return
    setTokens((current) => current.filter((entry) => entry !== token))
  }, [])

  useEffect(() => {
    setApiLoadingHandlers({ onRequestStart: startLoading, onRequestEnd: stopLoading })
  }, [startLoading, stopLoading])

  const value = useMemo(
    () => ({
      isGlobalLoading: tokens.length > 0,
      startLoading,
      stopLoading
    }),
    [tokens.length, startLoading, stopLoading]
  )

  return (
    <LoadingContext.Provider value={value}>
      {children}
      {value.isGlobalLoading ? (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-slate-950/70">
          <div className="rounded-xl border border-cyan-400/40 bg-slate-900/90 px-6 py-4 text-slate-100 shadow-2xl">
            Carregando...
          </div>
        </div>
      ) : null}
    </LoadingContext.Provider>
  )
}

export function useLoading() {
  return useContext(LoadingContext)
}

export default LoadingContext
