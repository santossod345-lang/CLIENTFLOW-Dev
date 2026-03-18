# -*- coding: utf-8 -*-
import shutil
import os
import sys

SSD = "D:\\"
CODEVAULT = os.path.join(SSD, "CodeVault Portable")
CLIENTFLOW_DST = os.path.join(SSD, "ClientFlow")
SRC = r"C:\Users\Sueli\Desktop\ClientFlow"

print("=" * 50)
print("  ORGANIZANDO SSD EXTERNO")
print("=" * 50)

# 1. Criar pasta CodeVault
os.makedirs(CODEVAULT, exist_ok=True)
print("[OK] Pasta CodeVault Portable criada")

# 2. Copiar VSCode, Python, Node
for folder, dst_name in [("vscode", "VSCode"), ("python", "Python"), ("node", "Node")]:
    src_path = os.path.join(SRC, "portable_tools", folder)
    dst_path = os.path.join(CODEVAULT, dst_name)
    if os.path.exists(dst_path):
        print(f"[JA EXISTE] {dst_name}")
        continue
    if os.path.exists(src_path):
        print(f"[COPIANDO] {dst_name}... aguarde")
        shutil.copytree(src_path, dst_path)
        print(f"[OK] {dst_name}")
    else:
        print(f"[ERRO] {src_path} nao encontrado!")

# 3. Copiar projeto ClientFlow
EXCLUDE = {"portable_tools", "offline_packages", ".venv", ".venv313",
           "__pycache__", ".pytest_cache", "node_modules", "setup_ssd.py",
           "setup_ssd_v2.py"}

def ignore_dirs(directory, contents):
    if os.path.normpath(directory) == os.path.normpath(SRC):
        return [c for c in contents if c in EXCLUDE]
    return ["__pycache__"] if "__pycache__" in contents else []

if os.path.exists(CLIENTFLOW_DST):
    print("[JA EXISTE] ClientFlow no SSD")
else:
    print("[COPIANDO] Projeto ClientFlow... aguarde")
    shutil.copytree(SRC, CLIENTFLOW_DST, ignore=ignore_dirs)
    print("[OK] ClientFlow copiado")

# 4. Criar ABRIR VSCODE.bat
bat1 = os.path.join(CODEVAULT, "ABRIR VSCODE.bat")
with open(bat1, "w") as f:
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
    f.write('    echo [ERRO] VS Code nao encontrado!\n')
    f.write('    pause\n')
    f.write('    exit /b 1\n')
    f.write(')\n')
    f.write('echo Abrindo VS Code...\n')
    f.write('call "%VSCODE%" .\n')
    f.write('pause\n')
print("[OK] ABRIR VSCODE.bat criado")

# 5. Criar ABRIR CLIENTFLOW.bat
bat2 = os.path.join(CODEVAULT, "ABRIR CLIENTFLOW.bat")
with open(bat2, "w") as f:
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
    f.write('    echo [ERRO] ClientFlow nao encontrado!\n')
    f.write('    pause\n')
    f.write('    exit /b 1\n')
    f.write(')\n')
    f.write('call "%VSCODE%" "%PROJECT%"\n')
    f.write('pause\n')
print("[OK] ABRIR CLIENTFLOW.bat criado")

# 6. Criar LEIA-ME.txt
readme = os.path.join(CODEVAULT, "LEIA-ME.txt")
with open(readme, "w") as f:
    f.write("========================================\n")
    f.write("  CodeVault Portable\n")
    f.write("  VS Code Movel / Portable VS Code\n")
    f.write("========================================\n\n")
    f.write("COMO USAR EM QUALQUER COMPUTADOR:\n")
    f.write("---------------------------------\n")
    f.write("1. Conecte o SSD no computador\n")
    f.write("2. Abra a pasta 'CodeVault Portable'\n")
    f.write("3. Clique duas vezes em:\n")
    f.write("   - ABRIR VSCODE.bat      -> abre VS Code vazio\n")
    f.write("   - ABRIR CLIENTFLOW.bat   -> abre o projeto ClientFlow\n\n")
    f.write("NAO PRECISA INSTALAR NADA!\n")
    f.write("Python, Node.js e VS Code ja estao incluidos.\n\n")
    f.write("REQUISITOS: Windows 10/11 (64-bit)\n")
print("[OK] LEIA-ME.txt criado")

# 7. Verificacao final
print()
print("=" * 50)
print("  VERIFICACAO FINAL")
print("=" * 50)
checks = [
    ("VSCode Code.exe", os.path.join(CODEVAULT, "VSCode", "Code.exe")),
    ("Python python.exe", os.path.join(CODEVAULT, "Python", "python.exe")),
    ("Node node.exe", os.path.join(CODEVAULT, "Node", "node.exe")),
    ("ClientFlow backend", os.path.join(CLIENTFLOW_DST, "backend", "main.py")),
    ("ABRIR VSCODE.bat", bat1),
    ("ABRIR CLIENTFLOW.bat", bat2),
]
ok = True
for name, path in checks:
    exists = os.path.exists(path)
    print(f"  {'[OK]' if exists else '[FALTA]'} {name}")
    if not exists:
        ok = False

print()
if ok:
    print("  TUDO PRONTO!")
else:
    print("  Alguns itens faltando!")
print()
print("SCRIPT_CONCLUIDO")
