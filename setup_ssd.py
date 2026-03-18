# Script para organizar o ambiente portatil no SSD externo D:\
import shutil
import os

SSD = "D:\\"
CODEVAULT = os.path.join(SSD, "CodeVault Portable")
CLIENTFLOW_DST = os.path.join(SSD, "ClientFlow")
SRC = r"C:\Users\Sueli\Desktop\ClientFlow"

def status(msg):
    print(f"  -> {msg}")

print("=" * 50)
print("  ORGANIZANDO SSD EXTERNO")
print("=" * 50)

# 1. Criar pasta CodeVault
os.makedirs(CODEVAULT, exist_ok=True)
status("Pasta 'CodeVault Portable' criada")

# 2. Copiar portable_tools subdirs
for folder, dst_name in [("vscode", "VSCode"), ("python", "Python"), ("node", "Node")]:
    src_path = os.path.join(SRC, "portable_tools", folder)
    dst_path = os.path.join(CODEVAULT, dst_name)
    if os.path.exists(dst_path):
        status(f"{dst_name} ja existe, pulando...")
        continue
    if os.path.exists(src_path):
        status(f"Copiando {dst_name}... (pode demorar)")
        shutil.copytree(src_path, dst_path)
        status(f"{dst_name} OK")
    else:
        status(f"AVISO: {src_path} nao encontrado!")

# 3. Copiar projeto ClientFlow
status("Copiando projeto ClientFlow...")
EXCLUDE = {"portable_tools", "offline_packages", ".venv", ".venv313", "__pycache__", ".pytest_cache", "node_modules"}

def ignore_dirs(directory, contents):
    if os.path.normpath(directory) == os.path.normpath(SRC):
        return [c for c in contents if c in EXCLUDE]
    return ["__pycache__"] if "__pycache__" in contents else []

if os.path.exists(CLIENTFLOW_DST):
    status("ClientFlow ja existe no SSD, pulando...")
else:
    shutil.copytree(SRC, CLIENTFLOW_DST, ignore=ignore_dirs)
    status("ClientFlow OK")

# 4. Verificacao
print()
print("=" * 50)
print("  VERIFICACAO")
print("=" * 50)
checks = [
    ("VSCode Code.exe", os.path.join(CODEVAULT, "VSCode", "Code.exe")),
    ("Python python.exe", os.path.join(CODEVAULT, "Python", "python.exe")),
    ("Node node.exe", os.path.join(CODEVAULT, "Node", "node.exe")),
    ("ClientFlow backend", os.path.join(CLIENTFLOW_DST, "backend", "main.py")),
]
all_ok = True
for name, path in checks:
    ok = os.path.exists(path)
    mark = "[OK]" if ok else "[FALHOU]"
    print(f"  {mark} {name}")
    if not ok:
        all_ok = False

# 5. Criar ABRIR VSCODE.bat
bat_path = os.path.join(CODEVAULT, "ABRIR VSCODE.bat")
with open(bat_path, "w", encoding="utf-8") as f:
    f.write('@echo off\n')
    f.write('chcp 65001 >nul 2>&1\n')
    f.write('title CodeVault Portable\n')
    f.write('set "VAULT=%~dp0"\n')
    f.write('set "VSCODE=%VAULT%VSCode\\bin\\code.cmd"\n')
    f.write('set "PATH=%VAULT%Python;%VAULT%Python\\Scripts;%VAULT%Node;%PATH%"\n')
    f.write('echo.\n')
    f.write('echo  CodeVault Portable - VS Code Movel\n')
    f.write('echo.\n')
    f.write('if not exist "%VSCODE%" (\n')
    f.write('    echo  [ERRO] VS Code nao encontrado!\n')
    f.write('    pause\n')
    f.write('    exit /b 1\n')
    f.write(')\n')
    f.write('echo  Abrindo VS Code...\n')
    f.write('call "%VSCODE%" .\n')
    f.write('pause\n')
status("ABRIR VSCODE.bat criado")

# 6. Criar ABRIR CLIENTFLOW.bat
bat_cf = os.path.join(CODEVAULT, "ABRIR CLIENTFLOW.bat")
with open(bat_cf, "w", encoding="utf-8") as f:
    f.write('@echo off\n')
    f.write('chcp 65001 >nul 2>&1\n')
    f.write('title CodeVault - ClientFlow\n')
    f.write('set "VAULT=%~dp0"\n')
    f.write('set "VSCODE=%VAULT%VSCode\\bin\\code.cmd"\n')
    f.write('set "PATH=%VAULT%Python;%VAULT%Python\\Scripts;%VAULT%Node;%PATH%"\n')
    f.write('for %%d in ("%VAULT%..") do set "SSD=%%~fd"\n')
    f.write('set "PROJECT=%SSD%\\ClientFlow"\n')
    f.write('echo.\n')
    f.write('echo  CodeVault - Abrindo ClientFlow\n')
    f.write('echo.\n')
    f.write('if not exist "%PROJECT%" (\n')
    f.write('    echo  [ERRO] ClientFlow nao encontrado!\n')
    f.write('    pause\n')
    f.write('    exit /b 1\n')
    f.write(')\n')
    f.write('call "%VSCODE%" "%PROJECT%"\n')
    f.write('pause\n')
status("ABRIR CLIENTFLOW.bat criado")

# 7. Criar LEIA-ME.txt
readme_path = os.path.join(CODEVAULT, "LEIA-ME.txt")
with open(readme_path, "w", encoding="utf-8") as f:
    f.write("CODEVAULT PORTABLE - VS CODE MOVEL\n")
    f.write("=" * 40 + "\n\n")
    f.write("COMO USAR EM QUALQUER COMPUTADOR:\n")
    f.write("-" * 40 + "\n")
    f.write("1. Conecte o SSD no computador\n")
    f.write("2. Abra a pasta 'CodeVault Portable'\n")
    f.write("3. Clique duas vezes em:\n")
    f.write("   - ABRIR VSCODE.bat      -> abre VS Code vazio\n")
    f.write("   - ABRIR CLIENTFLOW.bat   -> abre o projeto ClientFlow\n\n")
    f.write("NAO PRECISA INSTALAR NADA!\n")
    f.write("Python, Node.js e VS Code ja estao incluidos.\n\n")
    f.write("REQUISITOS: Windows 10/11 (64-bit)\n\n")
    f.write("ENGLISH: Portable dev environment. Plug SSD, double-click\n")
    f.write("'ABRIR VSCODE.bat' to start coding. No install needed.\n")
status("LEIA-ME.txt criado")

# 8. Resultado
print()
print("=" * 50)
print("  ESTRUTURA NO SSD")
print("=" * 50)
for item in sorted(os.listdir(CODEVAULT)):
    tipo = "[DIR]" if os.path.isdir(os.path.join(CODEVAULT, item)) else "[ARQ]"
    print(f"  {tipo} {item}")
print()
if all_ok:
    print("  TUDO PRONTO!")
else:
    print("  ALGUNS ITENS FALTANDO")
print()
print("SCRIPT_CONCLUIDO")
