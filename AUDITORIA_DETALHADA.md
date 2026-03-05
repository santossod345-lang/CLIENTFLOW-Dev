# AUDITORIA COMPLETA - ClientFlow Sistema de Autenticação
## Data: 2026-03-05

---

## SUMÁRIO EXECUTIVO

O usuário relata que o dashboard aparece "Não autenticado" e não carrega dados. Após auditoria completa, foram identificados **6 problemas críticos** que impedem o funcionamento adequado do sistema de autenticação.

---

## PROBLEMAS IDENTIFICADOS

### 1. ❌ FALTA DE LOGS DE DEBUG NO BACKEND
**Arquivo**: `backend/auth.py`, `backend/dependencies.py`, `backend/main.py`
**Problema**: 
- Não há logs quando `get_current_empresa_jwt()` falha
- Não há logs quando a empresa não é encontrada no banco
- Impossível diagnosticar por que o 401 está ocorrendo

**Impacto**: Usuário vê "Não autenticado" mas não sabe por quê (token inválido? expirou? banco offline?)

---

### 2. ❌ FALTA DE VALIDAÇÃO DO TOKEN NO FRONTEND ANTES DE USAR
**Arquivo**: `clientflow-frontend/src/pages/Dashboard.jsx`
**Problema**:
```javascript
const token = localStorage.getItem('access_token')
const authHeaders = useMemo(
  () => ({
    Authorization: `Bearer ${token}`  // ← Se token for null: "Bearer null" (INVÁLIDO!)
  }),
  [token]
)
```
- Se o token for null ou undefined, a requisição envia "Bearer null"
- Backend retorna 401 "Não autenticado"
- Frontend não verifica antes de fazer requisição

**Impacto**: Dashboard tenta fazer requisições com token inválido

---

### 3. ❌ AUTENTICAÇÃO NÃO SINCRONIZADA ENTRE PRIVATERUTE E AUTHCONTEXT
**Arquivo**: `clientflow-frontend/src/routes/PrivateRoute.jsx`
**Problema**:
```javascript
// PrivateRoute verifica localStorage
const token = localStorage.getItem('access_token')

// Mas AuthContext também existe e também tem token
const { auth, setAuth } = useContext(AuthContext)
```
- PrivateRoute usa localStorage diretamente
- AuthContext não é usado por PrivateRoute
- Isso causa desincronização entre state e localStorage

**Impacto**: Mudanças no Auth Context não afetam o PrivateRoute

---

### 4. ❌ FALTA DE VALIDAÇÃO PRÉVIA DO TOKEN NO APP.JSX
**Arquivo**: `clientflow-frontend/src/App.jsx`
**Problema**:
```javascript
useEffect(() => {
  const token = localStorage.getItem('access_token')
  if (token) {
    setAuth({ token })  // ← Apenas checa se existe, não se é válido!
  }
  setLoading(false)
}, [])
```
- App apenas checa se o token EXISTS
- Não valida se o token é válido (pode estar expirado)
- Token inválido passa por PrivateRoute → Dashboard tenta usar → 401

**Impacto**: Usuários com tokens expirados entram no dashboard mas recebem 401

---

### 5. ❌ FALTA DE INTERCEPTADOR AXIOS PARA REQUISIÇÕES NÃO AUTORIZADAS
**Arquivo**: `clientflow-frontend/src/pages/Dashboard.jsx`, `clientflow-frontend/src/pages/Login.jsx`
**Problema**:
- Dashboard.jsx faz requisições sem try/catch adequado
- Se receber 401, exibe erro vago
- Não há retry logic automático como em App.jsx

**Impacto**: Usuário vê erro confuso em vez de ser redirecionado para login

---

### 6. ❌ BACKEND NÃO TEM ENDPOINT PARA VALIDAR TOKEN
**Arquivo**: Inexistente
**Problema**:
- Não há rota tipo `GET /api/empresas/validate-token`
- Frontend não pode validar token antes de exibir dashboard
- Deve, eventualmente, implementar essa validação no startup

**Impacto**: Frontend não tem como saber se o token é válido ao iniciar

---

## ANÁLISE DETALHADA DO FLUXO

### Fluxo ESPERADO (correto):
```
1. Usuário faz login
2. Recebe access_token e refresh_token
3. Salva em localStorage
4. App verifica localStorage ao inicializar
5. App valida token (ou redireciona para login)
6. Usuário entra no dashboard com token válido
7. Dashboard faz requisições com Authorization: Bearer <valid_token>
8. API retorna dados
9. Se token expirar, AxiosBridge faz refresh automático
```

### Fluxo ATUAL (com problemas):
```
1. Usuário faz login ✓
2. Recebe access_token e refresh_token ✓
3. Salva em localStorage ✓
4. App verifica localStorage ao inicializar ✓ (MAS não valida!)
5. App pensa que está autenticado (token pode estar expirado)
6. Usuário entra no dashboard ✓ (MAS com token possivelmente inválido!)
7. Dashboard faz requisição com Authorization: Bearer <token>
8. API decodifica token → ERRO? → retorna 401
9. AxiosBridge tenta fazer refresh... (pode falha se refresh_token também expirou)
10. Usuário vê "Não autenticado" ✗
```

---

## SOLUÇÃO NECESSÁRIA

### Correção 1: Adicionar Logs no Backend
- Logar quando JWT é decodificado (sucesso)
- Logar quando JWT falha (erro específico)
- Logar quando empresa não é encontrada
- Logar quando plan_limits retorna erro

### Correção 2: Validar Token no Frontend Antes de Usar
- Verificar se token existe E não está vazio
- Se token for inválido, redirecionar para login
- Mostrar mensagem clara: "Token inválido ou expirado"

### Correção 3: Sincronizar PrivateRoute com AuthContext
- PrivateRoute deve usar AuthContext em vez de localStorage
- Ou AuthContext deve ser o source of truth
- Manter sincronização entre estado e persistência

### Correção 4: Criar Endpoint de Validação de Token
- Rota: `GET /api/empresas/validate-token`
- Retorna: { valid: true/false, empresa: { id, nome } }
- Frontend chama ao inicializar para validar token

### Correção 5: Melhorar Tratamento de Erro no Dashboard
- Adicionar try/catch mais específico
- Mostrar mensagem de erro clara
- Oferecer opção de fazer logout e login novamente

### Correção 6: Adicionar Validação de Token Expirado
- Decodificar JWT no frontend (sem validar assinatura)
- Verificar se "exp" já passou
- Se expirou, tentar refresh imediatamente

---

## IMPACTO DAS CORREÇÕES

Após aplicar as correções:
- ✓ Dashboard carregará corretamente
- ✓ Dados de clientes, faturamento, agenda serão exibidos
- ✓ Tokens expirados serão renovados automaticamente
- ✓ Mensagens de erro serão claras
- ✓ Debugging será muito mais fácil

---

## LINHAS DE CÓDIGO AFETADAS

| Arquivo | Problema | Linhas |
|---------|----------|--------|
| `backend/auth.py` | Falta de logs | 50-55 |
| `backend/dependencies.py` | Falta de logs | 6-12 |
| `clientflow-frontend/src/pages/Dashboard.jsx` | Validação de token | 65-75 |
| `clientflow-frontend/src/routes/PrivateRoute.jsx` | Sincronização | todos |
| `clientflow-frontend/src/App.jsx` | Validação no startup | 155-170 |
| Novo arquivo | Validação de token | novo |

