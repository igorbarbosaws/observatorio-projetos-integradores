"""
Script de seed — cria usuários e dados de exemplo.
    .venv\\Scripts\\python.exe observatorio_pi\\seed.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base, SessionLocal
from app.models.user import User
from app.models.project import Turma, Tematica, Equipe, EquipeMembro, EntregaProjeto, Avaliacao
from app.core.security import hash_senha

Base.metadata.create_all(bind=engine)
db = SessionLocal()

if db.query(User).count() > 0:
    print("Banco já possui dados. Delete observatorio.db para recriar.")
    db.close(); sys.exit(0)

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
    obj = User(nome=u["nome"], email=u["email"], senha_hash=hash_senha(u["senha"]), tipo=u["tipo"], ativo=True)
    db.add(obj); db.flush(); criados[u["email"]] = obj
db.commit()

prof=criados["professor@observatorio.pi"]; aluno1=criados["aluno1@observatorio.pi"]
aluno2=criados["aluno2@observatorio.pi"]; aluno3=criados["aluno3@observatorio.pi"]; aluno4=criados["aluno4@observatorio.pi"]

turma_a = Turma(nome="ADS-2A", semestre="2025-1", descricao="Turma manhã — ADS 2º módulo")
turma_b = Turma(nome="ADS-2B", semestre="2025-1", descricao="Turma noite — ADS 2º módulo")
db.add_all([turma_a, turma_b]); db.flush()

t1 = Tematica(titulo="Sistema de Gestão para Micro Empresas", descricao="Sistema web para controle de estoque, vendas e clientes de micro empresas locais.", turma_id=turma_a.id, professor_id=prof.id, status="EM_ANDAMENTO")
t2 = Tematica(titulo="Plataforma de Agendamento de Serviços", descricao="Sistema para agendamento online de salões, clínicas e prestadores autônomos.", turma_id=turma_b.id, professor_id=prof.id, status="EM_ANDAMENTO")
db.add_all([t1, t2]); db.flush()

eq1 = Equipe(nome="Equipe Alpha", tematica_id=t1.id, scrum_master_id=aluno1.id)
eq2 = Equipe(nome="Equipe Beta",  tematica_id=t2.id, scrum_master_id=aluno3.id)
db.add_all([eq1, eq2]); db.flush()

db.add_all([EquipeMembro(equipe_id=eq1.id, aluno_id=aluno2.id), EquipeMembro(equipe_id=eq2.id, aluno_id=aluno4.id)]); db.flush()

db.add(EntregaProjeto(equipe_id=eq1.id, autor_id=aluno1.id, titulo="Módulo de Cadastro de Clientes", descricao="CRUD de clientes com validação e histórico de compras.", tecnologias="Python, FastAPI, SQLite, Bootstrap", link_repositorio="https://github.com/exemplo/gestao"))
db.add(EntregaProjeto(equipe_id=eq1.id, autor_id=aluno2.id, titulo="Dashboard de Vendas", descricao="Painel com gráficos de vendas mensais e produtos mais vendidos.", tecnologias="Python, Chart.js, Jinja2"))
db.add(EntregaProjeto(equipe_id=eq2.id, autor_id=aluno3.id, titulo="Sistema de Agendamentos", descricao="Calendário interativo para criação de agendamentos.", tecnologias="Python, Django, FullCalendar"))
db.flush()

db.add(Avaliacao(equipe_id=eq1.id, professor_id=prof.id,
    conceito_conteudo="EXCELENTE", conceito_tecnica="OTIMO",
    conceito_apresentacao="EXCELENTE", conceito_inovacao="OTIMO",
    conceito_equipe="EXCELENTE", conceito_final="EXCELENTE",
    comentario="Excelente trabalho! Solução bem estruturada e documentação completa."))
db.commit(); db.close()

print("""
╔══════════════════════════════════════════════════════════════════════╗
║              USUÁRIOS DE TESTE — OBSERVATÓRIO PI                    ║
╠══════════════╦══════════════════════════════════╦═══════════════════╣
║ ADMIN        ║ admin@observatorio.pi            ║ admin1234         ║
║ PROFESSOR    ║ professor@observatorio.pi        ║ prof1234          ║
║ COORDENADOR  ║ coordenador@observatorio.pi      ║ coord1234         ║
║ ALUNO (SM)   ║ aluno1@observatorio.pi           ║ aluno1234         ║
║ ALUNO        ║ aluno2@observatorio.pi           ║ aluno1234         ║
║ ALUNO (SM)   ║ aluno3@observatorio.pi           ║ aluno1234         ║
║ ALUNO        ║ aluno4@observatorio.pi           ║ aluno1234         ║
║ EMPRESA      ║ empresa@observatorio.pi          ║ empresa1234       ║
╚══════════════╩══════════════════════════════════╩═══════════════════╝
Acesse: http://127.0.0.1:8000
""")
