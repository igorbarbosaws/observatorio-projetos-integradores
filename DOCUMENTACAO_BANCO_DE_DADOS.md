# Documentação do Banco de Dados
## Observatório de Projetos Integradores — SENAC ADS

> Projeto desenvolvido pelos alunos: **Danilo Henrique**, **Edson Aguiar**, **Evencio Neto**, **Estevão Enoque**, **Igor Barbosa** e **Paulo Coutinho**

---

## Tecnologia utilizada

O sistema usa **SQLite** como banco de dados, gerenciado pela biblioteca **SQLAlchemy** (versão 2.0). O SQLite é um banco que fica armazenado em um único arquivo no próprio computador, sem precisar instalar nenhum servidor separado — ideal para projetos acadêmicos e desenvolvimento local.

---

## Onde o banco de dados fica

O arquivo do banco é criado automaticamente dentro da pasta do projeto, no caminho:

```
observatorio_pi/observatorio.db
```

Isso é definido no arquivo `app/database.py`:

```python
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_URL = f"sqlite:///{os.path.join(_BASE_DIR, 'observatorio.db')}"
```

O código calcula o caminho de forma dinâmica, então não importa onde o projeto esteja instalado — ele sempre vai encontrar o lugar certo para criar o arquivo.

---

## Como o banco é criado

O banco **não precisa ser criado manualmente**. Quando a aplicação sobe pela primeira vez, uma única linha no `main.py` resolve tudo:

```python
Base.metadata.create_all(bind=engine)
```

Essa instrução percorre todos os modelos cadastrados e cria as tabelas que ainda não existem. Se o arquivo `observatorio.db` não existir, ele é criado do zero nesse momento.

---

## Como a conexão funciona

Três elementos em `database.py` cuidam disso:

- **`engine`** — é a "ponte" entre o Python e o arquivo SQLite. O parâmetro `check_same_thread=False` é necessário porque o FastAPI pode atender várias requisições ao mesmo tempo.
- **`SessionLocal`** — é a fábrica de sessões. Cada sessão representa uma conversa com o banco (consulta, inserção, atualização, etc.).
- **`get_db()`** — é uma função auxiliar que abre uma sessão, entrega ela para a rota que precisar, e fecha no final, independentemente de ter dado erro ou não.

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Nas rotas do sistema, sempre que alguma função precisa acessar o banco, ela declara `db: Session = Depends(get_db)` e o FastAPI cuida de passar a sessão correta.

---

## As tabelas do banco

O sistema tem **8 tabelas** no total. Veja cada uma:

---

### `users` — Usuários do sistema

Armazena todos os usuários, independentemente do tipo.

| Campo | Tipo | O que guarda |
|---|---|---|
| `id` | Inteiro (PK) | Identificador único |
| `nome` | Texto | Nome completo |
| `email` | Texto (único) | E-mail de acesso |
| `senha_hash` | Texto | Senha criptografada com bcrypt |
| `tipo` | Texto | ALUNO, PROFESSOR, COORDENADOR, EMPRESA ou ADMIN |
| `ativo` | Booleano | Se o usuário pode fazer login |
| `bio` | Texto | Apresentação pessoal |
| `linkedin` | Texto | URL do perfil no LinkedIn |
| `github` | Texto | URL do perfil no GitHub |
| `portfolio_url` | Texto | Link para portfólio pessoal |
| `area_interesse` | Texto | Exemplo: "Backend, IA, Mobile" |
| `cidade` | Texto | Localização do usuário |
| `telefone` | Texto | Contato (visível para empresas) |
| `foto_perfil` | Texto | Caminho relativo da foto em `static/avatars/` |

A senha nunca é guardada em texto puro. O sistema usa a biblioteca **passlib com bcrypt** para gerar um hash antes de salvar.

---

### `turmas` — Turmas do curso

Agrupa os projetos por turma e semestre.

