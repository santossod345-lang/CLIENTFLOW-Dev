import { useCallback, useEffect, useMemo, useState } from 'react'
import axios from 'axios'
import {
  Chart as ChartJS,
  ArcElement,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import { Doughnut, Line } from 'react-chartjs-2'

ChartJS.register(
  ArcElement,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
  Filler
)

const PERIOD_OPTIONS = [
  { key: 'today', label: 'Hoje' },
  { key: '7d', label: 'Semana' },
  { key: '30d', label: 'Mes' },
  { key: 'month', label: 'Mes atual' }
]

const SIDEBAR_MENU = [
  { label: 'Dashboard', icon: '▣', active: true },
  { label: 'CRM', icon: '◈' },
  { label: 'Atendimentos', icon: '◎' },
  { label: 'Financeiro', icon: '◉' },
  { label: 'Relatorios', icon: '◍' },
  { label: 'WhatsApp', icon: '◌' },
  { label: 'Agenda', icon: '◔' },
  { label: 'Marketing', icon: '◐' },
  { label: 'Configuracoes', icon: '⚙' }
]

const BOTTOM_HEALTH = [
  { label: 'Microsservicos', value: '5/5' },
  { label: 'Backup', value: '100%' },
  { label: 'SSL', value: 'Seguro' },
  { label: 'API', value: '99.3%' },
  { label: 'Tempo real', value: 'Ativo' }
]

const STATUS_COLOR = {
  novo: 'status-new',
  pendente: 'status-pending',
  'em andamento': 'status-progress',
  concluido: 'status-done',
  entregue: 'status-delivered'
}

const numberBR = (value) => new Intl.NumberFormat('pt-BR').format(Number(value) || 0)
const moneyBR = (value) =>
  new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(Number(value) || 0)

const pctFormat = (value) =>
  `${new Intl.NumberFormat('pt-BR', { minimumFractionDigits: 1, maximumFractionDigits: 1 }).format(
    Number(value) || 0
  )}%`

const safeDate = (value) => {
  const dt = value ? new Date(value) : null
  if (!dt || Number.isNaN(dt.getTime())) return '--:--'
  return dt.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
}

const safeDateShort = (value) => {
  const dt = value ? new Date(value) : null
  if (!dt || Number.isNaN(dt.getTime())) return '--/--'
  return dt.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })
}

function KpiCard({ title, value, delta, tone = 'blue', subtitle }) {
  return (
    <article className={`cf-panel kpi-card kpi-${tone}`}>
      <header className="kpi-head">
        <span className="kpi-title">{title}</span>
        <span className="kpi-delta">{delta}</span>
      </header>
      <p className="kpi-value">{value}</p>
      {subtitle ? <p className="kpi-subtitle">{subtitle}</p> : null}
    </article>
  )
}

function StatusBadge({ value }) {
  const normalized = String(value || 'pendente').toLowerCase().trim()
  const cls = STATUS_COLOR[normalized] || 'status-pending'
  return <span className={`status-pill ${cls}`}>{normalized}</span>
}

