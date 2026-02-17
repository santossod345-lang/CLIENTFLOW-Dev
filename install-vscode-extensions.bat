@echo off
REM Atalho para executar o instalador de extensões VS Code (PowerShell)
powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process powershell -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File "%~dp0install-vscode-extensions.ps1"' -Verb RunAs"
pause
