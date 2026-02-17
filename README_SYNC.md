# 📚 Guia de Sincronização de Repositórios - ClientFlow

## 🎯 Objetivo

Sincronizar automaticamente o projeto ClientFlow entre dois repositórios GitHub:
- **origin**: `santossod345-lang/CLIENTFLOW-Dev` (Conta Premium - Santos)
- **upstream**: `luizfernandoantonio345-webs/CLIENTFLOW` (Conta Original - Luiz)

---

## 📁 Arquivos Criados

### 1. **sync_repos.ps1** (Script Principal)
Script que realiza a sincronização entre os dois repositórios.

**Uso:**
```powershell
# Sincronização com confirmação manual
.\sync_repos.ps1

# Sincronização automática
.\sync_repos.ps1 -Auto

# Com modo verboso
.\sync_repos.ps1 -Verbose
```

**O que faz:**
- ✅ Verifica se há mudanças locais
- ✅ Faz commit automático (modo -Auto)
- ✅ Faz fetch dos dois remotes
- ✅ Faz push para origin e upstream
- ✅ Registra tudo em `sync_repos.log`

---

### 2. **setup_auto_sync.ps1** (Configurador)
Configura sincronização automática usando Task Scheduler do Windows.

**Requisitos:**
- ⚠️ Deve ser executado como **Administrador**

**Uso:**
```powershell
# Abra o PowerShell como Administrador, então:
.\setup_auto_sync.ps1
```

**Frequências disponíveis:**
- A cada 30 minutos
- A cada 1 hora
- A cada 4 horas
- Diariamente às 8h

---

### 3. **menu_sync.ps1** (Menu Interativo)
Interface amigável para gerenciar a sincronização.

**Uso:**
```powershell
.\menu_sync.ps1
```

**Opções do Menu:**
1. Sincronizar agora (com confirmação)
2. Sincronizar agora (modo automático)
3. Configurar sincronização automática
4. Ver histórico de sincronizações
5. Ver status dos repositórios
6. Limpar arquivo de log

---

## ⚡ Guia Rápido

### Primeira Vez - Configuração
```powershell
# 1. Abra como Administrador
# 2. Execute:
.\setup_auto_sync.ps1

# 3. Escolha a frequência desejada
```

### Sincronização Manual
```powershell
# Modo interativo
.\menu_sync.ps1

# Ou sincronize direto
.\sync_repos.ps1
```

### Modo Automático
```powershell
# Sem confirmação (para agendamento)
.\sync_repos.ps1 -Auto
```

---

## 📊 Fluxo de Sincronização

```
Local Changes
    ↓
Check Status
    ↓
Commit (se -Auto)
    ↓
Fetch origin & upstream
    ↓
Push to origin (Santos)
    ↓
Push to upstream (Luiz)
    ↓
Log Result
```

---

## 📝 Arquivo de Log

Todas as sincronizações são registradas em `sync_repos.log`:

```
[2026-02-17 10:30:45] [INFO] === INICIANDO SINCRONIZAÇÃO ===
[2026-02-17 10:30:45] [INFO] Verificando status do repositório...
[2026-02-17 10:30:46] [INFO] Fazendo fetch de origin (santossod345-lang)...
[2026-02-17 10:30:48] [INFO] Fazendo push para origin (santossod345-lang)...
[2026-02-17 10:30:50] [INFO] Push concluído com sucesso para ambos os repositórios
[2026-02-17 10:30:50] [INFO] === SINCRONIZAÇÃO CONCLUÍDA ===
```

---

## 🔄 Agendamento Automático

### Ver Tarefas Agendadas
```powershell
Get-ScheduledTask -TaskName "ClientFlow-RepoSync"
```

### Editar Tarefa
```powershell
$task = Get-ScheduledTask -TaskName "ClientFlow-RepoSync"
$task | Set-ScheduledTask -Trigger (New-ScheduledTaskTrigger -Daily -At 09:00)
```

### Remover Agendamento
```powershell
Unregister-ScheduledTask -TaskName "ClientFlow-RepoSync" -Confirm:$false
```

---

## ⚙️ Configuração Git

Os dois remotes já estão configurados:

```
origin   → https://github.com/santossod345-lang/CLIENTFLOW-Dev.git
upstream → git@github-luiz:luizfernandoantonio345-webs/CLIENTFLOW.git
```

Para adicionar manualmente:
```powershell
git remote add origin https://github.com/santossod345-lang/CLIENTFLOW-Dev.git
git remote add upstream git@github-luiz:luizfernandoantonio345-webs/CLIENTFLOW.git
```

---

## 🚨 Troubleshooting

### Erro de Autenticação
```
fatal: Authentication failed
```
**Solução:** Verifique se as chaves SSH ou tokens de acesso estão configuradas corretamente.

### Conflitos de Merge
Se houver conflitos, resolva-os manualmente:
```powershell
git status  # Ver conflitos
git merge --abort  # Cancelar merge
```

### Permissões Insuficientes
```
You do not have permission to push
```
**Solução:** Verifique se suas chaves SSH têm permissão de push nos repositórios.

### Task Scheduler Falha
```
0x80070005: Access Denied
```
**Solução:** Execute `setup_auto_sync.ps1` como Administrador.

---

## 💡 Dicas

1. **Modo Automático**: Use para CI/CD ou agendamentos sem interrupções
2. **Modo Manual**: Melhor para revisão antes de distribuir
3. **Log**: Monitore para detectar falhas de sincronização
4. **Backup**: Os dois repositórios funcionam como backup um do outro

---

## 📞 Suporte

Se encontrar problemas:

1. Verifique o arquivo `sync_repos.log`
2. Teste manualmente: `git push origin main`
3. Teste manualmente: `git push upstream main`
4. Verifique suas credenciais SSH/HTTPS
5. Confirme que tem permissão nos dois repositórios

---

**Última atualização:** 17/02/2026  
**Versão:** 1.0
