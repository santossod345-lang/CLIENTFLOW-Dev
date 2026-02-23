#!/usr/bin/env python
"""
Script para monitorar deploy no Railway
"""
import subprocess
import sys
import time
import json

def run_cmd(cmd):
    """Executar comando Railway"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True,
            timeout=30
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", "Timeout", 1
    except Exception as e:
        return "", str(e), 1

print("=" * 60)
print("🚀 MONITORANDO DEPLOY RAILWAY")
print("=" * 60)

# Tentar Railway logs
print("\n📋 Logs do Railway (últimas 50 linhas):\n")
stdout, stderr, code = run_cmd("railway logs --limit 50 2>&1")

if code == 0 and stdout:
    lines = stdout.split('\n')
    for line in lines[-50:]:
        if line.strip():
            # Highlight important patterns
            if "error" in line.lower() or "failed" in line.lower():
                print(f"❌ {line}")
            elif "startup" in line.lower() or "complete" in line.lower():
                print(f"✓ {line}")
            elif "502" in line or "timeout" in line:
                print(f"⚠️  {line}")
            else:
                print(f"   {line}")
else:
    print("❌ Não consegui acessar logs do Railway")
    print(f"Erro: {stderr}")
    print("\n📌 Login no Railway Dashboard em: https://railway.app")
    print("   Projeto: c15ea1ba-d177-40b4-8b6f-ed071aeeef08")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ Verificação concluída")
print("=" * 60)
print("\n📌 Dashboard Railway:")
print("   https://railway.app/project/c15ea1ba-d177-40b4-8b6f-ed071aeeef08")
print("\n Aguarde 2-5 minutos para o deploy completar.")
print(" Procure por:")
print("   ✓ 'Initializing ClientFlow API'")
print("   ✓ 'app ready'")
print("   ✗ Evite: 'ImportError', '502', 'timeout'")
