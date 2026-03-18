import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../services/api'

function Cadastro() {
  const [nomeEmpresa, setNomeEmpresa] = useState('')
  const [nicho, setNicho] = useState('')
  const [telefone, setTelefone] = useState('')
  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setSuccess('')

    try {
      console.log('[Cadastro] Tentando cadastrar empresa...')
      
      await api.post('/auth/register', {
        nome_empresa: nomeEmpresa,
        nicho,
        telefone,
        email_login: email,
        senha
      })

      console.log('[Cadastro] Cadastro realizado com sucesso!')
      setSuccess('Cadastro realizado com sucesso. Voce ja pode fazer login.')
      setTimeout(() => navigate('/login'), 1200)
    } catch (err) {
      console.error('[Cadastro] Erro ao cadastrar:', err)
      setError(err.response?.data?.detail || 'Erro ao cadastrar empresa')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary to-secondary">
      <div className="bg-white rounded-lg shadow-lg p-8 w-full max-w-md">
        <h1 className="text-3xl font-bold mb-2 text-center text-dark">Criar Conta</h1>
        <p className="text-sm text-center text-gray-600 mb-6">Cadastre sua empresa para acessar o sistema.</p>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {String(error)}
          </div>
        )}

        {success && (
          <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
            {success}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="text"
            value={nomeEmpresa}
            onChange={(e) => setNomeEmpresa(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            placeholder="Nome da empresa"
            minLength={3}
            required
          />

          <input
            type="text"
            value={nicho}
            onChange={(e) => setNicho(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            placeholder="Nicho"
            minLength={3}
            required
          />

          <input
            type="tel"
            value={telefone}
            onChange={(e) => setTelefone(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            placeholder="Telefone com DDD"
            required
          />

          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            placeholder="Email de login"
            required
          />

          <input
            type="password"
            value={senha}
            onChange={(e) => setSenha(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            placeholder="Senha (min 8, letra e numero)"
            minLength={8}
            required
          />

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-primary text-white py-2 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 transition"
          >
            {loading ? 'Cadastrando...' : 'Cadastrar Empresa'}
          </button>
        </form>

        <p className="text-center text-sm text-gray-600 mt-6">
          Ja tem conta?{' '}
          <Link to="/login" className="text-primary hover:underline">
            Entrar
          </Link>
        </p>
      </div>
    </div>
  )
}

export default Cadastro

