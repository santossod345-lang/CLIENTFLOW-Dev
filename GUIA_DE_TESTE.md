# 🚀 GUIA RÁPIDO DE TESTE - ClientFlow

## Como testar as correções imediatamente

### 1️⃣ Iniciar o Backend
```powershell
cd c:\Users\Sueli\Desktop\ClientFlow
.venv\Scripts\Activate.ps1
cd backend
python main.py
```

✅ **Esperado:** 
```
INFO: Started server process
INFO: Uvicorn running on http://0.0.0.0:8000
```

---

### 2️⃣ Iniciar o Frontend (em outro terminal)
```powershell
cd c:\Users\Sueli\Desktop\ClientFlow\clientflow-frontend
npm run dev
```

✅ **Esperado:**
```
VITE ready in XXX ms
Local: http://localhost:5173/
```

---

### 3️⃣ Acesse o navegador
Abra: **http://localhost:5173/#/login**

---

### 4️⃣ Teste o fluxo completo

#### **TESTE 1: Criar conta**
1. Clique em "Criar conta"
2. Preencha os dados
3. Clique em "Cadastrar"
4. ✅ Deve aparecer "Cadastro realizado com sucesso"

#### **TESTE 2: Fazer login**
1. Digite email e senha
2. Clique em "Entrar"
3. ✅ Deve redirecionar para `/dashboard`

#### **TESTE 3: Verificar dashboard**
1. ✅ **NÃO deve aparecer "Não autenticado"**
2. ✅ Clientes ativos deve mostrar número (não "—")
3. ✅ Atendimentos hoje deve mostrar número
4. ✅ Faturamento deve mostrar valor
5. ✅ Gráficos devem renderizar

#### **TESTE 4: Verificar console do navegador** (F12)
✅ **Deve aparecer:**
```
[AuthContext] Token encontrado ao carregar, restaurando sessão
[Dashboard] Carregando dados do dashboard...
[Dashboard] Dados carregados com sucesso
```

❌ **NÃO deve aparecer:**
```
[Dashboard] Não há token válido
[Dashboard] Token expirado ou inválido (401)
```

#### **TESTE 5: Verificar Network (F12 → Network)**
1. Recarregue a página (F5)
2. Filtre por "XHR"
3. Clique em qualquer requisição para `/api/...`
4. ✅ **Headers devem incluir:**
   ```
   Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

#### **TESTE 6: Persistência de sessão**
1. Recarregue a página (F5)
2. ✅ Deve continuar autenticado
3. ✅ Dashboard deve carregar automaticamente

#### **TESTE 7: Logout**
1. Clique no botão "X" (logout) no topo
2. ✅ Deve redirecionar para `/login`
3. ✅ Ao tentar acessar `/dashboard`, deve redirecionar para login

---

## ⚠️ SE ALGO NÃO FUNCIONAR

### Problema: "Não autenticado" ainda aparece

**Solução:**
1. Limpe o cache do navegador (Ctrl+Shift+Delete)
2. Limpe localStorage:
   ```javascript
   // No console do navegador (F12)
   localStorage.clear()
   location.reload()
   ```
3. Faça login novamente

### Problema: Erros de CORS

**Solução:**
1. Verifique variável de ambiente `ALLOWED_ORIGINS`
2. Backend deve aceitar `http://localhost:5173`
3. Reinicie o backend

### Problema: Erro 500 no backend

**Solução:**
1. Verifique se o banco de dados está inicializado
2. Execute migrations:
   ```powershell
   alembic upgrade head
   ```

### Problema: Frontend não conecta ao backend

**Solução:**
1. Verifique arquivo `.env.local`:
   ```
   VITE_API_URL=http://localhost:8000/api
   ```
2. Reinicie o frontend (Ctrl+C e `npm run dev`)

---

## 📊 LOGS IMPORTANTES

### Frontend Console (esperado):
```
[AuthContext] Token encontrado ao carregar, restaurando sessão
[Login] Tentando fazer login...
[Login] Login bem-sucedido! Token recebido.
[Login] Redirecionando para dashboard...
[Dashboard] Carregando dados do dashboard...
[Dashboard] Dados carregados com sucesso
```

### Backend Terminal (esperado):
```
INFO Token JWT criado para sub=1, expira em 60 minutos
INFO Login bem-sucedido para empresa ID=1 (teste@example.com)
INFO Token recebido na requisição: eyJhbG... (rota: /api/empresas/me)
INFO Empresa ID 1 extraída do JWT para rota /api/empresas/me
INFO Usuário autenticado: empresa 1 (Minha Empresa)
INFO Dashboard requisitado para empresa ID=1 (Minha Empresa)
```

---

## ✅ CHECKLIST DE SUCESSO

- [ ] Backend rodando na porta 8000
- [ ] Frontend rodando na porta 5173
- [ ] Login funciona
- [ ] Dashboard carrega sem "Não autenticado"
- [ ] Métricas mostram números (não "—")
- [ ] Gráficos aparecem
- [ ] Console não mostra erros 401
- [ ] Network mostra header Authorization
- [ ] Sessão persiste ao recarregar (F5)
- [ ] Logout funciona

---

**Se TODOS os itens acima funcionarem, o sistema está 100% operacional! 🎉**
