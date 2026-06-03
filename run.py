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


def _seed(db, hash_senha):
    """Cria usuários e dados de exemplo se o banco estiver vazio."""
    from app.models.user import User
    from app.models.project import Turma, Tematica, Equipe, EquipeMembro, EntregaProjeto, Avaliacao

    if db.query(User).count() > 0:
        return

    print("\n── Criando dados de exemplo ─────────────────────────────────────")

    seeds_u = [
        dict(nome="Administrador",       email="admin@observatorio.pi",       senha="admin1234",   tipo="ADMIN"),
        dict(nome="Prof. Carlos Mendes", email="professor@observatorio.pi",   senha="prof1234",    tipo="PROFESSOR"),
        dict(nome="Coord. Ana Lima",     email="coordenador@observatorio.pi", senha="coord1234",   tipo="COORDENADOR"),
        dict(nome="João Silva",          email="aluno1@observatorio.pi",      senha="aluno1234",   tipo="ALUNO"),
        dict(nome="Maria Souza",         email="aluno2@observatorio.pi",      senha="aluno1234",   tipo="ALUNO"),
        dict(nome="Pedro Oliveira",      email="aluno3@observatorio.pi",      senha="aluno1234",   tipo="ALUNO"),
        dict(nome="Lucas Ferreira",      email="aluno4@observatorio.pi",      senha="aluno1234",   tipo="ALUNO"),
        dict(nome="TechRecruit Ltda",    email="empresa@observatorio.pi",     senha="empresa1234", tipo="EMPRESA"),
    ]
    criados = {}
    for u in seeds_u:
        obj = User(nome=u["nome"], email=u["email"],
                   senha_hash=hash_senha(u["senha"]), tipo=u["tipo"], ativo=True)
        db.add(obj); db.flush(); criados[u["email"]] = obj
    db.commit()

    prof   = criados["professor@observatorio.pi"]
    aluno1 = criados["aluno1@observatorio.pi"]
    aluno2 = criados["aluno2@observatorio.pi"]
    aluno3 = criados["aluno3@observatorio.pi"]
    aluno4 = criados["aluno4@observatorio.pi"]

    turma_a = Turma(nome="ADS-2A", semestre="2025-1", descricao="Turma manhã — ADS 2º módulo")
    turma_b = Turma(nome="ADS-2B", semestre="2025-1", descricao="Turma noite — ADS 2º módulo")
    db.add_all([turma_a, turma_b]); db.flush()

    t1 = Tematica(titulo="Sistema de Gestão para Micro Empresas",
                  descricao="Desenvolver um sistema web para controle de estoque, vendas e clientes.",
                  turma_id=turma_a.id, professor_id=prof.id, status="EM_ANDAMENTO")
    t2 = Tematica(titulo="Plataforma de Agendamento de Serviços",
                  descricao="Sistema para agendamento online de salões, clínicas e autônomos.",
                  turma_id=turma_b.id, professor_id=prof.id, status="EM_ANDAMENTO")
    db.add_all([t1, t2]); db.flush()

    eq1 = Equipe(nome="Equipe Alpha", tematica_id=t1.id, scrum_master_id=aluno1.id)
    eq2 = Equipe(nome="Equipe Beta",  tematica_id=t2.id, scrum_master_id=aluno3.id)
    db.add_all([eq1, eq2]); db.flush()

    db.add_all([
        EquipeMembro(equipe_id=eq1.id, aluno_id=aluno2.id),
        EquipeMembro(equipe_id=eq2.id, aluno_id=aluno4.id),
    ]); db.flush()

    db.add(EntregaProjeto(equipe_id=eq1.id, autor_id=aluno1.id,
        titulo="Módulo de Cadastro de Clientes",
        descricao="CRUD de clientes com validação e histórico de compras.",
        tecnologias="Python, FastAPI, SQLite, Bootstrap",
        link_repositorio="https://github.com/exemplo/gestao-micro"))
    db.add(EntregaProjeto(equipe_id=eq1.id, autor_id=aluno2.id,
        titulo="Relatório de Vendas — Dashboard",
        descricao="Painel com gráficos de vendas mensais e produtos mais vendidos.",
        tecnologias="Python, Chart.js, Jinja2"))
    db.add(EntregaProjeto(equipe_id=eq2.id, autor_id=aluno3.id,
        titulo="Sistema de Agendamentos com Calendário",
        descricao="Calendário interativo para criação de agendamentos por serviço.",
        tecnologias="Python, Django, FullCalendar",
        link_repositorio="https://github.com/exemplo/agendamento"))
    db.flush()

    db.add(Avaliacao(
        equipe_id=eq1.id, professor_id=prof.id,
        conceito_conteudo="EXCELENTE", conceito_tecnica="OTIMO",
        conceito_apresentacao="EXCELENTE", conceito_inovacao="OTIMO",
        conceito_equipe="EXCELENTE", conceito_final="EXCELENTE",
        comentario="Excelente trabalho! Solução bem estruturada e documentação completa.",
    ))
    db.commit()

    print("""
╔══════════════════════════════════════════════════════════════════════╗
║              USUÁRIOS DE TESTE — OBSERVATÓRIO PI                    ║
╠══════════════╦══════════════════════════════════╦═══════════════════╣
║ TIPO         ║ E-MAIL                           ║ SENHA             ║
╠══════════════╬══════════════════════════════════╬═══════════════════╣
║ ADMIN        ║ admin@observatorio.pi            ║ admin1234         ║
║ PROFESSOR    ║ professor@observatorio.pi        ║ prof1234          ║
║ COORDENADOR  ║ coordenador@observatorio.pi      ║ coord1234         ║
║ ALUNO (SM)   ║ aluno1@observatorio.pi           ║ aluno1234         ║
║ ALUNO        ║ aluno2@observatorio.pi           ║ aluno1234         ║
║ ALUNO (SM)   ║ aluno3@observatorio.pi           ║ aluno1234         ║
║ ALUNO        ║ aluno4@observatorio.pi           ║ aluno1234         ║
║ EMPRESA      ║ empresa@observatorio.pi          ║ empresa1234       ║
╚══════════════╩══════════════════════════════════╩═══════════════════╝
""")


