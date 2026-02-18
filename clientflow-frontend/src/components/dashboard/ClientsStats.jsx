import React from 'react'

const ClientsStats = ({ data = [], loading = false }) => {
  // Calcula estatísticas a partir dos clientes
  const calculateStats = (clients) => {
    if (!Array.isArray(clients) || clients.length === 0) {
      return defaultStats
    }

    const convidados = clients.length // Total de clientes
    const orcamentos = clients.filter(c => c.status === 'pendente').length // Aguardando
    const aprovados = clients.filter(c => c.status === 'em_andamento').length // Em andamento
    const concluidos = clients.filter(c => c.status === 'concluido' || c.status === 'entregue').length // Finalizados

    return [
      {
        id: 1,
        title: 'Clientes Convidados',
        value: convidados,
        icon: '📨',
      },
      {
        id: 2,
        title: 'Orçamentos Abertos',
        value: orcamentos,
        icon: '📋',
      },
      {
        id: 3,
        title: 'Aprovados',
        value: aprovados,
        icon: '✓',
      },
      {
        id: 4,
        title: 'Concluídos',
        value: concluidos,
        icon: '🎉',
      },
    ]
  }

  const defaultStats = [
    {
      id: 1,
      title: 'Clientes Convidados',
      value: 125,
      icon: '📨',
    },
    {
      id: 2,
      title: 'Orçamentos Abertos',
      value: 87,
      icon: '📋',
    },
    {
      id: 3,
      title: 'Aprovados',
      value: 54,
      icon: '✓',
    },
    {
      id: 4,
      title: 'Concluídos',
      value: 32,
      icon: '🎉',
    },
  ]

  const stats = calculateStats(data)

  if (loading) {
    return (
      <div className="card-base col-span-full animate-pulse">
        <div className="h-6 bg-primary-700 rounded-lg w-32 mb-6" />
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="bg-primary-700 rounded-xl h-24" />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="card-base col-span-full">
      <h3 className="text-xl font-bold text-white mb-6 tracking-tight">Fluxo de Vendas</h3>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, idx) => (
          <div
            key={stat.id}
            className="bg-primary-800/60 rounded-xl p-6 text-center transition-colors duration-200 group cursor-pointer border border-primary-700/60 hover:border-accent-blue/30 hover:bg-primary-800/80"
          >
            <p className="text-3xl mb-4">{stat.icon}</p>
            <p className="text-xs text-gray-400 font-semibold uppercase tracking-wide mb-3">{stat.title}</p>
            <p className="text-3xl font-bold text-white tracking-tight">{stat.value}</p>
          </div>
        ))}
      </div>
    </div>
  )
}

export default ClientsStats
