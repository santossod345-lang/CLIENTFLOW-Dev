import React, { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { useCompany } from '../../context/CompanyContext'

const Header = ({ onMenuClick }) => {
  const [searchOpen, setSearchOpen] = useState(false)
  const [userMenuOpen, setUserMenuOpen] = useState(false)
  const userMenuRef = useRef(null)

  const navigate = useNavigate()
  const { user, logout } = useAuth()
  const { company } = useCompany()

  // Fechar menu ao clicar fora
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target)) {
        setUserMenuOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  // Get user initials
  const userInitials = user?.nome_empresa
    ?.split(' ')
    .slice(0, 2)
    .map((word) => word[0])
    .join('')
    .toUpperCase() || 'CF'

  const companyName = company?.nome_empresa || user?.nome_empresa || 'ClientFlow'
  const companyNiche = company?.nicho || user?.nicho || ''
  const companyLogo = company?.logo_url || user?.logo_url || null

  return (
    <header className="sticky top-0 glass-effect z-40 border-b border-primary-700/60">
      <div className="px-6 py-4 flex items-center justify-between">
        {/* Left Section - Menu & Search & Company */}
        <div className="flex items-center gap-6 flex-1">
          <button
            onClick={onMenuClick}
            className="lg:hidden text-gray-400 hover:text-accent-blue transition-colors duration-300"
            title="Menu"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>

          {/* Company Logo & Info */}
          <div className="hidden lg:flex items-center gap-3">
            {/* Logo ou Avatar */}
            {companyLogo ? (
              <img
                src={companyLogo}
                alt={companyName}
                className="w-8 h-8 rounded-lg object-cover border border-primary-700/60"
              />
            ) : (
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-blue to-accent-purple flex items-center justify-center text-xs font-bold text-white">
                {userInitials}
              </div>
            )}

            {/* Company Name & Niche */}
            <div className="flex flex-col">
              <p className="text-sm font-bold text-white truncate">{companyName}</p>
              {companyNiche && (
                <p className="text-xs text-gray-400 font-medium truncate">{companyNiche}</p>
              )}
            </div>
          </div>

          <div className="hidden lg:flex items-center gap-3 rounded-xl px-4 py-2 flex-1 max-w-sm bg-primary-800/70 border border-primary-700/60 transition-colors duration-200 focus-within:border-accent-blue/40">
            <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              type="text"
              placeholder="Buscar clientes, atendimentos..."
              className="bg-transparent outline-none text-sm flex-1 placeholder-gray-500 text-white"
            />
          </div>
        </div>

        {/* Right Section - Notifications & User */}
        <div className="flex items-center gap-4">
          {/* Notifications */}
          <button className="relative text-gray-400 hover:text-accent-blue transition-colors duration-200">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
            <span className="absolute top-1 right-1 w-2 h-2 bg-accent-orange rounded-full"></span>
          </button>

          {/* Divider */}
          <div className="hidden lg:block w-px h-6 bg-primary-700/60"></div>

          {/* Plan */}
          <div className="hidden lg:flex items-center gap-2 px-3 py-1 rounded-full bg-primary-800/60 border border-primary-700/60">
            <span className="text-sm text-gray-400 font-medium">Plano:</span>
            <span className="px-3 py-1 rounded-full text-accent-blue bg-accent-blue/15 text-xs font-bold">{user?.plano_empresa || 'Pro'}</span>
          </div>

          {/* User Menu */}
          <div className="relative" ref={userMenuRef}>
            <button
              onClick={() => setUserMenuOpen(!userMenuOpen)}
              className="w-10 h-10 bg-gradient-to-br from-accent-blue to-accent-purple rounded-xl shadow-md shadow-black/30 transition-colors duration-200 flex items-center justify-center font-bold text-white"
            >
              {userInitials}
            </button>

            {/* Dropdown Menu */}
            {userMenuOpen && (
              <div className="absolute right-0 mt-3 w-56 glass-effect rounded-xl shadow-lg z-50 overflow-hidden border border-primary-700/60">
                {/* User Info */}
                <div className="px-4 py-4 border-b border-primary-700/60 bg-primary-800/40">
                  <p className="text-sm font-bold text-white">{companyName}</p>
                  <p className="text-xs text-gray-500 font-medium">{user?.email_login || 'user@clientflow.com'}</p>
                </div>

                {/* Menu Items */}
                <div className="py-2">
                  <button
                    onClick={() => {
                      navigate('/empresa')
                      setUserMenuOpen(false)
                    }}
                    className="w-full px-4 py-2 text-left text-sm text-gray-300 hover:text-white hover:bg-primary-800/60 transition-colors duration-200 flex items-center gap-3 group"
                  >
                    <svg className="w-4 h-4 text-gray-500 group-hover:text-accent-blue transition-colors duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Perfil da Empresa
                  </button>

                  <button className="w-full px-4 py-2 text-left text-sm text-gray-300 hover:text-white hover:bg-primary-800/60 transition-colors duration-200 flex items-center gap-3 group">
                    <svg className="w-4 h-4 text-gray-500 group-hover:text-accent-blue transition-colors duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    Configurações
                  </button>

                  <button className="w-full px-4 py-2 text-left text-sm text-gray-300 hover:text-white hover:bg-primary-800/60 transition-colors duration-200 flex items-center gap-3 group">
                    <svg className="w-4 h-4 text-gray-500 group-hover:text-accent-blue transition-colors duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Ajuda
                  </button>

                  <div className="my-2 border-t border-primary-700/60" />

                  <button
                    onClick={handleLogout}
                    className="w-full px-4 py-2 text-left text-sm text-accent-orange hover:text-red-400 hover:bg-accent-orange/10 transition-colors duration-200 flex items-center gap-3 group"
                  >
                    <svg className="w-4 h-4 text-accent-orange group-hover:text-red-400 transition-colors duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                    </svg>
                    Sair
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header
