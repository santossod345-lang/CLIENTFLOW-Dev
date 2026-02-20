# 🚀 CLIENTFLOW - DEPLOY PRODUCTION

## ⚡ LINKS RÁPIDOS (Copie e Cole)

### Railway (Backend + Database)
```
https://railway.app
```

### Vercel (Frontend)
```
https://vercel.com/new
```

### Seu Repositório
```
https://github.com/santossod345-lang/CLIENTFLOW-Dev
```

---

## ⏱️ PROCESSO RÁPIDO (15 minutos)

### 1️⃣ RAILWAY (5 minutos)
```
1. https://railway.app → "Create New Project"
2. "Deploy from GitHub"
3. Selecione: santossod345-lang/CLIENTFLOW-Dev
4. Branch: main
5. Clique: Deploy
6. Aguarde build (3-5 min)
7. Copie a URL pública
```

### 2️⃣ VERCEL (5 minutos)
```
1. https://vercel.com/new
2. Selecione: CLIENTFLOW-Dev
3. Framework: Vite
4. Root: clientflow-frontend/
5. Clique: Deploy
6. Aguarde build (2-3 min)
```

### 3️⃣ CONECTAR (3 minutos)
```
1. Railway: <copie-url-publica>
2. Vercel: Settings → Environment Variables
3. Adicione: VITE_API_URL=<railway-url>
4. Redeploy
```

---

## 📋 VARIÁVEIS DE AMBIENTE

**Railway necessita:**
```
JWT_SECRET_KEY=seu-secret-seguro
JWT_ALGORITHM=HS256
ENVIRONMENT=production
CORS_ORIGINS=["https://seu-vercel.app"]
```

**Vercel necessita:**
```
VITE_API_URL=https://seu-railway.railway.app
```

---

## ✅ CHECKLIST

- [ ] Repositório está em `main`
- [ ] Último commit foi pushed
- [ ] Railway build completo
- [ ] PostgreSQL conectado
- [ ] Vercel build completo
- [ ] VITE_API_URL apontando para Railway
- [ ] Frontend carrega sem erros
- [ ] Backend /docs acessível
- [ ] Login funcional
- [ ] 🎉 LIVE!

---

## 🔗 STATUS

| Componente | Status | URL |
|-----------|--------|-----|
| Repositório | ✅ Pronto | https://github.com/santossod345-lang/CLIENTFLOW-Dev |
| Backend | ⏳ Aguardando Railway | - |
| Frontend | ⏳ Aguardando Vercel | - |
| Database | ⏳ Aguardando Railway | PostgreSQL 15 |

---

## 📞 GUIA COMPLETO

Veja: `DEPLOYMENT_INSTRUCTIONS.md`

---

## 🎯 RESUMO

```
Você está aqui: ✅ Código pronto
    ↓
Railway: ⏳ Deploy backend
    ↓
Vercel: ⏳ Deploy frontend
    ↓
Conectar: URLs (Railway → Vercel)
    ↓
🎉 PRODUCTION LIVE
```

**Tempo total: 15-20 minutos**  
**Dificuldade: Fácil (cliques + cópias)**  
**Resultado: SaaS em produção**

---

_Preparado em 19 de Fevereiro de 2026_
