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
    from app.models.user import User      # noqa: F401
    from app.models.project import Project  # noqa: F401

    Base.metadata.create_all(bind=engine)

    # ── 2. Migração: coluna 'ativo' para bancos antigos ───────────────────────
    with engine.connect() as conn:
        cols = [row[1] for row in conn.execute(text("PRAGMA table_info(users)"))]
        if "ativo" not in cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN ativo BOOLEAN NOT NULL DEFAULT 1"))
            conn.commit()
            print("Coluna 'ativo' adicionada ao banco.")

    # ── 3. Usuário admin padrão ───────────────────────────────────────────────
    from app.database import SessionLocal
    from app.core.security import hash_senha

    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            admin_email = os.getenv("ADMIN_EMAIL", "admin@observatorio.pi")
            admin_senha = os.getenv("ADMIN_PASSWORD", "admin1234")
            admin = User(
                nome="Administrador",
                email=admin_email,
                senha_hash=hash_senha(admin_senha),
                tipo="ADMIN",
                ativo=True,
            )
            db.add(admin)
            db.commit()
            print(f"Admin criado: {admin_email} / {admin_senha}")
            print("ATENÇÃO: Altere a senha após o primeiro login!")
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
