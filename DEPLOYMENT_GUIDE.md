# ClientFlow - Guia de Deploy em Produção

## 📋 Resumo do Projeto

ClientFlow é uma plataforma SaaS completa para gerenciamento de clientes e atendimentos com:
- ✅ Autenticação JWT multi-empresa
- ✅ Dashboard com métricas
- ✅ Gerenciamento de clientes e atendimentos
- ✅ Upload de logos
- ✅ Perfil personalizável da empresa

---

## 🚀 PARTE 1: DEPLOY DO BACKEND (RAILWAY)

### 1.1 Pré-requisitos
- Conta no [Railway.app](https://railway.app)
- SQL PostgreSQL (pode ser provisionado pelo Railway)
- Git configurado

### 1.2 Passos para Deploy

#### 1. Conectar repositório
```bash
cd ClientFlow
git init
git add .
git commit -m "Initial commit"
git branch -M main
# Adicionar remote do seu repositório GitHub/GitLab
git remote add origin <seu-repositorio>
git push -u origin main
```

#### 2. Provisionar no Railway
1. Acesse [railway.app](https://railway.app)
2. Clique em "New Project"
3. Selecione "Deploy from GitHub"
4. Autorize e selecione o repositório `ClientFlow`
5. Railway detectará automaticamente o `Procfile` e `requirements.txt`

#### 3. Configurar Variáveis de Ambiente

No painel do Railway, adicione estas variáveis de ambiente:

```
SECRET_KEY=seu-secret-key-super-seguro-aleatorio-32-caracteres
ENVIRONMENT=production
DATABASE_URL=postgresql://user:password@host:5432/dbname
ALLOWED_ORIGINS=https://clientflow.vercel.app,https://api.clientflow.app
LOG_LEVEL=INFO
ENABLE_AI_ASSISTANT=false
```

**Como gerar um SECRET_KEY seguro:**
```python
import secrets
print(secrets.token_urlsafe(32))
```

#### 4. Provisionar Banco de Dados PostgreSQL

No Railway:
1. Clique em "Add Service"
2. Selecione "PostgreSQL"
3. Railway configurará `DATABASE_URL` automaticamente
4. Migração executará automaticamente no deploy

#### 5. Deploy
```bash
# Se estiver usando Railway CLI:
railway up

# Ou simplesmente faça push para sua branch main
git push origin main
```

---

## 🎨 PARTE 2: DEPLOY DO FRONTEND (VERCEL)

### 2.1 Pré-requisitos
- Conta no [Vercel](https://vercel.com)
- Frontend no GitHub/GitLab

### 2.2 Passos para Deploy

#### 1. Conectar no Vercel
1. Acesse [vercel.com](https://vercel.com)
2. Clique em "New Project"
3. Selecione "Import Git Repository"
4. Selecione o repositório ClientFlow
5. Defina "Root Directory" como `clientflow-frontend`

#### 2. Configurar Variáveis de Ambiente

No painel do Vercel, adicione:

```
VITE_API_URL=https://seu-backend-railway.railway.app/api
```

#### 3. Build & Deploy

Vercel fará o build automaticamente:
- Executa `npm run build`
- Gera bundle otimizado em `dist/`
- Deploy automático ao fazer push para `main`

**Resultado:**
```
Frontend: https://clientflow.vercel.app
Backend:  https://seu-backend.railway.app/api
```

---

## 🗄️ PARTE 3: BANCO DE DADOS

### 3.1 Setup PostgreSQL no Railway

1. **Banco é criado automaticamente** quando você seleciona PostgreSQL no Railway
2. **Migração automática**: 
   ```bash
   python -m alembic upgrade head
   ```
   Executa automaticamente no Procfile

3. **Variáveis:
   - Railway gera `DATABASE_URL` automaticamente
   - Formato: `postgresql://user:password@host:port/dbname`

### 3.2 Backups
- Railway oferece backups automáticos
- Configure retenção de 30 dias no painel

---

## 🔐 PARTE 4: SEGURANÇA

### 4.1 Variáveis Sensíveis

**Nunca commitar** em Git:
```
.env (local development)
.env.production.local
SECRET_KEY
DATABASE_PASSWORD
OPENAI_API_KEY
```

Use Railway Variables para produção.

### 4.2 CORS

**Configurado em `backend/core/config.py`:**
```python
ALLOWED_ORIGINS = [
    "https://clientflow.vercel.app",
    "https://api.clientflow.app",
]
```

Ajuste conforme seus domínios.

### 4.3 JWT

- **Expiração**: 15 minutos (access token)
- **Refresh**: 7 dias (refresh token)
- **Secret**: Gerado aleatoriamente, armazenado em Railway Variables

### 4.4 Uploads

Logos são salvos em `/uploads/logos/` no container do Railway.

**⚠️ Importante**: Em produção com múltiplas instâncias, considere usar S3/Digital Ocean Spaces:

```python
# backend/routers/empresa.py
# Implementar upload para S3 em vez do filesystem
import boto3
```

---

## 📊 PARTE 5: MONITORAMENTO

### 5.1 Health Check

API expõe 2 endpoints de health check:
- `GET /health` - Full check (database)
- `GET /api/health` - Simple check (para load balancers)

### 5.2 Logs

**No Railway:**
- Acesse "Monitoring" → "Logs"
- Veja logs em tempo real

**Configurado:**
```
LOG_LEVEL=INFO
```

### 5.3 Performance

- **Workers**: 4 (configurado em Procfile)
- **Timeout**: 60 segundos
- **Rate limit**: 60 requests/minuto por padrão

---

## 🔄 PARTE 6: CI/CD

### 6.1 Fluxo de Deploy

```
Git push origin main
    ↓
Railway: Pega mudanças
    ↓
Executa: pip install + migrate + start
    ↓
Vercel: Detecta mudanças em clientflow-frontend
    ↓
Vercel: npm run build + deploy
    ↓
Sistema online!
```

### 6.2 Manual Deploy

Se precisar fazer deploy manualmente:

**Backend:**
```bash
git push origin main
# Railway pega mudanças automaticamente
```

**Frontend:**
```bash
git push origin main
# Vercel pega mudanças automaticamente
```

---

## 📱 PARTE 7: TESTAR EM PRODUÇÃO

1. **Frontend:**
   ```
   https://clientflow.vercel.app
   ```

2. **Login:**
   - Email: seu-email@empresa.com
   - Senha: sua-senha

3. **Testar Endpoints:**
   ```bash
   curl https://seu-backend.railway.app/api/health
   # Deve retornar: {"status": "ok", "version": "1.0.0"}
   ```

4. **Upload de Logo:**
   - Vá para /empresa
   - Faça upload de uma logo (JPG, PNG, WEBP)
   - Verifique se aparece no Header

---

## ⚙️ PART 8: TROUBLESHOOTING

### Erro: "Database connection failed"
```
Solução: Verificar DATABASE_URL no Railway
rails console: python -c "from sqlalchemy import create_engine; engine = create_engine(DATABASE_URL)"
```

### Erro: "CORS blocked request"
```
Solução: Adicionar domínio em ALLOWED_ORIGINS no Railway Variables
```

### Erro: "Build failed - npm not found"
```
Solução: Vercel detecta Node automaticamente. Confirme:
- Arquivo clientflow-frontend/package.json existe
- nodeVersion em vercel.json = "18.17.0"
```

### Uploads não aparecem em produção
```
Solução: Railway usa filesystem efêmero. Para produção:
1. Implemente S3/DigitalOcean Spaces
2. Ou use CDN (Cloudflare, AWS CloudFront)
```

---

## 📈 PRÓXIMOS PASSOS

1. ✅ Backend em Railway
2. ✅ Frontend em Vercel
3. ✅ Banco PostgreSQL
4. ⏭️ Implementar S3 para uploads
5. ⏭️ Configurar DNS personalizado
6. ⏭️ Adicionar SSL/TLS (automático em ambas plataformas)
7. ⏭️ Configurar backup automático de banco

---

## 📧 CONTATO & SUPORTE

- **Server Status**: `https://seu-backend.railway.app/api/health`
- **Documentation**: `https://seu-backend.railway.app/docs`
- **Logs**: Railway Dashboard → Monitoring → Logs

---

## ✨ Checklist Final

- [ ] Backend deployado no Railway
- [ ] Frontend deployado no Vercel
- [ ] Banco PostgreSQL em Railway
- [ ] CORS configurado
- [ ] Variáveis de ambiente definidas
- [ ] Health check funcionando
- [ ] Login funcionando em produção
- [ ] Upload de logo funcionando
- [ ] Domínios configurados (opcional)
- [ ] Backups configurados

**Parabéns! ClientFlow está em produção! 🎉**
