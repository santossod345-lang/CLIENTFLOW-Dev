import os, sys, time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient
from backend.main import app


client = TestClient(app)


def assert_status(resp, expected, label):
    if resp.status_code != expected:
        raise AssertionError(
            f"{label} expected {expected}, got {resp.status_code}, body={resp.text}"
        )


def main():
    suffix = str(int(time.time()))
    email1 = f"e2e_{suffix}_1@clientflow-e2e.com"
    email2 = f"e2e_{suffix}_2@clientflow-e2e.com"
    password = "Teste1234"

    r = client.post(
        "/auth/register",
        json={
            "nome_empresa": "E2E Company 1",
            "nicho": "Oficina",
            "telefone": "(11) 90000-0001",
            "email_login": email1,
            "senha": password,
        },
    )
    assert_status(r, 201, "/auth/register company1")

    r = client.post(
        "/auth/register",
        json={
            "nome_empresa": "E2E Company 2",
            "nicho": "Oficina",
            "telefone": "(11) 90000-0002",
            "email_login": email2,
            "senha": password,
        },
    )
    assert_status(r, 201, "/auth/register company2")

    r = client.post("/auth/login", json={"email_login": email1, "senha": password})
    assert_status(r, 200, "/auth/login")
    body = r.json()
    access = body["access_token"]
    refresh = body["refresh_token"]
    headers = {"Authorization": f"Bearer {access}"}

    r = client.get("/auth/me", headers=headers)
    assert_status(r, 200, "/auth/me")
    me1 = r.json()

    r = client.get("/api/clientes", headers=headers)
    assert_status(r, 200, "/api/clientes list 1")
    clients_before = len(r.json())

    r = client.post(
        "/api/clientes",
        headers=headers,
        json={
            "nome": "Cliente Tenant 1",
            "telefone": "(11) 91111-1111",
            "status_cliente": "novo",
            "origem_cliente": "manual",
            "anotacoes_rapidas": "e2e",
        },
    )
    assert_status(r, 201, "/api/clientes create tenant1")

    r = client.get("/api/clientes", headers=headers)
    assert_status(r, 200, "/api/clientes list after create")
    clients_after = len(r.json())
    assert clients_after >= clients_before + 1

    r = client.post("/auth/login", json={"email_login": email2, "senha": password})
    assert_status(r, 200, "/auth/login company2")
    headers2 = {"Authorization": f"Bearer {r.json()['access_token']}"}

    r = client.get("/api/clientes", headers=headers2)
    assert_status(r, 200, "/api/clientes list tenant2")
    names2 = {c.get("nome") for c in r.json()}
    assert (
        "Cliente Tenant 1" not in names2
    ), "tenant isolation failed: tenant2 can see tenant1 data"

    r = client.post("/auth/refresh", json={"refresh_token": refresh})
    assert_status(r, 200, "/auth/refresh")
    new_access = r.json()["access_token"]

    r = client.get("/auth/me", headers={"Authorization": f"Bearer {new_access}"})
    assert_status(r, 200, "/auth/me with refreshed token")

    print("E2E_AUTH_OK")
    print("company1_id=", me1.get("id"))
    print("clients_before=", clients_before)
    print("clients_after=", clients_after)


if __name__ == "__main__":
    main()
