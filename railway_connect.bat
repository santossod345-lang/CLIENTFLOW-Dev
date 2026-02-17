@echo off
REM Script para conectar ao Railway CLI de forma automática
REM Execute: railway_connect.bat

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║  CONECTANDO AO RAILWAY CLI - CLIENTFLOW              ║
echo ║  Opção 2: Railway CLI Setup                           ║
echo ╚════════════════════════════════════════════════════════╝
echo.

echo ✓ Railway CLI instalado
echo.
echo Digite os comandos abaixo no PowerShell ou CMD:
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 1. FAZER LOGIN:
echo.
echo    railway login
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 2. LISTAR PROJETOS:
echo.
echo    railway list
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 3. CONECTAR AO CLIENTFLOW:
echo.
echo    railway link
echo.
echo    (Selecione CLIENTFLOW na lista)
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 4. ABRIR A URL:
echo.
echo    railway open
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo Iniciando login...
echo.

railway login

if errorlevel 1 (
    echo.
    echo ❌ Erro ao fazer login
    echo Verifique sua conexão e tente novamente
    pause
    exit /b 1
)

echo.
echo ✓ Login realizado com sucesso!
echo.
echo Listando seus projetos...
echo.

railway list

echo.
echo Conectando ao projeto ClientFlow...
echo.

railway link

echo.
echo Abrindo URL do projeto...
echo.

railway open

echo.
echo ✅ Pronto!
echo.
echo Para ver logs em tempo real, use:
echo    railway logs --follow
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

pause
