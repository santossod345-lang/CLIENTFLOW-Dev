# ClientFlow - Deployment Rápido (5 minutos)

## ✅ Pré-requisitos

- [ ] Conta no [Railway.app](https://railway.app)
- [ ] Conta no [Vercel](https://vercel.app)
- [ ] GitHub/GitLab com código
- [ ] Git local configurado

---

## 🚀 PARTE 1: Backend (Railway) - 2 minutos

### 1. Push para GitHub
```bash
cd ClientFlow
git add .
git commit -m "Prepare for production deployment"
git push origin main
```

### 2. Deploy no Railway
```
1. Acesse railway.app
2. Clique "New Project"
3. Selecione "Deploy from GitHub"
4. Escolha repo ClientFlow
5. Railway detecta automaticamente Procfile + requirements.txt
```

### 3. Adicionar Variáveis (Railway Dashboard)

```
SECRET_KEY=<gerar com: python -c "import secrets; print(secrets.token_urlsafe(32))">
ENVIRONMENT=production
ALLOWED_ORIGINS=https://clientflow.vercel.app,https://api.clientflow.app
LOG_LEVEL=INFO
```

### 4. Adicionar PostgreSQL
```
1. Railway → Add Service → PostgreSQL
2. Railway configura DATABASE_URL automaticamente
3. Pronto! Deploy começa automático
```

### ✓ Resultado
```
Backend rodando em: https://seu-id.railway.app
Health check: https://seu-id.railway.app/api/health
API: https://seu-id.railway.app/api
```

---

## 🎨 PARTE 2: Frontend (Vercel) - 2 minutos

### 1. Deploy no Vercel
```
1. Acesse vercel.com
2. Clique "New Project"
3. Selecione repositório ClientFlow
4. Framework: Vite (detectado automaticamente)
5. Root Directory: clientflow-frontend
```

### 2. Variáveis de Ambiente (Vercel Dashboard)
```
VITE_API_URL=https://seu-id.railway.app/api
```

### 3. Deploy
```
Clique "Deploy"
Vercel faz build + deploy automaticamente
```

### ✓ Resultado
```
Frontend rodando em: https://seu-app.vercel.app
```

---

## 📊 PARTE 3: Testar - 1 minuto

### Health Check
```bash
curl https://seu-id.railway.app/api/health
# Resposta esperada: {"status": "ok", "version": "1.0.0"}
```

### Acessar Sistema
```
https://seu-app.vercel.app

Login com credenciais de teste
Dashboard em: https://seu-app.vercel.app/dashboard
```

### Testar Upload de Logo
```
1. Acesse /empresa
2. Faça upload de imagem JPG/PNG
3. Verifique se aparece no Header
```

---

## 🔐 Segurança Checklist

- [ ] SECRET_KEY é único e seguro (32+ caracteres)
- [ ] DATABASE_URL não está em código (em Railway Variables)
- [ ] CORS configurado apenas para seu domínio
- [ ] HTTS ativado (automático em Railway + Vercel)
- [ ] Logs em INFO (não DEBUG em produção)

---

## 📈 Escalabilidade (Opcional)

### Se tiver múltiplos usuários simultâneos:

**Railway:**
```
Railway → Project → Settings → Scaling
Aumento automático de workers quando necessário
```

**Vercel:**
```
Vercel → Project → Settings → Regions
Adicionar mais regions (automático)
```

---

## 🚨 Troubleshooting Rápido

### Erro de Build no Vercel
```
Solução: Verificar que clientflow-frontend/package.json existe
Vercel → Build Logs → ver erro específico
```

### Erro 502 no Backend (Railway)
```
Solução 1: Aguardar deploy (leva 2-3 min)
Solução 2: Railway → Logs → verificar erro
Solução 3: DATABASE_URL está configurada?
```

### CORS Error no Frontend
```
Solução: Adicionar domínio em ALLOWED_ORIGINS
Railway → Variables → adicionar seu domínio Vercel
```

---

## 📞 URLs em Produção

| Serviço | URL |
|---------|-----|
| Frontend | https://seu-app.vercel.app |
| Backend API | https://seu-id.railway.app/api |
| Health Check | https://seu-id.railway.app/api/health |
| API Docs | https://seu-id.railway.app/docs |
| Dashboard | https://seu-app.vercel.app/dashboard |

---

## 🎯 Próximas Melhorias

1. **Domínio personalizado**
   - Vercel: Domínios → Add Domain
   - Railway: Não necessário (use Railway domain ou seu DNS)

2. **Email de Recuperação**
   - Adicionar SendGrid/Mailgun para password recovery

3. **Backup de Banco**
   - Railway: Configurar backup automático (30 dias)

4. **Monitoring**
   - Railway: Habilitar monitoring em Databases
   - Vercel: Habilitar Analytics

5. **S3/Spaces para Logos**
   - Ver STORAGE_CONFIG.md para implementação

---

## ✨ Parabéns!

Sistema está em produção e acessível. 

**Próximo passo**: Convidar primeiros usuários! 🎉
