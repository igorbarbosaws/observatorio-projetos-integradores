import os
from datetime import datetime, timezone
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db
from app.models.user import User
from app.models.project import Project, Avaliacao
from app.routers import auth_router, project_router, user_router
from app.core.security import hash_senha, verificar_senha, criar_token, decodificar_token

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Observatório de Projetos Integradores")

app.include_router(auth_router.router)
app.include_router(project_router.router)
app.include_router(user_router.router)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


# ── Helper ────────────────────────────────────────────────────────────────────

def get_usuario_logado(request: Request, db: Session) -> User | None:
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


def requer_login(request: Request, db: Session):
    u = get_usuario_logado(request, db)
    if not u:
        return None, RedirectResponse(url="/", status_code=303)
    return u, None


# ── Rotas públicas ────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login", response_class=HTMLResponse)
def login(
    request: Request,
    email: str = Form(...),
    senha: str = Form(...),
    db: Session = Depends(get_db),
):
    usuario = db.query(User).filter(User.email == email).first()
    if not usuario or not verificar_senha(senha, usuario.senha_hash):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "erro": "E-mail ou senha inválidos"},
        )
    if not usuario.ativo:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "erro": "Usuário inativo. Contate o administrador."},
        )
    token = criar_token({"sub": usuario.email, "tipo": usuario.tipo, "id": usuario.id})
    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(key="token", value=token, httponly=True, samesite="lax")
    return response


@app.get("/logout")
def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("token")
    return response


# ── Dashboard ─────────────────────────────────────────────────────────────────

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)

    # Projetos recentes (últimos 5)
    projetos_recentes = (
        db.query(Project)
        .order_by(Project.data_submissao.desc())
        .limit(5)
        .all()
    )

    # Contagens por status
    total_submetidos = db.query(Project).filter(Project.status == "SUBMETIDO").count()
    total_avaliados = db.query(Project).filter(Project.status == "AVALIADO").count()

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "usuario": usuario,
            "total_usuarios": db.query(User).count(),
            "total_projetos": db.query(Project).count(),
            "total_submetidos": total_submetidos,
            "total_avaliados": total_avaliados,
            "projetos_recentes": projetos_recentes,
            "active_page": "dashboard",
        },
    )


# ── Usuários ──────────────────────────────────────────────────────────────────

@app.get("/usuarios", response_class=HTMLResponse)
def listar_usuarios_view(
    request: Request,
    filtro_tipo: str = "",
    filtro_ativo: str = "",
    db: Session = Depends(get_db),
):
    usuario = get_usuario_logado(request, db)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)

    query = db.query(User)
    if filtro_tipo:
        query = query.filter(User.tipo == filtro_tipo)
    if filtro_ativo != "":
        query = query.filter(User.ativo == (filtro_ativo == "true"))

    return templates.TemplateResponse(
        "usuarios.html",
        {
            "request": request,
            "usuario": usuario,
            "usuarios": query.order_by(User.nome).all(),
            "filtro_tipo": filtro_tipo,
            "filtro_ativo": filtro_ativo,
            "sucesso": request.query_params.get("sucesso"),
            "erro": request.query_params.get("erro"),
            "active_page": "usuarios",
        },
    )


@app.get("/usuarios/novo", response_class=HTMLResponse)
def novo_usuario_view(request: Request, db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(
        "usuario_form.html",
        {"request": request, "usuario": usuario, "editando": None, "active_page": "usuarios"},
    )


@app.post("/usuarios/novo", response_class=HTMLResponse)
def criar_usuario_view(
    request: Request,
    nome: str = Form(...),
    email: str = Form(...),
    senha: str = Form(...),
    tipo: str = Form(...),
    db: Session = Depends(get_db),
):
    usuario = get_usuario_logado(request, db)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)

    if db.query(User).filter(User.email == email.lower()).first():
        return templates.TemplateResponse(
            "usuario_form.html",
            {
                "request": request,
                "usuario": usuario,
                "editando": None,
                "erro": "E-mail já está em uso",
                "form": {"nome": nome, "email": email, "tipo": tipo},
                "active_page": "usuarios",
            },
        )

    db.add(User(
        nome=nome,
        email=email.lower(),
        senha_hash=hash_senha(senha),
        tipo=tipo.upper(),
        ativo=True,
    ))
    db.commit()
    return RedirectResponse(url="/usuarios?sucesso=Usuário+criado+com+sucesso", status_code=303)


