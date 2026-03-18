export default function Suporte() {
  return (
    <>
      <header className="cf-topbar cf-panel">
        <div className="topbar-search">
          <input type="text" placeholder="Buscar no suporte..." />
        </div>
        <div className="topbar-actions">
          <span className="plan-chip">Suporte</span>
        </div>
      </header>
      <section className="workspace-grid">
        <article className="cf-panel panel-lg" style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '4rem 2rem' }}>
          <h2 style={{ color: '#e0e8f5', marginBottom: '1rem', fontSize: '1.5rem' }}>Central de Suporte</h2>
          <p style={{ color: '#9eb5df', marginBottom: '1.5rem' }}>Precisa de ajuda? Entre em contato com nossa equipe.</p>
          <div style={{ display: 'flex', gap: '2rem', justifyContent: 'center', flexWrap: 'wrap' }}>
            <div className="cf-panel" style={{ padding: '2rem', minWidth: '200px' }}>
              <p style={{ color: '#35b9ff', fontWeight: 'bold', marginBottom: '0.5rem' }}>Email</p>
              <p style={{ color: '#9eb5df' }}>suporte@clientflow.com</p>
            </div>
            <div className="cf-panel" style={{ padding: '2rem', minWidth: '200px' }}>
              <p style={{ color: '#33d890', fontWeight: 'bold', marginBottom: '0.5rem' }}>Status</p>
              <p style={{ color: '#9eb5df' }}>Todos os sistemas operacionais</p>
            </div>
          </div>
        </article>
      </section>
    </>
  )
}
