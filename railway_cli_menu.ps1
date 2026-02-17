#!/usr/bin/env powershell

# Railway CLI Menu Interativo
# Script para conectar ao Railway e acessar ClientFlow

$cyan = "Cyan"
$green = "Green"
$yellow = "Yellow"
$red = "Red"
$white = "White"

function Show-Header {
    Write-Host ""
    Write-Host "======================================================" -ForegroundColor $cyan
    Write-Host "  CONECTAR AO RAILWAY CLI - CLIENTFLOW" -ForegroundColor $cyan
    Write-Host "  Opcao 2: Railway CLI" -ForegroundColor $cyan
    Write-Host "======================================================" -ForegroundColor $cyan
    Write-Host ""
}

function Show-Menu {
    Write-Host "MENU:" -ForegroundColor $yellow
    Write-Host "1. Fazer Login no Railway" -ForegroundColor $white
    Write-Host "2. Listar Projetos" -ForegroundColor $white
    Write-Host "3. Conectar ao ClientFlow" -ForegroundColor $white
    Write-Host "4. Abrir URL do Projeto" -ForegroundColor $white
    Write-Host "5. Ver Logs em Tempo Real" -ForegroundColor $white
    Write-Host "6. Ver Variaveis de Ambiente" -ForegroundColor $white
    Write-Host "7. Ver Status do Projeto" -ForegroundColor $white
    Write-Host "8. Executar Tudo Automaticamente" -ForegroundColor $green
    Write-Host "0. Sair" -ForegroundColor $red
    Write-Host ""
}

function Do-Login {
    Write-Host ""
    Write-Host "Fazendo login no Railway..." -ForegroundColor $cyan
    Write-Host "Seu navegador sera aberto para autenticacao" -ForegroundColor $yellow
    railway login
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Login realizado com sucesso!" -ForegroundColor $green
    } else {
        Write-Host "Erro ao fazer login" -ForegroundColor $red
    }
    Write-Host ""
}

function Do-ListProjects {
    Write-Host ""
    Write-Host "Listando seus projetos..." -ForegroundColor $cyan
    railway list
    Write-Host ""
    Write-Host "Procure por um projeto chamado 'CLIENTFLOW'" -ForegroundColor $yellow
    Write-Host ""
}

function Do-LinkProject {
    Write-Host ""
    Write-Host "Conectando ao projeto ClientFlow..." -ForegroundColor $cyan
    Write-Host "Selecione 'CLIENTFLOW' na lista" -ForegroundColor $yellow
    railway link
    Write-Host ""
}

function Do-OpenURL {
    Write-Host ""
    Write-Host "Abrindo URL do projeto..." -ForegroundColor $cyan
    Write-Host "Seu navegador sera aberto com o dashboard" -ForegroundColor $yellow
    railway open
    Write-Host "URL aberta no navegador!" -ForegroundColor $green
    Write-Host ""
}

function Do-Logs {
    Write-Host ""
    Write-Host "Mostrando logs em tempo real..." -ForegroundColor $cyan
    Write-Host "Pressione CTRL+C para parar" -ForegroundColor $yellow
    railway logs --follow
    Write-Host ""
}

function Do-Environment {
    Write-Host ""
    Write-Host "Variaveis de Ambiente do Railway:" -ForegroundColor $cyan
    railway env
    Write-Host ""
}

function Do-Status {
    Write-Host ""
    Write-Host "Status do Projeto:" -ForegroundColor $cyan
    railway status
    Write-Host ""
}

function Do-AutomaticSetup {
    Write-Host ""
    Write-Host "EXECUTANDO SETUP AUTOMATICO..." -ForegroundColor $green
    Write-Host ""
    
    Write-Host "[1/4] Fazendo login..." -ForegroundColor $yellow
    railway login
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Erro no login" -ForegroundColor $red
        return
    }
    
    Write-Host "[2/4] Listando projetos..." -ForegroundColor $yellow
    railway list
    
    Write-Host "[3/4] Conectando ao ClientFlow..." -ForegroundColor $yellow
    railway link
    
    Write-Host "[4/4] Abrindo URL..." -ForegroundColor $yellow
    railway open
    
    Write-Host ""
    Write-Host "SETUP AUTOMATICO CONCLUIDO!" -ForegroundColor $green
    Write-Host ""
}

# Main Loop
Clear-Host
Show-Header

$continue = $true
while ($continue) {
    Show-Menu
    $choice = Read-Host "Escolha uma opcao"
    
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
            Write-Host ""
            Write-Host "Ate logo!" -ForegroundColor $yellow
            Write-Host ""
        }
        default { 
            Write-Host ""
            Write-Host "Opcao invalida" -ForegroundColor $red
            Write-Host ""
        }
    }
}