@app.get("/usuarios/{user_id}/editar", response_class=HTMLResponse)
def editar_usuario_view(user_id: int, request: Request, db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)
    editando = db.query(User).filter(User.id == user_id).first()
    if not editando:
        return RedirectResponse(url="/usuarios?erro=Usuário+não+encontrado", status_code=303)
    return templates.TemplateResponse(
        "usuario_form.html",
        {"request": request, "usuario": usuario, "editando": editando, "active_page": "usuarios"},
    )


@app.post("/usuarios/{user_id}/editar", response_class=HTMLResponse)
def salvar_usuario_view(
    user_id: int,
    request: Request,
    nome: str = Form(...),
    email: str = Form(...),
    tipo: str = Form(...),
    ativo: str = Form("on"),
    senha: str = Form(""),
    db: Session = Depends(get_db),
):
    usuario = get_usuario_logado(request, db)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)

    editando = db.query(User).filter(User.id == user_id).first()
    if not editando:
        return RedirectResponse(url="/usuarios?erro=Usuário+não+encontrado", status_code=303)

    email_lower = email.lower()
    if email_lower != editando.email:
        if db.query(User).filter(User.email == email_lower).first():
            return templates.TemplateResponse(
                "usuario_form.html",
                {
                    "request": request,
                    "usuario": usuario,
                    "editando": editando,
                    "erro": "E-mail já está em uso por outro usuário",
                    "form": {"nome": nome, "email": email, "tipo": tipo},
                    "active_page": "usuarios",
                },
            )

    if senha.strip() and len(senha) < 8:
        return templates.TemplateResponse(
            "usuario_form.html",
            {
                "request": request,
                "usuario": usuario,
                "editando": editando,
                "erro": "A senha deve ter no mínimo 8 caracteres",
                "form": {"nome": nome, "email": email, "tipo": tipo},
                "active_page": "usuarios",
            },
        )

    editando.nome = nome
    editando.email = email_lower
    editando.tipo = tipo.upper()
    editando.ativo = ativo == "on"
    if senha.strip():
        editando.senha_hash = hash_senha(senha)

    db.commit()
    return RedirectResponse(url="/usuarios?sucesso=Usuário+atualizado+com+sucesso", status_code=303)


@app.post("/usuarios/{user_id}/deletar")
def deletar_usuario_view(user_id: int, request: Request, db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)
    alvo = db.query(User).filter(User.id == user_id).first()
    if alvo:
        db.delete(alvo)
        db.commit()
    return RedirectResponse(url="/usuarios?sucesso=Usuário+removido+com+sucesso", status_code=303)


# ── Projetos ──────────────────────────────────────────────────────────────────

@app.get("/projetos", response_class=HTMLResponse)
def listar_projetos_view(
    request: Request,
    filtro_turma: str = "",
    filtro_status: str = "",
    filtro_semestre: str = "",
    db: Session = Depends(get_db),
):
    usuario = get_usuario_logado(request, db)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)

    query = db.query(Project)

    # Aluno só vê os próprios projetos
    if usuario.tipo == "ALUNO":
        query = query.filter(Project.aluno_id == usuario.id)

    if filtro_turma:
        query = query.filter(Project.turma == filtro_turma)
    if filtro_status:
        query = query.filter(Project.status == filtro_status)
    if filtro_semestre:
        query = query.filter(Project.semestre == filtro_semestre)

    projetos = query.order_by(Project.data_submissao.desc()).all()

    # Listas para os filtros
    turmas = [r[0] for r in db.query(Project.turma).distinct().all() if r[0]]
    semestres = [r[0] for r in db.query(Project.semestre).distinct().all() if r[0]]

    return templates.TemplateResponse(
        "projetos.html",
        {
            "request": request,
            "usuario": usuario,
            "projetos": projetos,
            "filtro_turma": filtro_turma,
            "filtro_status": filtro_status,
            "filtro_semestre": filtro_semestre,
            "turmas": turmas,
            "semestres": semestres,
            "sucesso": request.query_params.get("sucesso"),
            "erro": request.query_params.get("erro"),
            "active_page": "projetos",
        },
    )


