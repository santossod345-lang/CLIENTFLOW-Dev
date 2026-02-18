📖 CONECTAR FRONTEND REACT AO FASTAPI BACKEND

═══════════════════════════════════════════════════════════════════

✅ O FRONTEND JÁ ESTÁ PRONTO PARA CONECTAR AO SEU BACKEND

Arquivo principal: src/services/api.js

═══════════════════════════════════════════════════════════════════

🔧 CONFIGURAÇÃO DA API:

1. Verifique o arquivo .env.local:
   
   VITE_API_URL=http://localhost:8000/api

2. Se sua API está em outra porta, edite:
   
   VITE_API_URL=http://localhost:SUAPORTA/api

3. Salve e reinicie:
   
   npm run dev

═══════════════════════════════════════════════════════════════════

🔌 ENDPOINTS JÁ CONFIGURADOS:

AUTENTICAÇÃO:
  POST /empresas/login
    ├─ Parâmetros: email_login, senha
    └─ Função: authService.login(email, password)
  
  POST /empresas/cadastrar
    ├─ Parâmetros: nome_empresa, nicho, telefone, email_login, senha
    └─ Função: authService.register(data)

CLIENTES:
  GET  /clientes
    └─ Função: clientsService.list()
  
  GET  /clientes/:id
    └─ Função: clientsService.get(id)
  
  POST /clientes
    └─ Função: clientsService.create(data)
  
  PUT  /clientes/:id
    └─ Função: clientsService.update(id, data)
  
  DELETE /clientes/:id
    └─ Função: clientsService.delete(id)

ATENDIMENTOS:
  GET  /atendimentos
    └─ Função: appointmentsService.list()
  
  GET  /atendimentos/:id
    └─ Função: appointmentsService.get(id)
  
  POST /atendimentos
    └─ Função: appointmentsService.create(data)
  
  PUT  /atendimentos/:id
    └─ Função: appointmentsService.update(id, data)
  
  DELETE /atendimentos/:id
    └─ Função: appointmentsService.delete(id)

DASHBOARD:
  GET /dashboard/metrics
    └─ Função: dashboardService.getMetrics()
  
  GET /dashboard/revenue
    └─ Função: dashboardService.getRevenue()
  
  GET /dashboard/appointments-status
    └─ Função: dashboardService.getAppointmentsStatus()

═══════════════════════════════════════════════════════════════════

💻 EXEMPLOS DE USO:

EXEMPLO 1: Carregar lista de clientes

  import { clientsService } from '../services/api'
  import { useEffect, useState } from 'react'
  
  export function MyComponent() {
    const [clients, setClients] = useState([])
    const [loading, setLoading] = useState(true)
  
    useEffect(() => {
      const fetchClients = async () => {
        try {
          const response = await clientsService.list()
          setClients(response.data)
        } catch (error) {
          console.error('Erro ao carregar clientes:', error)
        } finally {
          setLoading(false)
        }
      }
      fetchClients()
    }, [])
  
    return <div>{/* seu JSX */}</div>
  }

EXEMPLO 2: Enviar dados de um atendimento

  import { appointmentsService } from '../services/api'
  
  async function createAppointment(data) {
    try {
      const response = await appointmentsService.create({
        cliente_id: 123,
        data: '2024-02-20',
        hora: '14:00',
        descricao: 'Revisão de motor',
        status: 'pendente'
      })
      console.log('Atendimento criado:', response.data)
    } catch (error) {
      console.error('Erro:', error.response.data)
    }
  }

EXEMPLO 3: Login de empresa

  import { authService } from '../services/api'
  
  async function handleLogin(email, senha) {
    try {
      const response = await authService.login(email, senha)
      const { token, empresa } = response.data
      
      // Salvar token
      localStorage.setItem('token', token)
      
      // Redirecionar para dashboard
      window.location.href = '/dashboard'
    } catch (error) {
      console.error('Login falhou:', error.response.data.detail)
    }
  }

═══════════════════════════════════════════════════════════════════

🔐 AUTENTICAÇÃO COM JWT:

O frontend já está preparado para JWT!

AO FAZER LOGIN:

  1. Backend retorna token JWT
  2. Frontend salva em localStorage:
     
     localStorage.setItem('token', response.data.token)

3. Automaticamente, TODOS os requests incluem o header:
     
     Authorization: Bearer sua_token_aqui

O interceptor em api.js faz isso automaticamente:

  api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  })

═══════════════════════════════════════════════════════════════════

🪝 INTEGRAR COM COMPONENTES EXISTENTES:

EXEMPLO: Substituir dados mockados pelo componente ClientsTable

Arquivo: src/components/dashboard/ClientsTable.jsx

