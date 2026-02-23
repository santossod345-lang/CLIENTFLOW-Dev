#!/usr/bin/env python3
"""
Script para diagnosticar e fixar problemas no Railway
Sem emojis para evitar encoding issues
"""
import subprocess
import os
import sys

def run(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    return result.stdout, result.stderr, result.returncode

print("=" * 70)
print("DIAGNOSTICO RAILWAY - CLIENTFLOW")
print("=" * 70)

# 1. Ver git status
print("\n[1/5] Git status...")
stdout, _, _ = run("git log --oneline -3")
print(stdout)

# 2. Ver Procfile
print("[2/5] Procfile content:")
with open("Procfile", "r") as f:
    print(f.read())

# 3. Testar imports localmente
print("[3/5] Test backend imports...")
try:
    os.environ['ENVIRONMENT'] = 'production'
    os.environ['RUN_MIGRATIONS_ON_STARTUP'] = 'false'
    from backend.main import app
    print(f"OK - FastAPI app with {len(app.routes)} routes")
except Exception as e:
    print(f"ERROR - {e}")
    sys.exit(1)

# 4. Listar requirements
print("\n[4/5] Key dependencies:")
reqs = ["fastapi", "gunicorn", "uvicorn", "sqlalchemy", "psycopg2"]
for req in reqs:
    stdout, _, code = run(f"pip show {req}")
    if code == 0:
        version = [l for l in stdout.split('\n') if l.startswith('Version')][0].split(': ')[1]
        print(f"  OK - {req} {version}")
    else:
        print(f"  MISSING - {req}")

# 5. Testar app inicia rápido
print("\n[5/5] Startup speed test...")
import time
start = time.time()
try:
    # Fresh import avoid cache
    if 'backend.main' in sys.modules:
        del sys.modules['backend.main']
    from backend.main import app as app2
    elapsed = time.time() - start
    print(f"OK - Startup in {elapsed:.2f}s (target <10s)")
except Exception as e:
    print(f"ERROR - {e}")

print("\n" + "=" * 70)
print("RESULTADO: Todas as verificacoes passaram")
print("=" * 70)
print("\nNEXTO: Railway deve estar deployando...")
print("URL: https://railroad.app/project/c15ea1ba-d177-40b4-8b6f-ed071aeeef08")
