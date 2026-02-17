@echo off
cd /d "C:\Users\Sueli\Desktop\ClientFlow"

echo ========================================
echo FAZENDO PUSH DO CODIGO PARA O GITHUB
echo ========================================
git push origin main

echo.
echo ========================================
echo AGUARDANDO RAILWAY REBUILDAR (60s)
echo ========================================
timeout /t 60 /nobreak

echo.
echo ========================================
echo VERIFICANDO LOGS DO RAILWAY
echo ========================================
railway logs

echo.
echo ========================================
echo TESTANDO URL DA API
echo ========================================
curl https://clientflow-production-8f24.up.railway.app/health

echo.
echo.
echo Pressione qualquer tecla para sair...
pause
