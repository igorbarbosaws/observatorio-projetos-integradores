"""
Ponto de entrada único do Observatório PI.

Uso local (Windows):
    .venv\\Scripts\\python.exe run.py
    iniciar.bat  (duplo clique)

Produção (Render/Docker):
    Usar start.sh com Gunicorn — este arquivo não é usado em produção.
"""
import sys
import os
import subprocess


def _seed_usuarios_e_projetos(db, hash_senha):
    """Cria usuários de teste e projetos de exemplo se o banco estiver vazio."""
    from app.models.user import User
    from app.models.project import Project, Avaliacao
    from datetime import datetime, timezone

    if db.query(User).count() > 0:
        return  # Banco já populado, não faz nada

    print("\n── Criando dados de exemplo ─────────────────────────────────────")

    # ── Usuários ──────────────────────────────────────────────────────────────
    usuarios_seed = [
        dict(nome="Administrador",        email="admin@observatorio.pi",      senha="admin1234",      tipo="ADMIN"),
        dict(nome="Prof. Carlos Mendes",  email="professor@observatorio.pi",  senha="prof1234",       tipo="PROFESSOR"),
        dict(nome="Coord. Ana Lima",      email="coordenador@observatorio.pi",senha="coord1234",      tipo="COORDENADOR"),
        dict(nome="João Silva",           email="aluno1@observatorio.pi",     senha="aluno1234",      tipo="ALUNO"),
        dict(nome="Maria Souza",          email="aluno2@observatorio.pi",     senha="aluno1234",      tipo="ALUNO"),
        dict(nome="Pedro Oliveira",       email="aluno3@observatorio.pi",     senha="aluno1234",      tipo="ALUNO"),
        dict(nome="TechRecruit Ltda",     email="empresa@observatorio.pi",    senha="empresa1234",    tipo="EMPRESA"),
    ]

    criados = {}
    for u in usuarios_seed:
        obj = User(
            nome=u["nome"],
            email=u["email"],
            senha_hash=hash_senha(u["senha"]),
            tipo=u["tipo"],
            ativo=True,
        )
        db.add(obj)
        db.flush()          # garante que obj.id está disponível
        criados[u["email"]] = obj
        print(f"  [usuário] {u['tipo']:<12}  {u['email']}  /  {u['senha']}")

    db.commit()

    # ── Projetos ──────────────────────────────────────────────────────────────
    aluno1 = criados["aluno1@observatorio.pi"]
    aluno2 = criados["aluno2@observatorio.pi"]
    aluno3 = criados["aluno3@observatorio.pi"]
    prof   = criados["professor@observatorio.pi"]

    projetos_seed = [
        dict(
            titulo="Sistema de Gestão de Biblioteca",
            descricao=(
                "Aplicação web para gerenciamento de acervo bibliográfico, "
                "permitindo cadastro de livros, controle de empréstimos e "
                "geração de relatórios de uso. Desenvolvido com foco na "
                "experiência do usuário e acessibilidade."
            ),
            turma="ADS-2A", semestre="2025-1",
            tecnologias="Python, FastAPI, SQLite, Bootstrap, Jinja2",
            link_repositorio="https://github.com/exemplo/biblioteca",
            status="AVALIADO",
            aluno=aluno1,
        ),
        dict(
            titulo="App de Controle Financeiro Pessoal",
            descricao=(
                "Aplicativo mobile-first para controle de receitas e despesas, "
                "com categorização automática, gráficos de evolução mensal e "
                "alertas de orçamento. Interface responsiva e intuitiva."
            ),
            turma="ADS-2A", semestre="2025-1",
            tecnologias="Python, Flask, Chart.js, SQLAlchemy, Bootstrap",
            link_repositorio="https://github.com/exemplo/financeiro",
            status="SUBMETIDO",
            aluno=aluno1,
        ),
        dict(
            titulo="Plataforma de Agendamento Online",
            descricao=(
                "Sistema para agendamento de serviços (salões, clínicas, etc.) "
                "com painel do prestador, notificações por e-mail e calendário "
                "interativo. Integração com Google Calendar."
            ),
            turma="ADS-2B", semestre="2025-1",
            tecnologias="Python, Django, PostgreSQL, FullCalendar, Tailwind CSS",
            link_repositorio="https://github.com/exemplo/agendamento",
            status="AVALIADO",
            aluno=aluno2,
        ),
        dict(
            titulo="E-commerce de Produtos Artesanais",
            descricao=(
                "Loja virtual para artesãos locais venderem seus produtos, "
                "com carrinho de compras, sistema de pagamento integrado e "
                "painel de gestão de pedidos para os vendedores."
            ),
            turma="ADS-2B", semestre="2025-1",
            tecnologias="Python, FastAPI, React, Stripe API, MongoDB",
            link_repositorio="",
            status="SUBMETIDO",
            aluno=aluno2,
        ),
        dict(
            titulo="Sistema de Monitoramento de Estoque",
            descricao=(
                "Solução para pequenas empresas controlarem seu estoque em "
                "tempo real, com alertas de reposição, histórico de movimentações "
                "e relatórios de giro de produtos."
            ),
            turma="ADS-2A", semestre="2024-2",
            tecnologias="Python, Flask, SQLite, Bootstrap, Chart.js",
            link_repositorio="https://github.com/exemplo/estoque",
            status="AVALIADO",
            aluno=aluno3,
        ),
        dict(
            titulo="Portal de Vagas para Estudantes",
            descricao=(
                "Plataforma que conecta estudantes de tecnologia a empresas "
                "parceiras, com sistema de currículo online, filtros por área "
                "e nível de experiência, e chat entre candidato e recrutador."
            ),
            turma="ADS-2A", semestre="2025-1",
            tecnologias="Python, FastAPI, Vue.js, PostgreSQL, WebSocket",
            link_repositorio="https://github.com/exemplo/vagas",
            status="SUBMETIDO",
            aluno=aluno3,
        ),
    ]

    proj_objs = []
    for p in projetos_seed:
        aluno = p.pop("aluno")
        obj = Project(aluno_id=aluno.id, **p)
        db.add(obj)
        db.flush()
        proj_objs.append(obj)
        print(f"  [projeto]  '{obj.titulo[:45]}...' — {obj.turma} / {obj.status}")

    db.commit()

    # ── Avaliações ────────────────────────────────────────────────────────────
    avaliacoes_seed = [
        # (projeto_idx, nc, nt, na, ni, comentario)
        (0, 9.0, 8.5, 9.0, 8.0, "Excelente trabalho! Documentação muito bem elaborada e código limpo. Parabéns pela organização do projeto."),
        (2, 8.0, 9.0, 7.5, 9.5, "Ótima solução técnica com uso criativo das APIs. A interface ficou muito intuitiva. Recomendo explorar testes automatizados."),
        (4, 8.5, 8.0, 8.5, 7.5, "Projeto sólido e bem estruturado. O controle de estoque atende bem às necessidades do negócio. Boa apresentação."),
    ]

    for proj_idx, nc, nt, na, ni, comentario in avaliacoes_seed:
        media = round((nc + nt + na + ni) / 4, 2)
        av = Avaliacao(
            projeto_id=proj_objs[proj_idx].id,
            professor_id=prof.id,
            nota_conteudo=nc,
            nota_tecnica=nt,
            nota_apresentacao=na,
            nota_inovacao=ni,
            nota_final=media,
            comentario=comentario,
        )
        db.add(av)
        print(f"  [avaliação] projeto '{proj_objs[proj_idx].titulo[:35]}...' — nota {media}")

    db.commit()

    print("\n── Resumo dos acessos de teste ──────────────────────────────────")
    print("  TIPO          E-MAIL                          SENHA")
    print("  ─────────────────────────────────────────────────────────────")
    for u in usuarios_seed:
        print(f"  {u['tipo']:<13} {u['email']:<35} {u['senha']}")
    print("─────────────────────────────────────────────────────────────────\n")


