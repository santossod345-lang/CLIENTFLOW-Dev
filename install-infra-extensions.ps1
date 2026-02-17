# Instala extensões essenciais para Terraform, AWS, YAML, GitHub Actions e produtividade
$exts = @(
  'hashicorp.terraform',
  'redhat.vscode-yaml',
  'GitHub.vscode-github-actions',
  'AmazonWebServices.aws-toolkit-vscode',
  'EditorConfig.EditorConfig',
  'esbenp.prettier-vscode',
  'eamodio.gitlens',
  'usernamehw.errorlens',
  'streetsidesoftware.code-spell-checker'
)
foreach ($e in $exts) { code --install-extension $e }
Write-Host "Extensões instaladas. Para remover as que não precisa, use: code --uninstall-extension <id>" -ForegroundColor Cyan
