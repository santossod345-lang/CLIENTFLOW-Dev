import httpx
import pytest

BASE_URL = "http://localhost:8000"

# Exemplo de empresa fictícia para testes
EMPRESA = {
    "nome_empresa": "Empresa Teste",
    "nicho": "servicos",
    "tipo_empresa": "generico",
    "telefone": "11999999999",
    "email_login": "teste@clientflow.com",
    "senha": "123456"
}

@pytest.fixture(scope="session")
def client():
    return httpx.Client(base_url=BASE_URL)

def test_root(client):
    resp = client.get("/")
    assert resp.status_code in (200, 404)  # Ajuste conforme seu root

def test_estatisticas(client):
    resp = client.get("/estatisticas/1")
    assert resp.status_code in (200, 403, 404)

def test_clientes_crud(client):
    # Criação
    novo = {"nome": "Cliente Teste", "telefone": "11988887777"}
    resp = client.post("/api/clientes", json=novo)
    assert resp.status_code in (200, 201)
    cliente = resp.json()
    cliente_id = cliente.get("id")
    # Listagem
    resp = client.get("/api/clientes")
    assert resp.status_code == 200
    # Edição
    resp = client.put(f"/clientes/{cliente_id}", json={"nome": "Cliente Editado"})
    assert resp.status_code == 200
    # Exclusão
    resp = client.delete(f"/clientes/{cliente_id}")
    assert resp.status_code == 200

def test_atendimentos_crud(client):
    # Criação de cliente para o atendimento
    resp = client.post("/api/clientes", json={"nome": "Cliente Atend", "telefone": "11977776666"})
    cliente_id = resp.json().get("id")
    novo = {
        "cliente_id": cliente_id,
        "tipo_servico": "servico teste",
        "descricao_servico": "desc",
        "meses_retorno": 3
    }
    resp = client.post("/api/atendimentos", json=novo)
    assert resp.status_code in (200, 201)
    atendimento = resp.json()
    atendimento_id = atendimento.get("id")
    # Listagem
    resp = client.get("/atendimentos?token=")
    assert resp.status_code == 200
    # Edição
    resp = client.put(f"/atendimentos/{atendimento_id}", json={"descricao_servico": "editado"})
    assert resp.status_code == 200
    # Exclusão
    resp = client.delete(f"/atendimentos/{atendimento_id}")
    assert resp.status_code == 200
    # Limpeza
    client.delete(f"/clientes/{cliente_id}")

def test_logs_acoes(client):
    resp = client.get("/logs_acoes")
    assert resp.status_code == 200

def test_graficos(client):
    resp = client.get("/grafico/atendimentos/1")
    assert resp.status_code in (200, 404)
    resp = client.get("/grafico/clientes/1")
    assert resp.status_code in (200, 404)

def test_notificacoes_retorno(client):
    resp = client.get("/clientes_para_retorno/1")
    assert resp.status_code in (200, 404)

def test_exportacao_csv(client):
    resp = client.get("/api/clientes")
    assert resp.status_code == 200
    resp = client.get("/api/atendimentos")
    assert resp.status_code == 200
