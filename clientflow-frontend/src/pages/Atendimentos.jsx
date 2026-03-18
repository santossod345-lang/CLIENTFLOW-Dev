import { useState, useEffect, useCallback } from 'react'
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

export default function Atendimentos() {
  const [atendimentos, setAtendimentos] = useState([])
  const [clientes, setClientes] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({ cliente_id: '', tipo_servico: '', descricao_servico: '' })
  const [formError, setFormError] = useState('')
  const [saving, setSaving] = useState(false)

  const fetchData = useCallback(async () => {
    try {
      setLoading(true)
      const [atResp, clResp] = await Promise.all([
        api.get('/atendimentos'),
        api.get('/clientes')
      ])
      setAtendimentos(Array.isArray(atResp.data) ? atResp.data : [])
      setClientes(Array.isArray(clResp.data) ? clResp.data : [])
      setError('')
    } catch (err) {
      if (err.response?.status !== 401) {
        setError(err.response?.data?.detail || 'Erro ao carregar atendimentos')
      }
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchData() }, [fetchData])

  const getClienteName = (clienteId) => {
    const c = clientes.find(cl => cl.id === clienteId)
    return c ? c.nome : `Cliente #${clienteId}`
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setFormError('')
    if (!formData.cliente_id || !formData.tipo_servico.trim()) {
      setFormError('Cliente e tipo de serviço são obrigatórios')
      return
    }
    try {
      setSaving(true)
      await api.post('/atendimentos', {
        cliente_id: parseInt(formData.cliente_id, 10),
        tipo_servico: formData.tipo_servico,
        descricao_servico: formData.descricao_servico
      })
      setFormData({ cliente_id: '', tipo_servico: '', descricao_servico: '' })
      setShowForm(false)
      fetchData()
    } catch (err) {
      setFormError(err.response?.data?.detail || 'Erro ao criar atendimento')
    } finally {
      setSaving(false)
    }
  }

  const filtered = atendimentos.filter(a =>
    (a.tipo_servico || '').toLowerCase().includes(search.toLowerCase()) ||
    getClienteName(a.cliente_id).toLowerCase().includes(search.toLowerCase())
  )

  return (
    <>
      <header className="cf-topbar cf-panel">
        <div className="topbar-search">
          <input
            type="text"
            placeholder="Buscar atendimentos..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="topbar-actions">
          <button type="button" className="solid-btn" onClick={() => setShowForm(!showForm)}>
            {showForm ? 'Cancelar' : '+ Novo Atendimento'}
          </button>
          <button type="button" className="icon-btn" onClick={fetchData}>R</button>
        </div>
      </header>

      {error && <div className="cf-error">{error}</div>}

      {showForm && (
        <section className="workspace-grid">
          <article className="cf-panel panel-lg" style={{ gridColumn: '1 / -1' }}>
            <header className="panel-header"><h2>Novo Atendimento</h2></header>
            {formError && <div className="cf-error" style={{ marginBottom: '1rem' }}>{formError}</div>}
            {clientes.length === 0 ? (
              <p style={{ color: '#ff5b6d', padding: '1rem' }}>
                Nenhum cliente cadastrado. Cadastre um cliente no CRM primeiro.
              </p>
            ) : (
              <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                  <div>
                    <label style={{ display: 'block', color: '#9eb5df', marginBottom: '0.5rem', fontSize: '0.875rem' }}>Cliente *</label>
                    <select
                      value={formData.cliente_id}
                      onChange={(e) => setFormData({ ...formData, cliente_id: e.target.value })}
                      style={{ width: '100%', padding: '0.75rem', borderRadius: '0.5rem', border: '1px solid #1f3a7a', background: '#0a1628', color: '#e0e8f5' }}
                    >
                      <option value="">Selecione um cliente...</option>
                      {clientes.map(c => (
                        <option key={c.id} value={c.id}>{c.nome} - {c.telefone}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label style={{ display: 'block', color: '#9eb5df', marginBottom: '0.5rem', fontSize: '0.875rem' }}>Tipo de Serviço *</label>
                    <input
                      type="text"
                      value={formData.tipo_servico}
                      onChange={(e) => setFormData({ ...formData, tipo_servico: e.target.value })}
                      placeholder="Ex: Troca de óleo, Revisão..."
                      style={{ width: '100%', padding: '0.75rem', borderRadius: '0.5rem', border: '1px solid #1f3a7a', background: '#0a1628', color: '#e0e8f5' }}
                    />
                  </div>
                </div>
                <div>
                  <label style={{ display: 'block', color: '#9eb5df', marginBottom: '0.5rem', fontSize: '0.875rem' }}>Descrição</label>
                  <textarea
                    value={formData.descricao_servico}
                    onChange={(e) => setFormData({ ...formData, descricao_servico: e.target.value })}
                    placeholder="Detalhes do serviço..."
                    rows={3}
                    style={{ width: '100%', padding: '0.75rem', borderRadius: '0.5rem', border: '1px solid #1f3a7a', background: '#0a1628', color: '#e0e8f5', resize: 'vertical' }}
                  />
                </div>
                <div>
                  <button type="submit" className="solid-btn" disabled={saving}>
                    {saving ? 'Salvando...' : 'Criar Atendimento'}
                  </button>
                </div>
              </form>
            )}
          </article>
        </section>
      )}

      <section className="workspace-grid">
        <article className="cf-panel panel-lg" style={{ gridColumn: '1 / -1' }}>
          <header className="panel-header">
            <h2>Atendimentos ({filtered.length})</h2>
          </header>
          {loading ? (
            <p style={{ color: '#9eb5df', padding: '2rem', textAlign: 'center' }}>Carregando...</p>
          ) : filtered.length === 0 ? (
            <p style={{ color: '#9eb5df', padding: '2rem', textAlign: 'center' }}>
              {search ? 'Nenhum atendimento encontrado.' : 'Nenhum atendimento registrado. Clique em "+ Novo Atendimento" para começar.'}
            </p>
          ) : (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Cliente</th>
                    <th>Serviço</th>
                    <th>Status</th>
                    <th>Data</th>
                    <th>Descrição</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((a) => (
                    <tr key={a.id}>
                      <td>{getClienteName(a.cliente_id)}</td>
                      <td>{a.tipo_servico}</td>
                      <td><StatusBadge value={a.status_atendimento} /></td>
                      <td>{a.data_atendimento ? new Date(a.data_atendimento).toLocaleDateString('pt-BR') : '-'}</td>
                      <td style={{ maxWidth: '250px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {a.descricao_servico || '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </article>
      </section>
    </>
  )
}
