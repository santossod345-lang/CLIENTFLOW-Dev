# Menu de Sincronização de Repositórios - ClientFlow
# Gerenciador interativo para sincronizar com os dois repositórios

$RepoPath = "c:\Users\Sueli\Desktop\ClientFlow"
$SyncScript = "$RepoPath\sync_repos.ps1"
$SetupScript = "$RepoPath\setup_auto_sync.ps1"
$LogFile = "$RepoPath\sync_repos.log"

function Show-Menu {
    Clear-Host
    Write-Host "╔════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║   ClientFlow - Sincronizador de Repositórios      ║" -ForegroundColor Cyan
    Write-Host "║                                                    ║" -ForegroundColor Cyan
    Write-Host "║  Origin:   santossod345-lang/CLIENTFLOW-Dev       ║" -ForegroundColor Yellow
    Write-Host "║  Upstream: luizfernandoantonio345-webs/CLIENTFLOW ║" -ForegroundColor Yellow
    Write-Host "╚════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "OPÇÕES:" -ForegroundColor Green
    Write-Host "1. Sincronizar agora (com confirmação)" -ForegroundColor White
    Write-Host "2. Sincronizar agora (modo automático)" -ForegroundColor White
    Write-Host "3. Configurar sincronização automática" -ForegroundColor White
    Write-Host "4. Ver histórico de sincronizações (log)" -ForegroundColor White
    Write-Host "5. Ver status dos repositórios" -ForegroundColor White
    Write-Host "6. Limpar arquivo de log" -ForegroundColor White
    Write-Host "0. Sair" -ForegroundColor Red
    Write-Host ""
}

function Sync-Manual {
    Write-Host "Executando sincronização manual..." -ForegroundColor Yellow
    & powershell -NoProfile -ExecutionPolicy Bypass -File $SyncScript
}

function Sync-Auto {
    Write-Host "Executando sincronização em modo automático..." -ForegroundColor Yellow
    & powershell -NoProfile -ExecutionPolicy Bypass -File $SyncScript -Auto
}

function Setup-AutoSync {
    Write-Host "Iniciando configuration de sincronização automática..." -ForegroundColor Yellow
    Write-Host "(Nota: Requer privilégios de Administrador)" -ForegroundColor Cyan
    Write-Host ""
    
    # Verificar privilégios
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    
    if (-not $isAdmin) {
        Write-Host "⚠️  Você precisa executar como Administrador!" -ForegroundColor Red
        Write-Host "Por favor, abra uma nova janela do PowerShell como Administrador e execute novamente." -ForegroundColor Yellow
        Read-Host "Pressione Enter para continuar"
        return
    }
    
    & powershell -NoProfile -ExecutionPolicy Bypass -File $SetupScript
}

function Show-Log {
    if (Test-Path $LogFile) {
        Write-Host "=== HISTÓRICO DE SINCRONIZAÇÕES ===" -ForegroundColor Cyan
        Write-Host "(Últimas 50 linhas)" -ForegroundColor Gray
        Write-Host ""
        Get-Content $LogFile -Tail 50
        Write-Host ""
    }
    else {
        Write-Host "Nenhum histórico de sincronizações ainda." -ForegroundColor Yellow
    }
    
    Read-Host "Pressione Enter para continuar"
}

function Show-Status {
    Write-Host "=== STATUS DOS REPOSITÓRIOS ===" -ForegroundColor Cyan
    Write-Host ""
    
    Set-Location $RepoPath
    
    Write-Host "Remotes configurados:" -ForegroundColor Yellow
    git remote -v | ForEach-Object { Write-Host $_ }
    Write-Host ""
    
    Write-Host "Branch atual:" -ForegroundColor Yellow
    git branch --show-current
    Write-Host ""
    
    Write-Host "Commits não sincronizados:" -ForegroundColor Yellow
    $localCommits = git log --oneline origin/main..HEAD 2>$null | Measure-Object | Select-Object -ExpandProperty Count
    Write-Host "Para origin: $localCommits commits"
    
    $upstreamCommits = git log --oneline upstream/main..HEAD 2>$null | Measure-Object | Select-Object -ExpandProperty Count
    Write-Host "Para upstream: $upstreamCommits commits"
    Write-Host ""
    
    Write-Host "Status do repositório:" -ForegroundColor Yellow
    git status
    Write-Host ""
    
    Read-Host "Pressione Enter para continuar"
}

function Clear-Log {
    if (Test-Path $LogFile) {
        Write-Host "Limpando histórico de sincronizações..." -ForegroundColor Yellow
        Remove-Item $LogFile -Force
        Write-Host "✅ Histórico limpo com sucesso!" -ForegroundColor Green
    }
    else {
        Write-Host "Nenhum arquivo de log para limpar." -ForegroundColor Yellow
    }
    
    Read-Host "Pressione Enter para continuar"
}

# Loop principal
do {
    Show-Menu
    $choice = Read-Host "Escolha uma opção"
    
    switch ($choice) {
        "1" { Sync-Manual }
        "2" { Sync-Auto }
        "3" { Setup-AutoSync }
        "4" { Show-Log }
        "5" { Show-Status }
        "6" { Clear-Log }
        "0" { 
            Write-Host "Saindo..." -ForegroundColor Yellow
            exit 0
        }
        default { 
            Write-Host "Opção inválida!" -ForegroundColor Red
            Read-Host "Pressione Enter para continuar"
        }
    }
} while ($true)
