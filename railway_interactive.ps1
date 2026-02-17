#!/usr/bin/env powershell

<#
.SYNOPSIS
  Conectar ao Railway CLI e acessar ClientFlow
.DESCRIPTION
  Script interativo para:
  1. Login no Railway
  2. Listar projetos
  3. Conectar ao ClientFlow
  4. Abrir a URL
#>

# Cores para output
$cyan = [System.ConsoleColor]::Cyan
$green = [System.ConsoleColor]::Green
$yellow = [System.ConsoleColor]::Yellow
$red = [System.ConsoleColor]::Red
$white = [System.ConsoleColor]::White

function Show-Header {
    Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor $cyan
    Write-Host "║  CONECTAR AO RAILWAY CLI - CLIENTFLOW               ║" -ForegroundColor $cyan
    Write-Host "║  Opção 2: Railway CLI                               ║" -ForegroundColor $cyan
    Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor $cyan
}

function Show-Menu {
    Write-Host "`n📋 MENU:" -ForegroundColor $yellow
    Write-Host "1. Fazer Login no Railway" -ForegroundColor $white
    Write-Host "2. Listar Projetos" -ForegroundColor $white
    Write-Host "3. Conectar ao ClientFlow" -ForegroundColor $white
    Write-Host "4. Abrir URL do Projeto" -ForegroundColor $white
    Write-Host "5. Ver Logs em Tempo Real" -ForegroundColor $white
    Write-Host "6. Ver Variáveis de Ambiente" -ForegroundColor $white
    Write-Host "7. Ver Status do Projeto" -ForegroundColor $white
    Write-Host "8. Executar Tudo Automaticamente" -ForegroundColor $green
    Write-Host "0. Sair" -ForegroundColor $red
    Write-Host ""
}

function Do-Login {
    Write-Host "`n🚂 Fazendo login no Railway..." -ForegroundColor $cyan
    Write-Host "Seu navegador será aberto para autenticação" -ForegroundColor $yellow
    railway login
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Login realizado com sucesso!" -ForegroundColor $green
    } else {
        Write-Host "❌ Erro ao fazer login" -ForegroundColor $red
    }
}

function Do-ListProjects {
    Write-Host "`n🚂 Listando seus projetos..." -ForegroundColor $cyan
    railway list
    Write-Host "`n💡 Procure por um projeto chamado 'CLIENTFLOW'" -ForegroundColor $yellow
}

function Do-LinkProject {
    Write-Host "`n🚂 Conectando ao projeto ClientFlow..." -ForegroundColor $cyan
    Write-Host "Selecione 'CLIENTFLOW' na lista" -ForegroundColor $yellow
    railway link
}

function Do-OpenURL {
    Write-Host "`n🚂 Abrindo URL do projeto..." -ForegroundColor $cyan
    Write-Host "Seu navegador será aberto com o dashboard" -ForegroundColor $yellow
    railway open
    Write-Host "`n✅ URL aberta no navegador!" -ForegroundColor $green
}

function Do-Logs {
    Write-Host "`n🚂 Mostrando logs em tempo real..." -ForegroundColor $cyan
    Write-Host "Pressione CTRL+C para parar" -ForegroundColor $yellow
    railway logs --follow
}

function Do-Environment {
    Write-Host "`n🚂 Variáveis de Ambiente do Railway:" -ForegroundColor $cyan
    railway env
}

function Do-Status {
    Write-Host "`n🚂 Status do Projeto:" -ForegroundColor $cyan
    railway status
}

function Do-AutomaticSetup {
    Write-Host "`n🚀 Executando Setup Automático..." -ForegroundColor $green
    
    Write-Host "`n[1/4] Fazendo login..." -ForegroundColor $yellow
    railway login
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Erro no login" -ForegroundColor $red
        return
    }
    
    Write-Host "`n[2/4] Listando projetos..." -ForegroundColor $yellow
    railway list
    
    Write-Host "`n[3/4] Conectando ao ClientFlow..." -ForegroundColor $yellow
    railway link
    
    Write-Host "`n[4/4] Abrindo URL..." -ForegroundColor $yellow
    railway open
    
    Write-Host "`n✅ Setup Automático Concluído!" -ForegroundColor $green
}

# Main Loop
Show-Header

$continue = $true
while ($continue) {
    Show-Menu
    $choice = Read-Host "Escolha uma opção"
    
    switch ($choice) {
        "1" { Do-Login }
        "2" { Do-ListProjects }
        "3" { Do-LinkProject }
        "4" { Do-OpenURL }
        "5" { Do-Logs }
        "6" { Do-Environment }
        "7" { Do-Status }
        "8" { Do-AutomaticSetup }
        "0" { 
            $continue = $false
            Write-Host "`n👋 Até logo!" -ForegroundColor $yellow
        }
        default { 
            Write-Host "`n❌ Opção inválida" -ForegroundColor $red
        }
    }
}
