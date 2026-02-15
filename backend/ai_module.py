"""
ai_module.py
Módulo isolado para lógica de Inteligência Artificial do ClientFlow.
Não altera funcionalidades existentes.
"""

import os
import openai
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# Configuração da API OpenAI (pode ser adaptado para outras APIs)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

# Função utilitária para chamada segura à API de IA
def call_openai(prompt: str, max_tokens: int = 128) -> Optional[str]:
    if not OPENAI_API_KEY:
        return None
    try:
        response = openai.Completion.create(
            engine="gpt-3.5-turbo-instruct",
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=0.5
        )
        return response.choices[0].text.strip()
    except Exception as e:
        # Logar erro, mas não travar sistema
        print(f"[AI ERROR] {e}")
        return None

# 1. IA Analista de Clientes
def analisar_cliente(atendimentos: List[Dict[str, Any]]) -> str:
    """
    Recebe lista de atendimentos do cliente e retorna status_ia_cliente.
    """
    if not atendimentos:
        return "Cliente novo"
    total = len(atendimentos)
    datas = sorted([a['data'] for a in atendimentos if 'data' in a])
    if not datas:
        return "Cliente novo"
    ultima = datetime.strptime(datas[-1], "%Y-%m-%d")
    dias_desde_ultimo = (datetime.now() - ultima).days
    frequencia = dias_desde_ultimo / total if total > 0 else 0
    if dias_desde_ultimo > 180:
        return "Cliente inativo"
    elif total > 10:
        return "Cliente importante"
    elif frequencia < 60:
        return "Cliente frequente"
    else:
        return "Cliente ativo"

# 2. IA Geradora de Resumos
def gerar_resumo_cliente(atendimentos: List[Dict[str, Any]]) -> str:
    """
    Gera resumo automático do cliente baseado no histórico de atendimentos.
    """
    total = len(atendimentos)
    if total == 0:
        return "Cliente sem atendimentos registrados."
    datas = sorted([a['data'] for a in atendimentos if 'data' in a])
    if len(datas) < 2:
        return f"Cliente com {total} atendimento(s) registrado(s)."
    # Calcular tempo médio de retorno
    datas_dt = [datetime.strptime(d, "%Y-%m-%d") for d in datas]
    intervalos = [(datas_dt[i] - datas_dt[i-1]).days for i in range(1, len(datas_dt))]
    media_retorno = sum(intervalos) / len(intervalos) if intervalos else 0
    return (
        f"Cliente com {total} atendimentos registrados. "
        f"Costuma retornar a cada {int(media_retorno)} dias. "
        f"Perfil de cliente fiel."
    )

# 3. IA Sugestora de Ações
def sugerir_acoes(clientes: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    Recebe lista de clientes com atendimentos e gera sugestões de ação.
    """
    sugestoes = []
    hoje = datetime.now()
    for cliente in clientes:
        atend = cliente.get('atendimentos', [])
        if not atend:
            sugestoes.append({"cliente": cliente['nome'], "sugestao": "Sugerido entrar em contato"})
            continue
        datas = sorted([a['data'] for a in atend if 'data' in a])
        if not datas:
            sugestoes.append({"cliente": cliente['nome'], "sugestao": "Sugerido entrar em contato"})
            continue
        ultima = datetime.strptime(datas[-1], "%Y-%m-%d")
        dias = (hoje - ultima).days
        if dias > 120:
            sugestoes.append({"cliente": cliente['nome'], "sugestao": "Cliente sem atendimento há meses"})
        elif dias < 30:
            sugestoes.append({"cliente": cliente['nome'], "sugestao": "Possível retorno em breve"})
        elif cliente.get('status_ia_cliente') == 'Cliente importante' and dias > 60:
            sugestoes.append({"cliente": cliente['nome'], "sugestao": "Cliente importante parado"})
    return sugestoes

# 4. IA Insights do Negócio
def gerar_insights_empresa(clientes: List[Dict[str, Any]], atendimentos: List[Dict[str, Any]]) -> List[str]:
    """
    Analisa dados gerais da empresa e gera insights.
    """
    insights = []
    total_clientes = len(clientes)
    total_atend = len(atendimentos)
    if total_clientes == 0:
        insights.append("Sem clientes cadastrados.")
    if total_atend == 0:
        insights.append("Sem atendimentos registrados.")
    # Exemplo: crescimento de clientes
    # (Para produção, calcular variação mês a mês)
    if total_clientes > 50:
        insights.append("Empresa está crescendo.")
    if total_atend > 100:
        insights.append("Movimento aumentou.")
    if total_clientes < 10:
        insights.append("Clientes diminuíram.")
    # Frequência média
    if total_atend and total_clientes:
        freq_media = total_atend / total_clientes
        if freq_media > 3:
            insights.append("Frequência média alta.")
        elif freq_media < 1:
            insights.append("Frequência média baixa.")
    return insights

# 5. Assistente IA Interno
def responder_pergunta(pergunta: str, contexto: str = "") -> str:
    """
    Usa API de IA para responder perguntas sobre os dados da empresa.
    """
    prompt = (
        f"Dados da empresa:\n{contexto}\n"
        f"Pergunta: {pergunta}\nResposta:"
    )
    resposta = call_openai(prompt, max_tokens=128)
    return resposta or "Não foi possível gerar resposta no momento."

# Fim do módulo IA