Modificação:

  import { useEffect, useState } from 'react'
  import { clientsService } from '../../services/api'
  
  const ClientsTable = () => {
    const [clients, setClients] = useState([])
    const [loading, setLoading] = useState(true)
  
    useEffect(() => {
      clientsService.list()
        .then(res => setClients(res.data))
        .catch(err => console.error(err))
        .finally(() => setLoading(false))
    }, [])
  
    if (loading) return <div className="text-white">Carregando...</div>
  
    return (
      <div className="card-base col-span-full">
        <h3 className="text-lg font-bold text-white mb-4">Clientes Recentes</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-primary-700">
                <th className="text-left py-3 px-4">Cliente</th>
                <th className="text-left py-3 px-4">Contato</th>
                <th className="text-left py-3 px-4">Status</th>
              </tr>
            </thead>
            <tbody>
              {clients.map((client) => (
                <tr key={client.id} className="border-b border-primary-700">
                  <td className="py-4 px-4">{client.name}</td>
                  <td className="py-4 px-4">{client.contact}</td>
                  <td className="py-4 px-4">
                    <span className="text-green-300">✓ Ativo</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    )
  }
  
  export default ClientsTable

═══════════════════════════════════════════════════════════════════

🚨 TRATAMENTO DE ERROS:

try-catch-finally:

  try {
    const data = await clientsService.get(id)
    console.log('Sucesso:', data)
  } catch (error) {
    // error.response.status  → código HTTP (400, 404, 500)
    // error.response.data    → dados do erro do backend
    // error.message          → mensagem de erro
    console.error('Erro:', error.response?.data?.detail)
  } finally {
    setLoading(false)
  }

═══════════════════════════════════════════════════════════════════

📨 EXEMPLO: CHAMAR TODOS OS SERVIÇOS

import React, { useEffect } from 'react'
import {
  authService,
  clientsService,
  appointmentsService,
  dashboardService
} from '../services/api'

export function TestApi() {
  useEffect(() => {
    const test = async () => {
      try {
        // 1. Métricas do dashboard
        const metrics = await dashboardService.getMetrics()
        console.log('Métricas:', metrics.data)
        
        // 2. Faturamento
        const revenue = await dashboardService.getRevenue()
        console.log('Faturamento:', revenue.data)
        
        // 3. Clientes
        const clients = await clientsService.list()
        console.log('Clientes:', clients.data)
        
        // 4. Atendimentos
        const appointments = await appointmentsService.list()
        console.log('Atendimentos:', appointments.data)
        
      } catch (error) {
        console.error('Erro na API:', error)
      }
    }
    
    test()
  }, [])
  
  return <div className="text-white">Verificar console para resultados</div>
}

═══════════════════════════════════════════════════════════════════

🌐 CORS (Se backend está em domínio diferente):

No seu FastAPI backend, adicione CORS:

  from fastapi.middleware.cors import CORSMiddleware
  
  app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
  )

═══════════════════════════════════════════════════════════════════

🔄 RECARREGAR DADOS EX FONTE:

Para recarregar os dados do componente Dashboard:

  import Dashboard from '../pages/Dashboard'
  
  const [refresh, setRefresh] = useState(0)
  
  return (
    <>
      <button onClick={() => setRefresh(r => r + 1)}>
        Recarregar dados
      </button>
      <Dashboard key={refresh} />
    </>
  )

═══════════════════════════════════════════════════════════════════

📊 EXEMPLO COMPLETO: Atualizar MetaCard com dados reais

src/components/dashboard/StatCard.jsx

  import { useEffect, useState } from 'react'
  import { dashboardService } from '../../services/api'
  
  const StatCard = ({ metric }) => {
    const [data, setData] = useState(null)
    const [loading, setLoading] = useState(true)
  
    useEffect(() => {
      dashboardService.getMetrics()
        .then(res => {
          const metricData = res.data.find(m => m.name === metric)
          setData(metricData)
        })
        .finally(() => setLoading(false))
    }, [metric])
  
    if (loading) return <div className="card-base">Carregando...</div>
  
    return (
      <div className="card-base">
        <p className="metric-label mb-2">{data?.label}</p>
        <p className="metric-number">{data?.value}</p>
        <span className="text-green-400">↑ {data?.change}%</span>
      </div>
    )
  }
  
  export default StatCard

═══════════════════════════════════════════════════════════════════

✅ CHECKLIST DE INTEGRAÇÃO:

[ ] Backend FastAPI rodando em http://localhost:8000
[ ] Verificar CORS configurado no backend
[ ] Editar .env.local se API está em port diferente
[ ] npm run dev
[ ] Verificar Network tab no DevTools para requisições
[ ] Testar login com email/senha reais
[ ] Substituir dados mockados pelos reais
[ ] Implementar tratamento de erros
[ ] Testar em produção

═══════════════════════════════════════════════════════════════════

🆘 TROUBLESHOOTING:

ERRO: "CORS error"
→ Adicione CORSMiddleware no FastAPI com allow_origins

ERRO: "404 Not Found"
→ Verifique URL em .env.local
→ Verifique que FastAPI está rodando em 8000

ERRO: "Network Error"
→ Verifique se backend está rodando: python start_server.py
→ Verifique firewall/antivírus

ERRO: "Unauthorized 401"
→ Token vencido ou inválido
→ Limpar localStorage: localStorage.clear()
→ Fazer login novamente

═══════════════════════════════════════════════════════════════════

📚 DOCUMENTAÇÃO COMPLETA:

Veja arquivo: src/services/api.js

Cada função tem comentários explicando:
- Parâmetros esperados
- Retorno esperado
- Como usar

═══════════════════════════════════════════════════════════════════

🚀 PRONTO PARA CONECTAR!

Seu frontend React está 100% preparado para se conectar
ao seu backend FastAPI!

Comande:
  npm run dev

E teste sua integração! 🎉

═══════════════════════════════════════════════════════════════════
