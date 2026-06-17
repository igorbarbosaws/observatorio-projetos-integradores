# 🎓 Observatório de Projetos Integradores

> Uma plataforma web centralizada para submissão, avaliação e consulta de projetos acadêmicos do curso de Análise e Desenvolvimento de Sistemas (ADS) do SENAC. Desenvolvida como Projeto Integrador do **2º Módulo**.

[![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-yellow)](https://github.com/igorbarbosaws/observatorio-projetos-integradores)
[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Senac](https://img.shields.io/badge/Institution-Senac%20College-orange)](https://www.senac.br/)
[![LGPD](https://img.shields.io/badge/Conformidade-LGPD%20Ready-blueviolet)](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm)

---

## 🇧🇷 Português

### 📋 Visão Geral do Projeto

O **Observatório de Projetos Integradores** é uma solução para o problema da descentralização no envio de Projetos Integradores (PIs). A dependência de e-mails e plataformas genéricas causa perda de documentos, dificuldade no controle de versões e alto tempo gasto na organização manual por professores e coordenação. Este sistema centraliza todo esse fluxo em um ambiente seguro e organizado.

### Funcionalidades Principais

- **Submissão Centralizada:** Alunos submetem seus projetos diretamente na plataforma, com links para repositório, apresentação, documentos e Drive.
- **Avaliação por Rubricas:** Professores avaliam equipes e alunos individualmente usando conceitos pré-definidos (Insuficiente, Regular, Bom, Ótimo, Excelente).
- **Vitrine de Talentos:** Empresas parceiras acessam um portfólio digital com filtros por turma, semestre e tecnologias utilizadas.
- **Gestão Completa:** Coordenadores gerenciam turmas, temáticas, equipes e usuários em um único painel.

---

### 🔒 Conformidade com a LGPD (Lei Geral de Proteção de Dados)

Por tratar dados de alunos — incluindo informações de contato, histórico acadêmico e perfil profissional — a privacidade foi tratada como requisito desde o início do projeto, em conformidade com a Lei Federal nº 13.709/2018 (LGPD).

#### Padrões de Privacidade Implementados

- **Base Legal para Tratamento (Art. 7º e 11):** Os dados coletados, como e-mail, telefone e informações de perfil, são usados exclusivamente para as finalidades da plataforma, mediante cadastro explícito pelo administrador responsável.
- **Minimização de Dados:** Apenas as informações necessárias para o funcionamento do sistema são armazenadas. Dados de perfil como LinkedIn, GitHub e telefone são opcionais.
- **Segurança (Art. 46):** Todas as senhas são armazenadas como hash usando o algoritmo **bcrypt**, impedindo a leitura em caso de acesso não autorizado ao banco de dados.
- **Controle de Acesso:** O sistema adota um modelo de permissões por perfil, garantindo que cada usuário acesse apenas o que lhe é pertinente.
- **Direitos do Usuário (Art. 18) — Planejado:** Está previsto para versões futuras um painel de privacidade onde o usuário poderá:
  - Acessar todos os seus dados cadastrados (direito de acesso).
  - Corrigir informações incompletas ou incorretas.
  - Revogar o consentimento e solicitar a exclusão permanente de sua conta e histórico (*Direito ao Esquecimento*).

---

### 🛠️ Stack Tecnológica

- **Backend:** Python 3.11, FastAPI, SQLAlchemy 2.0
- **Frontend:** HTML5, CSS3, Jinja2 (templates server-side)
- **Banco de Dados:** SQLite (arquivo `observatorio.db`)
- **Autenticação:** JWT (python-jose) + bcrypt para hash de senhas
- **Servidor:** Uvicorn / Gunicorn
- **Versionamento:** Git e GitHub
- **Gestão de Projeto:** Trello

---

### ⚙️ Como Executar (Desenvolvimento Local)

#### 1. Pré-requisitos

- [Git](https://git-scm.com)
- [Python 3.11+](https://www.python.org/) instalado

#### 2. Configuração

Clone o repositório e entre na pasta:

```bash
git clone https://github.com/EdsonAguiar888/Observatorio_de_Projetos_Integradores.git
cd observatorio-projetos-integradores
```

Crie e ative o ambiente virtual:

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate
```

Instale as dependências:

```bash
pip install -r observatorio_pi/requirements.txt
```

#### 3. Execução

```bash
python run.py
```

No Windows, você também pode dar duplo clique no arquivo `iniciar.bat`.

Acesse no navegador: **http://127.0.0.1:8000**

**Login padrão:**

```
E-mail: admin@observatorio.pi
Senha:  admin1234
```

> ⚠️ Altere a senha do admin imediatamente após o primeiro acesso.

---

### 💼 Regras de Negócio e Controle de Acesso

O sistema adota um modelo de permissões por perfil. Cada tipo de usuário tem acesso restrito às suas responsabilidades:

| Perfil | Permissões |
|---|---|
| **ADMIN** | Cria e gerencia usuários e tem acesso completo ao sistema. |
| **Coordenador** | Gerencia/Cria turmas e temáticas. Acessa relatórios completos. |
| **Professor** | Cria equipes nas suas temáticas, adiciona alunos, define Scrum Master e registra avaliações. |
| **Aluno** | Submete e edita suas próprias entregas. O Scrum Master finaliza o projeto e exclui documentação se necessário. |
| **Empresa** | Visualiza o portfólio de projetos e perfis de alunos. |

- O cadastro de novos usuários é exclusivo do Administrador.
- Apenas o Scrum Master pode marcar um projeto como finalizado ou reabri-lo.
- Entregas não podem ser alteradas após o projeto ser finalizado.

---

### 📊 Principais Rotas da Aplicação

| Método | Rota | Descrição | Perfil necessário |
|---|---|---|---|
| `GET/POST` | `/login` | Autenticação do usuário | Todos |
| `GET` | `/dashboard` | Painel principal | Todos |
| `GET/POST` | `/usuarios` | Listagem e criação de usuários | Admin |
| `GET/POST` | `/turmas` | Gerenciamento de turmas | Admin / Coordenador |
| `GET/POST` | `/tematicas` | Gerenciamento de temáticas | Admin / Coordenador |
| `GET/POST` | `/equipes/{id}` | Detalhe e gestão da equipe | Professor / Aluno |
| `POST` | `/equipes/{id}/avaliar` | Avaliação coletiva da equipe | Professor |
| `POST` | `/equipes/{id}/avaliar-aluno` | Avaliação individual do aluno | Professor |
| `GET` | `/portfolio` | Vitrine pública de projetos | Todos |
| `GET` | `/relatorios` | Relatórios gerenciais | Admin / Coordenador |
| `GET/POST` | `/meu-perfil` | Perfil e foto do aluno | Aluno |
| `GET` | `/api/privacy/export` *(planejado)* | Exportar dados do usuário (LGPD Art. 18, II) | Todos |
| `DELETE` | `/api/privacy/purge` *(planejado)* | Exclusão permanente da conta (LGPD Art. 18, VI) | Todos |

---

### 🔮 Melhorias Futuras

Se tivéssemos mais um semestre, planejamos implementar:

- **Painel de Privacidade (LGPD):** Exportação dos dados do usuário em formato JSON e rota de exclusão permanente de conta e histórico.
- **Notificações em Tempo Real:** Alertas para professores quando novas entregas forem submetidas.
- **Integração com GitHub:** Buscar automaticamente dados do repositório (linguagens, commits, estrelas) para enriquecer o portfólio.
- **Machine Learning:** Modelos para recomendar temáticas a alunos com base em áreas de interesse e histórico.
- **App Mobile:** Versão responsiva com notificações push para alunos e professores.

---

### 👥 Equipe e Autores

| Nome | Papel |
|---|---|
| **Danilo Henrique** | Desenvolvedor |
| **Edson Aguiar** | Desenvolvedor |
| **Evencio Neto** | Desenvolvedor |
| **Estevão Enoque** | Desenvolvedor |
| **Igor Barbosa** | Desenvolvedor |
| **Paulo Coutinho** | Desenvolvedor |

**Professor orientador de Coding/Pesquisa, Tecnologia e Sociedade:** Prof. Guibson Santana
**Professor orientador de Inglês Técnico:** Prof. Leonardo Trevas
**Professor orientador de Banco de Dados:** Prof. Heuryk Wylk
**Professor orientador de Engenharia de Requisitos/Criatividade:** Prof. Paulo Pimentel
**Professor orientador de Legislação de Tecnologia da Informação:** Prof. Renata Andrade
**Professor orientador de Unidade de Extensão:** Prof. Arnott Caiado

---

### 📄 Documentação

- [Documentação do Banco de Dados](DOCUMENTACAO_BANCO_DE_DADOS.md)
- Documentação técnica completa (requisitos e modelagem): *[em breve]*

---

### 📜 Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---
---

## 🇺🇸 English

### 📋 Project Overview

The **Integrative Projects Observatory** is a solution to the decentralization problem in Capstone Project (*Projeto Integrador*) submissions. Relying on emails and generic file-sharing platforms leads to document loss, version control issues, and significant time spent on manual organization by professors and coordinators. This system centralizes the entire workflow in a secure and organized environment.

Developed as a Capstone Project for the **Systems Analysis and Development (ADS) Program** at **Senac College — 2nd Module**.

### Key Features

- **Centralized Submission:** Students submit their projects directly on the platform, including links to repository, presentation slides, documents, and Drive folders.
- **Rubric-Based Evaluation:** Professors evaluate teams and individual students using predefined concept grades (Insufficient, Regular, Good, Great, Excellent).
- **Talent Showcase:** Partner companies browse a digital portfolio filtered by class, semester, and tech stack.
- **Full Management Panel:** Coordinators manage classes, themes, teams, and users in a single dashboard.

---

### 🔒 LGPD & Data Privacy Compliance (Lei Geral de Proteção de Dados)

Because this application processes personal data from students — including contact information, academic history, and professional profile — privacy by design was a core requirement from the start, in compliance with Brazilian Federal Law nº 13.709/2018 (LGPD).

#### Implemented Privacy Standards

- **Legal Basis for Processing (Art. 7º & 11):** Collected data such as email, phone number, and profile information is used exclusively for the platform's stated purposes, registered through explicit sign-up by the responsible administrator.
- **Data Minimization:** Only the information necessary for the system to function is stored. Profile fields such as LinkedIn, GitHub, and phone number are optional.
- **Security (Art. 46):** All passwords are stored as hashes using the **bcrypt** algorithm, preventing readability in the event of unauthorized database access.
- **Access Control:** The system adopts a role-based permissions model, ensuring each user can only access what is relevant to their role.
- **User Rights (Art. 18) — Planned:** Future versions will include a Privacy Settings panel where users will be able to:
  - Access all their registered data (right to access).
  - Correct incomplete or inaccurate records.
  - Revoke consent and request permanent deletion of their account and all associated history (*Right to Erasure*).

---

### 🛠️ Tech Stack

- **Backend:** Python 3.11, FastAPI, SQLAlchemy 2.0
- **Frontend:** HTML5, CSS3, Jinja2 (server-side templates)
- **Database:** SQLite (`observatorio.db` file)
- **Authentication:** JWT (python-jose) + bcrypt for password hashing
- **Server:** Uvicorn / Gunicorn
- **Version Control:** Git and GitHub
- **Project Management:** Trello

---

### ⚙️ Getting Started (Local Development)

#### 1. Prerequisites

- [Git](https://git-scm.com)
- [Python 3.11+](https://www.python.org/) installed

#### 2. Configuration

Clone the repository and navigate into the folder:

```bash
git clone https://github.com/EdsonAguiar888/Observatorio_de_Projetos_Integradores.git
cd observatorio-projetos-integradores
```

Create and activate a virtual environment:

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r observatorio_pi/requirements.txt
```

#### 3. Execution

```bash
python run.py
```

On Windows, you can also double-click the `iniciar.bat` file.

Open in your browser: **http://127.0.0.1:8000**

**Default login:**

```
Email:    admin@observatorio.pi
Password: admin1234
```

> ⚠️ Change the admin password immediately after your first login.

---

### 💼 Business Rules & Access Control

The system uses a role-based permissions model. Each user type has access restricted to their responsibilities:

| Role | Permissions |
|---|---|
| **ADMIN / Coordinator** | Manages users, classes, and themes. Full access to reports. |
| **Professor** | Creates teams under their themes, adds students, and records evaluations. |
| **Student** | Submits, edits, and deletes their own deliverables. The Scrum Master finalizes the project. |
| **Company** | Views the project portfolio and student profiles. |

- Only the Administrator can register new users.
- Only the Scrum Master can mark a project as finalized or reopen it.
- Deliverables cannot be edited after a project is finalized.

---

### 📊 Core API Endpoints

| Method | Route | Description | Required Role |
|---|---|---|---|
| `GET/POST` | `/login` | User authentication | All |
| `GET` | `/dashboard` | Main panel | All |
| `GET/POST` | `/usuarios` | User listing and creation | Admin |
| `GET/POST` | `/turmas` | Class management | Admin / Coordinator |
| `GET/POST` | `/tematicas` | Theme management | Admin / Coordinator |
| `GET/POST` | `/equipes/{id}` | Team detail and management | Professor / Student |
| `POST` | `/equipes/{id}/avaliar` | Team collective evaluation | Professor |
| `POST` | `/equipes/{id}/avaliar-aluno` | Individual student evaluation | Professor |
| `GET` | `/portfolio` | Public project showcase | All |
| `GET` | `/relatorios` | Management reports | Admin / Coordinator |
| `GET/POST` | `/meu-perfil` | Student profile and photo | Student |
| `GET` | `/api/privacy/export` *(planned)* | Download user data package (LGPD Art. 18, II) | All |
| `DELETE` | `/api/privacy/purge` *(planned)* | Permanently delete account and records (LGPD Art. 18, VI) | All |

---

### 🔮 Future Improvements

If we had another semester, we plan to implement:

- **Privacy Panel (LGPD):** User data export in JSON format and a permanent account deletion route.
- **Real-Time Notifications:** Alerts for professors when new deliverables are submitted.
- **GitHub Integration:** Automatically pull repository data (languages, commits, stars) to enrich the portfolio.
- **Machine Learning:** Models to recommend themes to students based on their areas of interest and history.
- **Mobile App:** Responsive version with push notifications for students and professors.

---

### 👥 Authors & Project Team

| Name | Role |
|---|---|
| **Danilo Henrique** | Developer |
| **Edson Aguiar** | Developer |
| **Evencio Neto** | Developer |
| **Estevão Enoque** | Developer |
| **Igor Barbosa** | Developer |
| **Paulo Coutinho** | Developer |

**Tech English Course Professor:** Prof. Leonardo Trevas

---

### 📄 Documentation

- [Database Documentation](DOCUMENTACAO_BANCO_DE_DADOS.md)
- Full technical documentation (requirements and modeling): *[coming soon]*

---

### 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
