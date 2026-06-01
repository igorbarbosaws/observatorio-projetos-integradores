# Observatório de Projetos Integradores

![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-yellow)
![Linguagem](https://img.shields.io/badge/Python-3.x-blue)
![Faculdade](https://img.shields.io/badge/SENAC-ADS--2%C2%BA%20M%C3%B3dulo-orange)

Este repositório contém o desenvolvimento do **Observatório de Projetos Integradores**, uma plataforma web centralizada projetada para organizar a submissão, avaliação e consulta de projetos acadêmicos do curso de Análise e Desenvolvimento de Sistemas (ADS) do SENAC.

---

## 🇧🇷 Português

### 📝 Descrição do Sistema
O projeto surge como uma solução para a descentralização no envio de Projetos Integradores (PIs). Atualmente, a dependência de e-mails e plataformas genéricas causa perda de documentos, dificuldade no controle de versões e alto tempo gasto na organização manual por parte dos professores e coordenação. O sistema centraliza todo esse fluxo em um ambiente seguro e organizado.

### 🎯 Objetivos
* **Centralização:** Unificar a submissão e o armazenamento de todos os trabalhos em um único local.
* **Avaliação Eficiente:** Permitir que professores avaliem os projetos diretamente na plataforma através de rubricas.
* **Vitrine de Talentos:** Funcionar como um portfólio digital, permitindo que empresas parceiras visualizem projetos e identifiquem potenciais talentos para recrutamento.

### 🛠 Tecnologias Utilizadas
* **Linguagem Principal:** Python
* **Frontend:** HTML5, CSS3
* **Versionamento:** Git e GitHub
* **Gestão de Projeto:** Trello

### 💼 Regras de Negócio
* **Autenticação:** O acesso é restrito apenas a usuários cadastrados e logados.
* **Gestão de Usuários:** O cadastro de novos usuários é uma funcionalidade exclusiva do Administrador (Coordenador).
* **Painel do Aluno (CRUD):** Alunos podem submeter, visualizar, editar e excluir seus próprios projetos integradores.
* **Painel do Professor:** Permite filtrar projetos por turma e realizar avaliações utilizando rubricas pré-definidas.
* **Acesso para Empresas:** Empresas parceiras possuem um módulo de visualização para consulta de projetos e talentos.

### 👥 Equipe do Projeto
* Danilo Henrique
* Edson Aguiar
* Evencio Neto
* Estevão Enoque
* Igor Barbosa
* Paulo Coutinho

### 🚀 Como Executar o Projeto

#### Pré-requisitos
* Python 3.11 ou superior instalado

#### Passos

1.  Clone este repositório:
    ```bash
    git clone https://github.com/EdsonAguiar888/Observatorio_de_Projetos_Integradores.git
    cd observatorio-projetos-integradores
    ```

2.  Crie e ative o ambiente virtual:
    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # Linux/macOS
    source .venv/bin/activate
    ```

3.  Instale as dependências:
    ```bash
    pip install -r observatorio_pi/requirements.txt
    ```

4.  Execute o projeto:
    ```bash
    python run.py
    ```
    Ou no Windows, dê duplo clique em `iniciar.bat`.

5.  Acesse no navegador: **http://127.0.0.1:8000**

    Login padrão:
    - E-mail: `admin@observatorio.pi`
    - Senha: `admin1234`

> ⚠️ Altere a senha do admin após o primeiro login.

### 📄 Documentação
O link para a documentação técnica completa, incluindo requisitos e modelagem, pode ser encontrado aqui: [LINK DA DOCUMENTAÇÃO].

---

## 🇺🇸 English

### 📝 System Description
This project is a solution for the decentralization of Integrative Project (PI) submissions. Currently, relying on emails and generic platforms leads to document loss, version control issues, and significant time spent by teachers and coordinators on manual organization. The system centralizes this entire workflow in a secure and organized environment.

### 🎯 Objectives
* **Centralization:** Unify the submission and storage of all works in a single location.
* **Efficient Evaluation:** Enable teachers to evaluate projects directly on the platform using rubrics.
* **Talent Showcase:** Act as a digital portfolio, allowing partner companies to view projects and identify potential talents for recruitment.

### 🛠 Technologies Used
* **Primary Language:** Python
* **Frontend:** HTML5, CSS3
* **Versioning:** Git and GitHub
* **Project Management:** Trello

### 💼 Business Rules
* **Authentication:** Access is restricted to registered and logged-in users only.
* **User Management:** Registering new users is an exclusive feature of the Administrator (Coordinator).
* **Student Panel (CRUD):** Students can submit, view, edit, and delete their own integrative projects.
* **Teacher Panel:** Allows filtering projects by class and performing evaluations using predefined rubrics.
* **Company Access:** Partner companies have a viewing module to consult projects and talents.

### 👥 Project Team
* Danilo Henrique
* Edson Aguiar
* Evencio Neto
* Estevão Enoque
* Igor Barbosa
* Paulo Coutinho

### 🚀 How to Run the Project

#### Prerequisites
* Python 3.11 or higher installed

#### Steps

1.  Clone this repository:
    ```bash
    git clone https://github.com/EdsonAguiar888/Observatorio_de_Projetos_Integradores.git
    cd observatorio-projetos-integradores
    ```

2.  Create and activate the virtual environment:
    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # Linux/macOS
    source .venv/bin/activate
    ```

3.  Install dependencies:
    ```bash
    pip install -r observatorio_pi/requirements.txt
    ```

4.  Run the project:
    ```bash
    python run.py
    ```
    Or on Windows, double-click `iniciar.bat`.

5.  Open in browser: **http://127.0.0.1:8000**

    Default login:
    - Email: `admin@observatorio.pi`
    - Password: `admin1234`

> ⚠️ Change the admin password after the first login.

### 📄 Documentation
The link to the full technical documentation, including requirements and modeling, can be found here: [DOCUMENTATION LINK].
