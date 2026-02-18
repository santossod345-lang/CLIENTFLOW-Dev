@echo off
REM Script para iniciar o Frontend ClientFlow em desenvolvimento

cd /d "%~dp0"

echo 🚀 Iniciando Frontend ClientFlow...
echo.
echo 📍 URL: http://localhost:5173
echo.

npm run dev
