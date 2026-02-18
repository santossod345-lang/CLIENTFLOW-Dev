# ClientFlow - Validação Local Pré-Deploy

Antes de fazer deploy em Railway + Vercel, valide tudo localmente com este guia.

---

## ✅ Checklist - Antes do Deploy

### Base de Dados
- [ ] PostgreSQL instalado e rodando em localhost:5432
- [ ] Banco de dados criado: `createdb clientflow`
- [ ] Variável `DATABASE_URL` configurada (local)
- [ ] Migração executada: `alembic upgrade head`

### Backend
- [ ] Python 3.10+ instalado
- [ ] Venv ativado: `\venv\Scripts\activate` (Windows)
- [ ] Dependências: `pip install -r requirements.txt`
- [ ] `.env` criado com variáveis locais
- [ ] Backend rodando: `python -m uvicorn main:app --reload`
- [ ] Health check: `curl http://localhost:8000/api/health`
- [ ] API docs acessível: `http://localhost:8000/docs`

### Frontend
- [ ] Node.js 18.17+ instalado
- [ ] npm ou yarn disponível
- [ ] Frontend instalado: `npm install` (em clientflow-frontend)
- [ ] Dev server rodando: `npm run dev`
- [ ] Acessível em: `http://localhost:5173`
- [ ] API conectada corretamente

### Testes Funcionais
- [ ] Cadastro de empresa funcionando
- [ ] Login funcionando
- [ ] Dashboard carregando dados
- [ ] Upload de logo funcionando
- [ ] Perfil da empresa editável
- [ ] CORS sem erros no console

---

## 🔧 Setup Local Rápido

### 1. Banco de Dados PostgreSQL

**Windows (se usando PostgreSQL):**
```bash
# Criar banco
createdb clientflow

# Verificar
psql -l | grep clientflow
```

**Linux/Mac:**
```bash
createdb clientflow
```

**Variável de ambiente:**
```bash
# Windows (PowerShell)
$env:DATABASE_URL="postgresql://postgres:password@localhost:5432/clientflow"

# Linux/Mac
export DATABASE_URL="postgresql://postgres:password@localhost:5432/clientflow"

# Ou em .env
DATABASE_URL=postgresql://postgres:password@localhost:5432/clientflow
```

### 2. Backend

```bash
cd ClientFlow
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Executar migrations
python -m alembic upgrade head

# Rodar backend
python -m uvicorn main:app --reload
```

**Verificar:**
```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/health
```

### 3. Frontend

```bash
cd clientflow-frontend
npm install
npm run dev
```

**Acesso:**
```
http://localhost:5173
```

---

## 🧪 Testes de Validação

### 1. Teste de Cadastro

**Criar empresa:**
```bash
curl -X POST http://localhost:8000/api/empresas/cadastrar \
  -H "Content-Type: application/json" \
  -d '{
    "email_login": "teste@empresa.com",
    "senha": "Senha123!",
    "nome_empresa": "Minha Empresa",
    "nicho": "Serviços"
  }'
```

**Resposta esperada:**
```json
{
  "status": "success",
  "message": "Empresa criada com sucesso",
  "data": {...}
}
```

### 2. Teste de Login

```bash
curl -X POST http://localhost:8000/api/empresas/login \
  -H "Content-Type: application/json" \
  -d '{
    "email_login": "teste@empresa.com",
    "senha": "Senha123!"
  }'
```

**Resposta esperada:**
```json
{
  "status": "success",
  "data": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "bearer"
  }
}
```

### 3. Teste de Perfil

```bash
TOKEN="seu-access-token-aqui"

curl http://localhost:8000/api/empresas/me \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Teste de Upload de Logo

```bash
TOKEN="seu-access-token-aqui"

