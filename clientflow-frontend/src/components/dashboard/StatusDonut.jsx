import React from 'react'
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'

const StatusDonut = ({ data = [], loading = false }) => {
  // Dados padrão se API não retornar nada
  const defaultData = [
    { name: 'Concluído', value: 142, color: '#10b981' },
    { name: 'Em Andamento', value: 62, color: '#3b82f6' },
    { name: 'Pendente', value: 96, color: '#f97316' },
    { name: 'Entregue', value: 20, color: '#06b6d4' },
  ]

  const chartData = Array.isArray(data) && data.length > 0 ? data : defaultData

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="glass-effect rounded-xl p-3 shadow-md shadow-black/30">
          <p className="text-sm font-bold text-white">{payload[0].name}</p>
          <p className="text-sm text-gray-300 font-semibold">{payload[0].value} atendimentos</p>
        </div>
      )
    }
    return null
  }

  if (loading) {
    return (
      <div className="card-base">
        <div className="skeleton skeleton-title w-40 mb-6" />
        <div className="skeleton" style={{ height: '224px' }} />
        <div className="space-y-3 mt-4">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="skeleton skeleton-line w-full" />
          ))}
        </div>
      </div>
    )
  }

  const total = chartData.reduce((sum, item) => sum + item.value, 0)

  return (
    <div className="card-base">
      <h3 className="text-xl font-bold text-white mb-6 tracking-tight">Status dos Atendimentos</h3>
      <ResponsiveContainer width="100%" height={250}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={70}
            outerRadius={100}
            paddingAngle={5}
            dataKey="value"
            isAnimationActive={false}
          >
            {chartData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={entry.color}
                opacity={0.9}
              />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
        </PieChart>
      </ResponsiveContainer>
      <div className="mt-8 space-y-3">
        {chartData.map((item, idx) => (
          <div 
            key={item.name} 
            className="flex items-center justify-between p-3 rounded-lg transition-colors duration-200 hover:bg-primary-800/60 group cursor-pointer"
          >
            <div className="flex items-center gap-3">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: item.color }}
              ></div>
              <span className="text-gray-400 font-medium group-hover:text-white transition-colors duration-200">{item.name}</span>
            </div>
            <div>
              <span className="font-bold text-white">
                {item.value}
              </span>
              <span className="text-gray-600 font-medium ml-2 transition-colors duration-200">
                ({((item.value / total) * 100).toFixed(0)}%)
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default StatusDonut
