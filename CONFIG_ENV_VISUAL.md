# 🔧 GUIA VISUAL - Configurar Variáveis de Ambiente

## ✅ RESUMO RÁPIDO

```
Frontend (Vercel):    VITE_API_URL = https://clientflow-production-production.up.railway.app
Backend (Railway):    CORS_ORIGINS = ["https://clientflow-dev-one.vercel.app"]
```

---

## 🌐 VERCEL - VITE_API_URL

### Passo 1: Abra o Vercel
```
https://vercel.com/dashboard
```

### Passo 2: Clique no Projeto
- Procure por: **clientflow-dev-one**
- Clique nele

### Passo 3: Vá para Settings
```
Projeto → Settings (no topo)
```

### Passo 4: Environment Variables
```
Settings → Environment Variables (lado esquerdo)
```

### Passo 5: Adicione/Atualize a Variável

**Se JÁ EXISTE:**
1. Procure por `VITE_API_URL`
2. Clique no lápis (edit)
3. Altere o valor para:
```
https://clientflow-production-production.up.railway.app
```
4. Clique "Save"

**Se NÃO EXISTE:**
1. Clique "Add New"
2. Name: `VITE_API_URL`
3. Value: `https://clientflow-production-production.up.railway.app`
4. Clique "Add"

### Passo 6: Redeploy
- Vá para: **Deployments** (topo)
- Clique nos 3 pontinhos "..." do último deploy
- Selecione: **Redeploy**
- Aguarde ~2 minutos

✅ **Pronto! Vercel atualizado.**

---

## 🚂 RAILWAY - CORS_ORIGINS

### Passo 1: Abra o Railway
```
https://railway.app/dashboard
```

### Passo 2: Clique no Projeto
- Procure por: **ClientFlow** (ou seu nome de projeto)
- Clique nele

### Passo 3: Vá para Settings
```
Projeto → Settings (topo direito)
```

### Passo 4: Variables
```
Settings → Variables (lado esquerdo)
```

### Passo 5: Adicione/Atualize CORS_ORIGINS

**Se JÁ EXISTE:**
1. Procure por `CORS_ORIGINS`
2. Clique para editar
3. Altere o valor para:
```
["https://clientflow-dev-one.vercel.app"]
```
4. Clique "Save"

**Se NÃO EXISTE:**
1. Clique "Add New Variable"
2. Key: `CORS_ORIGINS`
3. Value: `["https://clientflow-dev-one.vercel.app"]`
4. Clique "Save"

### Passo 6: Reinicie
- Vá para: **Deployments**
- Clique no último deploy
- Clique "Restart"
- Aguarde ~1 minuto

✅ **Pronto! Railway atualizado.**

---

## 🧪 TESTAR

### 1. Backend Health Check
```
https://clientflow-production-production.up.railway.app/api/health
```
Deve retornar: `{"status":"ok"}`

### 2. Tente Logar
1. Abra: https://clientflow-dev-one.vercel.app
2. Email: `luizfernandoantonio345@gmail.com`
3. Senha: (a que você configurou no cadastro)
4. Clique: **Entrar**

✅ **Se funcionar, está tudo OK!**

---

## ⚠️ TROUBLESHOOTING

### Frontend diz "VITE_API_URL não configurada"
- ✗ Significa que a variável não foi adicionada ou não foi deployada
- ✓ Solução: Adicione em Vercel → Redeploy

### Backend retorna 401 (Não Autorizado)
- ✗ O usuário/empresa não existe no banco
- ✓ Solução: Cadastrar um novo usuário:

**POST** para:
```
https://clientflow-production-production.up.railway.app/api/empresas/cadastrar
```

Body:
```json
{
  "nome_empresa": "Minha Empresa",
  "nicho": "Oficina",
  "telefone": "11999999999",
  "email_login": "seu@email.com",
  "senha": "SenhaForte123!"
}
```

Depois tente logar com esse email e senha.

### Backend retorna 403 (CORS Error)
- ✗ CORS_ORIGINS não está configurado corretamente no Railway
- ✓ Solução: Verifique se adicionou exatamente:
```
["https://clientflow-dev-one.vercel.app"]
```

### Backend não responde (timeout)
- ✗ Railway pode estar desligado ou em build
- ✓ Solução: Vá para Railway → Logs e veja o status

---

## 📋 CHECKLIST

- [ ] Vercel: VITE_API_URL adicionado/atualizado
- [ ] Vercel: Redeploy feito
- [ ] Railway: CORS_ORIGINS adicionado/atualizado
- [ ] Railway: Reiniciado
- [ ] Backend health check respondendo
- [ ] Login funcionando
- [ ] 🎉 Tudo OK!

---

## 🆘 Se Ainda Não Funcionar

Abra DevTools (F12) → Network → tente logar e me diga:
1. Qual é o status do POST `/api/empresas/login`? (200, 401, 403, 404, 500?)
2. Qual é a resposta (response) exata?

Com isso eu identifíco na hora!

---

*Guia atualizado: 20 de Fevereiro de 2026*
