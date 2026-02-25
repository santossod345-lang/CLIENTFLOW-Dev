#!/bin/bash
# Deploy automático para Railway + Vercel

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "\n${BLUE}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  🚀 ClientFlow - Deploy para Produção             ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════╝${NC}\n"

# Verificar status git
echo -e "${YELLOW}[1/5]${NC} Verificando status do repositório..."
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${RED}✗ Há alterações não commitadas:${NC}"
    git status --short
    exit 1
fi
echo -e "${GREEN}✓ Repositório limpo${NC}\n"

# Verificar branch
echo -e "${YELLOW}[2/5]${NC} Verificando branch..."
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo -e "${RED}✗ Você não está na branch 'main' (está em: $CURRENT_BRANCH)${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Branch main ativa${NC}\n"

# Resumo
echo -e "${YELLOW}[3/5]${NC} Últimos commits:"
git log --oneline -3
echo ""

echo -e "${YELLOW}[4/5]${NC} Resumo do Projeto:"
echo "  📦 Backend: FastAPI (backend/)"
echo "  🎨 Frontend: React Vite (clientflow-frontend/)"
echo "  🗄️  Database: PostgreSQL (Railway)"
echo ""

# Instruções
echo -e "${YELLOW}[5/5]${NC} Próximas Etapas:\n"

echo -e "${BLUE}═══════ 🚂 RAILWAY ═══════${NC}"
echo "  1. https://railway.app → 'Create New Project'"
echo "  2. Deploy from GitHub → santossod345-lang/CLIENTFLOW-Dev"
echo "  3. Branch: main"
echo "  4. Adicione PostgreSQL 15"
echo "  5. Configure variáveis de ambiente"
echo "  6. Aguarde build completar"
echo ""

echo -e "${BLUE}═══════ 🌐 VERCEL ═══════${NC}"
echo "  1. https://vercel.com/new"
echo "  2. Repositório: CLIENTFLOW-Dev"
echo "  3. Framework: Vite"
echo "  4. Build: npm run build"
echo "  5. VITE_API_URL=<railway-url>"
echo "  6. Deploy"
echo ""

echo -e "${GREEN}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ Tudo pronto para deploy!                     ║${NC}"
echo -e "${GREEN}║  Siga as instruções acima para Railway e Vercel. ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════╝${NC}\n"
