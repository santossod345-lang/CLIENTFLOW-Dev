<#
Instala as extensões VS Code recomendadas globalmente para um dev sênior.
Uso: abra PowerShell e execute:
  powershell -ExecutionPolicy Bypass -File "install-vscode-extensions.ps1"
Se o comando `code` não estiver disponível, o script tentará localizar `code.cmd` na instalação do VS Code.
#>

# Lista de extensões (IDs)
$extensions = @(
  'ms-python.python',
  'ms-python.vscode-pylance',
  'ms-toolsai.jupyter',
  'eamodio.gitlens',
  'esbenp.prettier-vscode',
  'dbaeumer.vscode-eslint',
  'ms-azuretools.vscode-docker',
  'hashicorp.terraform',
  'EditorConfig.EditorConfig',
  'streetsidesoftware.code-spell-checker',
  'PKief.material-icon-theme',
  'redhat.vscode-yaml',
  'bungcip.better-toml',
  'yzhang.markdown-all-in-one',
  'VisualStudioExptTeam.vscodeintellicode',
  'oderwat.indent-rainbow',
  'github.copilot'
)

# Função para localizar o binário `code` se não estiver no PATH
function Find-CodeCmd {
    $cmd = Get-Command code -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }

    $candidates = @(
        "$Env:LOCALAPPDATA\Programs\Microsoft VS Code\bin\code.cmd",
        "$Env:ProgramFiles\Microsoft VS Code\bin\code.cmd",
        "$Env:ProgramFiles(x86)\Microsoft VS Code\bin\code.cmd"
    )
    foreach ($p in $candidates) { if (Test-Path $p) { return $p } }
    return $null
}

$codeCmd = Find-CodeCmd
if (-not $codeCmd) {
    Write-Host "ERRO: comando 'code' não encontrado no PATH e não foi possível localizar a instalação do VS Code." -ForegroundColor Red
    Write-Host "Abra o VS Code, abra o Command Palette e execute: 'Shell Command: Install 'code' command in PATH' e tente novamente." -ForegroundColor Yellow
    exit 1
}

Write-Host "Usando: $codeCmd" -ForegroundColor Green

foreach ($ext in $extensions) {
    Write-Host "Instalando: $ext" -NoNewline
    try {
        & $codeCmd --install-extension $ext --force > $null 2>&1
        Write-Host " -> OK" -ForegroundColor Green
    } catch {
        Write-Host " -> FALHOU" -ForegroundColor Red
        Write-Host $_.Exception.Message
    }
}

Write-Host "Instalação finalizada. Considere ativar Settings Sync no VS Code para sincronizar extensões e configurações entre máquinas." -ForegroundColor Cyan
