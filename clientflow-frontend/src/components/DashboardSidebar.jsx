import { NavLink, useLocation } from 'react-router-dom'
import { useContext } from 'react'
import AuthContext from '../context/AuthContext'

const SIDEBAR_MENU = [
  { key: 'dashboard', label: 'Painel', path: '/dashboard', icon: '[ ]' },
  { key: 'crm', label: 'CRM', path: '/crm', icon: '<>' },
  { key: 'atendimentos', label: 'Atendimentos', path: '/atendimentos', icon: '()' },
  { key: 'financeiro', label: 'Financeiro', path: '/financeiro', icon: '$$' },
  { key: 'relatorios', label: 'Relatorios', path: '/relatorios', icon: '[]' },
  { key: 'whatsapp', label: 'WhatsApp', path: '/whatsapp', icon: 'W' },
  { key: 'agenda', label: 'Agenda', path: '/agenda', icon: 'A' },
  { key: 'marketing', label: 'Marketing', path: '/marketing', icon: 'M' },
  { key: 'configuracoes', label: 'Configuracoes', path: '/configuracoes', icon: 'C' }
]

export default function DashboardSidebar() {
  const location = useLocation()
  const { logout } = useContext(AuthContext)

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
