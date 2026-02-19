from fastapi import APIRouter, Depends, HTTPException, status
from backend.schemas import EmpresaCreate, EmpresaLogin, EmpresaOut, RefreshRequest, TokenResponse
from backend import models, auth, database
from backend.dependencies import require_authenticated_empresa
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/empresas", tags=["empresas"])


@router.get("/me", response_model=EmpresaOut)
def obter_empresa_atual(empresa: models.Empresa = Depends(require_authenticated_empresa)):
    return empresa

@router.post("/cadastrar", response_model=EmpresaOut, status_code=status.HTTP_201_CREATED)
def cadastrar_empresa(empresa: EmpresaCreate, db: Session = Depends(database.get_db)):
    existing = db.query(models.Empresa).filter(models.Empresa.email_login == empresa.email_login).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email já cadastrado")
    senha_hash = auth.get_password_hash(empresa.senha)
    nova_empresa = models.Empresa(
        nome_empresa=empresa.nome_empresa,
        nicho=empresa.nicho,
        telefone=empresa.telefone,
        email_login=empresa.email_login,
        senha_hash=senha_hash
    )
    db.add(nova_empresa)
    db.commit()
    db.refresh(nova_empresa)
    return nova_empresa

@router.post("/login")
def login_empresa(login: EmpresaLogin, db: Session = Depends(database.get_db)):
    empresa = db.query(models.Empresa).filter(models.Empresa.email_login == login.email_login).first()
    if not empresa or not auth.verify_password(login.senha, empresa.senha_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email ou senha incorretos")
    access_token = auth.create_access_token({"sub": empresa.id})
    refresh_token = auth.create_refresh_token(db, empresa.id)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/logout")
def logout_empresa(token: str):
    # Implementar revogação de sessão/refresh
    return {"detail": "Logout realizado"}

@router.post("/refresh", response_model=TokenResponse)
def refresh_token_endpoint(body: RefreshRequest, db: Session = Depends(database.get_db)):
    rt = auth.verify_refresh_token(db, body.refresh_token)
    if not rt:
        raise HTTPException(status_code=401, detail="Refresh token inválido ou expirado")
    new_raw = auth.create_session_token()
    ok, new_token = auth.rotate_refresh_token(db, rt.jti, new_raw)
    if not ok:
        raise HTTPException(status_code=500, detail="Unable to rotate refresh token")
    access_token = auth.create_access_token({"sub": rt.empresa_id})
    return {"access_token": access_token, "refresh_token": new_token, "token_type": "bearer"}
