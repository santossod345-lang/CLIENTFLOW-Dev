import { useState, useEffect } from 'react'
import api from '../services/api'

export default function Relatorios() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/dashboard')
      .then(r => setStats(r.data))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  return (
    <>
      <header className="cf-topbar cf-panel">
        <div className="topbar-search">
          <input type="text" placeholder="Buscar relatórios..." />
        </div>
        <div className="topbar-actions">
          <span className="plan-chip">Relatórios</span>
        </div>
      </header>
      <section className="workspace-grid">
        <article className="cf-panel panel-lg" style={{ gridColumn: '1 / -1' }}>
          <header className="panel-header"><h2>Resumo Geral</h2></header>
          {loading ? (
            <p style={{ color: '#9eb5df', padding: '2rem', textAlign: 'center' }}>Carregando...</p>
          ) : stats ? (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem', padding: '1.5rem' }}>
              <div style={{ textAlign: 'center' }}>
                <p style={{ color: '#9eb5df', fontSize: '0.875rem' }}>Total de Clientes</p>
                <p style={{ color: '#e0e8f5', fontSize: '2rem', fontWeight: 'bold' }}>{stats.estatisticas?.total_clientes || 0}</p>
              </div>
              <div style={{ textAlign: 'center' }}>
                <p style={{ color: '#9eb5df', fontSize: '0.875rem' }}>Clientes Ativos</p>
                <p style={{ color: '#e0e8f5', fontSize: '2rem', fontWeight: 'bold' }}>{stats.estatisticas?.total_clientes_ativos || 0}</p>
              </div>
              <div style={{ textAlign: 'center' }}>
                <p style={{ color: '#9eb5df', fontSize: '0.875rem' }}>Total Atendimentos</p>
                <p style={{ color: '#e0e8f5', fontSize: '2rem', fontWeight: 'bold' }}>{stats.estatisticas?.total_atendimentos || 0}</p>
              </div>
            </div>
          ) : (
            <p style={{ color: '#9eb5df', padding: '2rem', textAlign: 'center' }}>Sem dados disponíveis.</p>
          )}
        </article>
        {stats?.top_clientes?.length > 0 && (
          <article className="cf-panel panel-lg" style={{ gridColumn: '1 / -1' }}>
            <header className="panel-header"><h2>Top Clientes</h2></header>
            <div className="table-wrap">
              <table>
                <thead><tr><th>Cliente</th><th>Atendimentos</th></tr></thead>
                <tbody>
                  {stats.top_clientes.map(c => (
                    <tr key={c.id}><td>{c.nome}</td><td>{c.total_atendimentos}</td></tr>
                  ))}
                </tbody>
              </table>
            </div>
          </article>
        )}
      </section>
    </>
  )
}
