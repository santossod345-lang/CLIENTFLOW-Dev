import { useCallback, useEffect, useMemo, useState } from 'react'
import axios from 'axios'

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import { Line } from 'react-chartjs-2'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend, Filler)

const PERIOD_OPTIONS = [
  { key: 'today', label: 'Hoje' },
  { key: '7d', label: '7 dias' },
  { key: '30d', label: '30 dias' },
  { key: 'month', label: 'Mês' }
]

const formatCurrencyBRL = (value) => {
  const numberValue = Number(value) || 0
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(numberValue)
}

const formatPercentOneDecimal = (value) => {
  const numberValue = Number(value) || 0
  return new Intl.NumberFormat('pt-BR', { minimumFractionDigits: 1, maximumFractionDigits: 1 }).format(numberValue)
}

const formatDateShort = (isoDate) => {
  if (!isoDate) return ''
  const dt = new Date(isoDate)
  if (Number.isNaN(dt.getTime())) return String(isoDate)
  return new Intl.DateTimeFormat('pt-BR', { day: '2-digit', month: '2-digit' }).format(dt)
}

const formatDateLong = (isoDate) => {
  if (!isoDate) return ''
  const dt = new Date(isoDate)
  if (Number.isNaN(dt.getTime())) return String(isoDate)
  return new Intl.DateTimeFormat('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' }).format(dt)
}

const hexToRgba = (hex, alpha) => {
  const raw = String(hex || '').trim().replace('#', '')
  if (raw.length !== 6) return `rgba(102,126,234,${alpha})`
  const r = parseInt(raw.slice(0, 2), 16)
  const g = parseInt(raw.slice(2, 4), 16)
  const b = parseInt(raw.slice(4, 6), 16)
  return `rgba(${r},${g},${b},${alpha})`
}

const getThemeColors = () => {
  if (typeof window === 'undefined' || typeof document === 'undefined') {
    return { primary: '#667eea', secondary: '#764ba2' }
  }
  const styles = getComputedStyle(document.documentElement)
  const primary = (styles.getPropertyValue('--color-primary') || '#667eea').trim()
  const secondary = (styles.getPropertyValue('--color-secondary') || '#764ba2').trim()
  return { primary, secondary }
}

function StatCard({ title, value, percentage }) {
  const pct = Number(percentage) || 0

  const variant = pct > 0 ? 'up' : pct < 0 ? 'down' : 'neutral'
  const badgeClass =
    variant === 'up'
      ? 'bg-green-100 text-green-700'
      : variant === 'down'
        ? 'bg-red-100 text-red-700'
        : 'bg-gray-100 text-gray-700'

  const badgeText =
    variant === 'up'
      ? `↑ ${formatPercentOneDecimal(pct)}% vs período anterior`
      : variant === 'down'
        ? `↓ ${formatPercentOneDecimal(Math.abs(pct))}% vs período anterior`
        : `${formatPercentOneDecimal(0)}% vs período anterior`

  return (
    <div className="bg-white rounded-lg shadow p-6 flex flex-col gap-3">
      <div className="flex items-start justify-between gap-4">
        <h3 className="text-gray-500 text-sm font-medium">{title}</h3>
        <span className={`px-3 py-1 rounded-full text-xs font-medium whitespace-nowrap ${badgeClass}`}
        >
          {badgeText}
        </span>
      </div>
      <p className="text-3xl font-bold text-dark">{value}</p>
    </div>
  )
}

function SkeletonCard() {
  return (
    <div className="bg-white rounded-lg shadow p-6 animate-pulse">
      <div className="flex items-start justify-between gap-4">
        <div className="h-4 w-32 bg-gray-200 rounded" />
        <div className="h-6 w-44 bg-gray-200 rounded-full" />
      </div>
      <div className="mt-4 h-8 w-40 bg-gray-200 rounded" />
    </div>
  )
}

function SkeletonChart({ title }) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="h-5 w-40 bg-gray-200 rounded animate-pulse" />
      <div className="mt-4 h-72 bg-gray-100 rounded animate-pulse" />
      <div className="sr-only">{title}</div>
    </div>
  )
}

