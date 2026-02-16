import secrets
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend import models, auth
from backend.database import Base as DBBase


def setup_inmemory_db():
    engine = create_engine("sqlite:///:memory:")
    DBBase.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    return Session()


def test_refresh_token_lifecycle():
    db = setup_inmemory_db()

    # create empresa
    empresa = models.Empresa(nome_empresa="T1", nicho="x", email_login="t1@example.com", senha_hash=auth.get_password_hash("pass"))
    db.add(empresa)
    db.commit()
    db.refresh(empresa)

    # create refresh token
    token = auth.create_refresh_token(db, empresa.id)
    assert isinstance(token, str) and "::" in token

    # verify token
    rt = auth.verify_refresh_token(db, token)
    assert rt is not None
    assert rt.empresa_id == empresa.id

    # rotate
    new_raw = secrets.token_urlsafe(48)
    ok, new_token = auth.rotate_refresh_token(db, rt.jti, new_raw)
    assert ok is True
    assert new_token is not None and "::" in new_token

    # old token should be revoked
    old_rt = db.query(models.RefreshToken).filter(models.RefreshToken.jti == rt.jti).first()
    assert old_rt.revoked == 1

    # new token should verify
    new_rt = auth.verify_refresh_token(db, new_token)
    assert new_rt is not None
    assert new_rt.revoked == 0
