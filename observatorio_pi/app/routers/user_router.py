from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.user import User
from app.schemas.user_schema import UserCreate, UserUpdate, UserResponse
from app.core.security import hash_senha

router = APIRouter(prefix="/users", tags=["Usuários"])


@router.get("/", response_model=list[UserResponse])
def listar_usuarios(
    tipo: Optional[str] = None,
    ativo: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    query = db.query(User)
    if tipo:
        query = query.filter(User.tipo == tipo.upper())
    if ativo is not None:
        query = query.filter(User.ativo == ativo)
    return query.order_by(User.nome).all()


@router.get("/{user_id}", response_model=UserResponse)
def obter_usuario(user_id: int, db: Session = Depends(get_db)):
    usuario = db.query(User).filter(User.id == user_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario


@router.post("/", response_model=UserResponse, status_code=201)
def criar_usuario(user: UserCreate, db: Session = Depends(get_db)):
    existente = db.query(User).filter(User.email == user.email).first()
    if existente:
        raise HTTPException(status_code=400, detail="E-mail já está em uso")

    novo = User(
        nome=user.nome,
        email=user.email,
        senha_hash=hash_senha(user.senha),
        tipo=user.tipo,
        ativo=True,
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


@router.put("/{user_id}", response_model=UserResponse)
def atualizar_usuario(user_id: int, dados: UserUpdate, db: Session = Depends(get_db)):
    usuario = db.query(User).filter(User.id == user_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if dados.email and dados.email != usuario.email:
        conflito = db.query(User).filter(User.email == dados.email).first()
        if conflito:
            raise HTTPException(status_code=400, detail="E-mail já está em uso")
        usuario.email = dados.email

    if dados.nome is not None:
        usuario.nome = dados.nome
    if dados.tipo is not None:
        usuario.tipo = dados.tipo
    if dados.ativo is not None:
        usuario.ativo = dados.ativo
    if dados.senha is not None:
        usuario.senha_hash = hash_senha(dados.senha)

    db.commit()
    db.refresh(usuario)
    return usuario


@router.delete("/{user_id}", status_code=204)
def deletar_usuario(user_id: int, db: Session = Depends(get_db)):
    usuario = db.query(User).filter(User.id == user_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    db.delete(usuario)
    db.commit()
