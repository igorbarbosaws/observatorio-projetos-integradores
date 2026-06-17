# Documentação do Projeto — Observatório de Projetos Integradores (OPI)

---

## O que é esse sistema?

Imagina que você é professor numa escola. Seus alunos precisam fazer um projeto grande no final do ano — tipo uma feira de ciências, só que de tecnologia. Cada grupo de alunos faz um projeto diferente.

Agora imagina que você tem **dezenas de turmas**, **centenas de alunos** e precisa:

- Saber quem está fazendo qual projeto
- Ver o que cada grupo entregou
- Dar uma nota para cada grupo
- Mostrar os projetos para empresas que possam contratar esses alunos

Fazer tudo isso no papel seria um caos. O **Observatório PI** é o sistema que resolve isso — uma espécie de **painel de controle digital** para organizar todos os Projetos Integradores do curso de Análise e Desenvolvimento de Sistemas (ADS) do SENAC Pernambuco.

---

## Mapa do Projeto — onde cada coisa fica

```
observatorio-projetos-integradores/
│
├── observatorio_pi/          ← o coração do sistema
│   ├── app/                  ← o código que roda
│   ├── tests/                ← os testes automáticos
│   ├── seed.py               ← popula o banco com dados reais
│   ├── seed_demo.py          ← popula com dados de demonstração
│   ├── requirements.txt      ← lista de ingredientes do projeto
│   └── observatorio.db       ← o banco de dados (arquivo SQLite)
│
├── .venv/                    ← caixa de ferramentas isolada
├── run.py                    ← botão de ligar o servidor
├── iniciar.bat               ← atalho para ligar no Windows
├── Dockerfile                ← receita para criar um contêiner
├── render.yaml               ← instruções para publicar na internet
└── .gitignore                ← lista do que o Git deve ignorar
```

---

## Os Tipos de Usuário — os "crachás do sistema"

O sistema tem cinco perfis de acesso diferentes. Pensa como um clube com crachás de cores diferentes:

| Crachá | Quem é | O que pode fazer |
|---|---|---|
| **ADMIN** | O dono do sistema | Tudo — criar usuários, ver tudo, avaliar equipes |
| **COORDENADOR** | Chefe do curso | Criar turmas e temáticas, ver relatórios |
| **PROFESSOR** | Orientador dos projetos | Ver suas temáticas, avaliar equipes |
| **ALUNO** | Estudante | Ver suas equipes, subir entregas |
| **EMPRESA** | Recrutador externo | Navegar no portfólio, ver perfis de alunos |

---

## A Hierarquia dos Dados — caixas dentro de caixas

Os dados do sistema se organizam em camadas, como bonecas russas:

```
TURMA  (ex: "ADS 2025-1")
  └── TEMÁTICA  (ex: "App de delivery para bairros")
        └── EQUIPE  (ex: "Equipe Alpha")
              ├── MEMBROS  (alunos participantes)
              ├── ENTREGAS  (GitHub, slides, documentos...)
              └── AVALIAÇÃO  (notas do professor)
```

É como uma **escola → sala → grupo de trabalho → trabalho entregue → nota**.

---

## A pasta `app/` — onde o código mora

### `main.py` — o maestro

É o arquivo mais importante do projeto. Pensa nele como o **porteiro de um prédio grande**: toda vez que alguém acessa uma página (`/dashboard`, `/turmas`, `/equipes/5`...), é o `main.py` que decide o que mostrar.

Ele contém cerca de 150 funções chamadas de **rotas**. Exemplos:

- `GET /dashboard` → exibe o painel inicial personalizado por tipo de usuário
- `GET /turmas?ano=2025` → lista turmas filtradas pelo ano
- `GET /tematicas?filtro_professor=7` → lista temáticas de um professor específico
- `POST /equipes/3/avaliar` → salva a avaliação de uma equipe no banco
- `GET /relatorios/professor/12` → exibe o relatório de orientação de um professor
- `POST /meu-perfil/foto` → faz upload e salva a foto de perfil

### `database.py` — a ponte para o banco de dados

É como um **tradutor**: faz o Python conseguir conversar com o arquivo `.db` onde ficam todos os dados. Cria a conexão com o SQLite e disponibiliza uma "sessão" para cada requisição entrar e sair sem conflito.

