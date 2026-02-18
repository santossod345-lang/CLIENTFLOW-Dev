@echo off
setlocal enabledelayedexpansion

echo.
echo 🚀 Instalando dependências do Frontend ClientFlow...
echo.

REM Verificar se Node.js está instalado
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Node.js não está instalado.
    echo Instale em: https://nodejs.org/
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('node -v') do set NODE_VERSION=%%i
for /f "tokens=*" %%i in ('npm -v') do set NPM_VERSION=%%i

echo ✓ Node.js encontrado: %NODE_VERSION%
echo ✓ npm encontrado: %NPM_VERSION%
echo.

echo 📦 Instalando packages...
call npm install

if exist ".env.local" (
    echo ✓ .env.local já existe
) else (
    echo 📝 Criando .env.local...
    copy .env.example .env.local
)

echo.
echo ✅ Setup completo!
echo.
echo Para iniciar o desenvolvimento:
echo   npm run dev
echo.
echo Para fazer build de produção:
echo   npm run build
echo.
pause
