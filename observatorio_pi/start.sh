#!/bin/sh
# Script de inicialização para produção (Render / Docker)
# Executado a partir de observatorio_pi/ (rootDir do Render)
set -e

# Cria tabelas e inicializa admin padrão
python -c "
import sys, os
sys.path.insert(0, '.')

from sqlalchemy import text
from app.database import engine, Base, SessionLocal
from app.models.user import User
from app.models.project import Turma, Tematica, Equipe, EquipeMembro, EntregaProjeto, Avaliacao
from app.core.security import hash_senha

# Cria todas as tabelas do novo modelo
Base.metadata.create_all(bind=engine)

# Migração: colunas de perfil de aluno (bancos antigos)
with engine.connect() as conn:
    cols = [row[1] for row in conn.execute(text('PRAGMA table_info(users)'))]
    for col, sql in [
        ('ativo',          'ALTER TABLE users ADD COLUMN ativo BOOLEAN NOT NULL DEFAULT 1'),
        ('bio',            'ALTER TABLE users ADD COLUMN bio TEXT DEFAULT \"\"'),
        ('linkedin',       'ALTER TABLE users ADD COLUMN linkedin VARCHAR DEFAULT \"\"'),
        ('github',         'ALTER TABLE users ADD COLUMN github VARCHAR DEFAULT \"\"'),
        ('portfolio_url',  'ALTER TABLE users ADD COLUMN portfolio_url VARCHAR DEFAULT \"\"'),
        ('area_interesse', 'ALTER TABLE users ADD COLUMN area_interesse VARCHAR DEFAULT \"\"'),
        ('cidade',         'ALTER TABLE users ADD COLUMN cidade VARCHAR DEFAULT \"\"'),
        ('telefone',       'ALTER TABLE users ADD COLUMN telefone VARCHAR DEFAULT \"\"'),
    ]:
        if col not in cols:
            conn.execute(text(sql))
            conn.commit()
            print(f'Coluna {col} adicionada.')

# Admin padrão (só cria se não existir nenhum usuário)
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
