<<<<<<< HEAD
# Observatório de Projetos Integradores

Sistema web para gerenciamento de Projetos Integradores do curso de ADS.
Construído com **FastAPI + SQLAlchemy + Jinja2 + Bootstrap 5**.

---

## Rodando localmente (Windows)

**Pré-requisito:** Python 3.11+ instalado.

```bash
# 1. Crie o ambiente virtual (só na primeira vez)
python -m venv .venv

# 2. Instale as dependências
.venv\Scripts\pip install -r observatorio_pi\requirements.txt

# 3. Inicie o servidor
.venv\Scripts\python run.py
```

Ou simplesmente dê duplo clique em **`iniciar.bat`**.

Acesse: http://127.0.0.1:8000  
Login padrão: `admin@observatorio.pi` / `admin1234`

---

## Deploy gratuito no Render

### Por que Render?
- Deploy direto do GitHub (sem CLI)
- Plano gratuito com HTTPS automático
- Suporte nativo a Python/FastAPI
- `render.yaml` já configurado neste repositório

### Passo a passo

#### 1. Suba o projeto no GitHub

```bash
git init
git add .
git commit -m "primeiro commit"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/observatorio-pi.git
git push -u origin main
```

#### 2. Crie uma conta no Render

Acesse [render.com](https://render.com) e crie uma conta gratuita (pode usar o GitHub para login).

#### 3. Crie o serviço

1. No dashboard do Render, clique em **"New +"** → **"Web Service"**
2. Conecte seu repositório GitHub
3. O Render detectará o `render.yaml` automaticamente e preencherá as configurações
4. Clique em **"Create Web Service"**

O deploy leva cerca de 2–3 minutos. Ao final, você receberá uma URL pública como:
`https://observatorio-pi.onrender.com`

#### 4. Variáveis de ambiente (opcional)

No painel do Render → seu serviço → **Environment**, você pode alterar:

| Variável         | Descrição                        | Padrão                    |
|------------------|----------------------------------|---------------------------|
| `SECRET_KEY`     | Chave JWT (gerada automaticamente) | —                       |
| `ADMIN_EMAIL`    | E-mail do admin inicial          | `admin@observatorio.pi`   |
| `ADMIN_PASSWORD` | Senha do admin inicial           | `admin1234`               |

> **Importante:** Altere `ADMIN_PASSWORD` antes de usar em produção.

---

## ⚠️ Limitações do plano gratuito do Render

| Limitação | Detalhe |
|-----------|---------|
| **Sleep após inatividade** | O serviço "dorme" após 15 min sem requisições. A primeira requisição após o sleep demora ~30s para acordar. |
| **Banco de dados efêmero** | O SQLite é armazenado no filesystem do container. **Os dados são apagados a cada redeploy.** Para persistência, migre para PostgreSQL (Render oferece plano gratuito de banco). |
| **750h/mês** | Suficiente para um serviço rodando continuamente. |

---

## Estrutura do projeto

```
.
├── render.yaml              # Configuração de deploy no Render
├── Dockerfile               # Para deploy via Docker (alternativa)
├── run.py                   # Ponto de entrada local (Windows)
├── iniciar.bat              # Atalho para rodar no Windows
└── observatorio_pi/
    ├── requirements.txt
    ├── start.sh             # Script de inicialização em produção
    └── app/
        ├── main.py          # Rotas web (Jinja2)
        ├── database.py      # Configuração SQLAlchemy
        ├── models/          # User, Project
        ├── schemas/         # Pydantic schemas
        ├── routers/         # API REST (auth, users, projects)
        ├── core/            # Config, segurança JWT
        └── templates/       # HTML (Bootstrap 5)
```
=======
# Observatório de Projetos Integradores

Sistema web para gerenciamento de Projetos Integradores do curso de ADS.
Construído com **FastAPI + SQLAlchemy + Jinja2 + Bootstrap 5**.

---

## Rodando localmente (Windows)

**Pré-requisito:** Python 3.11+ instalado.

```bash
# 1. Crie o ambiente virtual (só na primeira vez)
python -m venv .venv

# 2. Instale as dependências
.venv\Scripts\pip install -r observatorio_pi\requirements.txt

# 3. Inicie o servidor
.venv\Scripts\python run.py
```

Ou simplesmente dê duplo clique em **`iniciar.bat`**.

Acesse: http://127.0.0.1:8000  
Login padrão: `admin@observatorio.pi` / `admin1234`

---

## Deploy gratuito no Render

### Por que Render?
- Deploy direto do GitHub (sem CLI)
- Plano gratuito com HTTPS automático
- Suporte nativo a Python/FastAPI
- `render.yaml` já configurado neste repositório

### Passo a passo

#### 1. Suba o projeto no GitHub

```bash
git init
git add .
git commit -m "primeiro commit"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/observatorio-pi.git
git push -u origin main
```

#### 2. Crie uma conta no Render

Acesse [render.com](https://render.com) e crie uma conta gratuita (pode usar o GitHub para login).

#### 3. Crie o serviço

1. No dashboard do Render, clique em **"New +"** → **"Web Service"**
2. Conecte seu repositório GitHub
3. O Render detectará o `render.yaml` automaticamente e preencherá as configurações
4. Clique em **"Create Web Service"**

O deploy leva cerca de 2–3 minutos. Ao final, você receberá uma URL pública como:
`https://observatorio-pi.onrender.com`

#### 4. Variáveis de ambiente (opcional)

No painel do Render → seu serviço → **Environment**, você pode alterar:

| Variável         | Descrição                        | Padrão                    |
|------------------|----------------------------------|---------------------------|
| `SECRET_KEY`     | Chave JWT (gerada automaticamente) | —                       |
| `ADMIN_EMAIL`    | E-mail do admin inicial          | `admin@observatorio.pi`   |
| `ADMIN_PASSWORD` | Senha do admin inicial           | `admin1234`               |

> **Importante:** Altere `ADMIN_PASSWORD` antes de usar em produção.

---

## ⚠️ Limitações do plano gratuito do Render

| Limitação | Detalhe |
|-----------|---------|
| **Sleep após inatividade** | O serviço "dorme" após 15 min sem requisições. A primeira requisição após o sleep demora ~30s para acordar. |
| **Banco de dados efêmero** | O SQLite é armazenado no filesystem do container. **Os dados são apagados a cada redeploy.** Para persistência, migre para PostgreSQL (Render oferece plano gratuito de banco). |
| **750h/mês** | Suficiente para um serviço rodando continuamente. |

---

## Estrutura do projeto

```
.
├── render.yaml              # Configuração de deploy no Render
├── Dockerfile               # Para deploy via Docker (alternativa)
├── run.py                   # Ponto de entrada local (Windows)
├── iniciar.bat              # Atalho para rodar no Windows
└── observatorio_pi/
    ├── requirements.txt
    ├── start.sh             # Script de inicialização em produção
    └── app/
        ├── main.py          # Rotas web (Jinja2)
        ├── database.py      # Configuração SQLAlchemy
        ├── models/          # User, Project
        ├── schemas/         # Pydantic schemas
        ├── routers/         # API REST (auth, users, projects)
        ├── core/            # Config, segurança JWT
        └── templates/       # HTML (Bootstrap 5)
```
>>>>>>> 0879f9fd2a49c43f324990846de2e8d558d87942
