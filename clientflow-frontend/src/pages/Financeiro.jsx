import { useState, useEffect } from 'react'
import api from '../services/api'

const moneyBR = (v) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(Number(v) || 0)

export default function Financeiro() {
  const [atendimentos, setAtendimentos] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/atendimentos')
      .then(r => setAtendimentos(Array.isArray(r.data) ? r.data : []))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const total = atendimentos.reduce((s, a) => s + (parseFloat(a.valor_cobrado) || 0), 0)
  const concluidos = atendimentos.filter(a => String(a.status_atendimento || '').toLowerCase() === 'concluido')
  const pendentes = atendimentos.filter(a => String(a.status_atendimento || '').toLowerCase() === 'pendente')

  return (
    <>
      <header className="cf-topbar cf-panel">
        <div className="topbar-search">
          <input type="text" placeholder="Buscar transações..." />
        </div>
        <div className="topbar-actions">
          <span className="plan-chip">Financeiro</span>
        </div>
      </header>
      <section className="kpi-grid">
        <article className="cf-panel kpi-card kpi-green">
          <header className="kpi-head"><span className="kpi-title">Faturamento Total</span></header>
          <p className="kpi-value">{moneyBR(total)}</p>
          <p className="kpi-subtitle">{atendimentos.length} atendimentos</p>
        </article>
        <article className="cf-panel kpi-card kpi-blue">
          <header className="kpi-head"><span className="kpi-title">Concluídos</span></header>
          <p className="kpi-value">{concluidos.length}</p>
          <p className="kpi-subtitle">atendimentos finalizados</p>
        </article>
        <article className="cf-panel kpi-card kpi-amber">
          <header className="kpi-head"><span className="kpi-title">Pendentes</span></header>
          <p className="kpi-value">{pendentes.length}</p>
          <p className="kpi-subtitle">aguardando conclusão</p>
        </article>
      </section>
      <section className="workspace-grid">
        <article className="cf-panel panel-lg" style={{ gridColumn: '1 / -1' }}>
          <header className="panel-header">
            <h2>Resumo Financeiro</h2>
          </header>
          {loading ? (
            <p style={{ color: '#9eb5df', padding: '2rem', textAlign: 'center' }}>Carregando...</p>
          ) : atendimentos.length === 0 ? (
            <p style={{ color: '#9eb5df', padding: '2rem', textAlign: 'center' }}>Nenhum atendimento registrado ainda.</p>
          ) : (
            <p style={{ color: '#a8c1e7', padding: '1rem' }}>Dados sendo calculados com base nos {atendimentos.length} atendimentos registrados.</p>
          )}
        </article>
      </section>
    </>
  )
}
