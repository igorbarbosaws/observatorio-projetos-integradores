import os
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db
from app.models.user import User
from app.models.project import Project
from app.routers import auth_router, project_router, user_router
from app.core.security import hash_senha, verificar_senha, criar_token, decodificar_token

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Observatório de Projetos Integradores")

app.include_router(auth_router.router)
app.include_router(project_router.router)
app.include_router(user_router.router)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


# ── Helper ───────────────────────────────────────────────────────────────────

def get_usuario_logado(request: Request, db: Session) -> User | None:
    """Retorna o User autenticado via cookie JWT, ou None."""
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

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "usuario": usuario,
            "total_usuarios": db.query(User).count(),
            "total_projetos": db.query(Project).count(),
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
