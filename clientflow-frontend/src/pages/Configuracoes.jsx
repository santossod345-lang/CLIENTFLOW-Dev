import { useState, useEffect, useContext } from 'react'
import api from '../services/api'
import AuthContext from '../context/AuthContext'

export default function Configuracoes() {
  const [empresa, setEmpresa] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const { logout } = useContext(AuthContext)

  useEffect(() => {
    api.get('/empresas/me')
      .then(resp => { setEmpresa(resp.data); setError('') })
      .catch(err => {
        if (err.response?.status !== 401) {
          setError(err.response?.data?.detail || 'Erro ao carregar dados')
        }
      })
      .finally(() => setLoading(false))
  }, [])

  const fieldStyle = {
    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
    padding: '1rem 0', borderBottom: '1px solid rgba(31,58,122,0.3)'
  }
  const labelStyle = { color: '#9eb5df', fontSize: '0.875rem' }
  const valueStyle = { color: '#e0e8f5', fontWeight: '500' }

  return (
    <>
      <header className="cf-topbar cf-panel">
        <div className="topbar-search">
          <input type="text" placeholder="Buscar configurações..." />
        </div>
        <div className="topbar-actions">
          <button type="button" className="solid-btn" style={{ background: '#ff5b6d' }} onClick={logout}>
            Sair da conta
          </button>
        </div>
      </header>

      {error && <div className="cf-error">{error}</div>}

      <section className="workspace-grid">
        <article className="cf-panel panel-lg" style={{ gridColumn: '1 / -1' }}>
          <header className="panel-header"><h2>Dados da Empresa</h2></header>
          {loading ? (
            <p style={{ color: '#9eb5df', padding: '2rem', textAlign: 'center' }}>Carregando...</p>
          ) : empresa ? (
            <div style={{ padding: '0 1rem' }}>
              <div style={fieldStyle}>
                <span style={labelStyle}>Nome da empresa</span>
                <span style={valueStyle}>{empresa.nome_empresa}</span>
              </div>
              <div style={fieldStyle}>
                <span style={labelStyle}>Nicho</span>
                <span style={valueStyle}>{empresa.nicho}</span>
              </div>
              <div style={fieldStyle}>
                <span style={labelStyle}>Email</span>
                <span style={valueStyle}>{empresa.email_login}</span>
              </div>
              <div style={fieldStyle}>
                <span style={labelStyle}>Telefone</span>
                <span style={valueStyle}>{empresa.telefone || 'Não informado'}</span>
              </div>
              <div style={fieldStyle}>
                <span style={labelStyle}>Plano</span>
                <span className="plan-chip">{String(empresa.plano_empresa || 'free').toUpperCase()}</span>
              </div>
              <div style={fieldStyle}>
                <span style={labelStyle}>Limite de clientes</span>
                <span style={valueStyle}>{empresa.limite_clientes || 'Ilimitado'}</span>
              </div>
              <div style={{ ...fieldStyle, borderBottom: 'none' }}>
                <span style={labelStyle}>Limite de atendimentos</span>
                <span style={valueStyle}>{empresa.limite_atendimentos || 'Ilimitado'}</span>
              </div>
            </div>
          ) : null}
        </article>
      </section>
    </>
  )
}