curl -X POST http://localhost:8000/api/empresas/logo \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/caminho/para/logo.jpg"
```

**Resposta esperada:**
```json
{
  "status": "success",
  "data": {
    "logo_url": "/uploads/logos/logo_empresa_1.jpg",
    "filename": "logo_empresa_1.jpg"
  }
}
```

### 5. Teste de Dashboard

**No navegador:**
```
http://localhost:5173/dashboard
```

Deve carregar:
- ✓ Estatísticas
- ✓ Tabela de clientes
- ✓ Agendamentos
- ✓ Gráfico de faturamento
- ✓ Logo no header

---

## 🔍 Checklist de Validação

### Backend
- [ ] `python -m uvicorn main:app --reload` inicia sem erros
- [ ] `/api/health` retorna `{"status": "ok"}`
- [ ] `/docs` abre sem problemas
- [ ] Banco de dados conecta
- [ ] Migrações rodam sem erro
- [ ] Endpoint cadastro funciona
- [ ] Endpoint login funciona
- [ ] Endpoint perfil funciona
- [ ] Endpoint upload logo funciona

### Frontend
- [ ] `npm run dev` inicia sem erros
- [ ] `npm run build` completa sem erros
- [ ] Build size < 600KB
- [ ] Página de login carrega
- [ ] Cadastro funciona
- [ ] Login funciona
- [ ] Dashboard carrega dados
- [ ] Perfil da empresa exibe
- [ ] Upload de logo funciona
- [ ] Logo aparece no header

### Integrações
- [ ] Frontend conecta ao backend
- [ ] Sem erros CORS no console
- [ ] Tokens salvos em localStorage
- [ ] Refresh token funciona
- [ ] Logout limpa localStorage
- [ ] Rotas protegidas funcionam

### Performance
- [ ] Frontend carrega em < 3s
- [ ] API responde em < 200ms
- [ ] Sem memory leaks
- [ ] Sem console errors

---

## 🐛 Troubleshooting Local

### "Database connection refused"
```
Solução: PostgreSQL rodando?
1. windows: Services → PostgreSQL
2. Linux: sudo systemctl start postgresql
3. Verificar DATABASE_URL está correto
```

### "CORS error on login"
```
Solução: Backend não está rodando
1. Verificar se uvicorn está rodando em 8000
2. Verificar localhost:8000/api/health responde
```

### "Cannot find module 'react'"
```
Solução: npm install não foi executado
cd clientflow-frontend
npm install
```

### "npm run build fails"
```
Possíveis causas:
1. VITE_API_URL não definida → criar .env
2. Dependências faltam → npm install
3. Erro de dist → rm -rf dist && npm run build
```

### "API 404 on endpoints"
```
Solução: Verificar que main:app é o correto
1. Backend: from backend.main import app (NOT import main)
2. Ou simplificar: gunicorn backend.main:app
```

---

## 📝 Criar arquivo `.env` Local

**Arquivo: `.env` na raiz do projeto**

```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/clientflow

# Security
SECRET_KEY=seu-secret-super-seguro-para-desenvolvimento-local
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Environment
ENVIRONMENT=development
LOG_LEVEL=INFO

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8000

# Features
ENABLE_AI_ASSISTANT=false
```

**Arquivo: `clientflow-frontend/.env.local`**

```env
VITE_API_URL=http://localhost:8000/api
VITE_APP_NAME=ClientFlow
```

---

## ✅ Validação Final Pre-Deploy

Antes de fazer push para GitHub (que dispara deploy automático):

```bash
# 1. Parar todos serviços
# Ctrl+C no terminal do backend
# Ctrl+C no terminal do frontend

# 2. Limpar builds
rm -rf clientflow-frontend/dist
rm -rf clientflow-frontend/node_modules/.vite

# 3. Reinstalar fresh
pip install -r requirements.txt --upgrade
cd clientflow-frontend && npm install

# 4. Executar migrations novamente
python -m alembic downgrade base
python -m alembic upgrade head

# 5. Rodar completo
python -m uvicorn main:app --reload
# Em outro terminal:
cd clientflow-frontend && npm run dev

# 6. Testar tudo
# - Cadastrar empresa
# - Fazer login
# - Acessar dashboard
# - Fazer upload de logo
```

---

## 🎯 Quando Fazer Deploy

Você está pronto para deploy quando:

- [ ] Todos os testes passam locally
- [ ] Sem erros no console (browser + terminal)
- [ ] Sem warnings no build
- [ ] Funcionalidades principais testadas
- [ ] Credenciais sensíveis em `.env` (não commitadas)
- [ ] Código commitado e clean

---

## 📋 Comando Single de Deploy

Quando tudo está validado:

```bash
# 1. Fazer commit final
git add .
git commit -m "Prepare for production deployment - all tests passing"

# 2. Push para main (Railway + Vercel pegam automaticamente)
git push origin main

# 3. Monitorar deploy
# Railway: https://railway.app (logs em tempo real)
# Vercel: https://vercel.com (build status)

# 4. Testar URLs
# Frontend: https://seu-app.vercel.app
# Backend: https://seu-id.railway.app/api/health
```

---

## 🎉 Próximo Passo

Após validação com sucesso:

1. Seguir `DEPLOYMENT_QUICK_START.md`
2. Deploy leva ~2-3 minutos no Railway
3. Deploy leva ~2-3 minutos no Vercel
4. Sistema fica online

**Total: ~5 minutos do push ao ar!**

---

**Status**: ✅ Pronto para Validação Local
**Próximo**: DEPLOYMENT_QUICK_START.md
**Tempo Estimado**: 15-20 minutos (validação + testes)