@app.get("/projetos/novo", response_class=HTMLResponse)
def novo_projeto_view(request: Request, db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)
    if usuario.tipo not in ("ALUNO", "ADMIN", "COORDENADOR"):
        return RedirectResponse(url="/projetos?erro=Sem+permissão", status_code=303)
    return templates.TemplateResponse(
        "projeto_form.html",
        {"request": request, "usuario": usuario, "editando": None, "active_page": "projetos"},
    )


@app.post("/projetos/novo", response_class=HTMLResponse)
def criar_projeto_view(
    request: Request,
    titulo: str = Form(...),
    descricao: str = Form(""),
    turma: str = Form(""),
    semestre: str = Form(""),
    tecnologias: str = Form(""),
    link_repositorio: str = Form(""),
    db: Session = Depends(get_db),
):
    usuario = get_usuario_logado(request, db)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)

    novo = Project(
        titulo=titulo,
        descricao=descricao,
        turma=turma.upper(),
        semestre=semestre,
        tecnologias=tecnologias,
        link_repositorio=link_repositorio,
        status="SUBMETIDO",
        aluno_id=usuario.id,
    )
    db.add(novo)
    db.commit()
    return RedirectResponse(url="/projetos?sucesso=Projeto+submetido+com+sucesso", status_code=303)


@app.get("/projetos/{projeto_id}", response_class=HTMLResponse)
def detalhe_projeto_view(projeto_id: int, request: Request, db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)

    projeto = db.query(Project).filter(Project.id == projeto_id).first()
    if not projeto:
        return RedirectResponse(url="/projetos?erro=Projeto+não+encontrado", status_code=303)

    # Aluno só vê o próprio
    if usuario.tipo == "ALUNO" and projeto.aluno_id != usuario.id:
        return RedirectResponse(url="/projetos?erro=Sem+permissão", status_code=303)

    avaliacoes = db.query(Avaliacao).filter(Avaliacao.projeto_id == projeto_id).all()
    ja_avaliou = None
    if usuario.tipo == "PROFESSOR":
        ja_avaliou = db.query(Avaliacao).filter(
            Avaliacao.projeto_id == projeto_id,
            Avaliacao.professor_id == usuario.id,
        ).first()

    return templates.TemplateResponse(
        "projeto_detalhe.html",
        {
            "request": request,
            "usuario": usuario,
            "projeto": projeto,
            "avaliacoes": avaliacoes,
            "ja_avaliou": ja_avaliou,
            "sucesso": request.query_params.get("sucesso"),
            "erro": request.query_params.get("erro"),
            "active_page": "projetos",
        },
    )


@app.get("/projetos/{projeto_id}/editar", response_class=HTMLResponse)
def editar_projeto_view(projeto_id: int, request: Request, db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)

    projeto = db.query(Project).filter(Project.id == projeto_id).first()
    if not projeto:
        return RedirectResponse(url="/projetos?erro=Projeto+não+encontrado", status_code=303)

    if usuario.tipo == "ALUNO" and projeto.aluno_id != usuario.id:
        return RedirectResponse(url="/projetos?erro=Sem+permissão", status_code=303)

    return templates.TemplateResponse(
        "projeto_form.html",
        {"request": request, "usuario": usuario, "editando": projeto, "active_page": "projetos"},
    )


