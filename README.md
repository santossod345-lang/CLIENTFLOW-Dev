# ClientFlow - Sistema SaaS Multi-Tenant

Sistema completo de gestão de clientes e atendimentos para negócios locais (mecânicas, oficinas, etc).

## 🚀 Tecnologias

### Backend
- **Python 3.8+**
- **FastAPI** - Framework web moderno e rápido
- **SQLAlchemy** - ORM para banco de dados
- **SQLite** - Banco de dados (estrutura pronta para escalar)
- **Passlib + Bcrypt** - Criptografia de senhas

### Frontend
- **HTML5**
- **CSS3** (Tema escuro profissional)
- **JavaScript Puro** (Vanilla JS)

## 📁 Estrutura do Projeto

```
ClientFlow/
├── backend/
│   ├── main.py          # API principal com todas as rotas
│   ├── database.py      # Configuração do banco de dados
│   ├── models.py        # Modelos SQLAlchemy (Empresa, Cliente, Atendimento)
│   └── auth.py          # Sistema de autenticação e criptografia
├── frontend/
│   ├── login.html       # Página de login e cadastro
│   ├── dashboard.html   # Dashboard principal
│   ├── script.js        # Funções JavaScript compartilhadas
│   └── style.css        # Estilos CSS tema escuro
├── requirements.txt     # Dependências Python
├── clientflow.db       # Banco de dados SQLite (criado automaticamente)
└── README.md           # Este arquivo
```

## 🗄️ Estrutura do Banco de Dados

### Tabela: empresas
- id (PK)
- nome_empresa
- nicho
- telefone
- email_login (unique)
- senha_hash
- data_cadastro

### Tabela: clientes
- id (PK)
- empresa_id (FK)
- nome
- telefone
- data_primeiro_contato

### Tabela: atendimentos
- id (PK)
- empresa_id (FK)
- cliente_id (FK)
- tipo
- descricao
- veiculo
- data

## 🛠️ Instalação e Execução

### 1. Instalar dependências Python

```bash
pip install -r requirements.txt
```

### 2. Iniciar o servidor backend

```bash
cd backend
python main.py
```

O servidor estará disponível em: `http://localhost:8000`

### 3. Acessar o frontend

Abra o arquivo `frontend/login.html` em seu navegador ou use um servidor local:

```bash
cd frontend
python -m http.server 3000
```

Acesse: `http://localhost:3000/login.html`

## 📝 API Endpoints

### Autenticação
- `POST /api/empresas/cadastrar` - Cadastrar nova empresa
- `POST /api/empresas/login` - Fazer login
- `POST /api/empresas/logout` - Fazer logout

### Clientes
- `POST /api/clientes` - Criar cliente
- `GET /api/clientes` - Listar clientes da empresa
- `GET /api/clientes/{id}` - Obter cliente específico

### Atendimentos
- `POST /api/atendimentos` - Criar atendimento
- `GET /api/atendimentos` - Listar atendimentos da empresa
- `GET /api/atendimentos/{id}` - Obter atendimento específico

### Dashboard
- `GET /api/dashboard` - Obter estatísticas e dados do dashboard

## 🔐 Segurança

- Senhas criptografadas com **bcrypt**
- Sistema de sessão com tokens únicos
- Multi-tenant: cada empresa acessa apenas seus dados
- Validação de dados com Pydantic

## 🎨 Funcionalidades

### ✅ Implementadas (V1)
- [x] Sistema de login e cadastro de empresas
- [x] Dashboard com estatísticas
- [x] Cadastro de clientes
- [x] Registro de atendimentos
- [x] Listagem de clientes por empresa
- [x] Listagem de atendimentos por empresa
- [x] Interface moderna tema escuro
- [x] Sistema multi-tenant completo
- [x] API REST completa com FastAPI
- [x] Documentação automática (Swagger)

### 🔮 Próximas Funcionalidades (V2)
- [ ] Sistema de planos e assinaturas
- [ ] Integração com WhatsApp
- [ ] Notificações automáticas
- [ ] Relatórios e gráficos
- [ ] Busca avançada
- [ ] Filtros por data
- [ ] Exportação de dados
- [ ] Sistema de permissões

## 📊 Documentação da API

Acesse a documentação interativa automática do FastAPI:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🌐 Deploy (Produção)

### Backend
Para deploy do backend, recomenda-se:
- **Heroku, Railway, ou Render** para hospedagem
- Migrar para **PostgreSQL** em produção
- Implementar **Redis** para sessões
- Adicionar **JWT** para autenticação mais robusta

### Frontend
Para deploy do frontend, recomenda-se:
- **Netlify** ou **Vercel** para hospedagem
- Atualizar a URL da API em `script.js`
- Implementar variáveis de ambiente

## 🤝 Contribuindo

Este é um projeto base para SaaS. Sinta-se livre para:
- Adicionar novas funcionalidades
- Melhorar a interface
- Otimizar o código
- Adicionar testes

## 📄 Licença

Projeto desenvolvido para fins educacionais e comerciais.

## 👤 Autor

Sistema desenvolvido para automação de atendimento em negócios locais.

---

**ClientFlow v1.0.0** - Transformando conversas em dados organizados 🚀
