import React from 'react'

const ClientsTable = ({ data = [], loading = false }) => {
  const clients = Array.isArray(data) ? data : []

  const getStatusBadge = (status) => {
    const statusMap = {
      em_andamento: { bg: 'bg-accent-blue/20', text: 'text-accent-blue', label: 'Em Andamento' },
      pendente: { bg: 'bg-accent-orange/20', text: 'text-accent-orange', label: 'Pendente' },
      concluido: { bg: 'bg-accent-green/20', text: 'text-accent-green', label: 'Concluído' },
      entregue: { bg: 'bg-accent-cyan/20', text: 'text-accent-cyan', label: 'Entregue' },
    }
    return statusMap[status] || statusMap.pendente
  }

  if (loading) {
    return (
      <div className="card-base col-span-full">
        <div className="skeleton skeleton-title w-48 mb-6" />
        <div className="space-y-3">
          {[1, 2, 3, 4, 5].map(i => (
            <div key={i} className="skeleton skeleton-block" />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="card-base col-span-full fade-in">
      <h3 className="text-xl font-bold text-white mb-6 tracking-tight">Clientes Recentes</h3>
      {clients.length > 0 ? (
        <div className="overflow-x-auto rounded-xl">
          <table className="w-full">
            <thead>
              <tr className="border-b border-primary-700/60 bg-primary-800/40">
                <th className="text-left py-4 px-4 text-xs font-semibold text-gray-300 uppercase tracking-wider">
                  Cliente
                </th>
                <th className="text-left py-4 px-4 text-xs font-semibold text-gray-300 uppercase tracking-wider">
                  Contato
                </th>
                <th className="text-left py-4 px-4 text-xs font-semibold text-gray-300 uppercase tracking-wider">
                  Serviço
                </th>
                <th className="text-left py-4 px-4 text-xs font-semibold text-gray-300 uppercase tracking-wider">
                  Status
                </th>
                <th className="text-right py-4 px-4 text-xs font-semibold text-gray-300 uppercase tracking-wider">
                  Valor
                </th>
              </tr>
            </thead>
            <tbody>
              {clients.map((client) => {
                const badge = getStatusBadge(client.status)
                return (
                  <tr
                    key={client.id}
                    className="border-b border-primary-700/50 hover:bg-primary-800/50 transition-colors duration-200 group cursor-pointer"
                  >
                    <td className="py-4 px-4">
                      <p className="text-sm font-semibold text-white">
                        {client.nome_empresa || client.name}
                      </p>
                    </td>
                    <td className="py-4 px-4">
                      <p className="text-sm text-gray-400 transition-colors duration-200 font-medium">
                        {client.telefone || client.contact}
                      </p>
                    </td>
                    <td className="py-4 px-4">
                      <p className="text-sm text-gray-400 transition-colors duration-200 font-medium">
                        {client.servico || client.service}
                      </p>
                    </td>
                    <td className="py-4 px-4">
                      <span className={`text-xs font-semibold px-3 py-1 rounded-full border border-primary-700/60 ${badge.bg} ${badge.text}`}>
                        {badge.label}
                      </span>
                    </td>
                    <td className="py-4 px-4 text-right">
                      <p className="text-sm font-bold text-accent-green transition-colors duration-200">
                        R$ {(client.valor || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                      </p>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="py-8 text-center text-gray-400 font-medium">
          Você ainda não possui clientes cadastrados.
        </div>
      )}
      {clients.length > 0 && (
        <button className="w-full mt-6 py-2 text-sm font-bold text-accent-blue hover:text-accent-purple transition-colors duration-200 flex items-center justify-center gap-1">
          Ver todos os clientes
          <span>→</span>
        </button>
      )}
    </div>
  )
}

export default ClientsTable
