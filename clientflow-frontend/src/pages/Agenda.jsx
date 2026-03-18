import { useState, useEffect, useMemo } from 'react'
import api from '../services/api'

const STATUS_COLOR = {
  novo: 'status-new',
  pendente: 'status-pending',
  'em andamento': 'status-progress',
  concluido: 'status-done',
  entregue: 'status-delivered'
}

function StatusBadge({ value }) {
  const normalized = String(value || 'novo').toLowerCase().trim()
  const cls = STATUS_COLOR[normalized] || 'status-new'
  return <span className={`status-pill ${cls}`}>{normalized}</span>
}

export default function Agenda() {
  const [atendimentos, setAtendimentos] = useState([])
  const [clientes, setClientes] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      api.get('/atendimentos'),
      api.get('/clientes')
    ]).then(([aR, cR]) => {
      setAtendimentos(Array.isArray(aR.data) ? aR.data : [])
      setClientes(Array.isArray(cR.data) ? cR.data : [])
    }).catch(() => {}).finally(() => setLoading(false))
  }, [])

  const getClienteName = (id) => {
    const c = clientes.find(cl => cl.id === id)
    return c ? c.nome : `Cliente #${id}`
  }

  const hoje = new Date().toISOString().slice(0, 10)
  const agendaHoje = useMemo(() =>
    atendimentos.filter(a => (a.data_atendimento || '').slice(0, 10) === hoje)
      .sort((a, b) => new Date(a.data_atendimento) - new Date(b.data_atendimento)),
    [atendimentos, hoje]
  )
  const proximos = useMemo(() =>
    atendimentos.filter(a => (a.data_atendimento || '').slice(0, 10) > hoje)
      .sort((a, b) => new Date(a.data_atendimento) - new Date(b.data_atendimento))
      .slice(0, 10),
    [atendimentos, hoje]
  )

  return (
    <>
      <header className="cf-topbar cf-panel">
        <div className="topbar-search">
          <input type="text" placeholder="Buscar na agenda..." />
        </div>
        <div className="topbar-actions">
          <span className="plan-chip">Agenda</span>
        </div>
      </header>
      <section className="workspace-grid">
        <article className="cf-panel panel-lg" style={{ gridColumn: '1 / -1' }}>
          <header className="panel-header"><h2>Agenda de Hoje ({agendaHoje.length})</h2></header>
          {loading ? (
            <p style={{ color: '#9eb5df', padding: '2rem', textAlign: 'center' }}>Carregando...</p>
          ) : agendaHoje.length === 0 ? (
            <p style={{ color: '#9eb5df', padding: '2rem', textAlign: 'center' }}>Nenhum atendimento agendado para hoje.</p>
          ) : (
            <ul className="agenda-list">
              {agendaHoje.map(a => (
                <li key={a.id}>
                  <div>
                    <p>{new Date(a.data_atendimento).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })} - {a.tipo_servico}</p>
                    <small>{getClienteName(a.cliente_id)}</small>
                  </div>
                  <StatusBadge value={a.status_atendimento} />
                </li>
              ))}
            </ul>
          )}
        </article>
        {proximos.length > 0 && (
          <article className="cf-panel panel-lg" style={{ gridColumn: '1 / -1' }}>
            <header className="panel-header"><h2>Próximos Atendimentos</h2></header>
            <ul className="agenda-list">
              {proximos.map(a => (
                <li key={a.id}>
                  <div>
                    <p>{new Date(a.data_atendimento).toLocaleDateString('pt-BR')} - {a.tipo_servico}</p>
                    <small>{getClienteName(a.cliente_id)}</small>
                  </div>
                  <StatusBadge value={a.status_atendimento} />
                </li>
              ))}
            </ul>
          </article>
        )}
      </section>
    </>
  )
}
