import React from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'

const RevenueChart = ({ data = [], loading = false }) => {
  const chartData = Array.isArray(data) ? data : []

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="glass-effect rounded-xl p-3 shadow-md shadow-black/30">
          <p className="text-sm font-bold text-white">
            R$ {(payload[0].value / 1000).toFixed(1)}k
          </p>
        </div>
      )
    }
    return null
  }

  if (loading) {
    return (
      <div className="card-base col-span-full lg:col-span-2">
        <div className="mb-6">
          <div className="skeleton skeleton-title w-32 mb-2" />
          <div className="skeleton skeleton-line w-24" />
        </div>
        <div className="skeleton skeleton-chart" />
      </div>
    )
  }

  if (chartData.length === 0) {
    return (
      <div className="card-base col-span-full lg:col-span-2 fade-in">
        <div className="mb-6">
          <h3 className="text-xl font-bold text-white mb-1 tracking-tight">Evolução de Faturamento</h3>
          <p className="text-sm text-gray-500 font-medium">Sem dados de faturamento ainda.</p>
        </div>
        <div className="h-72 rounded-xl border border-primary-700/60 bg-primary-800/40 flex items-center justify-center text-gray-400">
          Sem dados de faturamento ainda.
        </div>
      </div>
    )
  }

  return (
    <div className="card-base col-span-full lg:col-span-2 fade-in">
      <div className="mb-6">
        <h3 className="text-xl font-bold text-white mb-1 tracking-tight">Evolução de Faturamento</h3>
        <p className="text-sm text-gray-500 font-medium">Últimos 9 meses com crescimento consistente</p>
      </div>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
          <defs>
            <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4} />
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.05} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(59, 130, 246, 0.1)" />
          <XAxis dataKey="month" stroke="#64748b" style={{ fontSize: '12px' }} />
          <YAxis stroke="#64748b" style={{ fontSize: '12px' }} />
          <Tooltip content={<CustomTooltip />} />
          <Line
            type="monotone"
            dataKey="revenue"
            stroke="url(#colorRevenue)"
            dot={{ fill: '#3b82f6', r: 4 }}
            activeDot={{ r: 7, fill: '#a855f7' }}
            strokeWidth={3}
            fillOpacity={1}
            fill="url(#colorRevenue)"
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

export default RevenueChart
