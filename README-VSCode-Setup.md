# VS Code — Setup recomendado para desenvolvedores sênior

Arquivos criados:
- `install-vscode-extensions.ps1` — PowerShell que instala extensões recomendadas.
- `install-vscode-extensions.bat` — atalho Windows para executar o script com elevação.

Como usar
1. Abra o Explorador e vá para a pasta do projeto:

```powershell
cd "C:\Users\Sueli\Desktop\ClientFlow"
```

2. Execute o atalho `.bat` com duplo clique ou via PowerShell:

```powershell
.\install-vscode-extensions.bat
```

Observações
- Se o comando `code` não for encontrado, abra o VS Code → Command Palette → `Shell Command: Install 'code' command in PATH` (ou reinstale/ative o binário). O script tenta localizar `code.cmd` automaticamente.
- Para sincronizar extensões e configurações entre máquinas, ative o **Settings Sync** no VS Code (canto inferior esquerdo → Turn on Settings Sync → entre com GitHub/Microsoft).

Sugestão de `settings.json` de usuário
Cole este bloco em `Preferences → Settings → Open Settings (JSON)` ou no arquivo `%APPDATA%\Code\User\settings.json`:

```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.tabSize": 4,
  "editor.rulers": [80, 120],
  "files.exclude": {
    "**/__pycache__": true,
    "**/.venv": true,
    "**/venv": true,
    ".env": true
  },
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.mypyEnabled": true,
  "python.analysis.typeCheckingMode": "basic",
  "git.enableSmartCommit": true,
  "terminal.integrated.defaultProfile.windows": "PowerShell",
  "workbench.colorTheme": "Default Dark+",
  "workbench.iconTheme": "material-icon-theme",
  "security.workspace.trust.untrustedFiles": "open"
}
```

Extensões recomendadas (lista de IDs usadas pelo instalador)
- ms-python.python
- ms-python.vscode-pylance
- ms-toolsai.jupyter
- eamodio.gitlens
- esbenp.prettier-vscode
- dbaeumer.vscode-eslint
- ms-azuretools.vscode-docker
- hashicorp.terraform
- EditorConfig.EditorConfig
- streetsidesoftware.code-spell-checker
- PKief.material-icon-theme
- redhat.vscode-yaml
- bungcip.better-toml
- yzhang.markdown-all-in-one
- VisualStudioExptTeam.vscodeintellicode
- oderwat.indent-rainbow
- github.copilot

Ajuda adicional
- Quer que eu rode o script agora (posso instruir os comandos ou executá-lo se você quiser que eu gere instruções passo-a-passo)?
- Quer que eu adicione mais extensões específicas (ex.: Ansible, Kubernetes, SQL)?

