"""
ai_module.py
Módulo isolado para lógica de Inteligência Artificial do ClientFlow.
Não altera funcionalidades existentes.
"""

import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger("clientflow.ai")


# -----------------------------
# Pluggable AI provider layer
# -----------------------------
class BaseAIProvider:
    def respond(self, prompt: str, max_tokens: int = 128) -> Optional[str]:
        raise NotImplementedError()


class OpenAIProvider(BaseAIProvider):
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        try:
            import openai
        except Exception as e:
            raise RuntimeError("openai library is required for OpenAIProvider") from e
        self.openai = openai
        self.api_key = api_key
        self.model = model
        self.openai.api_key = api_key

    def respond(self, prompt: str, max_tokens: int = 128) -> Optional[str]:
        try:
            resp = self.openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.2,
            )
            if resp and resp.choices:
                return resp.choices[0].message.content.strip()
        except Exception as e:
            logger.exception("OpenAIProvider error")
        return None


class LocalProvider(BaseAIProvider):
    """
    Lightweight local 'black-box' that uses simple heuristics from this module.
    This allows the app to function without an external API key in dev/offline.
    """
    def respond(self, prompt: str, max_tokens: int = 128) -> Optional[str]:
        try:
            text = prompt.lower()
            # If user asks for resumo or summary, attempt to synthesize using simple rules
            if "resumo" in text or "resum" in text:
                # try to extract counts from prompt
                import re
                m_clients = re.search(r"clientes:\s*\[(.*?)\]", prompt, re.IGNORECASE | re.DOTALL)
                m_atend = re.search(r"atendimentos:\s*(\d+)", prompt, re.IGNORECASE)
                clientes_list = []
                if m_clients:
                    raw = m_clients.group(1)
                    import re as _re
                    clientes_list = [_re.sub(r'^["\']|["\']$', '', c.strip()) for c in raw.split(',') if c.strip()]
                total = int(m_atend.group(1)) if m_atend else len(clientes_list)
                if total == 0:
                    return "Cliente sem atendimentos registrados (modo local)."
                return f"Modo local: detectados {len(clientes_list)} cliente(s) e {total} atendimento(s)."
            # perguntas sobre classificacao
            if "cliente importante" in text or "inativo" in text or "frequente" in text:
                return "Modo local: use a análise heurística do sistema (cliente importante / frequente / inativo)."
            # fallback safe response
            return "Resposta rápida (modo local): funcionalidade IA limitada sem chave externa."
        except Exception:
            return "Resposta (modo local) indisponível no momento."


def get_provider() -> BaseAIProvider:
    # Provider selection: environment variable AI_PROVIDER (openai|local)
    provider = os.getenv("AI_PROVIDER", "auto").lower()
    openai_key = os.getenv("OPENAI_API_KEY", "")
    if provider == "openai":
        if not openai_key:
            raise RuntimeError("OPENAI_API_KEY is required for AI_PROVIDER=openai")
        return OpenAIProvider(openai_key, model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"))
    if provider == "local":
        return LocalProvider()
    # auto: prefer OpenAI if key present, else local
    if openai_key:
        return OpenAIProvider(openai_key, model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"))
    return LocalProvider()


# singleton provider instance
_PROVIDER: Optional[BaseAIProvider] = None


def _get_provider_singleton() -> BaseAIProvider:
    global _PROVIDER
    if _PROVIDER is None:
        try:
            _PROVIDER = get_provider()
        except Exception as e:
            logger.warning("Falling back to LocalProvider: %s", e)
            _PROVIDER = LocalProvider()
    return _PROVIDER


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

# 5. Assistente IA Interno (usando provider configurável)
def responder_pergunta(pergunta: str, contexto: str = "") -> str:
    """
    Monta prompt simples e delega para o provider configurado.
    """
    prompt = (
        f"Dados da empresa:\n{contexto}\n"
        f"Pergunta: {pergunta}\nResposta:"
    )
    provider = _get_provider_singleton()
    resp = provider.respond(prompt, max_tokens=256)
    if resp:
        return resp
    return "Não foi possível gerar resposta no momento."


# -----------------------------
# Code assistance helpers
# -----------------------------
def code_fix_from_text(code_text: str, instruction: str) -> str:
    """
    Ask the configured provider to propose a fixed version of `code_text`
    according to `instruction`. Returns the provider response as plain text.
    """
    prompt = (
        "You are a helpful programming assistant.\n"
        "Instruction: " + instruction + "\n\n"
        "Here is the code to fix:\n\n" + code_text + "\n\n"
        "Provide the fixed code only, without extra commentary."
    )
    provider = _get_provider_singleton()
    resp = provider.respond(prompt, max_tokens=1500)
    return resp or ""


def code_fix_suggestion(file_path: str, instruction: str) -> str:
    """
    Read `file_path` and ask the provider to suggest a fixed version.
    Returns the suggested file contents as text.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            src = f.read()
    except Exception as e:
        logger.exception("Failed to read file for code fix suggestion")
        return f"ERROR: could not read file: {e}"
    return code_fix_from_text(src, instruction)

# Fim do módulo IA
