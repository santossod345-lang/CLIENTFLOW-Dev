import React from 'react'

const Sidebar = ({ isOpen, setIsOpen }) => {
  const [activeSection, setActiveSection] = React.useState('dashboard')

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'clientes', label: 'Clientes', icon: '👥' },
    { id: 'atendimentos', label: 'Atendimentos', icon: '🛠️' },
    { id: 'agenda', label: 'Agenda', icon: '📅' },
    { id: 'financeiro', label: 'Financeiro', icon: '💰' },
    { id: 'relatorios', label: 'Relatórios', icon: '📈' },
    { id: 'marketing', label: 'Marketing', icon: '📢' },
    { id: 'config', label: 'Configurações', icon: '⚙️' },
  ]

  return (
    <>
      {/* Overlay para mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 lg:hidden z-40"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed lg:static left-0 top-0 w-64 h-screen glass-effect flex flex-col transition-transform duration-300 z-50 border-r border-primary-700/60 ${
          isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        }`}
      >
        {/* Logo */}
        <div className="p-6 border-b border-primary-700/60 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-accent-blue to-accent-purple rounded-xl flex items-center justify-center shadow-md shadow-black/30">
              <span className="text-white font-bold text-lg">CF</span>
            </div>
            <div>
              <h1 className="text-white font-bold text-lg tracking-tight">ClientFlow</h1>
              <p className="text-xs text-gray-500 font-medium">Intelligence Platform</p>
            </div>
          </div>
          <button
            onClick={() => setIsOpen(false)}
            className="lg:hidden text-gray-400 hover:text-accent-blue transition-colors duration-300"
          >
            ✕
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto py-5 px-3">
          {menuItems.map((item) => (
            <button
              key={item.id}
              onClick={() => {
                setActiveSection(item.id)
                setIsOpen(false)
              }}
              className={`w-full relative flex items-center gap-3.5 px-4 py-3.5 rounded-xl mb-2 transition-colors duration-200 font-medium overflow-hidden ${
                activeSection === item.id
                  ? 'text-white bg-primary-800/80 border border-accent-blue/20'
                  : 'text-gray-400 hover:text-white hover:bg-primary-800/40'
              }`}
            >
              {activeSection === item.id && (
                <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-accent-blue rounded-r-full" />
              )}
              <span className="text-lg relative z-10">{item.icon}</span>
              <span className="relative z-10">{item.label}</span>
            </button>
          ))}
        </nav>

        {/* User Section */}
        <div className="p-4 border-t border-primary-700/60 mt-auto">
          <button className="w-full flex items-center gap-3 p-3 rounded-xl hover:bg-primary-800/50 transition-colors duration-200 group">
            <div className="w-10 h-10 bg-gradient-to-br from-accent-purple to-accent-blue rounded-xl shadow-md shadow-black/30" />
            <div className="text-left flex-1">
              <p className="text-sm font-bold text-white">João Silva</p>
              <p className="text-xs text-gray-500 font-medium">Plano Pro</p>
            </div>
          </button>
        </div>
      </aside>
    </>
  )
}

export default Sidebar
