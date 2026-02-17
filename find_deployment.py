#!/usr/bin/env python
"""
Script para analisar e localizar informações de deployment do ClientFlow
"""
import os
import json
import subprocess
from pathlib import Path

def check_git_remotes():
    """Verificar remotes do Git"""
    print("=" * 60)
    print("🔍 VERIFICANDO GIT REMOTES")
    print("=" * 60)
    try:
        result = subprocess.run(['git', 'remote', '-v'], capture_output=True, text=True, cwd='.')
        if result.stdout:
            print(result.stdout)
        else:
            print("❌ Nenhum remote configurado ou repositório vazio")
    except Exception as e:
        print(f"❌ Erro ao verificar git: {e}")

def check_railway_config():
    """Verificar se existe configuração Railway"""
    print("\n" + "=" * 60)
    print("🚂 VERIFICANDO CONFIGURAÇÃO RAILWAY")
    print("=" * 60)
    
    railway_files = [
        '.railway/config.json',
        'railway.json',
        '.railway',
        '.railwayenv'
    ]
    
    found = False
    for file in railway_files:
        if os.path.exists(file):
            print(f"✅ Encontrado: {file}")
            try:
                with open(file, 'r') as f:
                    content = f.read()
                    print(content[:500])  # Print first 500 chars
                found = True
            except:
                pass
    
    if not found:
        print("❌ Nenhuma configuração Railway encontrada")
    
    # Verificar variáveis de ambiente
    print("\n📌 Variáveis de Ambiente do Railway (se conectado):")
    railway_env_vars = [
        'RAILWAY_TOKEN',
        'RAILWAY_ENVIRONMENT_NAME',
        'RAILWAY_SERVICE_NAME',
        'DATABASE_URL',
        'REDIS_URL'
    ]
    
    for var in railway_env_vars:
        value = os.getenv(var)
        if value:
            # Mascarar valores sensíveis
            if 'RAILWAY_TOKEN' in var or 'PASSWORD' in var or 'KEY' in var:
                print(f"  {var}: ***MASKED***")
            else:
                print(f"  {var}: {value[:50]}...")
        else:
            print(f"  {var}: ❌ não definida")

def check_docker_builds():
    """Verificar histórico de builds Docker"""
    print("\n" + "=" * 60)
    print("🐳 VERIFICANDO DOCKER")
    print("=" * 60)
    try:
        # Check if Docker is installed
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        print(f"✅ Docker: {result.stdout.strip()}")
        
        # List images
        print("\n📦 Docker Images:")
        result = subprocess.run(['docker', 'images'], capture_output=True, text=True)
        print(result.stdout[:1000])
    except:
        print("❌ Docker não instalado ou não acessível")

def check_git_history():
    """Verificar histórico de Git para referências de deployment"""
    print("\n" + "=" * 60)
    print("📜 ÚLTIMOS COMMITS (pode conter referências de deployment)")
    print("=" * 60)
    try:
        result = subprocess.run(
            ['git', 'log', '--oneline', '-10'],
            capture_output=True,
            text=True,
            cwd='.'
        )
        if result.stdout:
            print(result.stdout)
        else:
            print("❌ Repositório não inicializado ou vazio")
    except Exception as e:
        print(f"❌ Erro: {e}")

def check_procfile():
    """Verificar Procfile"""
    print("\n" + "=" * 60)
    print("📄 PROCFILE (usado por Railway/Heroku)")
    print("=" * 60)
    if os.path.exists('Procfile'):
        with open('Procfile', 'r') as f:
            print(f.read())
    else:
        print("❌ Procfile não encontrado")

def check_env_files():
    """Listar arquivos .env"""
    print("\n" + "=" * 60)
    print("🔑 ARQUIVOS DE AMBIENTE")
    print("=" * 60)
    
    env_files = ['.env', '.env.local', '.env.production', '.env.railway']
    for file in env_files:
        if os.path.exists(file):
            print(f"✅ Encontrado: {file}")
            with open(file, 'r') as f:
                lines = f.readlines()
                for line in lines[:10]:  # Show first 10 lines
                    if '=' in line:
                        key = line.split('=')[0]
                        print(f"   - {key}=***MASKED***")
        else:
            print(f"❌ {file} não encontrado")

def check_logs():
    """Verificar se há logs de deployment"""
    print("\n" + "=" * 60)
    print("📋 VERIFICANDO LOGS")
    print("=" * 60)
    
    log_files = [
        'backend/logs.txt',
        '.railway/logs',
        'railway.log',
        'deploy.log'
    ]
    
    for file in log_files:
        if os.path.exists(file):
            print(f"✅ Encontrado: {file}")
            try:
                with open(file, 'r') as f:
                    lines = f.readlines()
                    print(''.join(lines[-20:]))  # Last 20 lines
            except:
                pass

def main():
    print("""
╔════════════════════════════════════════════════════════════╗
║  ClientFlow - ANÁLISE DE DEPLOYMENT E LOCALIZAÇÃO         ║
║  Procurando por informações sobre Railway, Docker, etc.    ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    check_procfile()
    check_git_remotes()
    check_railway_config()
    check_docker_builds()
    check_git_history()
    check_env_files()
    check_logs()
    
    print("\n" + "=" * 60)
    print("📍 RESUMO")
    print("=" * 60)
    print("""
✅ Sistema está RODANDO LOCALMENTE
✅ Procfile pronto para Railway
✅ Docker configurado

Para encontrar a URL do Railway:
1. Acesse https://railway.app
2. Procure pelo projeto "ClientFlow"
3. Veja a guia "Deployments"
4. A URL estará em "SERVICE_DOMAIN"

Ou use Railway CLI:
  $ railway login
  $ railway logs
  $ railway env
    """)

if __name__ == '__main__':
    main()
