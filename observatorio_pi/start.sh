#!/bin/sh
# Script de inicialização para produção (Render / Docker)
# Executado a partir de observatorio_pi/ (rootDir do Render)
set -e

# Cria tabelas e seed do admin
python -c "
import sys, os
sys.path.insert(0, '.')

from sqlalchemy import text
from app.database import engine, Base, SessionLocal
from app.models.user import User
from app.models.project import Project
from app.core.security import hash_senha

# Cria tabelas
Base.metadata.create_all(bind=engine)

# Migração: coluna 'ativo' para bancos antigos
with engine.connect() as conn:
    cols = [row[1] for row in conn.execute(text('PRAGMA table_info(users)'))]
    if 'ativo' not in cols:
        conn.execute(text('ALTER TABLE users ADD COLUMN ativo BOOLEAN NOT NULL DEFAULT 1'))
        conn.commit()
        print('Coluna ativo adicionada.')

# Admin padrão
db = SessionLocal()
try:
    if db.query(User).count() == 0:
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@observatorio.pi')
        admin_senha = os.getenv('ADMIN_PASSWORD', 'admin1234')
        db.add(User(
            nome='Administrador',
            email=admin_email,
            senha_hash=hash_senha(admin_senha),
            tipo='ADMIN',
            ativo=True,
        ))
        db.commit()
        print(f'Admin criado: {admin_email}')
        print('ATENCAO: Altere a senha apos o primeiro login!')
finally:
    db.close()
"

# Inicia o servidor com Gunicorn + Uvicorn workers
exec gunicorn app.main:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers 2 \
    --bind "0.0.0.0:${PORT:-8000}" \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
