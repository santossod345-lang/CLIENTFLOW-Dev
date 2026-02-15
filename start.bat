@echo off
echo ========================================
echo   ClientFlow - Sistema de Inicializacao
echo ========================================
echo.

echo [1/3] Verificando Python...
python --version
if errorlevel 1 (
    echo ERRO: Python nao encontrado! Instale Python 3.8 ou superior.
    pause
    exit
)
echo.

echo [2/3] Instalando dependencias...
pip install -r requirements.txt
echo.

echo [3/3] Iniciando servidor...
echo.
echo ========================================
echo   Servidor rodando em:
echo   http://localhost:8000
echo.
echo   Documentacao API:
echo   http://localhost:8000/docs
echo ========================================
echo.

cd backend
python main.py