def main():
    ROOT = os.path.dirname(os.path.abspath(__file__))

    # ── Garante que está rodando dentro do .venv (apenas Windows local) ───────
    VENV_PYTHON = os.path.join(ROOT, ".venv", "Scripts", "python.exe")

    if os.path.exists(VENV_PYTHON) and os.path.abspath(sys.executable) != os.path.abspath(VENV_PYTHON):
        print(f"Relançando com o venv: {VENV_PYTHON}")
        result = subprocess.run([VENV_PYTHON, __file__] + sys.argv[1:])
        sys.exit(result.returncode)

    # ── A partir daqui estamos no ambiente correto ────────────────────────────
    APP_DIR = os.path.join(ROOT, "observatorio_pi")

    os.chdir(APP_DIR)
    sys.path.insert(0, APP_DIR)

    # ── 1. Banco e tabelas ────────────────────────────────────────────────────
    from sqlalchemy import text
    from app.database import engine, Base
    from app.models.user import User            # noqa: F401
    from app.models.project import Project, Avaliacao  # noqa: F401

    Base.metadata.create_all(bind=engine)

    # ── 2. Migrações para bancos antigos ──────────────────────────────────────
    with engine.connect() as conn:
        # users: coluna ativo
        cols_users = [row[1] for row in conn.execute(text("PRAGMA table_info(users)"))]
        if "ativo" not in cols_users:
            conn.execute(text("ALTER TABLE users ADD COLUMN ativo BOOLEAN NOT NULL DEFAULT 1"))
            conn.commit()
            print("Coluna 'ativo' adicionada à tabela users.")

        # projects: novas colunas
        cols_proj = [row[1] for row in conn.execute(text("PRAGMA table_info(projects)"))]
        migrations = [
            ("turma",            "ALTER TABLE projects ADD COLUMN turma VARCHAR DEFAULT ''"),
            ("semestre",         "ALTER TABLE projects ADD COLUMN semestre VARCHAR DEFAULT ''"),
            ("tecnologias",      "ALTER TABLE projects ADD COLUMN tecnologias VARCHAR DEFAULT ''"),
            ("link_repositorio", "ALTER TABLE projects ADD COLUMN link_repositorio VARCHAR DEFAULT ''"),
            ("status",           "ALTER TABLE projects ADD COLUMN status VARCHAR DEFAULT 'SUBMETIDO'"),
        ]
        for col, sql in migrations:
            if col not in cols_proj:
                conn.execute(text(sql))
                conn.commit()
                print(f"Coluna '{col}' adicionada à tabela projects.")

    # ── 3. Seed: usuários e dados de exemplo ─────────────────────────────────
    from app.database import SessionLocal
    from app.core.security import hash_senha

    db = SessionLocal()
    try:
        _seed_usuarios_e_projetos(db, hash_senha)
    finally:
        db.close()

    # ── 4. Servidor ───────────────────────────────────────────────────────────
    import uvicorn

    # Em produção (PORT definida pelo Render), usa 0.0.0.0 e sem reload
    port = int(os.getenv("PORT", 8000))
    is_prod = "PORT" in os.environ

    host = "0.0.0.0" if is_prod else "127.0.0.1"
    reload = not is_prod

    print(f"\nServidor iniciando em: http://{host}:{port}")
    if not is_prod:
        print("Pressione CTRL+C para parar.\n")

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        reload_dirs=[APP_DIR] if reload else None,
    )


if __name__ == "__main__":
    main()
