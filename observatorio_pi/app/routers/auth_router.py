from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user_schema import UserLogin
from app.core.security import verificar_senha, criar_token

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login")
def login_api(user: UserLogin, db: Session = Depends(get_db)):
    """Endpoint de login para uso via API (retorna JWT)."""
    usuario = db.query(User).filter(User.email == user.email).first()
    if not usuario or not verificar_senha(user.senha, usuario.senha_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    if not usuario.ativo:
        raise HTTPException(status_code=403, detail="Usuário inativo")
    token = criar_token({"sub": usuario.email, "tipo": usuario.tipo, "id": usuario.id})
    return {"access_token": token, "token_type": "bearer"}
