from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.project import Project
from app.schemas.project_schema import ProjectCreate, ProjectUpdate
from app.core.security import decodificar_token

router = APIRouter(prefix="/projects", tags=["Projetos"])


def _requer_autenticacao(authorization: Optional[str] = Header(None)) -> dict:
    """Valida o header Authorization: Bearer <token> e retorna o payload."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token não fornecido")
    token = authorization.split(" ", 1)[1]
    payload = decodificar_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
    return payload


@router.get("/")
def listar_projetos(
    db: Session = Depends(get_db),
    _: dict = Depends(_requer_autenticacao),
):
    return db.query(Project).all()


@router.post("/", status_code=201)
def criar_projeto(
    projeto: ProjectCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(_requer_autenticacao),
):
    novo = Project(
        titulo=projeto.titulo,
        descricao=projeto.descricao,
        aluno_id=payload.get("id"),
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


@router.put("/{project_id}")
def atualizar_projeto(
    project_id: int,
    projeto: ProjectUpdate,
    db: Session = Depends(get_db),
    _: dict = Depends(_requer_autenticacao),
):
    projeto_db = db.query(Project).filter(Project.id == project_id).first()
    if not projeto_db:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")

    if projeto.titulo is not None:
        projeto_db.titulo = projeto.titulo
    if projeto.descricao is not None:
        projeto_db.descricao = projeto.descricao

    projeto_db.versao += 1
    projeto_db.ultima_atualizacao = datetime.now(timezone.utc)

    db.commit()
    db.refresh(projeto_db)
    return projeto_db


@router.delete("/{project_id}", status_code=204)
def deletar_projeto(
    project_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(_requer_autenticacao),
):
    projeto_db = db.query(Project).filter(Project.id == project_id).first()
    if not projeto_db:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    db.delete(projeto_db)
    db.commit()