def main():
    ROOT = os.path.dirname(os.path.abspath(__file__))
    VENV_PYTHON = os.path.join(ROOT, ".venv", "Scripts", "python.exe")

    if os.path.exists(VENV_PYTHON) and os.path.abspath(sys.executable) != os.path.abspath(VENV_PYTHON):
        print(f"Relançando com o venv: {VENV_PYTHON}")
        result = subprocess.run([VENV_PYTHON, __file__] + sys.argv[1:])
        sys.exit(result.returncode)

    APP_DIR = os.path.join(ROOT, "observatorio_pi")
    os.chdir(APP_DIR)
    sys.path.insert(0, APP_DIR)

    from sqlalchemy import text
    from app.database import engine, Base
    from app.models.user import User                 # noqa: F401
    from app.models.project import (                 # noqa: F401
        Turma, Tematica, Equipe, EquipeMembro, EntregaProjeto, Avaliacao,
    )

    Base.metadata.create_all(bind=engine)

    # Migração: coluna ativo (bancos muito antigos) + campos de perfil do aluno
    with engine.connect() as conn:
        cols = [row[1] for row in conn.execute(text("PRAGMA table_info(users)"))]
        migrações = [
            ("ativo",          "ALTER TABLE users ADD COLUMN ativo BOOLEAN NOT NULL DEFAULT 1"),
            ("bio",            "ALTER TABLE users ADD COLUMN bio TEXT DEFAULT ''"),
            ("linkedin",       "ALTER TABLE users ADD COLUMN linkedin VARCHAR DEFAULT ''"),
            ("github",         "ALTER TABLE users ADD COLUMN github VARCHAR DEFAULT ''"),
            ("portfolio_url",  "ALTER TABLE users ADD COLUMN portfolio_url VARCHAR DEFAULT ''"),
            ("area_interesse", "ALTER TABLE users ADD COLUMN area_interesse VARCHAR DEFAULT ''"),
            ("cidade",         "ALTER TABLE users ADD COLUMN cidade VARCHAR DEFAULT ''"),
            ("telefone",       "ALTER TABLE users ADD COLUMN telefone VARCHAR DEFAULT ''"),
        ]
        for col, sql in migrações:
            if col not in cols:
                conn.execute(text(sql)); conn.commit()

    from app.database import SessionLocal
    from app.core.security import hash_senha
    db = SessionLocal()
    try:
        _seed(db, hash_senha)
    finally:
        db.close()

    import uvicorn
    port = int(os.getenv("PORT", 8000))
    is_prod = "PORT" in os.environ
    host = "0.0.0.0" if is_prod else "127.0.0.1"
    reload = not is_prod

    print(f"\nServidor iniciando em: http://{host}:{port}")
    if not is_prod:
        print("Pressione CTRL+C para parar.\n")

    uvicorn.run("app.main:app", host=host, port=port, reload=reload,
                reload_dirs=[APP_DIR] if reload else None)


if __name__ == "__main__":
    main()
