import React, { useState, useEffect } from 'react'
import StatCard from '../components/dashboard/StatCard'
import RevenueChart from '../components/dashboard/RevenueChart'
import StatusDonut from '../components/dashboard/StatusDonut'
import AppointmentsList from '../components/dashboard/AppointmentsList'
import ClientsTable from '../components/dashboard/ClientsTable'
import ClientsStats from '../components/dashboard/ClientsStats'
import { clientsService, appointmentsService, dashboardService } from '../services/api'

const Dashboard = () => {
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({
    clientsCount: 0,
    appointmentsToday: 0,
    monthlyRevenue: 0,
    retentionRate: 0,
  })
  const [revenue, setRevenue] = useState([])
  const [appointmentsStatus, setAppointmentsStatus] = useState([])
  const [appointments, setAppointments] = useState([])
  const [clients, setClients] = useState([])
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true)
      try {
        // Buscar clientes
        const clientsRes = await clientsService.list()
        const clientsList = clientsRes.data?.data || clientsRes.data || []
        setClients(clientsList)

        // Buscar atendimentos
        const appointmentsRes = await appointmentsService.list()
        const appointmentsList = appointmentsRes.data?.data || appointmentsRes.data || []
        setAppointments(appointmentsList)

        // Buscar métricas do dashboard
        try {
          const metricsRes = await dashboardService.getMetrics()
          if (metricsRes.data) {
            setStats(metricsRes.data)
          }
        } catch (err) {
          console.warn('Endpoint /dashboard/metrics não disponível, usando cálculos locais')
          // Calcular métricas localmente
          const todayCount = appointmentsList.filter(apt => {
            const aptDate = new Date(apt.data).toDateString()
            return aptDate === new Date().toDateString()
          }).length

          setStats({
            clientsCount: clientsList.length,
            appointmentsToday: todayCount,
            monthlyRevenue: clientsList.reduce((sum, c) => sum + (c.valor || 0), 0),
            retentionRate: 94.2,
          })
        }

        // Buscar dados de receita
        try {
          const revenueRes = await dashboardService.getRevenue()
          if (Array.isArray(revenueRes.data)) {
            setRevenue(revenueRes.data)
          }
        } catch (err) {
          console.warn('Endpoint /dashboard/revenue não disponível')
        }

        // Buscar status dos atendimentos
        try {
          const statusRes = await dashboardService.getAppointmentsStatus()
          if (statusRes.data) {
            setAppointmentsStatus(statusRes.data)
          }
        } catch (err) {
          console.warn('Endpoint /dashboard/appointments-status não disponível')
        }

        setError(null)
      } catch (error) {
        console.error('Erro ao carregar dashboard:', error)
        setError('Erro ao carregar dados do dashboard')
      } finally {
        setLoading(false)
      }
    }

    fetchDashboardData()
  }, [])

  return (
    <div className="p-6 lg:p-10 bg-primary-900">
      {/* Header */}
      <div className="mb-10">
        <h1 className="text-3xl font-bold text-white mb-2 tracking-tight">Dashboard</h1>
        <p className="text-gray-400">Bem-vindo ao seu painel de controle</p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-6 p-4 bg-red-500/20 text-red-300 rounded-lg border border-red-500/50">
          ⚠️ {error}
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="mb-8 p-6 bg-primary-800 rounded-lg text-center">
          <p className="text-gray-400">Carregando dados do dashboard...</p>
        </div>
      )}

      {/* Main Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
        <StatCard
          icon="👥"
          title="Clientes Ativos"
          value={stats.clientsCount.toString()}
          change="12"
          changeType="positive"
          loading={loading}
        />
        <StatCard
          icon="🛠️"
          title="Atendimentos Hoje"
          value={stats.appointmentsToday.toString()}
          change="18"
          changeType="positive"
          loading={loading}
        />
        <StatCard
          icon="💰"
          title="Faturamento (Mês)"
          value={`R$ ${(stats.monthlyRevenue || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`}
          change="24"
          changeType="positive"
          loading={loading}
        />
        <StatCard
          icon="📈"
          title="Taxa de Retenção"
          value={`${stats.retentionRate || 0}%`}
          change="8"
          changeType="positive"
          loading={loading}
        />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-10">
        <RevenueChart data={revenue} loading={loading} />
        <StatusDonut data={appointmentsStatus} loading={loading} />
      </div>

      {/* Flow Stats */}
      <div className="mb-10">
        <ClientsStats data={clients} loading={loading} />
      </div>

      {/* Appointments & Table Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-10">
        <AppointmentsList data={appointments} loading={loading} />
      </div>

      {/* Clients Table */}
      <div className="mb-10">
        <ClientsTable data={clients} loading={loading} />
      </div>
    </div>
  )
}

export default Dashboard