| Campo | Tipo | O que guarda |
|---|---|---|
| `id` | Inteiro (PK) | Identificador único |
| `nome` | Texto | Nome da turma (ex: "ADS-T01") |
| `semestre` | Texto | Semestre (ex: "2025-1") |
| `descricao` | Texto | Descrição opcional |
| `ativa` | Booleano | Se a turma está ativa |
| `criado_em` | Data/hora | Quando foi criada |

---

### `tematicas` — Temáticas dos projetos

Cada turma tem várias temáticas. Uma temática é o tema central que as equipes vão desenvolver.

| Campo | Tipo | O que guarda |
|---|---|---|
| `id` | Inteiro (PK) | Identificador único |
| `titulo` | Texto | Nome da temática |
| `descricao` | Texto | Detalhamento do tema |
| `turma_id` | Inteiro (FK) | Referência à turma |
| `professor_id` | Inteiro (FK) | Professor responsável |
| `status` | Texto | ABERTA, EM_ANDAMENTO ou CONCLUIDA |
| `criado_em` | Data/hora | Data de criação |
| `atualizado_em` | Data/hora | Última atualização |

---

### `equipes` — Equipes de trabalho

Cada temática pode ter várias equipes. É aqui que os alunos são agrupados.

| Campo | Tipo | O que guarda |
|---|---|---|
| `id` | Inteiro (PK) | Identificador único |
| `nome` | Texto | Nome da equipe |
| `tematica_id` | Inteiro (FK) | Referência à temática |
| `scrum_master_id` | Inteiro (FK) | Aluno líder da equipe |
| `status` | Texto | EM_ANDAMENTO ou FINALIZADO |
| `criado_em` | Data/hora | Data de criação |

---

### `equipe_membros` — Membros das equipes

Tabela de ligação entre usuários e equipes. Cada linha representa um aluno em uma equipe.

| Campo | Tipo | O que guarda |
|---|---|---|
| `id` | Inteiro (PK) | Identificador único |
| `equipe_id` | Inteiro (FK) | Referência à equipe |
| `aluno_id` | Inteiro (FK) | Referência ao aluno |

---

### `entregas_projeto` — Entregas dos alunos

Guarda os links e informações de cada entrega submetida por uma equipe.

| Campo | Tipo | O que guarda |
|---|---|---|
| `id` | Inteiro (PK) | Identificador único |
| `equipe_id` | Inteiro (FK) | Equipe que fez a entrega |
| `autor_id` | Inteiro (FK) | Aluno que submeteu |
| `titulo` | Texto | Título do trabalho |
| `descricao` | Texto | Descrição do projeto |
| `tecnologias` | Texto | Stacks utilizadas (separadas por vírgula) |
| `link_repositorio` | Texto | Link do GitHub |
| `link_apresentacao` | Texto | Link do Canva ou slides |
| `link_documento` | Texto | Link de documento (Word, Google Docs) |
| `link_drive` | Texto | Link para pasta no Drive |
| `versao` | Inteiro | Número da versão (incrementa a cada edição) |
| `finalizado` | Booleano | Se a entrega foi marcada como concluída |
| `criado_em` | Data/hora | Data de criação |
| `atualizado_em` | Data/hora | Última atualização |

---

### `avaliacoes` — Avaliações coletivas

Registra a avaliação do professor sobre o desempenho geral da equipe.

| Campo | Tipo | O que guarda |
|---|---|---|
| `id` | Inteiro (PK) | Identificador único |
| `equipe_id` | Inteiro (FK) | Equipe avaliada |
| `professor_id` | Inteiro (FK) | Professor que avaliou |
| `conceito_conteudo` | Texto | Conceito do conteúdo |
| `conceito_tecnica` | Texto | Conceito técnico |
| `conceito_apresentacao` | Texto | Conceito da apresentação |
| `conceito_inovacao` | Texto | Conceito de inovação |
| `conceito_equipe` | Texto | Conceito do trabalho em equipe |
| `conceito_final` | Texto | Conceito geral da equipe |
| `comentario` | Texto | Observações do professor |
| `data_avaliacao` | Data/hora | Quando foi avaliado |