@app.post("/projetos/{projeto_id}/editar", response_class=HTMLResponse)
def salvar_projeto_view(
    projeto_id: int,
    request: Request,
    titulo: str = Form(...),
    descricao: str = Form(""),
    turma: str = Form(""),
    semestre: str = Form(""),
    tecnologias: str = Form(""),
    link_repositorio: str = Form(""),
    db: Session = Depends(get_db),
):
    usuario = get_usuario_logado(request, db)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)

    projeto = db.query(Project).filter(Project.id == projeto_id).first()
    if not projeto:
        return RedirectResponse(url="/projetos?erro=Projeto+não+encontrado", status_code=303)

    if usuario.tipo == "ALUNO" and projeto.aluno_id != usuario.id:
        return RedirectResponse(url="/projetos?erro=Sem+permissão", status_code=303)

    projeto.titulo = titulo
    projeto.descricao = descricao
    projeto.turma = turma.upper()
    projeto.semestre = semestre
    projeto.tecnologias = tecnologias
    projeto.link_repositorio = link_repositorio
    projeto.versao += 1
    projeto.ultima_atualizacao = datetime.now(timezone.utc)
    db.commit()
    return RedirectResponse(url=f"/projetos/{projeto_id}?sucesso=Projeto+atualizado", status_code=303)


@app.post("/projetos/{projeto_id}/deletar")
def deletar_projeto_view(projeto_id: int, request: Request, db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)

    projeto = db.query(Project).filter(Project.id == projeto_id).first()
    if projeto:
        if usuario.tipo == "ALUNO" and projeto.aluno_id != usuario.id:
            return RedirectResponse(url="/projetos?erro=Sem+permissão", status_code=303)
        db.delete(projeto)
        db.commit()
    return RedirectResponse(url="/projetos?sucesso=Projeto+removido+com+sucesso", status_code=303)


# ── Avaliações ────────────────────────────────────────────────────────────────

@app.post("/projetos/{projeto_id}/avaliar", response_class=HTMLResponse)
def avaliar_projeto_view(
    projeto_id: int,
    request: Request,
    nota_conteudo: float = Form(...),
    nota_tecnica: float = Form(...),
    nota_apresentacao: float = Form(...),
    nota_inovacao: float = Form(...),
    comentario: str = Form(""),
    db: Session = Depends(get_db),
):
    usuario = get_usuario_logado(request, db)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)
    if usuario.tipo not in ("PROFESSOR", "ADMIN", "COORDENADOR"):
        return RedirectResponse(url=f"/projetos/{projeto_id}?erro=Sem+permissão", status_code=303)

    projeto = db.query(Project).filter(Project.id == projeto_id).first()
    if not projeto:
        return RedirectResponse(url="/projetos?erro=Projeto+não+encontrado", status_code=303)

    # Clamp notas entre 0 e 10
    def clamp(v): return max(0.0, min(10.0, v))
    nc = clamp(nota_conteudo)
    nt = clamp(nota_tecnica)
    na = clamp(nota_apresentacao)
    ni = clamp(nota_inovacao)
    media = round((nc + nt + na + ni) / 4, 2)

    # Verifica se já avaliou
    existente = db.query(Avaliacao).filter(
        Avaliacao.projeto_id == projeto_id,
        Avaliacao.professor_id == usuario.id,
    ).first()

    if existente:
        existente.nota_conteudo = nc
        existente.nota_tecnica = nt
        existente.nota_apresentacao = na
        existente.nota_inovacao = ni
        existente.nota_final = media
        existente.comentario = comentario
        existente.data_avaliacao = datetime.now(timezone.utc)
    else:
        db.add(Avaliacao(
            projeto_id=projeto_id,
            professor_id=usuario.id,
            nota_conteudo=nc,
            nota_tecnica=nt,
            nota_apresentacao=na,
            nota_inovacao=ni,
            nota_final=media,
            comentario=comentario,
        ))

    projeto.status = "AVALIADO"
    db.commit()
    return RedirectResponse(
        url=f"/projetos/{projeto_id}?sucesso=Avaliação+registrada+com+sucesso",
        status_code=303,
    )


