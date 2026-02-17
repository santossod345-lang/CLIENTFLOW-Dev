"""
Camada de serviços para regras de negócio, inteligência e automações do ClientFlow
"""
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from backend import models

def classificar_cliente(cliente: models.Cliente, db: Session):
    """
    Atualiza status_cliente, nivel_atividade, score_atividade e importante
    """
    atendimentos = db.query(models.Atendimento).filter(models.Atendimento.cliente_id == cliente.id, models.Atendimento.empresa_id == cliente.empresa_id).all()
    total = len(atendimentos)
    if total == 0:
        cliente.status_cliente = "novo"
        cliente.nivel_atividade = "baixo"
        cliente.score_atividade = 0
        cliente.importante = 0
        return
    datas = [a.data_atendimento for a in atendimentos if a.data_atendimento]
    datas.sort(reverse=True)
    meses_sem_retorno = (datetime.now(timezone.utc) - datas[0]).days // 30 if datas else 99
    if total >= 5:
        cliente.status_cliente = "frequente"
        cliente.nivel_atividade = "alto"
        cliente.importante = 1
    elif meses_sem_retorno >= 6:
        cliente.status_cliente = "inativo"
        cliente.nivel_atividade = "baixo"
        cliente.importante = 0
    elif meses_sem_retorno <= 2:
        cliente.status_cliente = "recente"
        cliente.nivel_atividade = "medio"
        cliente.importante = 0
    else:
        cliente.status_cliente = "ativo"
        cliente.nivel_atividade = "medio"
        cliente.importante = 0
    cliente.score_atividade = min(100, total * 20 - meses_sem_retorno * 5)

def atualizar_status_todos_clientes(empresa_id: int, db: Session):
    clientes = db.query(models.Cliente).filter(models.Cliente.empresa_id == empresa_id).all()
    for cliente in clientes:
        classificar_cliente(cliente, db)
    db.commit()

def log_acao(empresa_id: int, usuario: str, acao: str, _db: Session = None):
    # Placeholder para logs, pode ser expandido para salvar em tabela/logfile
    print(f"[LOG] Empresa {empresa_id} | Usuário: {usuario} | {acao} | {datetime.now(timezone.utc)}")