Os conceitos possíveis são: `INSUFICIENTE`, `REGULAR`, `BOM`, `OTIMO` e `EXCELENTE`.

---

### `avaliacoes_aluno` — Avaliações individuais

Permite que o professor avalie cada aluno da equipe separadamente, além da avaliação coletiva.

| Campo | Tipo | O que guarda |
|---|---|---|
| `id` | Inteiro (PK) | Identificador único |
| `equipe_id` | Inteiro (FK) | Equipe do aluno |
| `aluno_id` | Inteiro (FK) | Aluno avaliado |
| `professor_id` | Inteiro (FK) | Professor que avaliou |
| `conceito` | Texto | Conceito individual |
| `comentario` | Texto | Observações individuais |
| `data_avaliacao` | Data/hora | Quando foi avaliado |

---

## Como as tabelas se relacionam

O diagrama abaixo mostra a hierarquia entre os dados:

```
users
  │
  ├── (professor) ──► tematicas ──► turmas
  │                       │
  │                       └──► equipes
  │                               │
  │                    ┌──────────┤
  │                    │          │
  │               equipe_membros  │
  │               (aluno_id)      │
  │                               ├──► entregas_projeto
  │                               │       (autor_id → users)
  │                               │
  │                               ├──► avaliacoes
  │                               │       (professor_id → users)
  │                               │
  │                               └──► avaliacoes_aluno
  │                                       (aluno_id → users)
  │                                       (professor_id → users)
  │
  └── (scrum_master) ──► equipes.scrum_master_id
```

Em resumo: uma **Turma** tem várias **Temáticas**, cada **Temática** tem várias **Equipes**, cada **Equipe** tem vários **Membros** (via `equipe_membros`), faz **Entregas** e recebe **Avaliações**.

---

## Deleção em cascata

O banco foi configurado para apagar registros dependentes automaticamente quando um pai é removido. Isso evita dados "soltos" sem referência:

- Deletar uma **Turma** → apaga todas as suas **Temáticas**
- Deletar uma **Temática** → apaga todas as suas **Equipes**
- Deletar uma **Equipe** → apaga seus **Membros**, **Entregas** e **Avaliações**

---

## Segurança das senhas

Nenhuma senha é salva em texto aberto. Quando um usuário é criado ou tem a senha alterada, o sistema passa a senha pela função `hash_senha()`, que usa o algoritmo **bcrypt** para gerar um hash irreversível. Na hora do login, o sistema compara o que foi digitado com esse hash usando `verificar_senha()`.

---

## Autenticação via JWT

Após o login, o sistema gera um token **JWT (JSON Web Token)** que fica guardado em um cookie `httponly` no navegador do usuário. Esse token carrega o e-mail, o tipo e o ID do usuário. A cada requisição, o servidor decodifica o token para saber quem está acessando, sem precisar consultar o banco a cada clique.

As configurações do token ficam em `app/core/config.py`:

- Algoritmo: **HS256**
- Expiração: **60 minutos**
- Chave secreta: definida pela variável de ambiente `SECRET_KEY`

---

## Dependências relacionadas ao banco

Do arquivo `requirements.txt`:

| Biblioteca | Versão | Função |
|---|---|---|
| `sqlalchemy` | 2.0.49 | ORM e conexão com o SQLite |
| `passlib[bcrypt]` | 1.7.4 | Hash de senhas |
| `bcrypt` | 4.0.1 | Algoritmo de criptografia |
| `python-jose[cryptography]` | 3.3.0 | Geração e validação de tokens JWT |

---

## Resumo rápido

| Item | Detalhe |
|---|---|
| Banco de dados | SQLite |
| Arquivo gerado | `observatorio_pi/observatorio.db` |
| ORM | SQLAlchemy 2.0 |
| Criação das tabelas | Automática ao iniciar a aplicação |
| Número de tabelas | 8 |
| Criptografia de senha | bcrypt |
| Autenticação | JWT (cookie httponly) |
