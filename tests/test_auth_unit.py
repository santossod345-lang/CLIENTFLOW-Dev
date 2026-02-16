import time
from backend import auth


def test_password_hash_and_verify():
    pwd = "MinhaSenhaSegura123!"
    h = auth.get_password_hash(pwd)
    assert h != pwd
    assert auth.verify_password(pwd, h)


def test_create_and_decode_access_token():
    payload = {"sub": 42}
    token = auth.create_access_token(data=payload, expires_delta=None)
    assert isinstance(token, str) and len(token) > 0
    decoded = auth.decode_access_token(token)
    assert decoded is not None
    assert decoded.get("sub") == 42
