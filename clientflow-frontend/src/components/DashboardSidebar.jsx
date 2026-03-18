import { NavLink } from 'react-router-dom'

const SIDEBAR_MENU = [
  { key: 'painel', label: 'Painel', path: '/painel', icon: '[ ]' },
  { key: 'clientes', label: 'Clientes', path: '/clientes', icon: '<>' },
  { key: 'atendimentos', label: 'Atendimentos', path: '/atendimentos', icon: '()' },
  { key: 'financeiro', label: 'Financeiro', path: '/financeiro', icon: '$$' },
  { key: 'relatorios', label: 'Relatorios', path: '/relatorios', icon: '[]' },
  { key: 'whatsapp', label: 'WhatsApp', path: '/whatsapp', icon: 'W' },
  { key: 'agenda', label: 'Agenda', path: '/agenda', icon: 'A' },
  { key: 'marketing', label: 'Marketing', path: '/marketing', icon: 'M' },
  { key: 'planos', label: 'Planos', path: '/planos', icon: 'P' },
  { key: 'configuracoes', label: 'Configuracoes', path: '/configuracoes', icon: 'C' }
]

export default function DashboardSidebar() {
  console.log('[Sidebar] Rendering navigation links')

  return (
    <aside className="cf-sidebar">
      <div className="cf-brand">
        <span className="brand-logo">{'<>'}</span>
        <div>
          <h1>ClientFlow</h1>
          <p>SaaS Intelligence Platform</p>
        </div>
      </div>

      <nav>
        {SIDEBAR_MENU.map((item) => (
          <NavLink
            key={item.key}
            to={item.path}
            className={({ isActive }) => `menu-item ${isActive ? 'active' : ''}`}
          >
            <span>{item.icon}</span>
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-foot">
        <NavLink 
          to="/suporte"
          className={({ isActive }) => `menu-item ${isActive ? 'active' : ''}`}
        >
          <span>?</span>
          <span>Suporte</span>
        </NavLink>
        <NavLink 
          to="/documentacao"
          className={({ isActive }) => `menu-item ${isActive ? 'active' : ''}`}
        >
          <span>i</span>
          <span>Documentacao</span>
        </NavLink>
      </div>
    </aside>
  )
}