function Dashboard() {
  const [period, setPeriod] = useState('30d')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [empresa, setEmpresa] = useState(null)
  const [analytics, setAnalytics] = useState(null)
  const [dashboardData, setDashboardData] = useState(null)
  const [atendimentos, setAtendimentos] = useState([])
  const [clientes, setClientes] = useState([])

  const rawApiUrl = import.meta.env.VITE_API_URL
  const apiBase = rawApiUrl
    ? rawApiUrl.replace(/\/$/, '').endsWith('/api')
      ? rawApiUrl.replace(/\/$/, '')
      : `${rawApiUrl.replace(/\/$/, '')}/api`
    : ''
  const token = localStorage.getItem('access_token')

  const authHeaders = useMemo(
    () => ({
      Authorization: `Bearer ${token}`
    }),
    [token]
  )

  const fetchData = useCallback(async () => {
    if (!apiBase) {
      setError('VITE_API_URL nao configurada')
      setLoading(false)
      return
    }

    try {
      setLoading(true)
      setError('')

      const [empresaResp, analyticsResp, dashboardResp, atendimentosResp, clientesResp] = await Promise.all([
        axios.get(`${apiBase}/empresas/me`, { headers: authHeaders }),
        axios.get(`${apiBase}/dashboard/analytics`, { params: { period }, headers: authHeaders }),
        axios.get(`${apiBase}/dashboard`, { params: { period }, headers: authHeaders }),
        axios.get(`${apiBase}/atendimentos`, { headers: authHeaders }),
        axios.get(`${apiBase}/clientes`, { headers: authHeaders })
      ])

      setEmpresa(empresaResp.data)
      setAnalytics(analyticsResp.data)
      setDashboardData(dashboardResp.data)
      setAtendimentos(Array.isArray(atendimentosResp.data) ? atendimentosResp.data : [])
      setClientes(Array.isArray(clientesResp.data) ? clientesResp.data : [])
    } catch (err) {
      setError(err.response?.data?.detail || 'Falha ao carregar dashboard')
    } finally {
      setLoading(false)
    }
  }, [apiBase, authHeaders, period])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    window.location.href = '/login'
  }

  const revenueMetric = analytics?.metrics?.revenue
  const clientsMetric = analytics?.metrics?.clients
  const appointmentsMetric = analytics?.metrics?.appointments

  const revenueSeries = analytics?.revenue_series || []
  const revenueChartData = useMemo(
    () => ({
      labels: revenueSeries.map((item) => safeDateShort(item.date)),
      datasets: [
        {
          data: revenueSeries.map((item) => Number(item.value) || 0),
          borderColor: '#35b9ff',
          borderWidth: 2.5,
          tension: 0.35,
          fill: true,
          backgroundColor: 'rgba(53, 185, 255, 0.12)',
          pointRadius: 1.8,
          pointHoverRadius: 4
        }
      ]
    }),
    [revenueSeries]
  )

  const revenueChartOptions = useMemo(
    () => ({
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#060d1f',
          borderColor: '#1f3a7a',
          borderWidth: 1,
          callbacks: {
            label: (item) => ` ${moneyBR(item.parsed.y)}`
          }
        }
      },
      scales: {
        x: { grid: { color: 'rgba(80, 116, 200, 0.12)' }, ticks: { color: '#9eb5df' } },
        y: { grid: { color: 'rgba(80, 116, 200, 0.12)' }, ticks: { color: '#9eb5df' } }
      }
    }),
    []
  )

  const statusBuckets = useMemo(() => {
    const base = { pendente: 0, 'em andamento': 0, concluido: 0, entregue: 0 }
    atendimentos.forEach((item) => {
      const key = String(item?.status_atendimento || 'pendente').toLowerCase().trim()
      if (base[key] === undefined) base[key] = 0
      base[key] += 1
    })
    return base
  }, [atendimentos])

  const statusChartData = useMemo(
    () => ({
      labels: ['Pendente', 'Em andamento', 'Concluido', 'Entregue'],
      datasets: [
        {
          data: [
            statusBuckets.pendente,
            statusBuckets['em andamento'],
            statusBuckets.concluido,
            statusBuckets.entregue
          ],
          borderWidth: 0,
          backgroundColor: ['#ff5b6d', '#ffc14d', '#33d890', '#39a3ff']
        }
      ]
    }),
    [statusBuckets]
  )

  const statusChartOptions = useMemo(
    () => ({
      responsive: true,
      maintainAspectRatio: false,
      cutout: '70%',
      plugins: { legend: { display: false } }
    }),
    []
  )

  const agenda = useMemo(() => {
    return [...atendimentos]
      .sort((a, b) => new Date(a.data_atendimento) - new Date(b.data_atendimento))
      .slice(0, 5)
  }, [atendimentos])

  const activeAppointment = useMemo(() => {
    return (
      atendimentos.find((item) => String(item.status_atendimento || '').toLowerCase().includes('andamento')) ||
      agenda[0]
    )
  }, [agenda, atendimentos])

  const clientesRecentes = useMemo(() => clientes.slice(0, 6), [clientes])
  const topClientes = dashboardData?.top_clientes || []

  const isOperational = !error

  return (
    <div className="cf-shell">
      <aside className="cf-sidebar">
        <div className="cf-brand">
          <span className="brand-logo">◈</span>
          <div>
            <h1>ClientFlow</h1>
            <p>SaaS Intelligence Platform</p>
          </div>
        </div>

        <nav>
          {SIDEBAR_MENU.map((item) => (
            <button key={item.label} type="button" className={`menu-item ${item.active ? 'active' : ''}`}>
              <span>{item.icon}</span>
              <span>{item.label}</span>
            </button>
          ))}
        </nav>

        <div className="sidebar-foot">
          <button type="button" className="menu-item">
            <span>◑</span>
            <span>Suporte</span>
          </button>
          <button type="button" className="menu-item">
            <span>◒</span>
            <span>Documentacao</span>
          </button>
        </div>
      </aside>

      <div className="cf-main">
        <header className="cf-topbar cf-panel">
          <div className="topbar-search">
            <input type="text" placeholder="Buscar clientes, atendimentos..." />
          </div>
          <div className="topbar-actions">
            <span className="plan-chip">
              Plano {String(empresa?.plano_empresa || 'pro').trim().toUpperCase()}
            </span>
            <button type="button" className="icon-btn" onClick={fetchData}>
              ↻
            </button>
            <button type="button" className="icon-btn" onClick={handleLogout}>
              ⎋
            </button>
          </div>
        </header>

        {error ? <div className="cf-error">{error}</div> : null}

        <section className="kpi-grid">
          <KpiCard
            title="Clientes ativos"
            value={numberBR(dashboardData?.estatisticas?.total_clientes_ativos)}
            delta={pctFormat(clientsMetric?.percentage)}
            tone="blue"
            subtitle={`${numberBR(clientes.length)} cadastrados`}
          />
          <KpiCard
            title="Atendimentos hoje"
            value={numberBR(appointmentsMetric?.current)}
            delta={pctFormat(appointmentsMetric?.percentage)}
            tone="amber"
            subtitle={`${numberBR(dashboardData?.estatisticas?.total_atendimentos)} no total`}
          />
          <KpiCard
            title="Faturamento"
            value={moneyBR(revenueMetric?.current)}
            delta={pctFormat(revenueMetric?.percentage)}
            tone="green"
            subtitle="Periodo selecionado"
          />
          <KpiCard
            title="Status do sistema"
            value={isOperational ? '100% operacional' : 'Instavel'}
            delta={isOperational ? 'Online' : 'Alerta'}
            tone={isOperational ? 'cyan' : 'amber'}
            subtitle={loading ? 'Sincronizando...' : 'Atualizado'}
          />
        </section>

        <section className="workspace-grid">
          <article className="cf-panel panel-lg">
            <header className="panel-header">
              <h2>Evolucao de atendimentos</h2>
              <div className="period-switch">
                {PERIOD_OPTIONS.map((item) => (
                  <button
                    key={item.key}
                    type="button"
                    className={period === item.key ? 'active' : ''}
                    onClick={() => setPeriod(item.key)}
                  >
                    {item.label}
                  </button>
                ))}
              </div>
            </header>
            <div className="chart-lg">
              <Line data={revenueChartData} options={revenueChartOptions} />
            </div>
          </article>

          <article className="cf-panel panel-md">
            <header className="panel-header">
              <h2>Agenda de hoje</h2>
              <button type="button" className="solid-btn">+ Novo</button>
            </header>
            <ul className="agenda-list">
              {agenda.length === 0 ? <li className="agenda-empty">Sem atendimentos no periodo.</li> : null}
              {agenda.map((item) => (
                <li key={item.id}>
                  <div>
                    <p>{safeDate(item.data_atendimento)} · {item.tipo_servico || 'Servico'}</p>
                    <small>{item.cliente_id ? `Cliente #${item.cliente_id}` : 'Cliente nao informado'}</small>
                  </div>
                  <StatusBadge value={item.status_atendimento} />
                </li>
              ))}
            </ul>
          </article>

          <article className="cf-panel panel-sm">
            <h2>Cliente em atendimento</h2>
            <div className="active-client">
              <strong>{activeAppointment?.tipo_servico || 'Sem atendimento ativo'}</strong>
              <p>Cliente #{activeAppointment?.cliente_id || '--'}</p>
              <p>Horario {safeDate(activeAppointment?.data_atendimento)}</p>
              <button type="button" className="solid-btn block">Finalizar atendimento</button>
            </div>
          </article>

          <article className="cf-panel panel-sm">
            <h2>Fluxo de vendas</h2>
            <ul className="funnel-list">
              <li><span>Leads</span><strong>{numberBR(clientes.length)}</strong></li>
              <li><span>Orcamentos</span><strong>{numberBR(statusBuckets.pendente + statusBuckets['em andamento'])}</strong></li>
              <li><span>Aprovados</span><strong>{numberBR(statusBuckets.concluido)}</strong></li>
              <li><span>Entregues</span><strong>{numberBR(statusBuckets.entregue)}</strong></li>
            </ul>
          </article>

          <article className="cf-panel panel-sm">
            <h2>Atendimentos por status</h2>
            <div className="chart-sm">
              <Doughnut data={statusChartData} options={statusChartOptions} />
            </div>
            <ul className="status-legend">
              {Object.entries(statusBuckets).map(([key, value]) => (
                <li key={key}><span>{key}</span><strong>{numberBR(value)}</strong></li>
              ))}
            </ul>
          </article>

          <article className="cf-panel panel-md">
            <header className="panel-header">
              <h2>Clientes recentes</h2>
              <button type="button" className="ghost-btn">Ver todos</button>
            </header>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Cliente</th>
                    <th>Contato</th>
                    <th>Status</th>
                    <th>Valor</th>
                  </tr>
                </thead>
                <tbody>
                  {clientesRecentes.map((item) => (
                    <tr key={item.id}>
                      <td>{item.nome}</td>
                      <td>{item.telefone || '-'}</td>
                      <td>
                        <StatusBadge value={item.status_cliente || 'novo'} />
                      </td>
                      <td>{moneyBR((item.score_atividade || 0) * 15)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </article>

          <article className="cf-panel panel-sm">
            <h2>Top clientes</h2>
            <ul className="top-client-list">
              {topClientes.length === 0 ? <li>Sem dados do periodo</li> : null}
              {topClientes.map((item) => (
                <li key={item.id}>
                  <span>{item.nome}</span>
                  <strong>{numberBR(item.total_atendimentos)}</strong>
                </li>
              ))}
            </ul>
          </article>
        </section>

        <footer className="cf-footer cf-panel">
          {BOTTOM_HEALTH.map((item) => (
            <div key={item.label}>
              <span>{item.label}</span>
              <strong>{item.value}</strong>
            </div>
          ))}
        </footer>
      </div>
    </div>
  )
}

export default Dashboard
