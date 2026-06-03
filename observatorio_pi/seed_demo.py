"""
Seed de demonstração completo — popula o banco com dados realistas.
    .venv\\Scripts\\python.exe observatorio_pi\\seed_demo.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timezone, timedelta
from app.database import engine, Base, SessionLocal
from app.models.user import User
from app.models.project import Turma, Tematica, Equipe, EquipeMembro, EntregaProjeto, Avaliacao
from app.core.security import hash_senha

Base.metadata.create_all(bind=engine)
db = SessionLocal()

if db.query(User).count() > 0:
    print("Banco já possui dados. Delete observatorio.db para recriar.")
    db.close(); sys.exit(0)

print("Populando banco de demonstração...")

# ── USUÁRIOS ──────────────────────────────────────────────────────────────────
def u(nome, email, senha, tipo, bio="", linkedin="", github="", area="", cidade="", telefone=""):
    obj = User(nome=nome, email=email, senha_hash=hash_senha(senha), tipo=tipo,
               ativo=True, bio=bio, linkedin=linkedin, github=github,
               area_interesse=area, cidade=cidade, telefone=telefone)
    db.add(obj); db.flush(); return obj

# Admin
admin = u("Administrador Sistema", "admin@observatorio.pi", "admin1234", "ADMIN")

# Coordenadores
coord1 = u("Profa. Dra. Ana Lima",    "coordenador@observatorio.pi", "coord1234", "COORDENADOR",
           bio="Coordenadora do curso de ADS. Mestre em Ciência da Computação pela UFPE.",
           cidade="Recife — PE")
coord2 = u("Prof. Dr. Carlos Neto",   "carlos.neto@senac.pi",        "coord1234", "COORDENADOR",
           bio="Coordenador adjunto. Doutor em Engenharia de Software.",
           cidade="Recife — PE")

# Professores
prof1 = u("Prof. Ricardo Mendes",  "professor@observatorio.pi",   "prof1234", "PROFESSOR",
          bio="Professor de Desenvolvimento Web e Banco de Dados. 10 anos de experiência no mercado.",
          linkedin="https://linkedin.com/in/ricardo-mendes", cidade="Recife — PE")
prof2 = u("Profa. Fernanda Costa", "fernanda.costa@senac.pi",    "prof1234", "PROFESSOR",
          bio="Professora de Engenharia de Software e UX/UI. Especialista em metodologias ágeis.",
          linkedin="https://linkedin.com/in/fernanda-costa", cidade="Recife — PE")
prof3 = u("Prof. Marcos Albuquerque", "marcos.albuquerque@senac.pi", "prof1234", "PROFESSOR",
          bio="Professor de Infraestrutura e DevOps. Certificado AWS e Azure.",
          cidade="Recife — PE")

db.commit()
print("  Admins, coordenadores e professores criados.")

# Alunos — Turma ADS-2A (manhã)
a1 = u("João Victor Silva",    "joao.silva@aluno.pi",    "aluno1234", "ALUNO",
       bio="Desenvolvedor back-end em formação. Apaixonado por Python e APIs RESTful.",
       github="https://github.com/joaosilva", linkedin="https://linkedin.com/in/joaosilva",
       area="Backend, APIs, Python", cidade="Recife — PE", telefone="(81) 99111-1111")
a2 = u("Maria Clara Souza",   "maria.souza@aluno.pi",   "aluno1234", "ALUNO",
       bio="Focada em front-end e experiência do usuário. Aprendendo React e design de interfaces.",
       github="https://github.com/mariaclara", linkedin="https://linkedin.com/in/mariaclara",
       area="Frontend, UX/UI, React", cidade="Olinda — PE", telefone="(81) 99222-2222")
a3 = u("Pedro Henrique Lima",  "pedro.lima@aluno.pi",    "aluno1234", "ALUNO",
       bio="Entusiasta de banco de dados e análise de dados. Experiência com MySQL e Power BI.",
       github="https://github.com/pedrolima",
       area="Banco de Dados, BI, Python", cidade="Caruaru — PE")
a4 = u("Ana Beatriz Ferreira", "ana.ferreira@aluno.pi",  "aluno1234", "ALUNO",
       bio="Desenvolvedora full-stack com interesse em automação e testes de software.",
       github="https://github.com/anabferreira", linkedin="https://linkedin.com/in/anabferreira",
       area="Full Stack, Testes, DevOps", cidade="Recife — PE", telefone="(81) 99333-3333")

# Alunos — Turma ADS-2B (noite)
a5 = u("Lucas Oliveira Santos", "lucas.santos@aluno.pi",  "aluno1234", "ALUNO",
       bio="Programador mobile em formação. Desenvolvendo apps com React Native e Flutter.",
       github="https://github.com/lucassantos",
       area="Mobile, React Native, Flutter", cidade="Jaboatão — PE", telefone="(81) 99444-4444")
a6 = u("Juliana Rodrigues",   "juliana.rodrigues@aluno.pi", "aluno1234", "ALUNO",
       bio="Interessada em segurança da informação e cloud computing. Estudando AWS.",
       linkedin="https://linkedin.com/in/julianarod",
       area="Segurança, Cloud, AWS", cidade="Recife — PE")
a7 = u("Rafael Costa Moura",  "rafael.moura@aluno.pi",   "aluno1234", "ALUNO",
       bio="Desenvolvedor back-end com foco em microsserviços e arquitetura de software.",
       github="https://github.com/rafaelmoura", linkedin="https://linkedin.com/in/rafaelmoura",
       area="Backend, Microsserviços, Java", cidade="Paulista — PE", telefone="(81) 99555-5555")
a8 = u("Camila Barros",       "camila.barros@aluno.pi",  "aluno1234", "ALUNO",
       bio="Designer e desenvolvedora front-end. Criando interfaces acessíveis e responsivas.",
       github="https://github.com/camilabarros", linkedin="https://linkedin.com/in/camilabarros",
       area="Frontend, Acessibilidade, CSS", cidade="Recife — PE", telefone="(81) 99666-6666")

# Alunos — Turma ADS-2C (tarde)
a9  = u("Thiago Nascimento",  "thiago.nascimento@aluno.pi", "aluno1234", "ALUNO",
        bio="Desenvolvedor Python com interesse em IA e machine learning.",
        github="https://github.com/thiagonasc",
        area="Python, IA, Machine Learning", cidade="Recife — PE")
a10 = u("Isabela Cardoso",    "isabela.cardoso@aluno.pi",   "aluno1234", "ALUNO",
        bio="Analista de sistemas em formação. Focada em gestão de projetos e metodologias ágeis.",
        linkedin="https://linkedin.com/in/isabelacardoso",
        area="Gestão de Projetos, Scrum, Análise", cidade="Olinda — PE", telefone="(81) 99777-7777")

# Empresas
emp1 = u("TechRecruit Nordeste",   "empresa@observatorio.pi",    "empresa1234", "EMPRESA",
         bio="Empresa de recrutamento especializada em tecnologia no Nordeste.")
emp2 = u("Inovação Digital Ltda",  "inovacao@empresa.pi",         "empresa1234", "EMPRESA",
         bio="Startup de transformação digital buscando talentos em ADS.")
emp3 = u("Softway Sistemas",       "softway@empresa.pi",          "empresa1234", "EMPRESA",
         bio="Software house com mais de 15 anos de mercado. Sempre em busca de novos talentos.")

db.commit()
print("  Alunos e empresas criados.")

# ── TURMAS ────────────────────────────────────────────────────────────────────
ta = Turma(nome="ADS-2A", semestre="2025-1", descricao="Turma manhã — 2º módulo ADS", ativa=True)
tb = Turma(nome="ADS-2B", semestre="2025-1", descricao="Turma noite — 2º módulo ADS", ativa=True)
tc = Turma(nome="ADS-2C", semestre="2025-1", descricao="Turma tarde — 2º módulo ADS", ativa=True)
td = Turma(nome="ADS-2A", semestre="2024-2", descricao="Turma manhã — semestre anterior", ativa=False)
db.add_all([ta, tb, tc, td]); db.flush()

# ── TEMÁTICAS ─────────────────────────────────────────────────────────────────
t1 = Tematica(titulo="Sistema de Gestão para Pequenos Negócios",
    descricao="Desenvolver uma aplicação web completa para micro e pequenas empresas controlarem estoque, vendas, clientes e fluxo de caixa. O sistema deve ter painel gerencial com relatórios e gráficos.",
    turma_id=ta.id, professor_id=prof1.id, status="EM_ANDAMENTO")
t2 = Tematica(titulo="Plataforma de Agendamento Online",
    descricao="Sistema para prestadores de serviço (salões, clínicas, oficinas) gerenciarem seus agendamentos. Deve incluir calendário interativo, notificações e painel do cliente.",
    turma_id=ta.id, professor_id=prof1.id, status="EM_ANDAMENTO")
t3 = Tematica(titulo="Aplicativo de Delivery Local",
    descricao="App para conectar restaurantes e mercados locais aos consumidores. Deve ter cadastro de estabelecimentos, cardápio digital, carrinho de compras e acompanhamento de pedidos.",
    turma_id=tb.id, professor_id=prof2.id, status="EM_ANDAMENTO")
t4 = Tematica(titulo="Portal de Empregos para Formandos",
    descricao="Plataforma que conecta alunos formandos de cursos técnicos e graduação com empresas parceiras. Deve incluir currículo online, filtros de vagas e sistema de candidatura.",
    turma_id=tb.id, professor_id=prof2.id, status="CONCLUIDA")
t5 = Tematica(titulo="Sistema de Monitoramento de Saúde",
    descricao="Aplicação para registro e acompanhamento de dados de saúde pessoal (pressão, glicemia, medicamentos). Deve gerar relatórios para médicos e pacientes.",
    turma_id=tc.id, professor_id=prof3.id, status="EM_ANDAMENTO")
# Temática do semestre anterior
t6 = Tematica(titulo="E-commerce de Artesanato Local",
    descricao="Loja virtual para artesãos pernambucanos venderem produtos. Inclui vitrine, carrinho, pagamento e painel do vendedor.",
    turma_id=td.id, professor_id=prof1.id, status="CONCLUIDA")
db.add_all([t1, t2, t3, t4, t5, t6]); db.flush()

print("  Turmas e temáticas criadas.")

# ── EQUIPES ───────────────────────────────────────────────────────────────────
# Temática 1 — 2 equipes
eq1 = Equipe(nome="Equipe Alpha", tematica_id=t1.id, scrum_master_id=a1.id, status="EM_ANDAMENTO")
eq2 = Equipe(nome="Equipe Beta",  tematica_id=t1.id, scrum_master_id=a3.id, status="EM_ANDAMENTO")
# Temática 2 — 1 equipe
eq3 = Equipe(nome="Equipe Delta", tematica_id=t2.id, scrum_master_id=a2.id, status="EM_ANDAMENTO")
# Temática 3 — 2 equipes
eq4 = Equipe(nome="Equipe Sigma", tematica_id=t3.id, scrum_master_id=a5.id, status="EM_ANDAMENTO")
eq5 = Equipe(nome="Equipe Omega", tematica_id=t3.id, scrum_master_id=a7.id, status="EM_ANDAMENTO")
# Temática 4 — CONCLUÍDA
eq6 = Equipe(nome="Equipe Gamma", tematica_id=t4.id, scrum_master_id=a6.id, status="FINALIZADO")
# Temática 5
eq7 = Equipe(nome="Equipe Zeta",  tematica_id=t5.id, scrum_master_id=a9.id,  status="EM_ANDAMENTO")
# Temática 6 — semestre anterior, concluída
eq8 = Equipe(nome="Equipe Theta", tematica_id=t6.id, scrum_master_id=a4.id, status="FINALIZADO")
db.add_all([eq1,eq2,eq3,eq4,eq5,eq6,eq7,eq8]); db.flush()

# Membros
db.add_all([
    EquipeMembro(equipe_id=eq1.id, aluno_id=a2.id),   # Alpha: João (SM) + Maria
    EquipeMembro(equipe_id=eq2.id, aluno_id=a4.id),   # Beta: Pedro (SM) + Ana
    EquipeMembro(equipe_id=eq3.id, aluno_id=a1.id),   # Delta: Maria (SM) + João
    EquipeMembro(equipe_id=eq3.id, aluno_id=a3.id),   # Delta: + Pedro
    EquipeMembro(equipe_id=eq4.id, aluno_id=a6.id),   # Sigma: Lucas (SM) + Juliana
    EquipeMembro(equipe_id=eq5.id, aluno_id=a8.id),   # Omega: Rafael (SM) + Camila
    EquipeMembro(equipe_id=eq6.id, aluno_id=a5.id),   # Gamma: Juliana (SM) + Lucas
    EquipeMembro(equipe_id=eq7.id, aluno_id=a10.id),  # Zeta: Thiago (SM) + Isabela
    EquipeMembro(equipe_id=eq8.id, aluno_id=a2.id),   # Theta: Ana (SM) + Maria
])
db.flush()
print("  Equipes e membros criados.")

# ── ENTREGAS ──────────────────────────────────────────────────────────────────
def entrega(equipe, autor, titulo, descricao, tecnologias, repo=""):
    e = EntregaProjeto(equipe_id=equipe.id, autor_id=autor.id, titulo=titulo,
        descricao=descricao, tecnologias=tecnologias, link_repositorio=repo)
    db.add(e); return e

# Equipe Alpha (Gestão PME) — João (SM) + Maria
entrega(eq1, a1, "Módulo de Cadastro e Gestão de Clientes",
    "CRUD completo de clientes com busca avançada, histórico de compras e exportação para CSV. Inclui validação de CPF/CNPJ e verificação de duplicatas.",
    "Python, FastAPI, SQLAlchemy, Bootstrap 5", "https://github.com/joaosilva/gestao-pme")
entrega(eq1, a2, "Dashboard Gerencial e Relatórios",
    "Painel com gráficos de vendas mensais, produtos mais vendidos, clientes inadimplentes e previsão de fluxo de caixa. Dados em tempo real com Chart.js.",
    "Python, Chart.js, Jinja2, Bootstrap 5", "https://github.com/mariaclara/dashboard-pme")

# Equipe Beta (Gestão PME) — Pedro (SM) + Ana
entrega(eq2, a3, "Controle de Estoque com Alertas",
    "Sistema de controle de estoque com categorias, fornecedores, movimentações e alertas automáticos de reposição por e-mail. Suporte a código de barras.",
    "Python, FastAPI, SQLite, Bootstrap, QR Code", "https://github.com/pedrolima/estoque")
entrega(eq2, a4, "Módulo Financeiro — Fluxo de Caixa",
    "Registro de entradas e saídas financeiras com categorização, conciliação bancária e relatórios mensais em PDF. Integração com planilhas Excel.",
    "Python, ReportLab, openpyxl, Bootstrap", "")

# Equipe Delta (Agendamento) — Maria (SM) + João + Pedro
entrega(eq3, a2, "Calendário Interativo de Agendamentos",
    "Sistema de agendamento com calendário visual (FullCalendar), seleção de serviços, profissionais e horários disponíveis. Confirmação por e-mail.",
    "Python, Django, FullCalendar, PostgreSQL", "https://github.com/mariaclara/agendamento")
entrega(eq3, a1, "Painel do Prestador de Serviço",
    "Dashboard exclusivo para o prestador com visão da agenda do dia, histórico de clientes, bloqueio de horários e configuração de serviços.",
    "Python, Django, Bootstrap 5, Chart.js", "")
entrega(eq3, a3, "Sistema de Notificações e Lembretes",
    "Envio automático de lembretes de agendamento por WhatsApp e e-mail. Cancelamento online com política de reagendamento.",
    "Python, Celery, Redis, Twilio API", "")

# Equipe Sigma (Delivery) — Lucas (SM) + Juliana
entrega(eq4, a5, "App Mobile de Pedidos (React Native)",
    "Aplicativo mobile para clientes fazerem pedidos com geolocalização, rastreamento em tempo real e múltiplas formas de pagamento.",
    "React Native, Node.js, Firebase", "https://github.com/lucassantos/delivery-app")
entrega(eq4, a6, "Painel Administrativo do Restaurante",
    "Interface web para o restaurante gerenciar cardápio, receber pedidos, controlar status de entregas e visualizar relatórios de vendas.",
    "Python, FastAPI, React, SQLAlchemy", "")

# Equipe Omega (Delivery) — Rafael (SM) + Camila
entrega(eq5, a7, "API de Pedidos e Integração de Pagamento",
    "API RESTful com autenticação JWT, endpoints para pedidos, integração com Stripe e PagSeguro, webhooks para notificação de status.",
    "Python, FastAPI, Stripe API, JWT", "https://github.com/rafaelmoura/delivery-api")
entrega(eq5, a8, "Interface de Acompanhamento em Tempo Real",
    "Front-end com mapa interativo mostrando localização do entregador em tempo real usando WebSocket e Google Maps API.",
    "JavaScript, WebSocket, Google Maps API, Bootstrap", "https://github.com/camilabarros/tracking-ui")

# Equipe Gamma (Portal de Empregos — CONCLUÍDA) — Juliana (SM) + Lucas
entrega(eq6, a6, "Sistema de Currículos Online",
    "Módulo para estudantes criarem currículos online com foto, habilidades, experiências e portfólio. Geração de PDF automática.",
    "Python, Django, ReportLab, Bootstrap", "https://github.com/julianarod/curriculo-online")
entrega(eq6, a5, "Motor de Busca de Vagas",
    "Sistema de busca de vagas com filtros por área, cidade, nível e salário. Empresas publicam vagas e candidatos se candidatam com 1 clique.",
    "Python, Django, Elasticsearch, Bootstrap", "https://github.com/lucassantos/portal-vagas")

# Equipe Zeta (Saúde) — Thiago (SM) + Isabela
entrega(eq7, a9, "Módulo de Registro de Dados de Saúde",
    "Interface para pacientes registrarem pressão arterial, glicemia, peso e medicamentos com alertas configuráveis e histórico gráfico.",
    "Python, FastAPI, SQLite, Chart.js, Bootstrap", "https://github.com/thiagonasc/saude-app")
entrega(eq7, a10, "Relatórios para Médicos e Pacientes",
    "Geração de relatórios em PDF com gráficos de evolução dos dados de saúde, prontos para levar à consulta médica.",
    "Python, Matplotlib, ReportLab, FastAPI", "")

# Equipe Theta (E-commerce — semestre anterior) — Ana (SM) + Maria
entrega(eq8, a4, "Loja Virtual Completa",
    "E-commerce com catálogo de produtos, carrinho de compras, checkout e integração com Mercado Pago. Design responsivo com identidade visual nordestina.",
    "Python, Django, Bootstrap, MercadoPago API", "https://github.com/anabferreira/artesanato-pe")
entrega(eq8, a2, "Painel do Artesão",
    "Dashboard para artesãos gerenciarem produtos, estoque, pedidos e configurarem o perfil da loja. Relatório de vendas com exportação.",
    "Python, Django, Chart.js, Bootstrap", "")

db.commit()
print("  Entregas criadas.")

# ── AVALIAÇÕES ────────────────────────────────────────────────────────────────
def av(equipe, professor, cc, ct, ca, ci, ce, cf, comentario):
    db.add(Avaliacao(equipe_id=equipe.id, professor_id=professor.id,
        conceito_conteudo=cc, conceito_tecnica=ct, conceito_apresentacao=ca,
        conceito_inovacao=ci, conceito_equipe=ce, conceito_final=cf,
        comentario=comentario))

av(eq1, prof1, "EXCELENTE","OTIMO","EXCELENTE","OTIMO","EXCELENTE","EXCELENTE",
   "Equipe Alpha demonstrou excelente domínio técnico e organização. O módulo de clientes está muito completo e o dashboard ficou visualmente impecável. Parabéns ao João pela liderança e à Maria pela qualidade do front-end.")
av(eq2, prof1, "OTIMO","OTIMO","BOM","BOM","OTIMO","OTIMO",
   "Equipe Beta entregou um sistema de estoque robusto. O módulo financeiro precisa de alguns ajustes na interface, mas a lógica está correta. Pedro demonstrou boa capacidade de gestão como Scrum Master.")
av(eq6, prof2, "EXCELENTE","EXCELENTE","EXCELENTE","EXCELENTE","EXCELENTE","EXCELENTE",
   "Projeto excepcional! O portal de empregos é altamente funcional e demonstra maturidade técnica da equipe. A integração com Elasticsearch para busca de vagas foi um diferencial impressionante. Juliana foi uma Scrum Master exemplar.")
av(eq8, prof1, "OTIMO","EXCELENTE","OTIMO","OTIMO","EXCELENTE","OTIMO",
   "E-commerce muito bem executado. A integração com o Mercado Pago funcionou perfeitamente durante a demonstração. O painel do artesão tem uma UX excelente. Ana demonstrou ótima liderança ao longo do projeto.")

db.commit()
print("  Avaliações criadas.")


db.close()

print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                   BANCO DE DEMONSTRAÇÃO — OBSERVATÓRIO PI                  ║
╠══════════════╦════════════════════════════════════════╦═════════════════════╣
║ TIPO         ║ E-MAIL                                 ║ SENHA               ║
╠══════════════╬════════════════════════════════════════╬═════════════════════╣
║ ADMIN        ║ admin@observatorio.pi                  ║ admin1234           ║
╠══════════════╬════════════════════════════════════════╬═════════════════════╣
║ COORDENADOR  ║ coordenador@observatorio.pi            ║ coord1234           ║
║ COORDENADOR  ║ carlos.neto@senac.pi                   ║ coord1234           ║
╠══════════════╬════════════════════════════════════════╬═════════════════════╣
║ PROFESSOR    ║ professor@observatorio.pi              ║ prof1234            ║
║ PROFESSOR    ║ fernanda.costa@senac.pi                ║ prof1234            ║
║ PROFESSOR    ║ marcos.albuquerque@senac.pi            ║ prof1234            ║
╠══════════════╬════════════════════════════════════════╬═════════════════════╣
║ ALUNO (SM)   ║ joao.silva@aluno.pi                    ║ aluno1234           ║
║ ALUNO        ║ maria.souza@aluno.pi                   ║ aluno1234           ║
║ ALUNO (SM)   ║ pedro.lima@aluno.pi                    ║ aluno1234           ║
║ ALUNO        ║ ana.ferreira@aluno.pi                  ║ aluno1234           ║
║ ALUNO (SM)   ║ lucas.santos@aluno.pi                  ║ aluno1234           ║
║ ALUNO        ║ juliana.rodrigues@aluno.pi             ║ aluno1234           ║
║ ALUNO (SM)   ║ rafael.moura@aluno.pi                  ║ aluno1234           ║
║ ALUNO        ║ camila.barros@aluno.pi                 ║ aluno1234           ║
║ ALUNO (SM)   ║ thiago.nascimento@aluno.pi             ║ aluno1234           ║
║ ALUNO        ║ isabela.cardoso@aluno.pi               ║ aluno1234           ║
╠══════════════╬════════════════════════════════════════╬═════════════════════╣
║ EMPRESA      ║ empresa@observatorio.pi                ║ empresa1234         ║
║ EMPRESA      ║ inovacao@empresa.pi                    ║ empresa1234         ║
║ EMPRESA      ║ softway@empresa.pi                     ║ empresa1234         ║
╚══════════════╩════════════════════════════════════════╩═════════════════════╝

Estrutura criada:
  3 turmas ativas (ADS-2A manhã, ADS-2B noite, ADS-2C tarde) + 1 semestre anterior
  6 temáticas (4 em andamento, 2 concluídas)
  8 equipes (2 finalizadas, 6 em andamento)
  16 entregas de projeto
  4 avaliações com conceitos SENAC
  10 alunos com perfis (bio, LinkedIn, GitHub, etc.)

Acesse: http://127.0.0.1:8000
""")
