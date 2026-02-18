#!/bin/bash
set -e

echo "🚀 Instalando dependências do Frontend ClientFlow..."

cd "$(dirname "$0")"

# Verificar se Node.js está instalado
if ! command -v node &> /dev/null; then
    echo "❌ Node.js não está instalado. Instale em: https://nodejs.org/"
    exit 1
fi

echo "✓ Node.js encontrado: $(node -v)"
echo "✓ npm encontrado: $(npm -v)"

# Instalar dependências
echo "📦 Instalando packages..."
npm install

# Criar .env.local se não existir
if [ ! -f .env.local ]; then
    echo "📝 Criando .env.local..."
    cp .env.example .env.local
fi

echo "✅ Setup completo!"
echo ""
echo "Para iniciar o desenvolvimento:"
echo "  npm run dev"
echo ""
echo "Para fazer build de produção:"
echo "  npm run build"
