# 🚀 DEPLOY DO CLIENTFLOW - PASSO A PASSO

## ⏱️ Leitura: 2 minutos | Execução: 5 minutos

---

## PASSO 1️⃣ - Gerar Secrets (1 min)

### Abrir Terminal na pasta ClientFlow

```bash
cd C:\Users\Sueli\Desktop\ClientFlow
python generate_secrets.py
```

**Saída esperada:**
```
🔐 SECRETS GERADOS (Salve em local seguro)
SECRET_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Copie o `SECRET_KEY` (você vai precisar)

---

## PASSO 2️⃣ - Fazer Commit (1 min)

### Terminal:
```bash
git add .
git commit -m "Prepare ClientFlow for production deployment"
git push origin main
```

### Ou via GitHub Desktop:
1. Abra GitHub Desktop
2. "Current Branch" → selecione "main"
3. Clique "Publish" ou "Push"

---

## PASSO 3️⃣ - Railway Setup (1 min)

### 3.1 Criar conta
- Acesse: https://railway.app
- Clique "Sign Up"
- Autorize com GitHub (recomendado)

### 3.2 Novo projeto
- Clique "New Project"
- "Deploy from GitHub"
- Selecione "ClientFlow"

### 3.3 Adicionar variáveis
- Click "Add Variable"
- Name: `SECRET_KEY`
- Value: `<copie do output do generate_secrets.py>`
- Click "Save"

**Adicione também:**
- `ENVIRONMENT` = `production`
- `ALLOWED_ORIGINS` = `https://seu-app.vercel.app`
- `LOG_LEVEL` = `INFO`

### 3.4 Adicionar PostgreSQL
- Click "Add Service"
- Selecione "PostgreSQL"
- Railway configura `DATABASE_URL` automaticamente
- Deploy começa!

**Aguarde**: ~3-5 minutos

---

## PASSO 4️⃣ - Vercel Setup (1 min)

### 4.1 Criar conta
- Acesse: https://vercel.com
- Clique "Sign Up"
- Autorize com GitHub

### 4.2 Novo projeto
- Clique "New Project"
- "Add GitHub App"
- Autorize
- Selecione "ClientFlow"

### 4.3 Configurar
- Framework: "Vite" (detectado automaticamente)
- Root Directory: `clientflow-frontend`
- Click "Deploy"

### 4.4 Adicionar variável
- Vercel → Settings → Environment Variables
- Name: `VITE_API_URL`
- Value: `https://seu-api.railway.app/api` (copie da Railway)
- Save e Redeploy

**Aguarde**: ~2-3 minutos

---

## PASSO 5️⃣ - Testar (1 min)

### Frontend
```
https://seu-app.vercel.app
Deve carregar página de login
```

### Backend
```bash
curl https://seu-api.railway.app/api/health
```
Respostaesperada:
```json
{"status": "ok", "version": "1.0.0"}
```

### Login
1. Acesse frontend
2. Clique "Cadastrar"
3. Preencha dados
4. Clique "Cadastrar empresa"
5. Faça login
6. Veja dashboard

---

## ✅ PRONTO!

### URLs em Produção:
```
Frontend:  https://seu-app.vercel.app
Backend:   https://seu-api.railway.app
Database:  PostgreSQL (Railway)
```

---

## 🆘 Se não funcionar

### Erro: "Connection refused"
```
→ Railway ainda está deployando (aguarde 5 min)
→ Ou SECRET_KEY não foi setado
```

### Erro: "CORS error"
```
→ ALLOWED_ORIGINS em Railway não tem seu domínio Vercel
→ Adicione em Railways Variables
```

### Erro: "Failed to fetch /api"
```
→ VITE_API_URL em Vercel está incorreto
→ Deve ser: https://seu-api.railway.app/api
```

### Verificar Logs

**Railway:**
- Acesse railway.app
- Projeto → Logs
- Ver erros em tempo real

**Vercel:**
- Acesse vercel.com
- Projeto → Deployments
- Clique no deploy
- Ver Build Logs

---

## 📝 Checklist

- [ ] `generate_secrets.py` executado
- [ ] Código commitado e feito push
- [ ] Railway setup completo
- [ ] PostgreSQL adicionado
- [ ] Vercel setup completo
- [ ] Variables configuradas em ambas
- [ ] Frontend carregando
- [ ] Backend respondendo
- [ ] Login funcionando
- [ ] Dashboard exibindo

---

## 🎉 SUCESSO!

ClientFlow está online!

### Próximas ações:
1. Repouso (você merece! ☕)
2. Ler DEPLOYMENT_GUIDE.md para detalhes
3. Implementar feature de S3 para uploads (opcional)
4. Adicionar domínio customizado (opcional)
5. Convidar usuários (IMPORTANTE!)

---

**Tempo Total:** ~5-10 minutos ⏱️
**Nível de dificuldade:** Fácil 🟢
**Status:** ✅ Pronto para produção

Parabéns! 🎊
