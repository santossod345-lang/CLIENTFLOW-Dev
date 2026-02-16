# Multi-tenant PostgreSQL SaaS: Documentação de Migração e Operação

## 1. Configuração do Banco
- Defina as variáveis de ambiente POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, POSTGRES_HOST, POSTGRES_PORT.
- O sistema cria um schema exclusivo para cada empresa ao cadastrar.

## 2. Migrations (Alembic)
- Use o template em `alembic/versions/multi_tenant_template.py` para criar/alterar tabelas em todos os schemas de empresas.
- Rode `alembic upgrade head` para aplicar migrations.

## 3. Migração de Dados
- Execute `python migrar_sqlite_postgres.py` para migrar dados do SQLite para o PostgreSQL multi-tenant.
- O script migra empresas (schema público) e clientes/atendimentos para o schema de cada empresa.

## 4. Operação Multi-tenant
- Cada requisição usa o schema correto do tenant, garantindo isolamento real.
- Novas empresas criam schemas automaticamente.

## 5. Recomendações
- Sempre versionar migrations.
- Testar integridade dos dados após migração.
- Monitorar uso de schemas e performance.

---

Dúvidas ou problemas? Consulte a equipe de arquitetura.
