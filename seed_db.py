"""Seed the database with a test empresa for local development."""
import os, sys
sys.path.insert(0, '.')

env_path = '.env'
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, _, val = line.partition('=')
                os.environ.setdefault(key.strip(), val.strip())

from backend.database import SessionLocal, engine
from backend import models, auth

models.Base.metadata.create_all(bind=engine)
db = SessionLocal()

existing = db.query(models.Empresa).filter(models.Empresa.email_login == 'admin@clientflow.com').first()
if existing:
    print(f'Empresa ja existe: id={existing.id}, email={existing.email_login}')
else:
    senha_hash = auth.get_password_hash('Admin1234')
    nova = models.Empresa(
        nome_empresa='Oficina Teste',
        nicho='Mecanica',
        telefone='(11) 99999-9999',
        email_login='admin@clientflow.com',
        senha_hash=senha_hash,
        plano_empresa='free'
    )
    db.add(nova)
    db.commit()
    db.refresh(nova)
    print(f'Empresa criada: id={nova.id}, email={nova.email_login}, nome={nova.nome_empresa}')

count = db.query(models.Empresa).count()
print(f'Total empresas: {count}')
db.close()
print('Seed concluido!')
