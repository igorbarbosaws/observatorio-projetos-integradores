import os
from datetime import datetime, timezone
from fastapi import FastAPI, Request, Form, Depends, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List

from app.database import engine, Base, get_db
from app.models.user import User
from app.models.project import (
    Turma, Tematica, Equipe, EquipeMembro,
    EntregaProjeto, Avaliacao, AvaliacaoAluno,
    CONCEITOS, CONCEITO_LABEL, CONCEITO_ORDEM,
)
from app.routers import auth_router, project_router, user_router
from app.core.security import hash_senha, verificar_senha, criar_token, decodificar_token

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Observatório de Projetos Integradores")
app.include_router(auth_router.router)
app.include_router(project_router.router)
app.include_router(user_router.router)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Diretório de avatars
AVATARS_DIR = os.path.join(BASE_DIR, "static", "avatars")
os.makedirs(AVATARS_DIR, exist_ok=True)

# Montar arquivos estáticos
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# ── Helpers ───────────────────────────────────────────────────────────────────

def get_usuario_logado(request: Request, db: Session) -> Optional[User]:
    token = request.cookies.get("token")
    if not token:
        return None
    payload = decodificar_token(token)
    if not payload:
        return None
    email = payload.get("sub")
    if not email:
        return None
    return db.query(User).filter(User.email == email, User.ativo == True).first()


def _url_perfil(usuario: User) -> str:
    """Retorna a URL de perfil correspondente ao tipo do usuário."""
    mapa = {
        "ALUNO":       f"/alunos/{usuario.id}",
        "PROFESSOR":   f"/perfil/professor/{usuario.id}",
        "COORDENADOR": f"/perfil/coordenador/{usuario.id}",
        "ADMIN":       f"/perfil/coordenador/{usuario.id}",
        "EMPRESA":     f"/perfil/empresa/{usuario.id}",
    }
    return mapa.get(usuario.tipo, "/dashboard")


# Registrar url_perfil como global Jinja2
templates.env.globals["url_perfil"] = _url_perfil


def _equipes_do_aluno(db: Session, aluno_id: int) -> List[Equipe]:
    """Retorna todas as equipes em que o aluno é membro ou scrum master."""
    ids_como_membro = [
        m.equipe_id for m in
        db.query(EquipeMembro).filter(EquipeMembro.aluno_id == aluno_id).all()
    ]
    ids_como_sm = [
        e.id for e in
        db.query(Equipe).filter(Equipe.scrum_master_id == aluno_id).all()
    ]
    todos_ids = list(set(ids_como_membro + ids_como_sm))
    if not todos_ids:
        return []
    return db.query(Equipe).filter(Equipe.id.in_(todos_ids)).all()


def _is_membro(db: Session, aluno_id: int, equipe_id: int) -> bool:
    """Verifica se o aluno é membro ou scrum master da equipe."""
    como_membro = db.query(EquipeMembro).filter(
        EquipeMembro.equipe_id == equipe_id,
        EquipeMembro.aluno_id == aluno_id,
    ).first()
    como_sm = db.query(Equipe).filter(
        Equipe.id == equipe_id,
        Equipe.scrum_master_id == aluno_id,
    ).first()
    return bool(como_membro or como_sm)


# ── Auth ──────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login", response_class=HTMLResponse)
def login(request: Request, email: str = Form(...), senha: str = Form(...), db: Session = Depends(get_db)):
    usuario = db.query(User).filter(User.email == email).first()
    if not usuario or not verificar_senha(senha, usuario.senha_hash):
        return templates.TemplateResponse("login.html", {"request": request, "erro": "E-mail ou senha inválidos"})
    if not usuario.ativo:
        return templates.TemplateResponse("login.html", {"request": request, "erro": "Usuário inativo. Contate o administrador."})
    token = criar_token({"sub": usuario.email, "tipo": usuario.tipo, "id": usuario.id})
    resp = RedirectResponse(url="/dashboard", status_code=303)
    resp.set_cookie(key="token", value=token, httponly=True, samesite="lax")
    return resp


@app.get("/logout")
def logout():
    resp = RedirectResponse(url="/", status_code=303)
    resp.delete_cookie("token")
    return resp


# ── Dashboard ─────────────────────────────────────────────────────────────────

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)

    ctx = {"request": request, "usuario": usuario, "active_page": "dashboard",
           "total_usuarios": 0, "total_tematicas": 0, "total_equipes": 0,
           "total_avaliadas": 0, "equipes_recentes": []}

    if usuario.tipo in ("ADMIN", "COORDENADOR"):
        ctx["total_usuarios"]  = db.query(User).count()
        ctx["total_tematicas"] = db.query(Tematica).count()
        ctx["total_equipes"]   = db.query(Equipe).count()
        ctx["total_avaliadas"] = db.query(Avaliacao).count()
        ctx["equipes_recentes"] = db.query(Equipe).order_by(Equipe.criado_em.desc()).limit(5).all()

    elif usuario.tipo == "PROFESSOR":
        tematica_ids = [t.id for t in db.query(Tematica).filter(Tematica.professor_id == usuario.id).all()]
        ctx["total_tematicas"] = len(tematica_ids)
        ctx["total_equipes"]   = db.query(Equipe).filter(Equipe.tematica_id.in_(tematica_ids)).count() if tematica_ids else 0
        ctx["total_avaliadas"] = db.query(Avaliacao).filter(Avaliacao.professor_id == usuario.id).count()
        ctx["equipes_recentes"] = (
            db.query(Equipe).filter(Equipe.tematica_id.in_(tematica_ids))
            .order_by(Equipe.criado_em.desc()).limit(5).all()
        ) if tematica_ids else []

    elif usuario.tipo == "ALUNO":
        equipes = _equipes_do_aluno(db, usuario.id)
        tematica_ids_aluno = [e.tematica_id for e in equipes]
        ctx["total_equipes"]   = len(equipes)
        ctx["total_tematicas"] = len(set(tematica_ids_aluno))
        # Usar joinedload para carregar professor sem N+1
        equipes_ids = [e.id for e in equipes]
        if equipes_ids:
            ctx["equipes_recentes"] = (
                db.query(Equipe)
                .options(joinedload(Equipe.tematica).joinedload(Tematica.professor))
                .filter(Equipe.id.in_(equipes_ids))
                .order_by(Equipe.criado_em.desc())
                .limit(5)
                .all()
            )
        else:
            ctx["equipes_recentes"] = []

    elif usuario.tipo == "EMPRESA":
        ctx["total_tematicas"] = db.query(Tematica).count()
        ctx["total_equipes"]   = db.query(Equipe).count()

    return templates.TemplateResponse("dashboard.html", ctx)


# ── Usuários (apenas ADMIN) ───────────────────────────────────────────────────

@app.get("/usuarios", response_class=HTMLResponse)
def listar_usuarios_view(request: Request, filtro_tipo: str = "", filtro_ativo: str = "", db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)
    if usuario.tipo != "ADMIN":
        return RedirectResponse(url="/dashboard", status_code=303)
    query = db.query(User)
    if filtro_tipo:
        query = query.filter(User.tipo == filtro_tipo)
    if filtro_ativo != "":
        query = query.filter(User.ativo == (filtro_ativo == "true"))
    return templates.TemplateResponse("usuarios.html", {
        "request": request, "usuario": usuario,
        "usuarios": query.order_by(User.nome).all(),
        "filtro_tipo": filtro_tipo, "filtro_ativo": filtro_ativo,
        "sucesso": request.query_params.get("sucesso"),
        "erro": request.query_params.get("erro"),
        "active_page": "usuarios",
    })


