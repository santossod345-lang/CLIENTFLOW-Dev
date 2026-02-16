from backend import sessions


def test_create_and_get_session():
    # This test assumes a local Redis is available at REDIS_URL; if not, it will error.
    token = sessions.create_session(123)
    assert isinstance(token, str) and len(token) > 0
    empresa_id = sessions.get_session_empresa(token)
    assert empresa_id == 123
    sessions.revoke_session(token)
    assert sessions.get_session_empresa(token) is None
