import { useState, useEffect, useContext, useCallback } from 'react'
import api from '../services/api'
import AuthContext from '../context/AuthContext'

const STATUS_COLOR = {
  novo: 'status-new',
  ativo: 'status-progress',
  inativo: 'status-pending',
  vip: 'status-done'
}

function StatusBadge({ value }) {
  const normalized = String(value || 'novo').toLowerCase().trim()
  const cls = STATUS_COLOR[normalized] || 'status-new'
  return <span className={`status-pill ${cls}`}>{normalized}</span>
}

export default function CRM() {
  const [clientes, setClientes] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({ nome: '', telefone: '', anotacoes_rapidas: '' })
  const [formError, setFormError] = useState('')
  const [saving, setSaving] = useState(false)
  const { token } = useContext(AuthContext)

  const fetchClientes = useCallback(async () => {
    try {
      setLoading(true)
      const resp = await api.get('/clientes')
      setClientes(Array.isArray(resp.data) ? resp.data : [])
      setError('')
    } catch (err) {
      if (err.response?.status !== 401) {
        setError(err.response?.data?.detail || 'Erro ao carregar clientes')
      }
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchClientes() }, [fetchClientes])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setFormError('')
    if (!formData.nome.trim() || !formData.telefone.trim()) {
      setFormError('Nome e telefone são obrigatórios')
      return
    }
    try {
      setSaving(true)
      await api.post('/clientes', formData)
      setFormData({ nome: '', telefone: '', anotacoes_rapidas: '' })
      setShowForm(false)
      fetchClientes()
    } catch (err) {
      setFormError(err.response?.data?.detail || 'Erro ao cadastrar cliente')
    } finally {
      setSaving(false)
    }
  }

  const filtered = clientes.filter(c =>
    c.nome.toLowerCase().includes(search.toLowerCase()) ||
    (c.telefone || '').includes(search)
  )

  return (
    <>
      <header className="cf-topbar cf-panel">
        <div className="topbar-search">
          <input
            type="text"
            placeholder="Buscar clientes por nome ou telefone..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="topbar-actions">
          <button type="button" className="solid-btn" onClick={() => setShowForm(!showForm)}>
            {showForm ? 'Cancelar' : '+ Novo Cliente'}
          </button>
          <button type="button" className="icon-btn" onClick={fetchClientes}>R</button>
        </div>
      </header>

      {error && <div className="cf-error">{error}</div>}

      {showForm && (
        <section className="workspace-grid">
          <article className="cf-panel panel-lg" style={{ gridColumn: '1 / -1' }}>
            <header className="panel-header"><h2>Cadastrar Novo Cliente</h2></header>
            {formError && <div className="cf-error" style={{ marginBottom: '1rem' }}>{formError}</div>}
            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div>
                  <label style={{ display: 'block', color: '#9eb5df', marginBottom: '0.5rem', fontSize: '0.875rem' }}>Nome *</label>
                  <input
                    type="text"
                    value={formData.nome}
                    onChange={(e) => setFormData({ ...formData, nome: e.target.value })}
                    placeholder="Nome do cliente"
                    style={{ width: '100%', padding: '0.75rem', borderRadius: '0.5rem', border: '1px solid #1f3a7a', background: '#0a1628', color: '#e0e8f5' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', color: '#9eb5df', marginBottom: '0.5rem', fontSize: '0.875rem' }}>Telefone *</label>
                  <input
                    type="text"
                    value={formData.telefone}
                    onChange={(e) => setFormData({ ...formData, telefone: e.target.value })}
                    placeholder="(11) 99999-9999"
                    style={{ width: '100%', padding: '0.75rem', borderRadius: '0.5rem', border: '1px solid #1f3a7a', background: '#0a1628', color: '#e0e8f5' }}
                  />
                </div>
              </div>
              <div>
                <label style={{ display: 'block', color: '#9eb5df', marginBottom: '0.5rem', fontSize: '0.875rem' }}>Anotações</label>
                <textarea
                  value={formData.anotacoes_rapidas}
                  onChange={(e) => setFormData({ ...formData, anotacoes_rapidas: e.target.value })}
                  placeholder="Observações sobre o cliente..."
                  rows={3}
                  style={{ width: '100%', padding: '0.75rem', borderRadius: '0.5rem', border: '1px solid #1f3a7a', background: '#0a1628', color: '#e0e8f5', resize: 'vertical' }}
                />
              </div>
              <div>
                <button type="submit" className="solid-btn" disabled={saving}>
                  {saving ? 'Salvando...' : 'Cadastrar Cliente'}
                </button>
              </div>
            </form>
          </article>
        </section>
      )}

      <section className="workspace-grid">
        <article className="cf-panel panel-lg" style={{ gridColumn: '1 / -1' }}>
          <header className="panel-header">
            <h2>Clientes ({filtered.length})</h2>
          </header>
          {loading ? (
            <p style={{ color: '#9eb5df', padding: '2rem', textAlign: 'center' }}>Carregando...</p>
          ) : filtered.length === 0 ? (
            <p style={{ color: '#9eb5df', padding: '2rem', textAlign: 'center' }}>
              {search ? 'Nenhum cliente encontrado.' : 'Nenhum cliente cadastrado. Clique em "+ Novo Cliente" para começar.'}
            </p>
          ) : (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Nome</th>
                    <th>Telefone</th>
                    <th>Status</th>
                    <th>Desde</th>
                    <th>Anotações</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((c) => (
                    <tr key={c.id}>
                      <td>{c.nome}</td>
                      <td>{c.telefone || '-'}</td>
                      <td><StatusBadge value={c.status_cliente} /></td>
                      <td>{c.data_primeiro_contato ? new Date(c.data_primeiro_contato).toLocaleDateString('pt-BR') : '-'}</td>
                      <td style={{ maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {c.anotacoes_rapidas || '-'}
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