@app.get("/usuarios/novo", response_class=HTMLResponse)
def novo_usuario_view(request: Request, db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario or usuario.tipo != "ADMIN":
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse("usuario_form.html", {"request": request, "usuario": usuario, "editando": None, "active_page": "usuarios"})


@app.post("/usuarios/novo", response_class=HTMLResponse)
def criar_usuario_view(request: Request, nome: str = Form(...), email: str = Form(...), senha: str = Form(...), tipo: str = Form(...), db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario or usuario.tipo != "ADMIN":
        return RedirectResponse(url="/dashboard", status_code=303)
    if db.query(User).filter(User.email == email.lower()).first():
        return templates.TemplateResponse("usuario_form.html", {"request": request, "usuario": usuario, "editando": None, "erro": "E-mail já está em uso", "form": {"nome": nome, "email": email, "tipo": tipo}, "active_page": "usuarios"})
    db.add(User(nome=nome, email=email.lower(), senha_hash=hash_senha(senha), tipo=tipo.upper(), ativo=True))
    db.commit()
    return RedirectResponse(url="/usuarios?sucesso=Usuário+criado+com+sucesso", status_code=303)


@app.get("/usuarios/{user_id}/editar", response_class=HTMLResponse)
def editar_usuario_view(user_id: int, request: Request, db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario or usuario.tipo != "ADMIN":
        return RedirectResponse(url="/dashboard", status_code=303)
    editando = db.query(User).filter(User.id == user_id).first()
    if not editando:
        return RedirectResponse(url="/usuarios?erro=Usuário+não+encontrado", status_code=303)
    return templates.TemplateResponse("usuario_form.html", {"request": request, "usuario": usuario, "editando": editando, "active_page": "usuarios"})


@app.post("/usuarios/{user_id}/editar", response_class=HTMLResponse)
def salvar_usuario_view(user_id: int, request: Request, nome: str = Form(...), email: str = Form(...), tipo: str = Form(...), ativo: str = Form("on"), senha: str = Form(""), db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario or usuario.tipo != "ADMIN":
        return RedirectResponse(url="/dashboard", status_code=303)
    editando = db.query(User).filter(User.id == user_id).first()
    if not editando:
        return RedirectResponse(url="/usuarios?erro=Usuário+não+encontrado", status_code=303)
    email_lower = email.lower()
    if email_lower != editando.email and db.query(User).filter(User.email == email_lower).first():
        return templates.TemplateResponse("usuario_form.html", {"request": request, "usuario": usuario, "editando": editando, "erro": "E-mail já está em uso por outro usuário", "form": {"nome": nome, "email": email, "tipo": tipo}, "active_page": "usuarios"})
    if senha.strip() and len(senha) < 8:
        return templates.TemplateResponse("usuario_form.html", {"request": request, "usuario": usuario, "editando": editando, "erro": "A senha deve ter no mínimo 8 caracteres", "form": {"nome": nome, "email": email, "tipo": tipo}, "active_page": "usuarios"})
    editando.nome = nome; editando.email = email_lower; editando.tipo = tipo.upper(); editando.ativo = (ativo == "on")
    if senha.strip():
        editando.senha_hash = hash_senha(senha)
    db.commit()
    return RedirectResponse(url="/usuarios?sucesso=Usuário+atualizado+com+sucesso", status_code=303)


@app.post("/usuarios/{user_id}/deletar")
def deletar_usuario_view(user_id: int, request: Request, db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario or usuario.tipo != "ADMIN":
        return RedirectResponse(url="/dashboard", status_code=303)
    alvo = db.query(User).filter(User.id == user_id).first()
    if alvo:
        db.delete(alvo); db.commit()
    return RedirectResponse(url="/usuarios?sucesso=Usuário+removido+com+sucesso", status_code=303)


# ── Turmas ────────────────────────────────────────────────────────────────────

@app.get("/turmas", response_class=HTMLResponse)
def listar_turmas(request: Request, ano: str = "", db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)
    if usuario.tipo not in ("ADMIN", "COORDENADOR"):
        return RedirectResponse(url="/dashboard", status_code=303)
    todas_turmas = db.query(Turma).all()
    anos_disponiveis = sorted(
        set(t.semestre.split("-")[0] for t in todas_turmas if "-" in t.semestre),
        reverse=True,
    )
    query = db.query(Turma)
    if ano:
        query = query.filter(Turma.semestre.startswith(f"{ano}-"))
    turmas = query.order_by(Turma.semestre.desc(), Turma.nome).all()
    return templates.TemplateResponse("turmas.html", {
        "request": request, "usuario": usuario, "turmas": turmas,
        "anos_disponiveis": anos_disponiveis, "ano_selecionado": ano,
        "sucesso": request.query_params.get("sucesso"),
        "erro": request.query_params.get("erro"),
        "active_page": "turmas",
    })


@app.get("/turmas/nova", response_class=HTMLResponse)
def nova_turma_view(request: Request, db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario or usuario.tipo not in ("ADMIN", "COORDENADOR"):
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse("turma_form.html", {
        "request": request, "usuario": usuario, "editando": None, "active_page": "turmas"
    })


@app.post("/turmas/nova", response_class=HTMLResponse)
def criar_turma(request: Request, nome: str = Form(...), semestre: str = Form(...), descricao: str = Form(""), db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario or usuario.tipo not in ("ADMIN", "COORDENADOR"):
        return RedirectResponse(url="/dashboard", status_code=303)
    db.add(Turma(nome=nome.upper(), semestre=semestre, descricao=descricao))
    db.commit()
    return RedirectResponse(url="/turmas?sucesso=Turma+criada+com+sucesso", status_code=303)


@app.get("/turmas/{turma_id}/editar", response_class=HTMLResponse)
def editar_turma_view(turma_id: int, request: Request, db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario or usuario.tipo not in ("ADMIN", "COORDENADOR"):
        return RedirectResponse(url="/dashboard", status_code=303)
    editando = db.query(Turma).filter(Turma.id == turma_id).first()
    if not editando:
        return RedirectResponse(url="/turmas?erro=Turma+não+encontrada", status_code=303)
    return templates.TemplateResponse("turma_form.html", {
        "request": request, "usuario": usuario, "editando": editando, "active_page": "turmas"
    })


@app.post("/turmas/{turma_id}/editar", response_class=HTMLResponse)
def salvar_turma(turma_id: int, request: Request, nome: str = Form(...), semestre: str = Form(...), descricao: str = Form(""), ativa: str = Form("on"), db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario or usuario.tipo not in ("ADMIN", "COORDENADOR"):
        return RedirectResponse(url="/dashboard", status_code=303)
    t = db.query(Turma).filter(Turma.id == turma_id).first()
    if not t:
        return RedirectResponse(url="/turmas?erro=Turma+não+encontrada", status_code=303)
    t.nome = nome.upper(); t.semestre = semestre; t.descricao = descricao; t.ativa = (ativa == "on")
    db.commit()
    return RedirectResponse(url="/turmas?sucesso=Turma+atualizada+com+sucesso", status_code=303)


@app.post("/turmas/{turma_id}/deletar")
def deletar_turma(turma_id: int, request: Request, db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario or usuario.tipo not in ("ADMIN", "COORDENADOR"):
        return RedirectResponse(url="/dashboard", status_code=303)
    t = db.query(Turma).filter(Turma.id == turma_id).first()
    if t:
        db.delete(t); db.commit()
    return RedirectResponse(url="/turmas?sucesso=Turma+removida+com+sucesso", status_code=303)


# ── Temáticas ─────────────────────────────────────────────────────────────────

@app.get("/tematicas", response_class=HTMLResponse)
def listar_tematicas(request: Request, filtro_turma: str = "", filtro_professor: str = "", db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)

    query = db.query(Tematica)

    if usuario.tipo == "ALUNO":
        # Aluno vê apenas as temáticas das equipes em que participa
        equipes = _equipes_do_aluno(db, usuario.id)
        tematica_ids = list(set(e.tematica_id for e in equipes))
        if tematica_ids:
            query = query.filter(Tematica.id.in_(tematica_ids))
        else:
            return templates.TemplateResponse("tematicas.html", {
                "request": request, "usuario": usuario, "tematicas": [],
                "turmas": [], "filtro_turma": filtro_turma,
                "professores": [], "filtro_professor": "",
                "sucesso": request.query_params.get("sucesso"),
                "erro": request.query_params.get("erro"),
                "active_page": "tematicas",
            })
    elif usuario.tipo == "PROFESSOR":
        # Professor vê apenas suas temáticas
        query = query.filter(Tematica.professor_id == usuario.id)
    # Admin/Coordenador/Empresa vê todas

    if filtro_turma:
        query = query.filter(Tematica.turma_id == int(filtro_turma))

    # Filtro por professor — apenas ADMIN/COORDENADOR
    filtro_professor_aplicado = ""
    if usuario.tipo in ("ADMIN", "COORDENADOR") and filtro_professor:
        prof_id = int(filtro_professor) if filtro_professor.isdigit() else None
        if prof_id:
            prof_valido = db.query(User).filter(User.id == prof_id, User.tipo == "PROFESSOR").first()
            if prof_valido:
                query = query.filter(Tematica.professor_id == prof_id)
                filtro_professor_aplicado = filtro_professor
            # Se inválido, ignora silenciosamente

    tematicas = query.order_by(Tematica.criado_em.desc()).all()
    turmas = db.query(Turma).filter(Turma.ativa == True).order_by(Turma.nome).all()
    professores = db.query(User).filter(User.tipo == "PROFESSOR", User.ativo == True).order_by(User.nome).all()
    return templates.TemplateResponse("tematicas.html", {
        "request": request, "usuario": usuario, "tematicas": tematicas,
        "turmas": turmas, "filtro_turma": filtro_turma,
        "professores": professores, "filtro_professor": filtro_professor_aplicado,
        "sucesso": request.query_params.get("sucesso"),
        "erro": request.query_params.get("erro"),
        "active_page": "tematicas",
    })


@app.get("/tematicas/nova", response_class=HTMLResponse)
def nova_tematica_view(request: Request, db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario or usuario.tipo not in ("ADMIN", "COORDENADOR"):
        return RedirectResponse(url="/dashboard", status_code=303)
    turmas = db.query(Turma).filter(Turma.ativa == True).order_by(Turma.nome).all()
    professores = db.query(User).filter(User.tipo == "PROFESSOR", User.ativo == True).order_by(User.nome).all()
    return templates.TemplateResponse("tematica_form.html", {
        "request": request, "usuario": usuario, "editando": None,
        "turmas": turmas, "professores": professores, "active_page": "tematicas"
    })


@app.post("/tematicas/nova", response_class=HTMLResponse)
def criar_tematica(request: Request, titulo: str = Form(...), descricao: str = Form(""), turma_id: int = Form(...), professor_id: str = Form(""), db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario or usuario.tipo not in ("ADMIN", "COORDENADOR"):
        return RedirectResponse(url="/dashboard", status_code=303)
    db.add(Tematica(
        titulo=titulo, descricao=descricao, turma_id=turma_id,
        professor_id=int(professor_id) if professor_id else None,
    ))
    db.commit()
    return RedirectResponse(url="/tematicas?sucesso=Temática+criada+com+sucesso", status_code=303)


@app.get("/tematicas/{tematica_id}", response_class=HTMLResponse)
def detalhe_tematica(tematica_id: int, request: Request, db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)
    tematica = db.query(Tematica).filter(Tematica.id == tematica_id).first()
    if not tematica:
        return RedirectResponse(url="/tematicas?erro=Temática+não+encontrada", status_code=303)
    alunos_turma = db.query(User).filter(User.tipo == "ALUNO", User.ativo == True).order_by(User.nome).all()
    return templates.TemplateResponse("tematica_detalhe.html", {
        "request": request, "usuario": usuario, "tematica": tematica,
        "alunos_turma": alunos_turma,
        "sucesso": request.query_params.get("sucesso"),
        "erro": request.query_params.get("erro"),
        "active_page": "tematicas",
    })


@app.get("/tematicas/{tematica_id}/editar", response_class=HTMLResponse)
def editar_tematica_view(tematica_id: int, request: Request, db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario or usuario.tipo not in ("ADMIN", "COORDENADOR"):
        return RedirectResponse(url="/dashboard", status_code=303)
    editando = db.query(Tematica).filter(Tematica.id == tematica_id).first()
    if not editando:
        return RedirectResponse(url="/tematicas?erro=Temática+não+encontrada", status_code=303)
    turmas = db.query(Turma).filter(Turma.ativa == True).order_by(Turma.nome).all()
    professores = db.query(User).filter(User.tipo == "PROFESSOR", User.ativo == True).order_by(User.nome).all()
    return templates.TemplateResponse("tematica_form.html", {
        "request": request, "usuario": usuario, "editando": editando,
        "turmas": turmas, "professores": professores, "active_page": "tematicas"
    })


@app.post("/tematicas/{tematica_id}/editar", response_class=HTMLResponse)
def salvar_tematica(tematica_id: int, request: Request, titulo: str = Form(...), descricao: str = Form(""), turma_id: int = Form(...), professor_id: str = Form(""), status: str = Form("ABERTA"), db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario or usuario.tipo not in ("ADMIN", "COORDENADOR"):
        return RedirectResponse(url="/dashboard", status_code=303)
    t = db.query(Tematica).filter(Tematica.id == tematica_id).first()
    if not t:
        return RedirectResponse(url="/tematicas?erro=Temática+não+encontrada", status_code=303)
    t.titulo = titulo; t.descricao = descricao; t.turma_id = turma_id
    t.professor_id = int(professor_id) if professor_id else None
    t.status = status; t.atualizado_em = datetime.now(timezone.utc)
    db.commit()
    return RedirectResponse(url=f"/tematicas/{tematica_id}?sucesso=Temática+atualizada", status_code=303)


@app.post("/tematicas/{tematica_id}/deletar")
def deletar_tematica(tematica_id: int, request: Request, db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario or usuario.tipo not in ("ADMIN", "COORDENADOR"):
        return RedirectResponse(url="/dashboard", status_code=303)
    t = db.query(Tematica).filter(Tematica.id == tematica_id).first()
    if t:
        db.delete(t); db.commit()
    return RedirectResponse(url="/tematicas?sucesso=Temática+removida+com+sucesso", status_code=303)


# ── Equipes ───────────────────────────────────────────────────────────────────

def _professor_da_tematica(db: Session, professor_id: int, tematica_id: int) -> bool:
    """Verifica se o usuário é o professor responsável pela temática."""
    t = db.query(Tematica).filter(
        Tematica.id == tematica_id,
        Tematica.professor_id == professor_id,
    ).first()
    return bool(t)


@app.post("/tematicas/{tematica_id}/equipes/nova", response_class=HTMLResponse)
def criar_equipe(tematica_id: int, request: Request, nome: str = Form(...), db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)
    # Apenas Professor responsável (COORDENADOR não gerencia equipes)
    if usuario.tipo not in ("ADMIN",):
        if usuario.tipo != "PROFESSOR" or not _professor_da_tematica(db, usuario.id, tematica_id):
            return RedirectResponse(url=f"/tematicas/{tematica_id}?erro=Sem+permissão+para+criar+equipes+nesta+temática", status_code=303)
    db.add(Equipe(nome=nome, tematica_id=tematica_id))
    db.commit()
    return RedirectResponse(url=f"/tematicas/{tematica_id}?sucesso=Equipe+criada+com+sucesso", status_code=303)


@app.get("/equipes/{equipe_id}", response_class=HTMLResponse)
def detalhe_equipe(equipe_id: int, request: Request, db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)
    equipe = db.query(Equipe).filter(Equipe.id == equipe_id).first()
    if not equipe:
        return RedirectResponse(url="/dashboard?erro=Equipe+não+encontrada", status_code=303)
    # Aluno só acessa sua própria equipe
    if usuario.tipo == "ALUNO" and not _is_membro(db, usuario.id, equipe_id):
        return RedirectResponse(url="/dashboard?erro=Sem+permissão", status_code=303)
    ids_membros = [m.aluno_id for m in equipe.membros]
    alunos_disponiveis = db.query(User).filter(
        User.tipo == "ALUNO", User.ativo == True,
        ~User.id.in_(ids_membros + ([equipe.scrum_master_id] if equipe.scrum_master_id else []))
    ).order_by(User.nome).all()
    avaliacao = db.query(Avaliacao).filter(Avaliacao.equipe_id == equipe_id).first()
    # Formulário de avaliação: apenas o professor responsável pela temática (não coordenador)
    eh_professor_da_tematica = (
        usuario.tipo == "PROFESSOR" and
        equipe.tematica_id is not None and
        _professor_da_tematica(db, usuario.id, equipe.tematica_id)
    )
    pode_avaliar = (usuario.tipo == "ADMIN") or eh_professor_da_tematica
    ja_avaliou = db.query(Avaliacao).filter(
        Avaliacao.equipe_id == equipe_id, Avaliacao.professor_id == usuario.id
    ).first() if pode_avaliar else None

    # Avaliações individuais dos alunos
    avals_individuais = {}
    if pode_avaliar:
        for av_ind in db.query(AvaliacaoAluno).filter(
            AvaliacaoAluno.equipe_id == equipe_id,
            AvaliacaoAluno.professor_id == usuario.id,
        ).all():
            avals_individuais[av_ind.aluno_id] = av_ind

    # Todos os membros da equipe (para exibir avaliações individuais)
    todos_membros_ids = ([equipe.scrum_master_id] if equipe.scrum_master_id else []) + \
                        [m.aluno_id for m in equipe.membros]
    todos_membros = db.query(User).filter(User.id.in_(todos_membros_ids)).all() if todos_membros_ids else []

    return templates.TemplateResponse("equipe_detalhe.html", {
        "request": request, "usuario": usuario, "equipe": equipe,
        "alunos_disponiveis": alunos_disponiveis,
        "avaliacao": avaliacao, "ja_avaliou": ja_avaliou,
        "pode_avaliar": pode_avaliar,
        "avals_individuais": avals_individuais,
        "todos_membros": todos_membros,
        "conceitos": CONCEITOS, "conceito_label": CONCEITO_LABEL,
        "sucesso": request.query_params.get("sucesso"),
        "erro": request.query_params.get("erro"),
        "active_page": "tematicas",
    })


@app.post("/equipes/{equipe_id}/adicionar-membro", response_class=HTMLResponse)
def adicionar_membro(equipe_id: int, request: Request, aluno_id: int = Form(...), db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)
    equipe = db.query(Equipe).filter(Equipe.id == equipe_id).first()
    if not equipe:
        return RedirectResponse(url="/dashboard", status_code=303)
    if usuario.tipo not in ("ADMIN",):
        if usuario.tipo != "PROFESSOR" or not _professor_da_tematica(db, usuario.id, equipe.tematica_id):
            return RedirectResponse(url=f"/equipes/{equipe_id}?erro=Apenas+o+professor+responsável+pode+adicionar+alunos", status_code=303)
    existente = db.query(EquipeMembro).filter(EquipeMembro.equipe_id == equipe_id, EquipeMembro.aluno_id == aluno_id).first()
    if not existente:
        db.add(EquipeMembro(equipe_id=equipe_id, aluno_id=aluno_id))
        db.commit()
    return RedirectResponse(url=f"/equipes/{equipe_id}?sucesso=Aluno+adicionado", status_code=303)


@app.post("/equipes/{equipe_id}/remover-membro/{aluno_id}", response_class=HTMLResponse)
def remover_membro(equipe_id: int, aluno_id: int, request: Request, db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)
    equipe = db.query(Equipe).filter(Equipe.id == equipe_id).first()
    if not equipe:
        return RedirectResponse(url="/dashboard", status_code=303)
    if usuario.tipo not in ("ADMIN",):
        if usuario.tipo != "PROFESSOR" or not _professor_da_tematica(db, usuario.id, equipe.tematica_id):
            return RedirectResponse(url=f"/equipes/{equipe_id}?erro=Apenas+o+professor+responsável+pode+remover+alunos", status_code=303)
    m = db.query(EquipeMembro).filter(EquipeMembro.equipe_id == equipe_id, EquipeMembro.aluno_id == aluno_id).first()
    if m:
        db.delete(m); db.commit()
    return RedirectResponse(url=f"/equipes/{equipe_id}?sucesso=Aluno+removido", status_code=303)


@app.post("/equipes/{equipe_id}/definir-scrum-master", response_class=HTMLResponse)
def definir_scrum_master(equipe_id: int, request: Request, aluno_id: int = Form(...), db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)
    equipe = db.query(Equipe).filter(Equipe.id == equipe_id).first()
    if not equipe:
        return RedirectResponse(url="/dashboard", status_code=303)
    if usuario.tipo not in ("ADMIN",):
        if usuario.tipo != "PROFESSOR" or not _professor_da_tematica(db, usuario.id, equipe.tematica_id):
            return RedirectResponse(url=f"/equipes/{equipe_id}?erro=Apenas+o+professor+responsável+pode+definir+o+Scrum+Master", status_code=303)
    equipe.scrum_master_id = aluno_id; db.commit()
    return RedirectResponse(url=f"/equipes/{equipe_id}?sucesso=Scrum+Master+definido", status_code=303)


@app.post("/equipes/{equipe_id}/renomear", response_class=HTMLResponse)
def renomear_equipe(equipe_id: int, request: Request, nome: str = Form(...), db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)
    equipe = db.query(Equipe).filter(Equipe.id == equipe_id).first()
    if not equipe:
        return RedirectResponse(url="/dashboard", status_code=303)
    if usuario.tipo not in ("ADMIN",):
        if usuario.tipo != "PROFESSOR" or not _professor_da_tematica(db, usuario.id, equipe.tematica_id):
            return RedirectResponse(url=f"/equipes/{equipe_id}?erro=Sem+permissão", status_code=303)
    if nome.strip():
        equipe.nome = nome.strip(); db.commit()
    return RedirectResponse(url=f"/equipes/{equipe_id}?sucesso=Equipe+renomeada+com+sucesso", status_code=303)


@app.post("/equipes/{equipe_id}/finalizar", response_class=HTMLResponse)
def finalizar_equipe(equipe_id: int, request: Request, db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)
    equipe = db.query(Equipe).filter(Equipe.id == equipe_id).first()
    if not equipe:
        return RedirectResponse(url="/dashboard", status_code=303)
    if usuario.tipo == "ALUNO" and equipe.scrum_master_id != usuario.id:
        return RedirectResponse(url=f"/equipes/{equipe_id}?erro=Apenas+o+Scrum+Master+pode+marcar+como+finalizado", status_code=303)
    if usuario.tipo not in ("ALUNO", "PROFESSOR", "ADMIN", "COORDENADOR"):
        return RedirectResponse(url=f"/equipes/{equipe_id}?erro=Sem+permissão", status_code=303)
    equipe.status = "FINALIZADO"; db.commit()
    return RedirectResponse(url=f"/equipes/{equipe_id}?sucesso=Projeto+marcado+como+finalizado", status_code=303)


@app.post("/equipes/{equipe_id}/reabrir", response_class=HTMLResponse)
def reabrir_equipe(equipe_id: int, request: Request, db: Session = Depends(get_db)):
    """Apenas o Scrum Master pode desfazer o 'Finalizado'."""
    usuario = get_usuario_logado(request, db)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)
    equipe = db.query(Equipe).filter(Equipe.id == equipe_id).first()
    if not equipe:
        return RedirectResponse(url="/dashboard", status_code=303)
    if usuario.tipo == "ALUNO" and equipe.scrum_master_id != usuario.id:
        return RedirectResponse(url=f"/equipes/{equipe_id}?erro=Apenas+o+Scrum+Master+pode+reabrir+o+projeto", status_code=303)
    if usuario.tipo not in ("ALUNO", "PROFESSOR", "ADMIN"):
        return RedirectResponse(url=f"/equipes/{equipe_id}?erro=Sem+permissão", status_code=303)
    equipe.status = "EM_ANDAMENTO"; db.commit()
    return RedirectResponse(url=f"/equipes/{equipe_id}?sucesso=Projeto+reaberto+para+edição", status_code=303)


@app.post("/equipes/{equipe_id}/deletar")
def deletar_equipe(equipe_id: int, request: Request, db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)
    equipe = db.query(Equipe).filter(Equipe.id == equipe_id).first()
    if not equipe:
        return RedirectResponse(url="/tematicas", status_code=303)
    if usuario.tipo not in ("ADMIN",):
        if usuario.tipo != "PROFESSOR" or not _professor_da_tematica(db, usuario.id, equipe.tematica_id):
            return RedirectResponse(url=f"/equipes/{equipe_id}?erro=Sem+permissão", status_code=303)
    tematica_id = equipe.tematica_id
    db.delete(equipe); db.commit()
    return RedirectResponse(url=f"/tematicas/{tematica_id}?sucesso=Equipe+removida", status_code=303)


# ── Entregas ──────────────────────────────────────────────────────────────────

@app.get("/equipes/{equipe_id}/entregas/nova", response_class=HTMLResponse)
def nova_entrega_view(equipe_id: int, request: Request, db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)
    # Apenas alunos membros da equipe podem criar entregas
    if usuario.tipo != "ALUNO":
        return RedirectResponse(url=f"/equipes/{equipe_id}?erro=Apenas+alunos+podem+subir+entregas", status_code=303)
    equipe = db.query(Equipe).filter(Equipe.id == equipe_id).first()
    if not equipe:
        return RedirectResponse(url="/dashboard", status_code=303)
    if equipe.status == "FINALIZADO":
        return RedirectResponse(url=f"/equipes/{equipe_id}?erro=Projeto+já+finalizado", status_code=303)
    if not _is_membro(db, usuario.id, equipe_id):
        return RedirectResponse(url=f"/equipes/{equipe_id}?erro=Você+não+faz+parte+desta+equipe", status_code=303)
    return templates.TemplateResponse("entrega_form.html", {
        "request": request, "usuario": usuario, "equipe": equipe, "editando": None, "active_page": "tematicas"
    })


@app.post("/equipes/{equipe_id}/entregas/nova", response_class=HTMLResponse)
def criar_entrega(equipe_id: int, request: Request,
    titulo: str = Form(...), descricao: str = Form(""),
    tecnologias: str = Form(""), link_repositorio: str = Form(""),
    link_apresentacao: str = Form(""), link_documento: str = Form(""),
    link_drive: str = Form(""), db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario or usuario.tipo != "ALUNO":
        return RedirectResponse(url="/dashboard", status_code=303)
    equipe = db.query(Equipe).filter(Equipe.id == equipe_id).first()
    if not equipe or equipe.status == "FINALIZADO":
        return RedirectResponse(url=f"/equipes/{equipe_id}?erro=Projeto+finalizado.+Não+é+possível+adicionar+entregas", status_code=303)
    if not _is_membro(db, usuario.id, equipe_id):
        return RedirectResponse(url=f"/equipes/{equipe_id}?erro=Você+não+faz+parte+desta+equipe", status_code=303)
    db.add(EntregaProjeto(
        equipe_id=equipe_id, autor_id=usuario.id,
        titulo=titulo, descricao=descricao, tecnologias=tecnologias,
        link_repositorio=link_repositorio, link_apresentacao=link_apresentacao,
        link_documento=link_documento, link_drive=link_drive,
    ))
    db.commit()
    return RedirectResponse(url=f"/equipes/{equipe_id}?sucesso=Entrega+adicionada+com+sucesso", status_code=303)


@app.get("/entregas/{entrega_id}/editar", response_class=HTMLResponse)
def editar_entrega_view(entrega_id: int, request: Request, db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)
    entrega = db.query(EntregaProjeto).filter(EntregaProjeto.id == entrega_id).first()
    if not entrega:
        return RedirectResponse(url="/dashboard", status_code=303)
    if entrega.equipe.status == "FINALIZADO":
        return RedirectResponse(url=f"/equipes/{entrega.equipe_id}?erro=Projeto+finalizado.+Não+é+possível+editar", status_code=303)
    if usuario.tipo != "ALUNO" or entrega.autor_id != usuario.id:
        return RedirectResponse(url=f"/equipes/{entrega.equipe_id}?erro=Apenas+o+autor+pode+editar+sua+entrega", status_code=303)
    return templates.TemplateResponse("entrega_form.html", {
        "request": request, "usuario": usuario, "equipe": entrega.equipe, "editando": entrega, "active_page": "tematicas"
    })


@app.post("/entregas/{entrega_id}/editar", response_class=HTMLResponse)
def salvar_entrega(entrega_id: int, request: Request,
    titulo: str = Form(...), descricao: str = Form(""),
    tecnologias: str = Form(""), link_repositorio: str = Form(""),
    link_apresentacao: str = Form(""), link_documento: str = Form(""),
    link_drive: str = Form(""), db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)
    entrega = db.query(EntregaProjeto).filter(EntregaProjeto.id == entrega_id).first()
    if not entrega:
        return RedirectResponse(url="/dashboard", status_code=303)
    if entrega.equipe.status == "FINALIZADO":
        return RedirectResponse(url=f"/equipes/{entrega.equipe_id}?erro=Projeto+finalizado.+Não+é+possível+editar", status_code=303)
    if usuario.tipo != "ALUNO" or entrega.autor_id != usuario.id:
        return RedirectResponse(url=f"/equipes/{entrega.equipe_id}?erro=Apenas+o+autor+pode+editar+sua+entrega", status_code=303)
    entrega.titulo = titulo; entrega.descricao = descricao
    entrega.tecnologias = tecnologias; entrega.link_repositorio = link_repositorio
    entrega.link_apresentacao = link_apresentacao; entrega.link_documento = link_documento
    entrega.link_drive = link_drive
    entrega.versao += 1; entrega.atualizado_em = datetime.now(timezone.utc)
    db.commit()
    return RedirectResponse(url=f"/equipes/{entrega.equipe_id}?sucesso=Entrega+atualizada", status_code=303)


@app.post("/entregas/{entrega_id}/deletar")
def deletar_entrega(entrega_id: int, request: Request, db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)
    entrega = db.query(EntregaProjeto).filter(EntregaProjeto.id == entrega_id).first()
    if not entrega:
        return RedirectResponse(url="/dashboard", status_code=303)
    equipe = entrega.equipe
    if equipe.status == "FINALIZADO":
        return RedirectResponse(url=f"/equipes/{equipe.id}?erro=Projeto+finalizado.+Não+é+possível+excluir+entregas", status_code=303)
    if usuario.tipo != "ALUNO" or equipe.scrum_master_id != usuario.id:
        return RedirectResponse(url=f"/equipes/{equipe.id}?erro=Apenas+o+Scrum+Master+pode+excluir+entregas", status_code=303)
    db.delete(entrega); db.commit()
    return RedirectResponse(url=f"/equipes/{equipe.id}?sucesso=Entrega+removida", status_code=303)


# ── Avaliações ────────────────────────────────────────────────────────────────

@app.post("/equipes/{equipe_id}/avaliar", response_class=HTMLResponse)
def avaliar_equipe(equipe_id: int, request: Request,
    conceito_conteudo: str = Form(...), conceito_tecnica: str = Form(...),
    conceito_apresentacao: str = Form(...), conceito_inovacao: str = Form(...),
    conceito_equipe: str = Form(...), conceito_final: str = Form(...),
    comentario: str = Form(""), db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)
    equipe = db.query(Equipe).filter(Equipe.id == equipe_id).first()
    if not equipe:
        return RedirectResponse(url="/dashboard", status_code=303)
    # Apenas professor da temática ou admin (não coordenador)
    if usuario.tipo not in ("ADMIN",):
        if usuario.tipo != "PROFESSOR" or not _professor_da_tematica(db, usuario.id, equipe.tematica_id):
            return RedirectResponse(url=f"/equipes/{equipe_id}?erro=Apenas+o+professor+responsável+pode+avaliar", status_code=303)
    validos = set(CONCEITOS)
    if not all(c in validos for c in [conceito_conteudo, conceito_tecnica, conceito_apresentacao, conceito_inovacao, conceito_equipe, conceito_final]):
        return RedirectResponse(url=f"/equipes/{equipe_id}?erro=Conceito+inválido", status_code=303)
    existente = db.query(Avaliacao).filter(Avaliacao.equipe_id == equipe_id, Avaliacao.professor_id == usuario.id).first()
    if existente:
        existente.conceito_conteudo = conceito_conteudo; existente.conceito_tecnica = conceito_tecnica
        existente.conceito_apresentacao = conceito_apresentacao; existente.conceito_inovacao = conceito_inovacao
        existente.conceito_equipe = conceito_equipe; existente.conceito_final = conceito_final
        existente.comentario = comentario; existente.data_avaliacao = datetime.now(timezone.utc)
    else:
        db.add(Avaliacao(equipe_id=equipe_id, professor_id=usuario.id,
            conceito_conteudo=conceito_conteudo, conceito_tecnica=conceito_tecnica,
            conceito_apresentacao=conceito_apresentacao, conceito_inovacao=conceito_inovacao,
            conceito_equipe=conceito_equipe, conceito_final=conceito_final, comentario=comentario))
    db.commit()
    return RedirectResponse(url=f"/equipes/{equipe_id}?sucesso=Avaliação+registrada+com+sucesso", status_code=303)


@app.post("/equipes/{equipe_id}/avaliar-aluno", response_class=HTMLResponse)
def avaliar_aluno(equipe_id: int, request: Request,
    aluno_id: int = Form(...), conceito: str = Form(...),
    comentario: str = Form(""), db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)
    equipe = db.query(Equipe).filter(Equipe.id == equipe_id).first()
    if not equipe:
        return RedirectResponse(url="/dashboard", status_code=303)
    if usuario.tipo not in ("ADMIN",):
        if usuario.tipo != "PROFESSOR" or not _professor_da_tematica(db, usuario.id, equipe.tematica_id):
            return RedirectResponse(url=f"/equipes/{equipe_id}?erro=Apenas+o+professor+responsável+pode+avaliar+alunos", status_code=303)
    if conceito not in CONCEITOS:
        return RedirectResponse(url=f"/equipes/{equipe_id}?erro=Conceito+inválido", status_code=303)
    existente = db.query(AvaliacaoAluno).filter(
        AvaliacaoAluno.equipe_id == equipe_id,
        AvaliacaoAluno.aluno_id == aluno_id,
        AvaliacaoAluno.professor_id == usuario.id,
    ).first()
    if existente:
        existente.conceito = conceito; existente.comentario = comentario
        existente.data_avaliacao = datetime.now(timezone.utc)
    else:
        db.add(AvaliacaoAluno(
            equipe_id=equipe_id, aluno_id=aluno_id, professor_id=usuario.id,
            conceito=conceito, comentario=comentario,
        ))
    db.commit()
    return RedirectResponse(url=f"/equipes/{equipe_id}?sucesso=Avaliação+individual+registrada", status_code=303)


# ── Portfólio ─────────────────────────────────────────────────────────────────

@app.get("/portfolio", response_class=HTMLResponse)
def portfolio_view(request: Request, busca: str = "", filtro_turma: str = "",
                   filtro_semestre: str = "", filtro_stack: str = "", db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)
    query = db.query(Equipe).join(Tematica).join(Turma)
    if filtro_turma:
        query = query.filter(Turma.id == int(filtro_turma))
    if filtro_semestre:
        query = query.filter(Turma.semestre == filtro_semestre)
    if busca:
        query = query.filter(Tematica.titulo.ilike(f"%{busca}%") | Equipe.nome.ilike(f"%{busca}%"))
    equipes = query.order_by(Equipe.criado_em.desc()).all()
    # Filtro de stack (pós-query, pois tecnologias ficam nas entregas)
    if filtro_stack:
        filtro_lower = filtro_stack.lower()
        equipes = [
            e for e in equipes
            if any(filtro_lower in tag.strip().lower()
                   for ent in e.entregas
                   for tag in ent.tecnologias.split(',') if tag.strip())
        ]
    # Todas as stacks únicas para o select de filtro
    todas_stacks = sorted({
        tag.strip()
        for eq in db.query(Equipe).join(Tematica).join(Turma).all()
        for ent in eq.entregas
        for tag in ent.tecnologias.split(',') if tag.strip()
    })
    turmas = db.query(Turma).filter(Turma.ativa == True).order_by(Turma.nome).all()
    semestres = [r[0] for r in db.query(Turma.semestre).distinct().all() if r[0]]
    return templates.TemplateResponse("portfolio.html", {
        "request": request, "usuario": usuario, "equipes": equipes,
        "turmas": turmas, "semestres": semestres, "todas_stacks": todas_stacks,
        "busca": busca, "filtro_turma": filtro_turma,
        "filtro_semestre": filtro_semestre, "filtro_stack": filtro_stack,
        "conceito_label": CONCEITO_LABEL,
        "active_page": "portfolio",
    })


# ── Relatórios ────────────────────────────────────────────────────────────────

@app.get("/relatorios", response_class=HTMLResponse)
def relatorios_view(request: Request, db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario or usuario.tipo not in ("ADMIN", "COORDENADOR"):
        return RedirectResponse(url="/dashboard", status_code=303)
    from sqlalchemy import func
    total_tematicas = db.query(Tematica).count()
    total_equipes   = db.query(Equipe).count()
    total_finalizadas = db.query(Equipe).filter(Equipe.status == "FINALIZADO").count()
    total_avaliacoes  = db.query(Avaliacao).count()
    por_turma = (db.query(Turma.nome, func.count(Tematica.id).label("total"))
        .join(Tematica, Tematica.turma_id == Turma.id).group_by(Turma.id)
        .order_by(func.count(Tematica.id).desc()).all())
    por_conceito = (db.query(Avaliacao.conceito_final, func.count(Avaliacao.id).label("total"))
        .group_by(Avaliacao.conceito_final).all())
    por_conceito_dict = {c: 0 for c in CONCEITOS}
    for c, t in por_conceito:
        if c in por_conceito_dict:
            por_conceito_dict[c] = t
    top_professores = (db.query(User.id, User.nome, func.count(Avaliacao.id).label("total"))
        .join(Avaliacao, Avaliacao.professor_id == User.id)
        .group_by(User.id).order_by(func.count(Avaliacao.id).desc()).limit(10).all())
    return templates.TemplateResponse("relatorios.html", {
        "request": request, "usuario": usuario,
        "total_tematicas": total_tematicas, "total_equipes": total_equipes,
        "total_finalizadas": total_finalizadas, "total_avaliacoes": total_avaliacoes,
        "por_turma": por_turma, "por_conceito": por_conceito_dict,
        "top_professores": top_professores,
        "conceitos": CONCEITOS, "conceito_label": CONCEITO_LABEL,
        "active_page": "relatorios",
    })


# ── Relatório por professor ───────────────────────────────────────────────────

@app.get("/relatorios/professor/{professor_id}", response_class=HTMLResponse)
def relatorio_professor(professor_id: int, request: Request, db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)
    if usuario.tipo not in ("ADMIN", "COORDENADOR"):
        return RedirectResponse(url="/dashboard", status_code=303)

    professor = db.query(User).filter(
        User.id == professor_id, User.tipo == "PROFESSOR"
    ).first()
    if not professor:
        return RedirectResponse(
            url="/relatorios?erro=Professor+não+encontrado", status_code=303
        )

    tematicas = db.query(Tematica).filter(
        Tematica.professor_id == professor_id
    ).order_by(Tematica.criado_em.desc()).all()

    dados_tematicas = []
    total_equipes = 0
    total_avaliacoes = 0
    for t in tematicas:
        n_equipes = len(t.equipes)
        equipe_ids = [e.id for e in t.equipes]
        n_avaliacoes = db.query(Avaliacao).filter(
            Avaliacao.professor_id == professor_id,
            Avaliacao.equipe_id.in_(equipe_ids)
        ).count() if equipe_ids else 0
        total_equipes += n_equipes
        total_avaliacoes += n_avaliacoes
        dados_tematicas.append({
            "tematica": t, "n_equipes": n_equipes, "n_avaliacoes": n_avaliacoes
        })

    return templates.TemplateResponse("relatorio_professor.html", {
        "request": request, "usuario": usuario, "professor": professor,
        "dados_tematicas": dados_tematicas,
        "total_tematicas": len(tematicas),
        "total_equipes": total_equipes,
        "total_avaliacoes": total_avaliacoes,
        "active_page": "relatorios",
    })


# ── Perfil do Aluno ───────────────────────────────────────────────────────────

@app.get("/meu-perfil", response_class=HTMLResponse)
def meu_perfil_view(request: Request, db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)
    if usuario.tipo != "ALUNO":
        return RedirectResponse(url="/dashboard", status_code=303)
    equipes = _equipes_do_aluno(db, usuario.id)
    return templates.TemplateResponse("perfil_aluno.html", {
        "request": request, "usuario": usuario,
        "perfil": usuario, "eh_proprio": True,
        "equipes": equipes, "conceito_label": CONCEITO_LABEL,
        "active_page": "perfil",
    })


@app.post("/meu-perfil", response_class=HTMLResponse)
def salvar_meu_perfil(
    request: Request,
    bio: str = Form(""),
    linkedin: str = Form(""),
    github: str = Form(""),
    portfolio_url: str = Form(""),
    area_interesse: str = Form(""),
    cidade: str = Form(""),
    telefone: str = Form(""),
    db: Session = Depends(get_db),
):
    usuario = get_usuario_logado(request, db)
    if not usuario or usuario.tipo != "ALUNO":
        return RedirectResponse(url="/", status_code=303)
    usuario.bio = bio
    usuario.linkedin = linkedin
    usuario.github = github
    usuario.portfolio_url = portfolio_url
    usuario.area_interesse = area_interesse
    usuario.cidade = cidade
    usuario.telefone = telefone
    db.commit()
    return RedirectResponse(url="/meu-perfil?sucesso=Perfil+atualizado+com+sucesso", status_code=303)


@app.get("/alunos/{aluno_id}", response_class=HTMLResponse)
def perfil_publico_aluno(aluno_id: int, request: Request, db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)
    perfil = db.query(User).filter(User.id == aluno_id, User.tipo == "ALUNO", User.ativo == True).first()
    if not perfil:
        return RedirectResponse(url="/portfolio?erro=Aluno+não+encontrado", status_code=303)
    equipes = _equipes_do_aluno(db, aluno_id)
    return templates.TemplateResponse("perfil_aluno.html", {
        "request": request, "usuario": usuario,
        "perfil": perfil, "eh_proprio": (usuario.id == aluno_id),
        "equipes": equipes, "conceito_label": CONCEITO_LABEL,
        "active_page": "portfolio",
        "sucesso": request.query_params.get("sucesso"),
    })


# ── Upload de foto de perfil ──────────────────────────────────────────────────

ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp"}
MAX_SIZE_BYTES = 2 * 1024 * 1024  # 2 MB


@app.post("/meu-perfil/foto", response_class=HTMLResponse)
async def upload_foto_perfil(
    request: Request,
    foto: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    usuario = get_usuario_logado(request, db)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)

    redirect_url = _url_perfil(usuario)

    # Validar tipo MIME
    if foto.content_type not in ALLOWED_MIME:
        return RedirectResponse(
            url=f"{redirect_url}?erro=Arquivo+inválido.+Envie+uma+imagem+JPEG%2C+PNG+ou+WebP+com+até+2+MB",
            status_code=303,
        )

    # Ler conteúdo e validar tamanho
    conteudo = await foto.read()
    if len(conteudo) > MAX_SIZE_BYTES:
        return RedirectResponse(
            url=f"{redirect_url}?erro=Arquivo+inválido.+Envie+uma+imagem+JPEG%2C+PNG+ou+WebP+com+até+2+MB",
            status_code=303,
        )

    # Determinar extensão
    ext_map = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}
    ext = ext_map[foto.content_type]
    filename = f"avatar_{usuario.id}.{ext}"
    filepath = os.path.join(AVATARS_DIR, filename)

    # Salvar arquivo (substitui o anterior)
    with open(filepath, "wb") as f:
        f.write(conteudo)

    # Atualizar banco
    usuario.foto_perfil = f"avatars/{filename}"
    db.commit()

    return RedirectResponse(
        url=f"{redirect_url}?sucesso=Foto+de+perfil+atualizada+com+sucesso",
        status_code=303,
    )


# ── Perfis por tipo de usuário ────────────────────────────────────────────────

@app.get("/perfil/professor/{professor_id}", response_class=HTMLResponse)
def perfil_professor(professor_id: int, request: Request, db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)
    perfil = db.query(User).filter(
        User.id == professor_id, User.tipo == "PROFESSOR", User.ativo == True
    ).first()
    if not perfil:
        return RedirectResponse(url="/dashboard?erro=Professor+não+encontrado", status_code=303)
    tematicas = db.query(Tematica).filter(Tematica.professor_id == professor_id).order_by(Tematica.criado_em.desc()).all()
    return templates.TemplateResponse("perfil_professor.html", {
        "request": request, "usuario": usuario,
        "perfil": perfil, "eh_proprio": (usuario.id == professor_id),
        "tematicas": tematicas,
        "sucesso": request.query_params.get("sucesso"),
        "erro": request.query_params.get("erro"),
        "active_page": "tematicas",
    })


@app.post("/perfil/professor/{professor_id}", response_class=HTMLResponse)
def salvar_perfil_professor(
    professor_id: int, request: Request,
    bio: str = Form(""), cidade: str = Form(""), telefone: str = Form(""),
    linkedin: str = Form(""), db: Session = Depends(get_db),
):
    usuario = get_usuario_logado(request, db)
    if not usuario or usuario.id != professor_id:
        return RedirectResponse(url="/dashboard", status_code=303)
    perfil = db.query(User).filter(User.id == professor_id, User.tipo == "PROFESSOR").first()
    if not perfil:
        return RedirectResponse(url="/dashboard", status_code=303)
    perfil.bio = bio; perfil.cidade = cidade; perfil.telefone = telefone; perfil.linkedin = linkedin
    db.commit()
    return RedirectResponse(url=f"/perfil/professor/{professor_id}?sucesso=Perfil+atualizado+com+sucesso", status_code=303)


@app.get("/perfil/coordenador/{coordenador_id}", response_class=HTMLResponse)
def perfil_coordenador(coordenador_id: int, request: Request, db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)
    perfil = db.query(User).filter(
        User.id == coordenador_id, User.tipo.in_(["COORDENADOR", "ADMIN"]), User.ativo == True
    ).first()
    if not perfil:
        return RedirectResponse(url="/dashboard?erro=Usuário+não+encontrado", status_code=303)
    return templates.TemplateResponse("perfil_coordenador.html", {
        "request": request, "usuario": usuario,
        "perfil": perfil, "eh_proprio": (usuario.id == coordenador_id),
        "sucesso": request.query_params.get("sucesso"),
        "erro": request.query_params.get("erro"),
        "active_page": "dashboard",
    })


@app.post("/perfil/coordenador/{coordenador_id}", response_class=HTMLResponse)
def salvar_perfil_coordenador(
    coordenador_id: int, request: Request,
    bio: str = Form(""), cidade: str = Form(""), telefone: str = Form(""),
    linkedin: str = Form(""), db: Session = Depends(get_db),
):
    usuario = get_usuario_logado(request, db)
    if not usuario or usuario.id != coordenador_id:
        return RedirectResponse(url="/dashboard", status_code=303)
    perfil = db.query(User).filter(User.id == coordenador_id).first()
    if not perfil:
        return RedirectResponse(url="/dashboard", status_code=303)
    perfil.bio = bio; perfil.cidade = cidade; perfil.telefone = telefone; perfil.linkedin = linkedin
    db.commit()
    return RedirectResponse(url=f"/perfil/coordenador/{coordenador_id}?sucesso=Perfil+atualizado+com+sucesso", status_code=303)


@app.get("/perfil/empresa/{empresa_id}", response_class=HTMLResponse)
def perfil_empresa(empresa_id: int, request: Request, db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)
    perfil = db.query(User).filter(
        User.id == empresa_id, User.tipo == "EMPRESA", User.ativo == True
    ).first()
    if not perfil:
        return RedirectResponse(url="/dashboard?erro=Empresa+não+encontrada", status_code=303)
    return templates.TemplateResponse("perfil_empresa.html", {
        "request": request, "usuario": usuario,
        "perfil": perfil, "eh_proprio": (usuario.id == empresa_id),
        "sucesso": request.query_params.get("sucesso"),
        "erro": request.query_params.get("erro"),
        "active_page": "portfolio",
    })


@app.post("/perfil/empresa/{empresa_id}", response_class=HTMLResponse)
def salvar_perfil_empresa(
    empresa_id: int, request: Request,
    bio: str = Form(""), cidade: str = Form(""), telefone: str = Form(""),
    linkedin: str = Form(""), db: Session = Depends(get_db),
):
    usuario = get_usuario_logado(request, db)
    if not usuario or usuario.id != empresa_id:
        return RedirectResponse(url="/dashboard", status_code=303)
    perfil = db.query(User).filter(User.id == empresa_id, User.tipo == "EMPRESA").first()
    if not perfil:
        return RedirectResponse(url="/dashboard", status_code=303)
    perfil.bio = bio; perfil.cidade = cidade; perfil.telefone = telefone; perfil.linkedin = linkedin
    db.commit()
    return RedirectResponse(url=f"/perfil/empresa/{empresa_id}?sucesso=Perfil+atualizado+com+sucesso", status_code=303)
