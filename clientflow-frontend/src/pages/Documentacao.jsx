export default function Documentacao() {
  return (
    <>
      <header className="cf-topbar cf-panel">
        <div className="topbar-search">
          <input type="text" placeholder="Buscar na documentação..." />
        </div>
        <div className="topbar-actions">
          <span className="plan-chip">Docs</span>
        </div>
      </header>
      <section className="workspace-grid">
        <article className="cf-panel panel-lg" style={{ gridColumn: '1 / -1' }}>
          <header className="panel-header"><h2>Documentação do Sistema</h2></header>
          <div style={{ padding: '1rem' }}>
            <div style={{ marginBottom: '2rem' }}>
              <h3 style={{ color: '#35b9ff', marginBottom: '0.5rem' }}>Como usar o ClientFlow</h3>
              <ol style={{ color: '#9eb5df', paddingLeft: '1.5rem', lineHeight: '2' }}>
                <li><strong>CRM:</strong> Cadastre seus clientes com nome e telefone</li>
                <li><strong>Atendimentos:</strong> Registre cada serviço prestado</li>
                <li><strong>Painel:</strong> Acompanhe KPIs e gráficos em tempo real</li>
                <li><strong>Financeiro:</strong> Veja o resumo de faturamento</li>
                <li><strong>Relatórios:</strong> Análise dos dados consolidados</li>
                <li><strong>Configurações:</strong> Gerencie dados da empresa e plano</li>
              </ol>
            </div>
            <div style={{ marginBottom: '2rem' }}>
              <h3 style={{ color: '#35b9ff', marginBottom: '0.5rem' }}>Planos</h3>
              <p style={{ color: '#9eb5df' }}>O plano FREE permite até 1000 clientes e 5000 atendimentos. Faça upgrade para PRO para limites ilimitados.</p>
            </div>
            <div>
              <h3 style={{ color: '#35b9ff', marginBottom: '0.5rem' }}>API</h3>
              <p style={{ color: '#9eb5df' }}>Acesse a documentação interativa da API em <code style={{ color: '#ffc14d' }}>/docs</code> no backend.</p>
            </div>
          </div>
        </article>
      </section>
    </>
  )
}
