# Plano de Row-Level Security (RLS) para ClientFlow

## Objetivo
Garantir isolamento real de dados entre empresas (multi-tenant) no banco de dados, impedindo acesso cruzado por queries acidentais ou maliciosas.

## Estratégia Atual
- Cada empresa possui um schema próprio (`empresa_{id}`) no PostgreSQL.
- Todas queries são executadas com `SET search_path TO empresa_{id}, public`.
- Todas tabelas possuem coluna `empresa_id` e as queries filtram por `empresa_id`.

## Auditoria de Queries
- Todas rotas usam `tenant_db` com search_path isolado.
- Filtros explícitos por `empresa_id` em todas queries:
  - `clientes`: `.filter(models.Cliente.empresa_id == empresa.id)`
  - `atendimentos`: `.filter(models.Atendimento.empresa_id == empresa.id)`
  - `dashboard`: `.filter(models.Cliente.empresa_id == empresa.id)`
- Rotas de IA, dashboard, CRUD, logs, exportação: sempre filtram por empresa.
- Não há queries sem filtro de empresa_id.

## Plano de RLS (PostgreSQL)
1. **Ativar RLS nas tabelas**:
   ```sql
   ALTER TABLE clientes ENABLE ROW LEVEL SECURITY;
   ALTER TABLE atendimentos ENABLE ROW LEVEL SECURITY;
   ALTER TABLE logs_acoes ENABLE ROW LEVEL SECURITY;
   ```
2. **Política de acesso por empresa**:
   ```sql
   CREATE POLICY empresa_isolation ON clientes
     USING (empresa_id = current_setting('app.empresa_id')::int);
   CREATE POLICY empresa_isolation ON atendimentos
     USING (empresa_id = current_setting('app.empresa_id')::int);
   CREATE POLICY empresa_isolation ON logs_acoes
     USING (empresa_id = current_setting('app.empresa_id')::int);
   ```
3. **Setar variável de sessão**:
   - No início de cada request:
     ```sql
     SET app.empresa_id = <empresa_id>;
     ```
   - Pode ser feito via SQLAlchemy:
     ```python
     db.execute(f"SET app.empresa_id = {empresa.id}")
     ```

## Benefícios
- Impede acesso cruzado mesmo em caso de bug na query.
- Segurança garantida no nível do banco.
- Compatível com auditoria e logs.

## Observações
- RLS requer PostgreSQL.
- Para SQLite, apenas filtro manual.
- Recomenda-se auditar queries periodicamente.

---

**Plano pronto para produção.**