function Dashboard() {
  const [period, setPeriod] = useState('30d')

  const [empresa, setEmpresa] = useState(null)

  const [dashboardData, setDashboardData] = useState(null)
  const [dashboardLoading, setDashboardLoading] = useState(true)

  const [analytics, setAnalytics] = useState(null)
  const [analyticsLoading, setAnalyticsLoading] = useState(true)

  const [error, setError] = useState('')

  const rawApiUrl = import.meta.env.VITE_API_URL
  const apiBase = rawApiUrl
    ? rawApiUrl.replace(/\/$/, '').endsWith('/api')
      ? rawApiUrl.replace(/\/$/, '')
      : `${rawApiUrl.replace(/\/$/, '')}/api`
    : ''
  const token = localStorage.getItem('access_token')

  const themeColors = useMemo(() => getThemeColors(), [])

  const fetchDashboard = useCallback(async () => {
    try {
      setError('')
      setDashboardLoading(true)
      const response = await axios.get(`${apiBase}/dashboard`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setDashboardData(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao carregar dashboard')
    } finally {
      setDashboardLoading(false)
    }
  }, [apiBase, token])

  const fetchEmpresa = useCallback(async () => {
    try {
      const response = await axios.get(`${apiBase}/empresas/me`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setEmpresa(response.data)
    } catch {
      // Ignore errors here; main flows already handle auth redirects.
    }
  }, [apiBase, token])

  const fetchAnalytics = useCallback(
    async (periodKey) => {
      try {
        setError('')
        setAnalyticsLoading(true)
        const response = await axios.get(`${apiBase}/dashboard/analytics`, {
          params: { period: periodKey },
          headers: { Authorization: `Bearer ${token}` }
        })
        setAnalytics(response.data)
      } catch (err) {
        setError(err.response?.data?.detail || 'Erro ao carregar analytics')
      } finally {
        setAnalyticsLoading(false)
      }
    },
    [apiBase, token]
  )

  useEffect(() => {
    if (!apiBase) {
      setError('VITE_API_URL nao configurada')
      setDashboardLoading(false)
      setAnalyticsLoading(false)
      return
    }
    fetchDashboard()
    fetchEmpresa()
  }, [apiBase, fetchDashboard, fetchEmpresa])

  useEffect(() => {
    if (!apiBase) return
    fetchAnalytics(period)
  }, [apiBase, fetchAnalytics, period])

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    window.location.href = '/login'
  }

  const revenueMetric = analytics?.metrics?.revenue
  const clientsMetric = analytics?.metrics?.clients
  const appointmentsMetric = analytics?.metrics?.appointments

  const revenueSeries = analytics?.revenue_series || []
  const clientsSeries = analytics?.clients_series || []

  const revenueDates = useMemo(() => revenueSeries.map((p) => p.date), [revenueSeries])
  const revenueLabels = useMemo(() => revenueSeries.map((p) => formatDateShort(p.date)), [revenueSeries])
  const revenueValues = useMemo(() => revenueSeries.map((p) => Number(p.value) || 0), [revenueSeries])

  const clientsDates = useMemo(() => clientsSeries.map((p) => p.date), [clientsSeries])
  const clientsLabels = useMemo(() => clientsSeries.map((p) => formatDateShort(p.date)), [clientsSeries])
  const clientsValues = useMemo(() => clientsSeries.map((p) => Number(p.value) || 0), [clientsSeries])

  const commonLineOptions = useMemo(
    () => ({
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          intersect: false,
          mode: 'index'
        }
      },
      interaction: { intersect: false, mode: 'index' },
      scales: {
        x: {
          grid: { display: false },
          ticks: { maxRotation: 0, autoSkip: true, maxTicksLimit: 8 }
        },
        y: {
          grid: { color: 'rgba(0,0,0,0.06)' },
          ticks: { precision: 0 }
        }
      },
      elements: {
        line: { tension: 0.35 },
        point: { radius: 0, hitRadius: 10, hoverRadius: 4 }
      }
    }),
    []
  )

  const revenueChartData = useMemo(
    () => ({
      labels: revenueLabels,
      datasets: [
        {
          label: 'Receita',
          data: revenueValues,
          borderColor: themeColors.primary,
          backgroundColor: hexToRgba(themeColors.primary, 0.12),
          borderWidth: 2,
          fill: false
        }
      ]
    }),
    [revenueLabels, revenueValues, themeColors.primary]
  )

  const revenueChartOptions = useMemo(
    () => ({
      ...commonLineOptions,
      plugins: {
        ...commonLineOptions.plugins,
        tooltip: {
          ...commonLineOptions.plugins.tooltip,
          callbacks: {
            title: (items) => {
              const idx = items?.[0]?.dataIndex ?? 0
              return formatDateLong(revenueDates[idx])
            },
            label: (item) => formatCurrencyBRL(item.parsed.y)
          }
        }
      },
      scales: {
        ...commonLineOptions.scales,
        y: {
          ...commonLineOptions.scales.y,
          ticks: {
            callback: (v) => formatCurrencyBRL(v)
          }
        }
      }
    }),
    [commonLineOptions, revenueDates]
  )

  const clientsChartData = useMemo(
    () => ({
      labels: clientsLabels,
      datasets: [
        {
          label: 'Clientes',
          data: clientsValues,
          borderColor: themeColors.secondary,
          backgroundColor: hexToRgba(themeColors.secondary, 0.12),
          borderWidth: 2,
          fill: true
        }
      ]
    }),
    [clientsLabels, clientsValues, themeColors.secondary]
  )

  const clientsChartOptions = useMemo(
    () => ({
      ...commonLineOptions,
      plugins: {
        ...commonLineOptions.plugins,
        tooltip: {
          ...commonLineOptions.plugins.tooltip,
          callbacks: {
            title: (items) => {
              const idx = items?.[0]?.dataIndex ?? 0
              return formatDateLong(clientsDates[idx])
            },
            label: (item) => `${item.parsed.y} clientes`
          }
        }
      }
    }),
    [clientsDates, commonLineOptions]
  )

  return (
    <div className="min-h-screen bg-light">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold text-primary">ClientFlow</h1>
            <span className="px-3 py-1 rounded-full text-xs font-semibold bg-gray-100 text-gray-700">
              {String(empresa?.plano_empresa || 'free').trim().toUpperCase()}
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

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {/* Global Period Filter */}
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div>
              <h2 className="text-lg font-semibold text-dark">Dashboard</h2>
              <p className="text-sm text-gray-500">Insights do período selecionado</p>
            </div>
            <div className="inline-flex rounded-lg border border-gray-200 bg-gray-50 p-1 w-full sm:w-auto">
              {PERIOD_OPTIONS.map((opt) => {
                const isActive = opt.key === period
                return (
                  <button
                    key={opt.key}
                    type="button"
                    onClick={() => setPeriod(opt.key)}
                    className={
                      `px-4 py-2 text-sm font-medium rounded-md transition ` +
                      (isActive
                        ? 'bg-primary text-white'
                        : 'text-gray-700 hover:bg-white')
                    }
                    aria-pressed={isActive}
                  >
                    {opt.label}
                  </button>
                )
              })}
            </div>
          </div>
        </div>

        {/* Premium KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {analyticsLoading ? (
            <>
              <SkeletonCard />
              <SkeletonCard />
              <SkeletonCard />
            </>
          ) : (
            <>
              <StatCard
                title="Receita"
                value={formatCurrencyBRL(revenueMetric?.current)}
                percentage={revenueMetric?.percentage}
              />
              <StatCard
                title="Novos Clientes"
                value={new Intl.NumberFormat('pt-BR').format(Number(clientsMetric?.current) || 0)}
                percentage={clientsMetric?.percentage}
              />
              <StatCard
                title="Atendimentos"
                value={new Intl.NumberFormat('pt-BR').format(Number(appointmentsMetric?.current) || 0)}
                percentage={appointmentsMetric?.percentage}
              />
            </>
          )}
        </div>

        {/* Charts */}
        <div className="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
          {analyticsLoading ? (
            <>
              <SkeletonChart title="Receita" />
              <SkeletonChart title="Clientes" />
            </>
          ) : (
            <>
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-gray-700 text-sm font-semibold mb-4">Receita</h3>
                <div className="h-72">
                  <Line data={revenueChartData} options={revenueChartOptions} />
                </div>
              </div>
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-gray-700 text-sm font-semibold mb-4">Clientes</h3>
                <div className="h-72">
                  <Line data={clientsChartData} options={clientsChartOptions} />
                </div>
              </div>
            </>
          )}
        </div>

        {/* Recently Updated */}
        {!dashboardLoading && dashboardData?.ultimos_atendimentos && dashboardData.ultimos_atendimentos.length > 0 && (
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
                  {dashboardData.ultimos_atendimentos.map((atendimento, idx) => (
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
                        {new Date(atendimento.data_atendimento || atendimento.data_criacao).toLocaleDateString()}
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