### A pasta `models/` — os formulários em branco

Antes de guardar qualquer coisa num banco de dados, você precisa definir a forma do dado. Os models são como **fichas cadastrais vazias** que o sistema preenche com informação real.

**`user.py`** — a ficha do usuário:

| Campo | O que guarda |
|---|---|
| `id` | Número único de identificação |
| `nome` | Nome completo |
| `email` | Endereço de e-mail (único no sistema) |
| `senha_hash` | Senha transformada em código irreversível |
| `tipo` | ALUNO, PROFESSOR, COORDENADOR, ADMIN ou EMPRESA |
| `ativo` | Se a conta está ativa ou bloqueada |
| `bio` | Apresentação pessoal |
| `linkedin` / `github` / `portfolio_url` | Links profissionais |
| `area_interesse` | Áreas de interesse separadas por vírgula |
| `cidade` | Localização |
| `telefone` | Contato (visível para empresas) |
| `foto_perfil` | Caminho da foto de perfil salva no servidor |

**`project.py`** — contém cinco fichas:

- **Turma**: nome, semestre (ex: "2025-1"), descrição, status ativo/inativo
- **Temática**: título, descrição, turma vinculada, professor responsável, status (Aberta / Em andamento / Concluída)
- **Equipe**: nome, temática vinculada, Scrum Master, status (Em andamento / Finalizado)
- **EntregaProjeto**: título, descrição, tecnologias usadas, links para GitHub, slides, documento, Drive
- **Avaliacao**: seis critérios avaliados com conceito SENAC (Insuficiente → Regular → Bom → Ótimo → Excelente)
- **AvaliacaoAluno**: avaliação individual de cada membro da equipe

### A pasta `core/` — os bastidores de segurança

**`security.py`** — o sistema de crachás digitais. Quando você faz login:

1. O sistema verifica sua senha usando **bcrypt** (como um cofre com combinação)
2. Cria um **token JWT** — um crachá digital criptografado com prazo de validade
3. Guarda esse crachá no navegador como cookie

Em cada página protegida, o sistema lê o crachá e sabe quem você é, sem precisar pedir senha novamente.

**`config.py`** — guarda configurações globais como a chave secreta usada para assinar os tokens.

### A pasta `routers/` — delegação de tarefas

O `main.py` é grande, mas algumas responsabilidades são delegadas para módulos específicos:

- **`auth_router.py`** — rotas de autenticação via API
- **`project_router.py`** — rotas de projetos via API
- **`user_router.py`** — rotas de perfil e upload de foto

### A pasta `schemas/` — validação de dados

São como **filtros de segurança**: definem exatamente que formato os dados precisam ter quando chegam pela API. Se alguém tentar enviar um e-mail sem `@`, o schema rejeita antes mesmo de chegar ao banco de dados.

### A pasta `templates/` — as páginas que o usuário vê

São arquivos HTML com "buracos" que o Python preenche com dados reais. É como um **molde de bolo**: o molde é sempre o mesmo (HTML), mas o recheio muda a cada acesso.

A estrutura de herança funciona assim:

```
base.html              ← estrutura raiz (HTML, CSS global, Bootstrap)
  └── base_auth.html  ← adiciona navbar, sidebar, FAB (páginas logadas)
        ├── dashboard.html
        ├── turmas.html
        ├── equipe_detalhe.html
        └── ... (todas as demais páginas)
```

**Tabela completa de templates:**

| Template | Descrição |
|---|---|
| `base.html` | Estrutura HTML raiz, CSS global, Bootstrap |
| `base_auth.html` | Layout para usuários logados: navbar, sidebar retrátil, FAB |
| `login.html` | Tela de entrada com toggle de senha |
| `dashboard.html` | Painel inicial com métricas e equipes recentes |
| `turmas.html` | Lista de turmas com filtro por ano |
| `turma_form.html` | Formulário para criar/editar turma |
| `tematicas.html` | Grid de cards de projetos com filtros |
| `tematica_detalhe.html` | Detalhes de um projeto + gestão de equipes |
| `tematica_form.html` | Formulário para criar/editar temática |
| `equipe_detalhe.html` | Membros, entregas e formulário de avaliação |
| `entrega_form.html` | Formulário para subir uma entrega |
| `portfolio.html` | Galeria pública de projetos com busca e filtros |
| `relatorios.html` | Gráficos e estatísticas gerais |
| `relatorio_professor.html` | Relatório detalhado de um professor |
| `perfil_aluno.html` | Perfil público do aluno com projetos |
| `perfil_professor.html` | Perfil do professor com temáticas |
| `perfil_coordenador.html` | Perfil do coordenador/admin |
| `perfil_empresa.html` | Perfil da empresa recrutadora |
| `usuarios.html` | Listagem de usuários (só ADMIN) |
| `usuario_form.html` | Formulário para criar/editar usuário |

