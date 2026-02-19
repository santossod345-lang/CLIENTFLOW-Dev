import { useEffect, useMemo, useState } from 'react'
import axios from 'axios'

function Planos() {
  const [empresa, setEmpresa] = useState(null)
  const [error, setError] = useState('')

  const rawApiUrl = import.meta.env.VITE_API_URL
  const apiBase = rawApiUrl
    ? rawApiUrl.replace(/\/$/, '').endsWith('/api')
      ? rawApiUrl.replace(/\/$/, '')
      : `${rawApiUrl.replace(/\/$/, '')}/api`
    : ''

  const token = localStorage.getItem('access_token')

  useEffect(() => {
    let active = true
    const run = async () => {
      try {
        setError('')
        const resp = await axios.get(`${apiBase}/empresas/me`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        if (!active) return
        setEmpresa(resp.data)
      } catch (err) {
        if (!active) return
        setError(err.response?.data?.detail || 'Erro ao carregar plano')
      }
    }

    if (!apiBase) {
      setError('VITE_API_URL nao configurada')
      return
    }
    if (token) run()
    return () => {
      active = false
    }
  }, [apiBase, token])

  const planoLabel = useMemo(() => {
    const p = (empresa?.plano_empresa || 'free').toString().trim().toUpperCase()
    return p || 'FREE'
  }, [empresa])

  const freeClientes = empresa?.limite_clientes ?? 'X'
  const freeAtendimentos = empresa?.limite_atendimentos ?? 'X'

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    window.location.href = '/login'
  }

  return (
    <div className="min-h-screen bg-light">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold text-primary">ClientFlow</h1>
            <span className="px-3 py-1 rounded-full text-xs font-semibold bg-gray-100 text-gray-700">
              {planoLabel}
            </span>
          </div>
          <button
            onClick={handleLogout}
            className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600"
          >
            Logout
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        <h2 className="text-xl font-semibold text-dark mb-6">Planos</h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-dark mb-4">FREE</h3>
            <ul className="text-sm text-gray-700 space-y-2">
              <li>{freeClientes} clientes</li>
              <li>{freeAtendimentos} atendimentos</li>
            </ul>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-dark mb-4">PRO</h3>
            <ul className="text-sm text-gray-700 space-y-2">
              <li>Ilimitado</li>
            </ul>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-dark mb-4">ENTERPRISE</h3>
            <ul className="text-sm text-gray-700 space-y-2">
              <li>Personalizado</li>
            </ul>
          </div>
        </div>
      </main>
    </div>
  )
}

export default Planos
