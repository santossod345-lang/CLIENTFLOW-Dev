import { useContext } from 'react'
import { NavLink } from 'react-router-dom'
import AuthContext from '../context/AuthContext'

const MENU = [
  { path: '/painel', label: 'Painel' },
  { path: '/clientes', label: 'Clientes' },
  { path: '/planos', label: 'Planos' },
  { path: '/whatsapp', label: 'WhatsApp' },
  { path: '/marketing', label: 'Marketing' },
  { path: '/atendimentos', label: 'Atendimentos' },
  { path: '/financeiro', label: 'Financeiro' },
  { path: '/relatorios', label: 'Relatorios' },
  { path: '/agenda', label: 'Agenda' },
  { path: '/configuracoes', label: 'Configuracoes' }
]

export default function Sidebar() {
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
        {MENU.map((item) => (
          <NavLink key={item.path} to={item.path} className={({ isActive }) => `menu-item ${isActive ? 'active' : ''}`}>
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-foot">
        <NavLink to="/suporte" className={({ isActive }) => `menu-item ${isActive ? 'active' : ''}`}>
          <span>Suporte</span>
        </NavLink>
        <NavLink to="/documentacao" className={({ isActive }) => `menu-item ${isActive ? 'active' : ''}`}>
          <span>Documentacao</span>
        </NavLink>
        <button type="button" onClick={logout} className="menu-item">
          <span>Sair</span>
        </button>
      </div>
    </aside>
  )
}
