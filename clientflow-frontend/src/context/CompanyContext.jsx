import React, { createContext, useState, useCallback, useEffect } from 'react'
import { useAuth } from './AuthContext'
import { companyService } from '../services/api'

export const CompanyContext = createContext(null)

export const CompanyProvider = ({ children }) => {
  const { user } = useAuth()
  const [company, setCompany] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [successMessage, setSuccessMessage] = useState(null)

  // Carregar dados da empresa ao fazer login
  useEffect(() => {
    if (user && user.nome_empresa) {
      // Usar dados do user que vieram do login
      setCompany({
        id: user.id,
        nome_empresa: user.nome_empresa,
        nicho: user.nicho,
        telefone: user.telefone,
        email_login: user.email_login,
        plano_empresa: user.plano_empresa,
      })

      // Tentar buscar dados atualizados da API
      loadCompany()
    }
  }, [user])

  const loadCompany = useCallback(async () => {
    if (!user) return

    setLoading(true)
    setError(null)

    try {
      const response = await companyService.getProfile()
      if (response.data) {
        const companyData = response.data.data || response.data
        setCompany(companyData)
      }
    } catch (err) {
      console.warn('Erro ao carregar perfil da empresa:', err.message)
      // Continua usando dados locais se API falhar
    } finally {
      setLoading(false)
    }
  }, [user])

  const updateCompany = useCallback(async (updatedData) => {
    if (!company) return { success: false, error: 'Empresa não carregada' }

    setLoading(true)
    setError(null)
    setSuccessMessage(null)

    try {
      const response = await companyService.updateProfile(updatedData)
      const updatedCompany = response.data.data || response.data

      setCompany(updatedCompany)
      setSuccessMessage('Dados atualizados com sucesso')

      // Limpar mensagem de sucesso após 3 segundos
      setTimeout(() => setSuccessMessage(null), 3000)

      return { success: true, data: updatedCompany }
    } catch (err) {
      const errorMessage = err.response?.data?.error?.message || err.message || 'Erro ao atualizar dados'
      setError(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      setLoading(false)
    }
  }, [company])

  const clearMessages = useCallback(() => {
    setError(null)
    setSuccessMessage(null)
  }, [])

  const uploadLogo = useCallback(async (file) => {
    if (!file || !company) {
      return { success: false, error: 'Arquivo ou empresa não carregada' }
    }

    setLoading(true)
    setError(null)
    setSuccessMessage(null)

    try {
      const response = await companyService.uploadLogo(file)
      const result = response.data.data || response.data

      // Atualizar company com nova logo_url
      setCompany((prevCompany) => ({
        ...prevCompany,
        logo_url: result.logo_url,
      }))

      setSuccessMessage('Logo atualizada com sucesso')

      // Limpar mensagem após 3 segundos
      setTimeout(() => setSuccessMessage(null), 3000)

      return { success: true, data: result }
    } catch (err) {
      const errorMessage = err.response?.data?.error?.message || err.message || 'Erro ao enviar logo'
      setError(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      setLoading(false)
    }
  }, [company])

  const value = {
    company,
    loading,
    error,
    successMessage,
    loadCompany,
    updateCompany,
    clearMessages,
    uploadLogo,
  }

  return <CompanyContext.Provider value={value}>{children}</CompanyContext.Provider>
}

// Hook para usar o contexto
export const useCompany = () => {
  const context = React.useContext(CompanyContext)
  if (!context) {
    throw new Error('useCompany deve ser usado dentro de um CompanyProvider')
  }
  return context
}
