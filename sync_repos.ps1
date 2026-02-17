# Script de Sincronização de Repositórios - ClientFlow
# Sincroniza automaticamente entre santossod345-lang e luizfernandoantonio345-webs

param(
    [switch]$Auto = $false,
    [switch]$Verbose = $false
)

$RepoPath = "c:\Users\Sueli\Desktop\ClientFlow"
$Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $LogMessage = "[$Timestamp] [$Level] $Message"
    Write-Host $LogMessage
    Add-Content -Path "$RepoPath\sync_repos.log" -Value $LogMessage
}

function Sync-Repos {
    Set-Location $RepoPath
    
    Write-Log "=== INICIANDO SINCRONIZAÇÃO ===" "INFO"
    
    # Verificar status do repositório
    Write-Log "Verificando status do repositório..." "INFO"
    $status = git status --porcelain
    
    if ($status) {
        Write-Log "Mudanças detectadas no repositório:" "WARN"
        Write-Log "$status" "WARN"
        
        # Fazer commit automático se houver mudanças
        if ($Auto) {
            Write-Log "Modo automático: Commitando as mudanças..." "INFO"
            git add -A
            git commit -m "Auto-sync: $(Get-Date -Format 'dd/MM/yyyy HH:mm:ss')"
            Write-Log "Commit realizado com sucesso" "INFO"
        }
        else {
            Write-Log "A sincronização requer um commit manual. Use 'git add' e 'git commit'" "WARN"
            return $false
        }
    }
    else {
        Write-Log "Nenhuma mudança local detectada" "INFO"
    }
    
    # Fazer fetch de ambos os remotes
    Write-Log "Fazendo fetch de origin (santossod345-lang)..." "INFO"
    git fetch origin 2>&1 | ForEach-Object { Write-Log $_ "DEBUG" }
    
    Write-Log "Fazendo fetch de upstream (luizfernandoantonio345-webs)..." "INFO"
    git fetch upstream 2>&1 | ForEach-Object { Write-Log $_ "DEBUG" }
    
    # Verificar diferenças
    Write-Log "Verificando diferenças..." "INFO"
    $diffOrigin = git log --oneline origin/main..HEAD 2>$null
    $diffUpstream = git log --oneline upstream/main..HEAD 2>$null
    
    if ($diffOrigin -or $diffUpstream) {
        Write-Log "Mudanças pendentes para push detectadas" "WARN"
        
        # Push para origin (Santos)
        Write-Log "Fazendo push para origin (santossod345-lang)..." "INFO"
        git push origin main 2>&1 | ForEach-Object { 
            if ($_ -match "error|fatal") {
                Write-Log $_ "ERROR"
            } else {
                Write-Log $_ "DEBUG"
            }
        }
        
        # Push para upstream (Luiz)
        Write-Log "Fazendo push para upstream (luizfernandoantonio345-webs)..." "INFO"
        git push upstream main 2>&1 | ForEach-Object { 
            if ($_ -match "error|fatal") {
                Write-Log $_ "ERROR"
            } else {
                Write-Log $_ "DEBUG"
            }
        }
        
        Write-Log "Push concluído com sucesso para ambos os repositórios" "INFO"
    }
    else {
        Write-Log "Repositórios já estão sincronizados" "INFO"
    }
    
    # Mostrar status final
    Write-Log "=== STATUS FINAL ===" "INFO"
    Write-Log "Origin (Santos): $(git rev-parse origin/main)" "INFO"
    Write-Log "Upstream (Luiz): $(git rev-parse upstream/main)" "INFO"
    Write-Log "Local (HEAD): $(git rev-parse HEAD)" "INFO"
    Write-Log "=== SINCRONIZAÇÃO CONCLUÍDA ===" "INFO"
    
    return $true
}

# Executar sincronização
try {
    $result = Sync-Repos
    if ($result) {
        exit 0
    }
    else {
        exit 1
    }
}
catch {
    Write-Log "Erro durante sincronização: $_" "ERROR"
    exit 2
}
