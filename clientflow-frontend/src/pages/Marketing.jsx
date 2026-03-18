export default function Marketing() {
  return (
    <>
      <header className="cf-topbar cf-panel">
        <div className="topbar-search">
          <input type="text" placeholder="Buscar campanhas..." />
        </div>
        <div className="topbar-actions">
          <span className="plan-chip">Marketing</span>
        </div>
      </header>
      <section className="workspace-grid">
        <article className="cf-panel panel-lg" style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '4rem 2rem' }}>
          <h2 style={{ color: '#e0e8f5', marginBottom: '1rem', fontSize: '1.5rem' }}>Marketing</h2>
          <p style={{ color: '#9eb5df', marginBottom: '0.5rem' }}>Crie campanhas, envie promoções e acompanhe resultados.</p>
          <p style={{ color: '#ffc14d', fontSize: '0.875rem' }}>Módulo em desenvolvimento — disponível em breve.</p>
        </article>
      </section>
    </>
  )
}
