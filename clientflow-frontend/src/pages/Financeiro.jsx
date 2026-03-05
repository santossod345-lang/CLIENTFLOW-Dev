export default function Financeiro() {
  return (
    <>
      <header className="cf-topbar cf-panel">
        <div className="topbar-search">
          <input type="text" placeholder="Buscar..." />
        </div>
        <div className="topbar-actions">
          <span className="plan-chip">Plano PRO</span>
          <button type="button" className="icon-btn">R</button>
          <button type="button" className="icon-btn">X</button>
        </div>
      </header>
      <section className="workspace-grid">
        <article className="cf-panel panel-lg" style={{ gridColumn: '1 / -1' }}>
          <header className="panel-header">
            <h2>Financeiro</h2>
          </header>
          <p style={{ color: '#a8c1e7' }}>Tela conectada com o menu. Modulo pronto para receber funcionalidades.</p>
        </article>
      </section>
    </>
  )
}
