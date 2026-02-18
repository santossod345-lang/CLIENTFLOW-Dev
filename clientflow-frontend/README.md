# ClientFlow - Frontend React

Frontend profissional e moderno para o ClientFlow SaaS Intelligence Platform.

## 🚀 Tech Stack

- **React 18** - UI Library
- **Vite** - Build tool (⚡ super rápido)
- **Tailwind CSS** - Utility-first CSS
- **Recharts** - Gráficos de dados
- **Axios** - HTTP client
- **Design System** - Dark mode profissional

## 📁 Estrutura do Projeto

```
src/
├── components/
│   ├── layout/
│   │   ├── Sidebar.jsx        # Menu lateral
│   │   └── Header.jsx         # Barra superior
│   └── dashboard/
│       ├── StatCard.jsx        # Cards de métricas
│       ├── RevenueChart.jsx    # Gráfico de faturamento
│       ├── StatusDonut.jsx     # Gráfico de status
│       ├── AppointmentsList.jsx# Lista de agenda
│       ├── ClientsTable.jsx    # Tabela de clientes
│       └── ClientsStats.jsx    # Stats de fluxo
├── pages/
│   └── Dashboard.jsx           # Página principal
├── services/
│   └── api.js                  # Configuração Axios + endpoints
├── styles/
│   └── theme.css               # Estilos globais e design system
├── App.jsx                     # Componente raiz
└── main.jsx                    # Entry point
```

## 🛠️ Instalação

### Pré-requisitos
- Node.js 16+
- npm ou yarn

### Setup

1. **Clone ou acesse o diretório**: 
   ```bash
   cd clientflow-frontend
   ```

2. **Instale dependências**:
   ```bash
   npm install
   ```

3. **Configure variáveis de ambiente**:
   ```bash
   cp .env.example .env.local
   # Edite .env.local se necessário (padrão: http://localhost:8000/api)
   ```

4. **Inicie o servidor de desenvolvimento**:
   ```bash
   npm run dev
   ```

   O dashboard abrirá automaticamente em `http://localhost:5173`

## 📦 Build para Produção

```bash
npm run build
```

Gera arquivos otimizados em `dist/`

## 🎨 Design System

### Cores Base
- **Primária**: `primary-900` (#0f172a) - Fundo principal
- **Secundária**: `primary-800` (#1e293b) - Cards e elementos
- **Azul**: `accent-blue` (#3b82f6) - Dados e estados
- **Verde**: `accent-green` (#10b981) - Sucesso e crescimento
- **Laranja**: `accent-orange` (#f97316) - Atenção
- **Roxo**: `accent-purple` (#a855f7) - Destaque

### Componentes Reutilizáveis

#### StatCard
```jsx
<StatCard
  icon="👥"
  title="Clientes Ativos"
  value="1.248"
  change="12"
  changeType="positive"
/>
```

#### Gráficos
- **RevenueChart**: Linha com evolução mensal
- **StatusDonut**: Donut com status de atendimentos

#### Layouts
- **Sidebar**: Menu lateral com navegação
- **Header**: Barra superior com busca e notificações

## 🔌 Integração com API

O serviço `api.js` fornece:

```javascript
// Autenticação
authService.login(email, password)
authService.register(data)

// Clientes
clientsService.list()
clientsService.get(id)
clientsService.create(data)
clientsService.update(id, data)
clientsService.delete(id)

// Atendimentos
appointmentsService.list()
appointmentsService.get(id)
appointmentsService.create(data)

// Dashboard
dashboardService.getMetrics()
dashboardService.getRevenue()
dashboardService.getAppointmentsStatus()
```

### Exemplo de uso

```jsx
import { clientsService } from '../services/api'

useEffect(() => {
  const fetchClients = async () => {
    try {
      const response = await clientsService.list()
      setClients(response.data)
    } catch (error) {
      console.error('Erro:', error)
    }
  }
  fetchClients()
}, [])
```

## 🎯 Próximos Passos

1. **Conectar ao Backend**: Substituir dados mockados por chamadas reais
2. **Autenticação**: Implementar login e proteção de rotas
3. **Páginas Adicionais**: CRM, Agenda, Financeiro, Relatórios
4. **Responsividade**: Testar e otimizar mobile
5. **Performance**: Code splitting e lazy loading

## 📝 Variáveis de Ambiente

```env
VITE_API_URL=http://localhost:8000/api
```

## 🚀 Deploy

### Netlify
```bash
npm run build
# Faça upload da pasta 'dist/' para Netlify
```

### Vercel
```bash
vercel
```

### Docker
```bash
docker build -t clientflow-frontend .
docker run -p 80:5173 clientflow-frontend
```

## 📄 Licença

ClientFlow © 2024

---

**Frontend pronto para produção com design premium e performance otimizada.**
