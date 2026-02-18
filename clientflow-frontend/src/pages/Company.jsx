import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useCompany } from '../context/CompanyContext'
import { useAuth } from '../context/AuthContext'

const Company = () => {
  const navigate = useNavigate()
  const { user } = useAuth()
  const { company, loading, error, successMessage, updateCompany, uploadLogo, clearMessages } = useCompany()

  const [formData, setFormData] = useState({
    nome_empresa: '',
    telefone: '',
    nicho: '',
  })

  const [isSubmitting, setIsSubmitting] = useState(false)
  const [logoFile, setLogoFile] = useState(null)
  const [logoPreview, setLogoPreview] = useState(null)
  const [isUploadingLogo, setIsUploadingLogo] = useState(false)

  // Carregar dados da empresa no formulário
  useEffect(() => {
    if (company) {
      setFormData({
        nome_empresa: company.nome_empresa || '',
        telefone: company.telefone || '',
        nicho: company.nicho || '',
      })
    }
  }, [company])

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
    clearMessages()
  }

  const handleLogoChange = (e) => {
    const file = e.target.files?.[0]
    if (file) {
      setLogoFile(file)
      clearMessages()

      // Criar preview
      const reader = new FileReader()
      reader.onload = (event) => {
        setLogoPreview(event.target?.result)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleUploadLogo = async () => {
    if (!logoFile) return

    setIsUploadingLogo(true)
    const result = await uploadLogo(logoFile)
    setIsUploadingLogo(false)

    if (result.success) {
      setLogoFile(null)
      setLogoPreview(null)
      // Reset input
      const input = document.getElementById('logo-input')
      if (input) input.value = ''
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!formData.nome_empresa.trim()) {
      return
    }

    setIsSubmitting(true)

    const result = await updateCompany({
      nome_empresa: formData.nome_empresa,
      telefone: formData.telefone,
      nicho: formData.nicho,
    })

    setIsSubmitting(false)

    if (result.success) {
      // Sucesso - mostrar mensagem por 3 segundos
      setTimeout(() => {
        navigate('/dashboard')
      }, 2000)
    }
  }

  // Get user initials for avatar
  const userInitials = user?.nome_empresa
    ?.split(' ')
    .slice(0, 2)
    .map((word) => word[0])
    .join('')
    .toUpperCase() || 'CF'

  if (loading && !company) {
    return (
      <div className="p-6 lg:p-10 bg-primary-900 min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent-blue mx-auto mb-4" />
          <p className="text-gray-400">Carregando perfil da empresa...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 lg:p-10 bg-primary-900 min-h-screen">
      {/* Header */}
      <div className="mb-10">
        <h1 className="text-3xl font-bold text-white mb-2 tracking-tight">Perfil da Empresa</h1>
        <p className="text-gray-400">Gerencie informações da sua empresa</p>
      </div>

      {/* Success Message */}
      {successMessage && (
        <div className="mb-6 p-4 bg-accent-green/20 border border-accent-green/60 rounded-lg fade-in">
          <p className="text-accent-green text-sm font-medium">✓ {successMessage}</p>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="mb-6 p-4 bg-red-500/20 border border-red-500/50 rounded-lg fade-in">
          <p className="text-red-300 text-sm font-medium">⚠️ {error}</p>
        </div>
      )}

      {/* Logo Card */}
      <div className="card-base fade-in max-w-2xl mb-8">
        <h2 className="text-lg font-bold text-white mb-6">Logo da Empresa</h2>

        <div className="flex flex-col items-center gap-6">
          {/* Logo Preview */}
          <div className="relative">
            {logoPreview ? (
              <img
                src={logoPreview}
                alt="Preview"
                className="w-24 h-24 rounded-xl object-cover border-2 border-accent-blue/50"
              />
            ) : company?.logo_url ? (
              <img
                src={company.logo_url}
                alt={company.nome_empresa}
                className="w-24 h-24 rounded-xl object-cover border-2 border-primary-700/60"
              />
            ) : (
              <div className="w-24 h-24 rounded-xl bg-gradient-to-br from-accent-blue to-accent-purple flex items-center justify-center text-2xl font-bold text-white border-2 border-primary-700/60">
                {userInitials}
              </div>
            )}
          </div>

          {/* File Input */}
          <div className="w-full">
            <label className="block text-sm font-semibold text-gray-300 mb-3">Selecione uma imagem</label>
            <input
              id="logo-input"
              type="file"
              accept="image/jpeg,image/jpg,image/png,image/webp"
              onChange={handleLogoChange}
              disabled={isUploadingLogo}
              className="w-full px-4 py-3 bg-primary-800/70 border-2 border-dashed border-primary-700/60 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-accent-blue/40 transition-all disabled:opacity-50 cursor-pointer hover:border-primary-700"
            />
            <p className="text-xs text-gray-500 mt-2">JPG, PNG ou WEBP. Máximo 5MB</p>
          </div>

          {/* Upload Button */}
          {logoFile && (
            <button
              onClick={handleUploadLogo}
              disabled={isUploadingLogo}
              className="w-full py-3 px-4 bg-gradient-to-r from-accent-blue to-accent-cyan rounded-lg font-semibold text-primary-900 hover:shadow-lg hover:shadow-accent-blue/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isUploadingLogo ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-primary-900 border-t-transparent" />
                  Enviando...
                </>
              ) : (
                '↑ Enviar nova logo'
              )}
            </button>
          )}
        </div>
      </div>

      {/* Form Card */}
      <div className="card-base fade-in max-w-2xl">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Nome da Empresa */}
          <div>
            <label htmlFor="nome_empresa" className="block text-sm font-semibold text-gray-300 mb-3">
              Nome da Empresa
            </label>
            <input
              id="nome_empresa"
              type="text"
              name="nome_empresa"
              value={formData.nome_empresa}
              onChange={handleInputChange}
              disabled={isSubmitting}
              className="w-full px-4 py-3 bg-primary-800/70 border border-primary-700/60 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-accent-blue/40 focus:ring-2 focus:ring-accent-blue/30 transition-all disabled:opacity-50 font-medium"
              placeholder="Ex: Oficina ABC"
            />
            <p className="text-xs text-gray-500 mt-2">Nome público da sua empresa</p>
          </div>

          {/* Telefone */}
          <div>
            <label htmlFor="telefone" className="block text-sm font-semibold text-gray-300 mb-3">
              Telefone
            </label>
            <input
              id="telefone"
              type="tel"
              name="telefone"
              value={formData.telefone}
              onChange={handleInputChange}
              disabled={isSubmitting}
              className="w-full px-4 py-3 bg-primary-800/70 border border-primary-700/60 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-accent-blue/40 focus:ring-2 focus:ring-accent-blue/30 transition-all disabled:opacity-50 font-medium"
              placeholder="Ex: (11) 9999-9999"
            />
            <p className="text-xs text-gray-500 mt-2">Telefone de contato da empresa</p>
          </div>

          {/* Nicho */}
          <div>
            <label htmlFor="nicho" className="block text-sm font-semibold text-gray-300 mb-3">
              Nicho / Setor
            </label>
            <input
              id="nicho"
              type="text"
              name="nicho"
              value={formData.nicho}
              onChange={handleInputChange}
              disabled={isSubmitting}
              className="w-full px-4 py-3 bg-primary-800/70 border border-primary-700/60 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-accent-blue/40 focus:ring-2 focus:ring-accent-blue/30 transition-all disabled:opacity-50 font-medium"
              placeholder="Ex: Manutenção de Veículos"
            />
            <p className="text-xs text-gray-500 mt-2">Área de atuação da sua empresa</p>
          </div>

          {/* Divider */}
          <div className="border-t border-primary-700/60 pt-6" />

          {/* Buttons */}
          <div className="flex gap-3 pt-2">
            <button
              type="submit"
              disabled={isSubmitting || !formData.nome_empresa.trim()}
              className="flex-1 py-3 px-4 bg-gradient-to-r from-accent-blue to-accent-cyan rounded-lg font-semibold text-primary-900 hover:shadow-lg hover:shadow-accent-blue/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isSubmitting ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-primary-900 border-t-transparent" />
                  Salvando...
                </>
              ) : (
                '✓ Salvar alterações'
              )}
            </button>

            <button
              type="button"
              onClick={() => navigate('/dashboard')}
              disabled={isSubmitting}
              className="flex-1 py-3 px-4 bg-primary-800/70 border border-primary-700/60 rounded-lg font-semibold text-gray-300 hover:text-white hover:bg-primary-800 transition-all disabled:opacity-50"
            >
              Cancelar
            </button>
          </div>
        </form>

        {/* Info Section */}
        <div className="mt-8 pt-8 border-t border-primary-700/60">
          <h3 className="text-sm font-bold text-gray-300 uppercase tracking-wide mb-4">Informações da Conta</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-sm text-gray-400">Email:</span>
              <span className="text-sm font-medium text-white">{company?.email_login || 'N/A'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-400">Plano:</span>
              <span className="text-sm font-medium text-accent-green">{company?.plano_empresa ? company.plano_empresa.toUpperCase() : 'N/A'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-400">Status:</span>
              <span className="text-sm font-medium text-accent-cyan">Ativa</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Company