### A pasta `static/avatars/` — as fotos de perfil

Quando um usuário faz upload de foto, ela é salva aqui como `avatar_42.jpg` (onde 42 é o ID do usuário). O servidor serve esses arquivos diretamente pelo caminho `/static/avatars/`.

---

## O Banco de Dados — `observatorio.db`

É um **arquivo único** no formato SQLite. Pensa nele como uma planilha do Excel bem organizada, mas muito mais rápida e com regras de consistência. Contém as seguintes tabelas:

| Tabela | O que guarda |
|---|---|
| `users` | Todos os usuários do sistema |
| `turmas` | As turmas por semestre letivo |
| `tematicas` | Os projetos propostos |
| `equipes` | Os grupos de alunos |
| `equipe_membros` | Relação de quem está em qual equipe |
| `entregas_projeto` | Links e descrições das entregas |
| `avaliacoes` | Notas coletivas das equipes (6 critérios) |
| `avaliacoes_aluno` | Notas individuais dos membros |

---

## Os Testes Automáticos — `tests/test_properties.py`

Pensa nos testes como um **inspetor de qualidade** que verifica o sistema automaticamente, sem precisar abrir o navegador.

### Testes Unitários
Verificam casos específicos e previsíveis:
- Se não há avaliação prévia, o padrão exibido deve ser "Bom"
- Se o professor de uma temática é nulo, o dashboard exibe "—"
- Após salvar uma avaliação, recarregar a página exibe os mesmos valores

### Property-based Tests com Hypothesis
São mais poderosos. Em vez de testar um caso, testam **centenas de casos gerados aleatoriamente** e verificam se a regra sempre vale. O projeto tem 11 propriedades:

| Propriedade | O que garante |
|---|---|
| 1 | Filtro de turmas por ano retorna só turmas do ano correto |
| 2 | Anos extraídos dos semestres são únicos e ordenados do mais recente ao mais antigo |
| 3 | O ano filtrado é sempre refletido corretamente no contexto do template |
| 4 | Filtro de temáticas por professor retorna só temáticas daquele professor |
| 5 | Aplicar filtro de turma e professor juntos retorna a interseção correta |
| 6 | O botão de conceito correto fica selecionado na avaliação |
| 7 | Salvar e recarregar a avaliação sempre mostra os mesmos valores salvos |
| 8 | Totais de equipes e avaliações no relatório são aritmeticamente corretos |
| 10 | A URL do perfil corresponde corretamente ao tipo do usuário |
| 11 | O botão FAB exibe exatamente as ações definidas para cada tipo de usuário |

---

## As Dependências — `requirements.txt`

Cada biblioteca é uma ferramenta especializada. Versões fixadas para garantir que o sistema funciona igual em qualquer computador:

| Biblioteca | Versão | Para que serve |
|---|---|---|
| **fastapi** | 0.115.12 | O framework principal — recebe e responde às requisições HTTP |
| **uvicorn** | 0.34.2 | Servidor web ultra-rápido que executa o FastAPI |
| **gunicorn** | 23.0.0 | Gerencia múltiplos processos em produção (servidor de produção) |
| **sqlalchemy** | 2.0.49 | ORM — traduz objetos Python para SQL e o banco de dados para Python |
| **passlib[bcrypt]** | 1.7.4 | Biblioteca de segurança para hash de senhas |
| **bcrypt** | 4.0.1 | Algoritmo de hash irreversível para proteger senhas |
| **python-jose** | 3.3.0 | Criação e validação de tokens JWT para autenticação |
| **python-multipart** | 0.0.20 | Suporte ao recebimento de arquivos via formulários (upload de fotos) |
| **jinja2** | 3.1.6 | Motor de templates — preenche o HTML com dados dinâmicos |
| **hypothesis** | 6.131.15 | Geração automática de centenas de casos de teste aleatórios |
| **pytest** | 8.3.5 | Framework que organiza e executa os testes automáticos |

