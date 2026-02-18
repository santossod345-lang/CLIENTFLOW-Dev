# ⚡ GUIA RÁPIDO DE USO - FRONTEND CLIENTFLOW

## 🚀 INÍCIO RÁPIDO

```bash
# Entrar na pasta do frontend
cd clientflow-frontend

# Iniciar servidor de desenvolvimento
npm run dev

# Abrir em http://localhost:5173
```

---

## 📋 COMANDOS ESSENCIAIS

### Desenvolvimento
```bash
npm run dev              # Inicia o server (hot reload automático)
npm run build            # Cria build otimizado na pasta dist/
npm run preview          # Preview do build
```

### Manutenção
```bash
npm install              # Instalar dependências
npm update               # Atualizar pacotes
npm audit                # Verificar vulnerabilidades
npm audit fix            # Corrigir vulnerabilidades
```

### Adicionar Pacotes
```bash
npm install react-icons  # Exemplo: adicionar ícones
npm install --save-dev tailwindcss  # Dev dependency
```

---

## 🔐 COMO FAZER LOGIN

1. Abrir http://localhost:5173
2. Ser redirecionado para /login automaticamente
3. Email: seu_email@example.com
4. Senha: sua_senha
5. Token será salvo em localStorage

---

## 🎨 MODIFICAR DESIGN (SEM DEIXAR PESADO)

### Ajustar Cores
```bash
# Arquivo: tailwind.config.js
# Adicionar cores em 'accent:' (não cause overhead)
```

### Adicionar Animação Leve
```css
/* Em src/styles/theme.css */
.seu-elemento {
  transition: transform 0.15s ease, background 0.15s ease;
}

.seu-elemento:hover {
  transform: translateY(-1px);  /* Máximo leve */
}
```

### NÃO FAÇA (Deixa Pesado)
```css
❌ backdrop-filter: blur(10px);
❌ animation: infinite-glow 2s infinite;
❌ box-shadow: 0 0 50px 50px rgba(...);
❌ filter: drop-shadow(...) blur(...) brightness(...);
```

---

## 🐛 SOLUCIONAR PROBLEMAS

### Frontend não abre
```bash
# Limpar cache
rm -r node_modules/.vite
npm run dev
```

### Erro de memória
```bash
# Aumentar limite Node
$env:NODE_OPTIONS="--max-old-space-size=4096"
npm run dev
```

### API não conecta
- Verificar se backend está rodando
- Verificar URL da API em src/services/api.js
- Verificar CORS no backend

### Login não funciona
- Abrir console (F12)
- Verificar se token é retornado
- Verificar localStorage (Application tab)
- Verificar response no Network tab

---

## 📁 ESTRUTURA DO PROJETO

```
clientflow-frontend/
├── src/
│   ├── pages/          # Login, Dashboard
│   ├── components/     # UI components
│   ├── context/        # AuthContext (não mexer!)
│   ├── services/       # API calls
│   ├── routes/         # PrivateRoute
│   ├── styles/         # theme.css (otimizado)
│   ├── App.jsx         # Routes
│   └── main.jsx        # Entry point
├── package.json
├── vite.config.js      # (otimizado)
├── tailwind.config.js  # (otimizado)
└── dist/               # Build output
```

---

## 💾 GIT & VERSIONAMENTO

```bash
# Ver status
git status

# Adicionar mudanças
git add .

# Commit
git commit -m "Descrição da mudança"

# Push
git push origin main
```

---

## 🔗 INTEGRAÇÕES

### Backend
- URL: http://localhost:8000 (default)
- Endpoints: /api/auth, /api/clients, /api/appointments
- Token: Enviado em Authorization header

### Banco de Dados
- PostgreSQL como backend
- Operações gerenciadas pelo backend
- Frontend apenas consome API

---

## ⚙️ CONFIGURAÇÕES IMPORTANTES

### src/services/api.js
```javascript
// Verificar base URL
const API_BASE_URL = process.env.VITE_API_URL || 'http://localhost:8000'
```

### src/context/AuthContext.jsx
```javascript
// Token salvo em localStorage
// Nunca salve em cookies (segurança)
```

---

## 📊 PERFORMANCE

### Monitorar
```bash
# DevTools do navegador (F12)
- Abra Performance tab
- Grave ação
- Analise timeline
```

### Otimizar Imagens
```bash
# Se adicionar imagens
npm install --save-dev imagemin
```

---

## 🆘 EMERGÊNCIA

Se o sistema travar:

```bash
# 1. Parar servidor (Ctrl+C no terminal)
# 2. Limpar tudo
rm -r node_modules dist
# 3. Reinstalar
npm install
# 4. Tentar novamente
npm run dev
```

---

**✅ Sistema Pronto para Producção**  
**📈 Otimizado para 8GB RAM**  
**🔒 Segurança JWT Implementada**  
**🎨 Visual Premium Mantido**

Boa sorte! 🚀
