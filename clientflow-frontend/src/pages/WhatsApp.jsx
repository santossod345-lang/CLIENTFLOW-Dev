export default function WhatsApp() {
  return (
    <>
      <header className="cf-topbar cf-panel">
        <div className="topbar-search">
          <input type="text" placeholder="Buscar conversas..." />
        </div>
        <div className="topbar-actions">
          <span className="plan-chip">WhatsApp</span>
        </div>
      </header>
      <section className="workspace-grid">
        <article className="cf-panel panel-lg" style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '4rem 2rem' }}>
          <h2 style={{ color: '#e0e8f5', marginBottom: '1rem', fontSize: '1.5rem' }}>Integração WhatsApp</h2>
          <p style={{ color: '#9eb5df', marginBottom: '0.5rem' }}>Envie mensagens automáticas e gerencie conversas com seus clientes.</p>
          <p style={{ color: '#ffc14d', fontSize: '0.875rem' }}>Módulo em desenvolvimento — disponível em breve.</p>
        </article>
      </section>
    </>
  )
}
