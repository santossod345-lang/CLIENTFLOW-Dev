import { useState, useEffect } from 'react'
import axios from 'axios'

function Dashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
  const token = localStorage.getItem('access_token')

  useEffect(() => {
    fetchDashboard()
  }, [])

  const fetchDashboard = async () => {
    try {
      const response = await axios.get(`${apiUrl}/dashboard`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setData(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao carregar dashboard')
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    window.location.href = '/login'
  }

  return (
    <div className="min-h-screen bg-light">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6 flex justify-between items-center">
          <h1 className="text-3xl font-bold text-primary">ClientFlow Dashboard</h1>
          <button
            onClick={handleLogout}
            className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600"
          >
            Logout
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {loading ? (
          <div className="text-center py-12">
            <p className="text-gray-600 text-lg">Carregando dados...</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Stats Cards */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-gray-500 text-sm font-medium mb-2">Total de Clientes</h3>
              <p className="text-3xl font-bold text-primary">
                {data?.total_clientes || 0}
              </p>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-gray-500 text-sm font-medium mb-2">Total de Atendimentos</h3>
              <p className="text-3xl font-bold text-secondary">
                {data?.total_atendimentos || 0}
              </p>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-gray-500 text-sm font-medium mb-2">Pendentes</h3>
              <p className="text-3xl font-bold text-yellow-500">
                {data?.atendimentos_pendentes || 0}
              </p>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-gray-500 text-sm font-medium mb-2">Concluídos</h3>
              <p className="text-3xl font-bold text-green-500">
                {data?.atendimentos_concluidos || 0}
              </p>
            </div>
          </div>
        )}

        {/* Recently Updated */}
        {data?.ultimos_atendimentos && data.ultimos_atendimentos.length > 0 && (
          <div className="mt-8 bg-white rounded-lg shadow overflow-hidden">
            <div className="px-6 py-4 bg-gray-50 border-b">
              <h2 className="text-lg font-semibold text-dark">Últimos Atendimentos</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Cliente</th>
                    <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Status</th>
                    <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Data</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {data.ultimos_atendimentos.map((atendimento, idx) => (
                    <tr key={idx} className="hover:bg-gray-50">
                      <td className="px-6 py-4 text-sm text-gray-700">
                        {atendimento.cliente_nome || 'N/A'}
                      </td>
                      <td className="px-6 py-4 text-sm">
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-medium ${
                            atendimento.status === 'concluido'
                              ? 'bg-green-100 text-green-700'
                              : 'bg-yellow-100 text-yellow-700'
                          }`}
                        >
                          {atendimento.status || 'pendente'}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        {new Date(atendimento.data_criacao).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default Dashboard