---

## Os Arquivos de Configuração e Deploy

### `run.py` — o botão de ligar
Inicia o servidor de desenvolvimento na porta 8000:
```
http://127.0.0.1:8000
```

### `iniciar.bat` — atalho para Windows
Com um duplo-clique, este script:
1. Verifica se o ambiente virtual `.venv` existe; se não, cria
2. Instala todas as dependências do `requirements.txt`
3. Liga o servidor automaticamente

### `Dockerfile` — a receita do contêiner
Empacota o sistema numa "caixa selada" que contém Python, todas as bibliotecas e o código. Essa caixa roda igual em qualquer computador ou servidor na nuvem.

### `render.yaml` — publicação automática
Instruções para o serviço **Render.com** publicar o sistema na internet automaticamente toda vez que o código é atualizado no GitHub.

### `seed.py` e `seed_demo.py` — dados iniciais
Scripts que populam o banco com dados de exemplo:
- `seed.py` — dados reais para uso inicial em produção
- `seed_demo.py` — dados fictícios ricos para demonstração (turmas, alunos, projetos, avaliações já preenchidas)

### `.venv/` — caixa de ferramentas isolada
Contém todas as bibliotecas instaladas localmente para este projeto, sem interferir com outros projetos Python do computador.

---

## O Fluxo Completo de uma Requisição

Para entender tudo junto, veja o que acontece quando um professor acessa a página de uma equipe:

```
1. O professor digita no navegador: /equipes/5

2. Uvicorn recebe a requisição HTTP GET

3. FastAPI (main.py) encontra a função: def detalhe_equipe(equipe_id=5)

4. get_usuario_logado() lê o cookie JWT e identifica quem está logado

5. Verifica permissão: professor só acessa equipes das suas temáticas

6. SQLAlchemy consulta o banco:
   - Busca a equipe id=5
   - Carrega membros, entregas, avaliações

7. Jinja2 preenche equipe_detalhe.html com esses dados

8. HTML completo com CSS (Bootstrap) e ícones volta para o navegador

9. O navegador exibe a página finalizada
```

---

## Interface do Sistema — componentes visuais

### Navbar Superior
Barra azul fixa no topo com:
- Botão hamburger para recolher/expandir a sidebar
- Logo e nome do sistema (link para o dashboard)
- Avatar, nome, e-mail e badge de tipo do usuário logado (clicável, leva ao perfil)
- Botão de sair

### Sidebar Lateral Retrátil
Menu de navegação que começa recolhido e expande ao clicar:

| Ícone | Página |
|---|---|
| Velocímetro | Dashboard |
| Diploma | Turmas (só ADMIN/COORD) |
| Lâmpada | Temáticas |
| Coleção | Portfólio |
| Pessoas | Usuários (só ADMIN) |
| Gráfico | Relatórios (só ADMIN/COORD) |

O estado (expandido/recolhido) é salvo no `localStorage` do navegador.

### FAB — Botão de Ações Rápidas
Botão laranja fixo no canto inferior direito com ícone de raio (⚡). Ao clicar, abre um menu com atalhos contextuais por tipo de usuário:

- **ALUNO**: Temáticas, Portfólio, Meu perfil
- **PROFESSOR**: Temáticas, Meu perfil, Portfólio
- **COORDENADOR**: Nova turma, Nova temática, Relatórios
- **ADMIN**: Novo usuário, Nova turma, Nova temática, Relatórios
- **EMPRESA**: Portfólio

---

## Em Resumo

O **Observatório PI** é uma aplicação web completa feita em Python com FastAPI, que permite ao SENAC Pernambuco gerenciar todo o ciclo de vida dos Projetos Integradores:

1. **Organização** — criação de turmas e temáticas pelos coordenadores
2. **Participação** — alunos se organizam em equipes e subem suas entregas
3. **Avaliação** — professores avaliam equipes e alunos individualmente com o conceito SENAC
4. **Visibilidade** — portfólio público para empresas recrutadoras descobrirem talentos
5. **Gestão** — relatórios e métricas para coordenadores acompanharem tudo

---

*Documentação gerada em junho de 2026.*
