#!/usr/bin/env python
"""
ClientFlow - Generate Production Secrets
Gera SECRET_KEY seguro e outras configurações para produção
"""

import secrets
import json
from datetime import datetime
import sys

def generate_secret_key(length=32):
    """Gera uma chave segura para JWT"""
    return secrets.token_urlsafe(length)

def generate_config():
    """Gera configuração completa para produção"""
    
    config = {
        "timestamp": datetime.now().isoformat(),
        "secrets": {
            "SECRET_KEY": generate_secret_key(32),
            "DATABASE_ADMIN_PASSWORD": generate_secret_key(16),
        },
        "environment": {
            "ENVIRONMENT": "production",
            "LOG_LEVEL": "INFO",
            "ACCESS_TOKEN_EXPIRE_MINUTES": 15,
            "REFRESH_TOKEN_EXPIRE_DAYS": 7,
        },
        "optional": {
            "ENABLE_AI_ASSISTANT": "false",
            "REDIS_URL": "redis://localhost:6379",
            "MAX_CLIENTS_PER_COMPANY": "10000",
            "MAX_SERVICES_PER_COMPANY": "50000",
        }
    }
    
    return config

def main():
    print("=" * 70)
    print("ClientFlow - Gerador de Secrets para Produção")
    print("=" * 70)
    print()
    
    config = generate_config()
    
    print("🔐 SECRETS GERADOS (Salve em local seguro)")
    print("-" * 70)
    print(f"SECRET_KEY = {config['secrets']['SECRET_KEY']}")
    print()
    print("⚠️  NUNCA comitar SECRET_KEY no Git!")
    print("    Adicionar em Railway → Variables → SECRET_KEY")
    print()
    
    print("📋 VARIÁVEIS DE AMBIENTE RAILWAY")
    print("-" * 70)
    print("Copie e adicione em Railway Dashboard → Variables:")
    print()
    
    env_vars = {
        **config['secrets'],
        **config['environment'],
        "ALLOWED_ORIGINS": "https://seu-app.vercel.app,https://api.seu-dominio.com",
        "DATABASE_URL": "postgresql://user:password@host:5432/clientflow",
    }
    
    for key, value in env_vars.items():
        if key == "SECRET_KEY":
            print(f"SECRET_KEY={value}")
        elif key == "DATABASE_URL":
            print(f"DATABASE_URL=<Railway gera automaticamente>")
        else:
            print(f"{key}={value}")
    
    print()
    print("📋 VARIÁVEIS DE AMBIENTE VERCEL")
    print("-" * 70)
    print("Copie e adicione em Vercel → Settings → Environment Variables:")
    print()
    print("VITE_API_URL=https://seu-id.railway.app/api")
    print()
    
    print("✅ PRÓXIMOS PASSOS")
    print("-" * 70)
    print("1. Copie o SECRET_KEY acima")
    print("2. Vá para Railway Dashboard → Variables")
    print("3. Clique 'Add Variable'")
    print("4. Name: SECRET_KEY")
    print("5. Value: <cole o valor gerado>")
    print("6. Click 'Save'")
    print()
    print("7. Repita para outras variáveis")
    print("8. Deploy acontecerá automaticamente")
    print()
    
    print("🔗 LINKS ÚTEIS")
    print("-" * 70)
    print("Railway:   https://railway.app")
    print("Vercel:    https://vercel.com")
    print("Docs:      DEPLOYMENT_QUICK_START.md")
    print()
    
    # Exportar para arquivo também
    config_file = "prod_secrets.json"
    
    output = {
        "generated_at": config['timestamp'],
        "warning": "NUNCA comitar este arquivo! Salvar em local seguro!",
        "secrets": config['secrets'],
        "instructions": {
            "step_1": "Adicionar SECRET_KEY em Railway Variables",
            "step_2": "Adicionar ALLOWED_ORIGINS em Railway Variables (seu domínio Vercel)",
            "step_3": "Adicionar VITE_API_URL em Vercel Variables",
            "step_4": "Git push origin main",
            "step_5": "Aguardar deploy automático",
        }
    }
    
    try:
        with open(config_file, 'w') as f:
            json.dump(output, f, indent=2)
        print(f"📁 Configuração salva em: {config_file}")
        print("   ⚠️  Não commitar este arquivo!")
        print("   ⚠️  Adicionar em .gitignore: prod_secrets.json")
    except Exception as e:
        print(f"Erro ao salvar: {e}")
    
    print()
    print("=" * 70)
    print("✨ Secrets gerados com sucesso!")
    print("=" * 70)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)
