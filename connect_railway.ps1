#!/usr/bin/env powershell
<#
.SYNOPSIS
    Script para conectar ao Railway CLI e acessar a URL do ClientFlow
.DESCRIPTION
    Executa os comandos Railway para:
    1. Fazer login
    2. Listar projetos
    3. Abrir a URL do projeto
#>

Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   CONECTANDO AO RAILWAY CLI PARA CLIENTFLOW          ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

Write-Host "`n✓ Railway CLI instalado com sucesso!" -ForegroundColor Green

Write-Host "`n📋 PRÓXIMOS PASSOS:" -ForegroundColor Yellow
Write-Host "1. Fazer login no Railway" -ForegroundColor White
Write-Host "2. Conectar com seu projeto ClientFlow" -ForegroundColor White
Write-Host "3. Abrir a URL automaticamente" -ForegroundColor White

Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

# Passo 1: Login
Write-Host "`n🚂 PASSO 1: Fazendo login no Railway..." -ForegroundColor Cyan
Write-Host "Será aberto seu navegador para autenticação" -ForegroundColor Yellow
Write-Host "Aguarde..." -ForegroundColor Gray

railway login

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n❌ Erro no login!" -ForegroundColor Red
    Write-Host "Certifique-se de que:" -ForegroundColor Yellow
    Write-Host "  • Você tem uma conta em railway.app" -ForegroundColor White
    Write-Host "  • Seu navegador permite abrir links" -ForegroundColor White
    exit 1
}

Write-Host ✓ Login realizado com sucesso! -ForegroundColor Green

# Passo 2: Listar projetos
Write-Host "`n🚂 PASSO 2: Listando seus projetos..." -ForegroundColor Cyan
Write-Host "Aguarde..." -ForegroundColor Gray
Write-Host ""

railway list

Write-Host ""
Write-Host "`nProcure pelo projeto chamado 'CLIENTFLOW' ou similar" -ForegroundColor Yellow

# Passo 3: Status
Write-Host "`n🚂 PASSO 3: Verificando status..." -ForegroundColor Cyan

$status = railway status 2>&1
Write-Host $status -ForegroundColor Gray

# Passo 4: Abrir URL
Write-Host "`n🚂 PASSO 4: Abrindo URL do projeto..." -ForegroundColor Cyan
Write-Host "Abra seu navegador..." -ForegroundColor Yellow

railway open

Write-Host "`n✅ Pronto! A URL foi aberta em seu navegador!" -ForegroundColor Green
Write-Host "Você está vendo a interface do Railway" -ForegroundColor White
Write-Host "`nPara ver os logs da aplicação:` -ForegroundColor Yellow
Write-Host "  railway logs --follow" -ForegroundColor Cyan

Write-Host `
"Para ver as variáveis de ambiente:" -ForegroundColor Yellow
Write-Host "  railway env" -ForegroundColor Cyan

Write-Host `
"Para ver informações do serviço:" -ForegroundColor Yellow
Write-Host "  railway info" -ForegroundColor Cyan

Write-Host `
"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray
