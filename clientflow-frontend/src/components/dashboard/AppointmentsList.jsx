import React from 'react'

const AppointmentsList = ({ data = [], loading = false }) => {
  const appointments = Array.isArray(data) ? data : []

  const getStatusBadge = (status) => {
    const statusMap = {
      confirmado: { bg: 'bg-accent-green/20', text: 'text-accent-green', label: '✓ Confirmado' },
      pendente: { bg: 'bg-accent-orange/20', text: 'text-accent-orange', label: '! Pendente' },
      em_andamento: { bg: 'bg-accent-blue/20', text: 'text-accent-blue', label: '→ Em Andamento' },
    }
    return statusMap[status] || statusMap.pendente
  }

  if (loading) {
    return (
      <div className="card-base">
        <div className="skeleton skeleton-title w-40 mb-2" />
        <div className="skeleton skeleton-line w-32 mb-6" />
        <div className="space-y-3 max-h-80">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="skeleton skeleton-block" />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="card-base fade-in">
      <h3 className="text-xl font-bold text-white mb-1 tracking-tight">Agenda de Hoje</h3>
      <p className="text-sm text-gray-500 font-medium mb-6">Próximos atendimentos confirmados</p>

      <div className="space-y-2 max-h-80 overflow-y-auto pr-2">
        {appointments.length > 0 ? (
          appointments.map((apt, idx) => {
            const badge = getStatusBadge(apt.status)
            return (
              <div
                key={apt.id}
                className="flex items-start gap-4 p-4 rounded-xl transition-colors duration-200 group cursor-pointer hover:bg-primary-800/60"
              >
                <div className="text-center min-w-fit">
                  <p className="text-lg font-bold text-accent-blue transition-colors duration-200">{apt.time}</p>
                  <p className="text-xs text-gray-500 font-medium">Horário</p>
                </div>

                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-white truncate">{apt.client}</p>
                  <p className="text-xs text-gray-400 transition-colors duration-200">{apt.contact}</p>
                  <p className="text-xs text-gray-500 transition-colors duration-200 mt-1">{apt.service}</p>
                </div>

                <div className={`px-3 py-1 rounded-full text-xs font-semibold whitespace-nowrap border border-primary-700/60 ${badge.bg} ${badge.text}`}>
                  {badge.label}
                </div>
              </div>
            )
          })
        ) : (
          <p className="text-center text-gray-400 py-6 font-medium">Nenhum atendimento agendado para hoje.</p>
        )}
      </div>

      {appointments.length > 0 && (
        <button className="w-full mt-6 py-2 text-sm font-bold text-accent-blue hover:text-accent-purple transition-colors duration-200 flex items-center justify-center gap-1">
          Ver agenda completa
          <span>→</span>
        </button>
      )}
    </div>
  )
}

export default AppointmentsList