# ── Portfólio público (Empresas) ──────────────────────────────────────────────

@app.get("/portfolio", response_class=HTMLResponse)
def portfolio_view(
    request: Request,
    filtro_turma: str = "",
    filtro_semestre: str = "",
    busca: str = "",
    db: Session = Depends(get_db),
):
    usuario = get_usuario_logado(request, db)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)

    query = db.query(Project)
    if filtro_turma:
        query = query.filter(Project.turma == filtro_turma)
    if filtro_semestre:
        query = query.filter(Project.semestre == filtro_semestre)
    if busca:
        query = query.filter(
            Project.titulo.ilike(f"%{busca}%") |
            Project.descricao.ilike(f"%{busca}%") |
            Project.tecnologias.ilike(f"%{busca}%")
        )

    projetos = query.order_by(Project.data_submissao.desc()).all()
    turmas = [r[0] for r in db.query(Project.turma).distinct().all() if r[0]]
    semestres = [r[0] for r in db.query(Project.semestre).distinct().all() if r[0]]

    return templates.TemplateResponse(
        "portfolio.html",
        {
            "request": request,
            "usuario": usuario,
            "projetos": projetos,
            "filtro_turma": filtro_turma,
            "filtro_semestre": filtro_semestre,
            "busca": busca,
            "turmas": turmas,
            "semestres": semestres,
            "active_page": "portfolio",
        },
    )


# ── Relatórios (Admin/Coordenador) ────────────────────────────────────────────

@app.get("/relatorios", response_class=HTMLResponse)
def relatorios_view(request: Request, db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario:
        return RedirectResponse(url="/", status_code=303)
    if usuario.tipo not in ("ADMIN", "COORDENADOR"):
        return RedirectResponse(url="/dashboard?erro=Sem+permissão", status_code=303)

    # Estatísticas gerais
    total_projetos = db.query(Project).count()
    total_avaliados = db.query(Project).filter(Project.status == "AVALIADO").count()
    total_submetidos = db.query(Project).filter(Project.status == "SUBMETIDO").count()
    total_em_avaliacao = db.query(Project).filter(Project.status == "EM_AVALIACAO").count()

    # Projetos por turma
    from sqlalchemy import func
    por_turma = (
        db.query(Project.turma, func.count(Project.id).label("total"))
        .group_by(Project.turma)
        .order_by(func.count(Project.id).desc())
        .all()
    )

    # Projetos por semestre
    por_semestre = (
        db.query(Project.semestre, func.count(Project.id).label("total"))
        .group_by(Project.semestre)
        .order_by(Project.semestre.desc())
        .all()
    )

    # Alunos com mais projetos
    top_alunos = (
        db.query(User.nome, func.count(Project.id).label("total"))
        .join(Project, Project.aluno_id == User.id)
        .group_by(User.id)
        .order_by(func.count(Project.id).desc())
        .limit(10)
        .all()
    )

    # Professores com mais avaliações
    top_professores = (
        db.query(User.nome, func.count(Avaliacao.id).label("total"))
        .join(Avaliacao, Avaliacao.professor_id == User.id)
        .group_by(User.id)
        .order_by(func.count(Avaliacao.id).desc())
        .limit(10)
        .all()
    )

    # Média geral das avaliações
    from sqlalchemy import func as f
    media_geral = db.query(f.avg(Avaliacao.nota_final)).scalar()
    media_geral = round(media_geral, 2) if media_geral else 0

    return templates.TemplateResponse(
        "relatorios.html",
        {
            "request": request,
            "usuario": usuario,
            "total_projetos": total_projetos,
            "total_avaliados": total_avaliados,
            "total_submetidos": total_submetidos,
            "total_em_avaliacao": total_em_avaliacao,
            "por_turma": por_turma,
            "por_semestre": por_semestre,
            "top_alunos": top_alunos,
            "top_professores": top_professores,
            "media_geral": media_geral,
            "active_page": "relatorios",
        },
    )
