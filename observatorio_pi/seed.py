"""
Script de seed — cria usuários de teste e projetos de exemplo.
Execute uma vez antes de iniciar o servidor:

    .venv\\Scripts\\python.exe observatorio_pi\\seed.py
    ou
    python observatorio_pi/seed.py  (dentro do venv)
"""
import sys
import os

# Garante que o app é encontrado
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.database import engine, Base, SessionLocal
from app.models.user import User
from app.models.project import Project, Avaliacao
from app.core.security import hash_senha

# Cria tabelas e aplica migrações
Base.metadata.create_all(bind=engine)

with engine.connect() as conn:
    cols_users = [row[1] for row in conn.execute(text("PRAGMA table_info(users)"))]
    if "ativo" not in cols_users:
        conn.execute(text("ALTER TABLE users ADD COLUMN ativo BOOLEAN NOT NULL DEFAULT 1"))
        conn.commit()

    cols_proj = [row[1] for row in conn.execute(text("PRAGMA table_info(projects)"))]
    for col, sql in [
        ("turma",            "ALTER TABLE projects ADD COLUMN turma VARCHAR DEFAULT ''"),
        ("semestre",         "ALTER TABLE projects ADD COLUMN semestre VARCHAR DEFAULT ''"),
        ("tecnologias",      "ALTER TABLE projects ADD COLUMN tecnologias VARCHAR DEFAULT ''"),
        ("link_repositorio", "ALTER TABLE projects ADD COLUMN link_repositorio VARCHAR DEFAULT ''"),
        ("status",           "ALTER TABLE projects ADD COLUMN status VARCHAR DEFAULT 'SUBMETIDO'"),
    ]:
        if col not in cols_proj:
            conn.execute(text(sql))
            conn.commit()

db = SessionLocal()

if db.query(User).count() > 0:
    print("Banco já possui dados. Para recriar, delete o arquivo observatorio.db e rode novamente.")
    db.close()
    sys.exit(0)

print("\n── Criando usuários de teste ────────────────────────────────────────")

usuarios_seed = [
    dict(nome="Administrador",        email="admin@observatorio.pi",       senha="admin1234",   tipo="ADMIN"),
    dict(nome="Prof. Carlos Mendes",  email="professor@observatorio.pi",   senha="prof1234",    tipo="PROFESSOR"),
    dict(nome="Coord. Ana Lima",      email="coordenador@observatorio.pi", senha="coord1234",   tipo="COORDENADOR"),
    dict(nome="João Silva",           email="aluno1@observatorio.pi",      senha="aluno1234",   tipo="ALUNO"),
    dict(nome="Maria Souza",          email="aluno2@observatorio.pi",      senha="aluno1234",   tipo="ALUNO"),
    dict(nome="Pedro Oliveira",       email="aluno3@observatorio.pi",      senha="aluno1234",   tipo="ALUNO"),
    dict(nome="TechRecruit Ltda",     email="empresa@observatorio.pi",     senha="empresa1234", tipo="EMPRESA"),
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
    db.flush()
    criados[u["email"]] = obj

db.commit()
print(f"  {len(usuarios_seed)} usuários criados.")

# ── Projetos ──────────────────────────────────────────────────────────────────
print("\n── Criando projetos de exemplo ──────────────────────────────────────")

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
        status="AVALIADO", aluno_id=aluno1.id,
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
        status="SUBMETIDO", aluno_id=aluno1.id,
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
        status="AVALIADO", aluno_id=aluno2.id,
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
        status="SUBMETIDO", aluno_id=aluno2.id,
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
        status="AVALIADO", aluno_id=aluno3.id,
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
        status="SUBMETIDO", aluno_id=aluno3.id,
    ),
]

proj_objs = []
for p in projetos_seed:
    obj = Project(**p)
    db.add(obj)
    db.flush()
    proj_objs.append(obj)

db.commit()
print(f"  {len(projetos_seed)} projetos criados.")

# ── Avaliações ────────────────────────────────────────────────────────────────
print("\n── Criando avaliações de exemplo ────────────────────────────────────")

avaliacoes_seed = [
    (0, 9.0, 8.5, 9.0, 8.0,
     "Excelente trabalho! Documentação muito bem elaborada e código limpo. Parabéns pela organização do projeto."),
    (2, 8.0, 9.0, 7.5, 9.5,
     "Ótima solução técnica com uso criativo das APIs. A interface ficou muito intuitiva. Recomendo explorar testes automatizados."),
    (4, 8.5, 8.0, 8.5, 7.5,
     "Projeto sólido e bem estruturado. O controle de estoque atende bem às necessidades do negócio. Boa apresentação."),
]

for proj_idx, nc, nt, na, ni, comentario in avaliacoes_seed:
    media = round((nc + nt + na + ni) / 4, 2)
    db.add(Avaliacao(
        projeto_id=proj_objs[proj_idx].id,
        professor_id=prof.id,
        nota_conteudo=nc,
        nota_tecnica=nt,
        nota_apresentacao=na,
        nota_inovacao=ni,
        nota_final=media,
        comentario=comentario,
    ))

db.commit()
print(f"  {len(avaliacoes_seed)} avaliações criadas.")
db.close()

# ── Resumo ────────────────────────────────────────────────────────────────────
print("""
╔══════════════════════════════════════════════════════════════════════╗
║              USUÁRIOS DE TESTE — OBSERVATÓRIO PI                    ║
╠══════════════╦══════════════════════════════════╦═══════════════════╣
║ TIPO         ║ E-MAIL                           ║ SENHA             ║
╠══════════════╬══════════════════════════════════╬═══════════════════╣
║ ADMIN        ║ admin@observatorio.pi            ║ admin1234         ║
║ PROFESSOR    ║ professor@observatorio.pi        ║ prof1234          ║
║ COORDENADOR  ║ coordenador@observatorio.pi      ║ coord1234         ║
║ ALUNO        ║ aluno1@observatorio.pi           ║ aluno1234         ║
║ ALUNO        ║ aluno2@observatorio.pi           ║ aluno1234         ║
║ ALUNO        ║ aluno3@observatorio.pi           ║ aluno1234         ║
║ EMPRESA      ║ empresa@observatorio.pi          ║ empresa1234       ║
╚══════════════╩══════════════════════════════════╩═══════════════════╝

Acesse: http://127.0.0.1:8000
""")
