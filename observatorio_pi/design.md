# Technical Design — UI Improvements and New Features

## Overview

Este documento descreve as alterações técnicas necessárias para implementar os 10 requisitos definidos em `requirements.md`. O sistema é uma aplicação **FastAPI + Jinja2 + SQLite** com Bootstrap 5 e Bootstrap Icons. Todas as mudanças respeitam os padrões de código existentes (sem frameworks JS adicionais, sem ORM migration tool — alterações de schema via `Base.metadata.create_all`).

As melhorias abrangem:
- Filtros de navegação (Req 1, Req 2)
- Correção de bug de UI (Req 3)
- Nova página de relatório por professor (Req 4)
- Limpeza visual da sidebar (Req 5)
- Upload e exibição de fotos de perfil (Req 6)
- Páginas de perfil por tipo de usuário com redirecionamento (Req 7)
- Informação de professor no dashboard do aluno (Req 8)
- Sidebar retrátil com localStorage (Req 9)
- Botão de ações rápidas global (FAB) (Req 10)

---

## Architecture

O sistema segue uma arquitetura **MVC monolítica** com FastAPI como controlador/roteador e Jinja2 como view engine. Não há frontend SPA — toda renderização é server-side.

```
┌──────────────────────────────────────────────────────────────┐
│                        Browser (HTTP)                         │
└──────────────────────┬───────────────────────────────────────┘
                       │ HTTP GET/POST
┌──────────────────────▼───────────────────────────────────────┐
│                  FastAPI Application                          │
│  ┌─────────────┐   ┌──────────────┐   ┌──────────────────┐  │
│  │  main.py    │   │  auth_router │   │  user_router     │  │
│  │  (rotas     │   │  project_    │   │  (perfis,        │  │
│  │  principais)│   │  router      │   │   foto upload)   │  │
│  └──────┬──────┘   └──────┬───────┘   └────────┬─────────┘  │
│         │                 │                     │             │
│  ┌──────▼─────────────────▼─────────────────────▼──────────┐ │
│  │                  SQLAlchemy ORM                          │ │
│  │   User  │  Turma  │  Tematica  │  Equipe  │  Avaliacao  │ │
│  └──────────────────────────┬─────────────────────────────┘ │
│                             │                                │
│  ┌──────────────────────────▼─────────────────────────────┐ │
│  │                  SQLite Database                        │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │              Jinja2 Templates                          │  │
│  │  base_auth.html → herança → templates específicos      │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │              Static Files (/static)                    │  │
│  │  /static/avatars/  ← uploads de fotos de perfil        │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

### Fluxo de autenticação

Todas as rotas autenticadas chamam `get_usuario_logado(request, db)` que lê o cookie `token` (JWT), decodifica e retorna o `User` ou `None`. Redireciona para `/` se não autenticado.

### Estrutura de arquivos relevante

```
observatorio_pi/
└── app/
    ├── main.py                    ← rotas monolíticas (modifcar: Req 1,2,4,6,7,8)
    ├── models/
    │   ├── user.py                ← adicionar foto_perfil (Req 6)
    │   └── project.py             ← sem alterações de schema
    ├── routers/
    │   ├── user_router.py         ← adicionar upload de foto (Req 6)
    │   └── project_router.py      ← sem alterações
    ├── templates/
    │   ├── base_auth.html         ← modificar: Req 5, 6 (macro), 7, 9, 10
    │   ├── turmas.html            ← Req 1
    │   ├── tematicas.html         ← Req 2
    │   ├── equipe_detalhe.html    ← Req 3
    │   ├── relatorios.html        ← Req 4 (link no nome do professor)
    │   ├── dashboard.html         ← Req 8
    │   ├── perfil_aluno.html      ← Req 6 (macro de avatar)
    │   ├── relatorio_professor.html   ← NOVO (Req 4)
    │   ├── perfil_professor.html      ← NOVO (Req 7)
    │   ├── perfil_coordenador.html    ← NOVO (Req 7)
    │   └── perfil_empresa.html        ← NOVO (Req 7)
    └── static/
        └── avatars/               ← NOVO diretório (Req 6)
```

---

## Components and Interfaces

### 1. Filtro de Turmas por Ano (`main.py` → `GET /turmas`)

**Interface:** `GET /turmas?ano=2025`

Parâmetro `ano: str = ""` adicionado à rota. A lógica de extração de anos e filtragem fica encapsulada na rota.

```python
@app.get("/turmas", response_class=HTMLResponse)
def listar_turmas(request: Request, ano: str = "", db: Session = Depends(get_db)):
    todas_turmas = db.query(Turma).all()
    anos_disponiveis = sorted(
        set(t.semestre.split("-")[0] for t in todas_turmas if "-" in t.semestre),
        reverse=True
    )
    query = db.query(Turma)
    if ano:
        query = query.filter(Turma.semestre.startswith(f"{ano}-"))
    turmas = query.order_by(Turma.semestre.desc(), Turma.nome).all()
    return templates.TemplateResponse("turmas.html", {
        ..., "anos_disponiveis": anos_disponiveis, "ano_selecionado": ano,
    })
```

**Template `turmas.html`:** `<form method="get">` com `<select name="ano">`. Exibe mensagem de estado vazio quando `turmas` for vazio com `ano` preenchido.

---

### 2. Filtro de Temáticas por Professor (`main.py` → `GET /tematicas`)

**Interface:** `GET /tematicas?filtro_turma=1&filtro_professor=42`

Parâmetro `filtro_professor: str = ""` adicionado. Visível apenas para ADMIN/COORDENADOR.

```python
@app.get("/tematicas", response_class=HTMLResponse)
def listar_tematicas(
    request: Request,
    filtro_turma: str = "",
    filtro_professor: str = "",
    db: Session = Depends(get_db)
):
    professores = db.query(User).filter(
        User.tipo == "PROFESSOR", User.ativo == True
    ).order_by(User.nome).all()

    if usuario.tipo in ("ADMIN", "COORDENADOR") and filtro_professor:
        prof_id = int(filtro_professor) if filtro_professor.isdigit() else None
        prof_valido = prof_id and db.query(User).filter(User.id == prof_id).first()
        if prof_valido:
            query = query.filter(Tematica.professor_id == prof_id)
        else:
            filtro_professor = ""  # ignora param inválido

    return templates.TemplateResponse("tematicas.html", {
        ..., "professores": professores, "filtro_professor": filtro_professor,
    })
```

---

### 3. Correção dos Radio Buttons de Avaliação (`equipe_detalhe.html`)

**Componente:** Template Jinja2. Comparação string-a-string explícita para cada um dos 6 critérios.

```html
<input type="radio" name="conceito_conteudo" value="{{ c }}"
  {% if avaliacao and avaliacao.conceito_conteudo == c %}checked
  {% elif not avaliacao and c == 'BOM' %}checked{% endif %}>
```

Aplicar para: `conceito_conteudo`, `conceito_tecnica`, `conceito_apresentacao`, `conceito_inovacao`, `conceito_equipe`, `conceito_final`.

---

### 4. Rota e Template de Relatório por Professor

**Interface:** `GET /relatorios/professor/{professor_id}`

Acesso restrito a ADMIN/COORDENADOR. Redireciona para `/relatorios?erro=...` se professor não encontrado.

```python
@app.get("/relatorios/professor/{professor_id}", response_class=HTMLResponse)
def relatorio_professor(professor_id: int, request: Request, db: Session = Depends(get_db)):
    usuario = get_usuario_logado(request, db)
    if not usuario or usuario.tipo not in ("ADMIN", "COORDENADOR"):
        return RedirectResponse(url="/dashboard", status_code=303)

    professor = db.query(User).filter(
        User.id == professor_id, User.tipo == "PROFESSOR"
    ).first()
    if not professor:
        return RedirectResponse(
            url="/relatorios?erro=Professor+não+encontrado", status_code=303
        )

    tematicas = db.query(Tematica).filter(
        Tematica.professor_id == professor_id
    ).order_by(Tematica.criado_em.desc()).all()

    dados_tematicas = []
    total_equipes = 0
    total_avaliacoes = 0
    for t in tematicas:
        n_equipes = len(t.equipes)
        equipe_ids = [e.id for e in t.equipes]
        n_avaliacoes = db.query(Avaliacao).filter(
            Avaliacao.professor_id == professor_id,
            Avaliacao.equipe_id.in_(equipe_ids)
        ).count() if equipe_ids else 0
        total_equipes += n_equipes
        total_avaliacoes += n_avaliacoes
        dados_tematicas.append({
            "tematica": t, "n_equipes": n_equipes, "n_avaliacoes": n_avaliacoes
        })

    return templates.TemplateResponse("relatorio_professor.html", {
        "request": request, "usuario": usuario, "professor": professor,
        "dados_tematicas": dados_tematicas,
        "total_tematicas": len(tematicas),
        "total_equipes": total_equipes,
        "total_avaliacoes": total_avaliacoes,
        "active_page": "relatorios",
    })
```

**Template `relatorio_professor.html`:** Estende `base_auth.html`. Cards de totais (Temáticas, Equipes, Avaliações) + tabela de temáticas + estado vazio.

**Ajuste em `relatorios.html`:** A query `top_professores` deve retornar tuplas `(professor_id, nome, total)` para habilitar o link.

---

### 5. Limpeza da Sidebar (`base_auth.html`)

**Remover:** Bloco `<div class="px-3 pt-3 border-top...">` (avatar + nome + email na posição `bottom:1rem`).

**Adicionar na navbar superior:** E-mail do usuário abaixo do nome, truncado a 30 caracteres.

```html
<div class="text-end">
    <div class="text-white small fw-semibold lh-1">{{ usuario.nome }}</div>
    <div class="text-white-50" style="font-size:.68rem;">
        {{ usuario.email[:30] }}{% if usuario.email|length > 30 %}…{% endif %}
    </div>
</div>
<span class="badge rounded-pill" style="background:var(--senac-orange);">{{ usuario.tipo }}</span>
```

---

### 6. Upload de Foto de Perfil

**Novo campo no modelo (`user.py`):**
```python
foto_perfil = Column(String, nullable=True, default=None)
```

**Registro de arquivos estáticos (`main.py`):**
```python
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
```

**Interface:** `POST /meu-perfil/foto` com `multipart/form-data`.

Validações: tipo MIME (`image/jpeg`, `image/png`, `image/webp`) e tamanho máximo 2 MB. Nome do arquivo: `avatar_{usuario.id}.{ext}`. Salva em `static/avatars/`.

**Helper de URL de perfil (global em `main.py`):**
```python
def _url_perfil(usuario: User) -> str:
    mapa = {
        "ALUNO":       f"/alunos/{usuario.id}",
        "PROFESSOR":   f"/perfil/professor/{usuario.id}",
        "COORDENADOR": f"/perfil/coordenador/{usuario.id}",
        "ADMIN":       f"/perfil/coordenador/{usuario.id}",
        "EMPRESA":     f"/perfil/empresa/{usuario.id}",
    }
    return mapa.get(usuario.tipo, "/dashboard")
```

**Macro Jinja2 `avatar(u, size=32)`** em `base_auth.html`: exibe `<img>` se `u.foto_perfil` existir, caso contrário gera div com inicial colorida.

---

### 7. Páginas de Perfil e Redirecionamento pelo Nome/Foto

**Filtro Jinja2 global:** `templates.env.globals["url_perfil"] = _url_perfil` em `main.py`.

**Novas rotas:**
- `GET /perfil/professor/{professor_id}` → `perfil_professor.html`
- `GET /perfil/coordenador/{coordenador_id}` → `perfil_coordenador.html`
- `GET /perfil/empresa/{empresa_id}` → `perfil_empresa.html`

Cada rota detecta se `usuario.id == perfil_id` para habilitar edição. Caso contrário, modo somente leitura.

**Navbar superior:** O bloco de nome/avatar envolto em `<a href="{{ url_perfil(usuario) }}">`.

**Remover** item "Meu Perfil" da sidebar (o `{% if usuario.tipo == 'ALUNO' %}` com link para `/meu-perfil`).

---

### 8. Nome do Professor nas Equipes Recentes (`dashboard.html`)

**Backend (`GET /dashboard`):** Usar `joinedload` para evitar N+1 queries.

```python
from sqlalchemy.orm import joinedload

equipes_recentes = (
    db.query(Equipe)
    .options(joinedload(Equipe.tematica).joinedload(Tematica.professor))
    .filter(Equipe.tematica_id.in_(tematica_ids))
    .order_by(Equipe.criado_em.desc())
    .limit(5)
    .all()
)
```

**Template (`dashboard.html`):** Nova coluna "Professor" na tabela de equipes do ALUNO. Exibe `eq.tematica.professor.nome` ou `—` quando nulo.

---

### 9. Sidebar Retrátil

**CSS em `base_auth.html`:** Variáveis `--sidebar-width: 16.666%` e `--sidebar-collapsed: 60px`. Transições de 250ms. Classe `.collapsed` oculta textos via `.nav-link-text { display: none }`.

**HTML:** Botão hamburger `#sidebarToggle` na navbar. Textos dos links envolvidos em `<span class="nav-link-text">`.

**JavaScript:**
```javascript
(function () {
    const sidebar = document.querySelector('.sidebar');
    const btn     = document.getElementById('sidebarToggle');
    const KEY     = 'opi_sidebar_collapsed';

    function applyState(collapsed) {
        sidebar.classList.toggle('collapsed', collapsed);
        try { localStorage.setItem(KEY, collapsed ? '1' : '0'); } catch(e) {}
    }

    let saved = false;
    try { saved = localStorage.getItem(KEY) === '1'; } catch(e) {}
    applyState(saved);

    btn.addEventListener('click', () => {
        applyState(!sidebar.classList.contains('collapsed'));
    });
})();
```

---

### 10. Botão de Ações Rápidas (FAB)

**HTML em `base_auth.html`** (antes de `</body>`): Container fixo `position:fixed;bottom:24px;right:24px;z-index:1050` com botão principal `#fabBtn` e menu `#fabMenu`.

**Macro `fab_item(url, icon, label)`:** Label + ícone circular em pill layout.

**Ações por tipo:** ALUNO (3 ações), PROFESSOR (2), COORDENADOR (3), ADMIN (4), EMPRESA (1).

**JavaScript:** Toggle do menu com fechamento automático ao clicar fora. Ícone alterna entre `bi-plus-lg` (fechado) e `bi-x-lg` (aberto).

---

## Data Models

### Alteração no modelo `User`

Adição do campo `foto_perfil` — único campo novo nesta feature. Sem migrations de schema necessárias (SQLAlchemy `create_all` cria a coluna em bancos novos; para bancos existentes, migração manual via SQL direto):

```python
# app/models/user.py
class User(Base):
    __tablename__ = "users"

    id             = Column(Integer, primary_key=True, index=True)
    nome           = Column(String, nullable=False)
    email          = Column(String, unique=True, index=True, nullable=False)
    senha_hash     = Column(String, nullable=False)
    tipo           = Column(String, default="ALUNO", nullable=False)
    ativo          = Column(Boolean, default=True, nullable=False)
    bio            = Column(Text, default="")
    linkedin       = Column(String, default="")
    github         = Column(String, default="")
    portfolio_url  = Column(String, default="")
    area_interesse = Column(String, default="")
    cidade         = Column(String, default="")
    telefone       = Column(String, default="")
    foto_perfil    = Column(String, nullable=True, default=None)  # ← NOVO (Req 6)
```

**Script de migração para banco existente:**
```sql
ALTER TABLE users ADD COLUMN foto_perfil TEXT;
```

### Modelos sem alteração

Os modelos `Turma`, `Tematica`, `Equipe`, `EquipeMembro`, `EntregaProjeto`, `Avaliacao` e `AvaliacaoAluno` em `project.py` não sofrem alterações de schema. As novas funcionalidades (filtros, relatórios, dashboard) utilizam os campos existentes.

### Contexto de template (variáveis adicionadas por rota)

| Rota | Variáveis adicionadas |
|---|---|
| `GET /turmas` | `anos_disponiveis: list[str]`, `ano_selecionado: str` |
| `GET /tematicas` | `professores: list[User]`, `filtro_professor: str` |
| `GET /relatorios/professor/{id}` | `professor`, `dados_tematicas`, `total_tematicas`, `total_equipes`, `total_avaliacoes` |
| `GET /dashboard` (ALUNO) | `equipes_recentes` com `joinedload` de `tematica.professor` |
| Todos os templates autenticados | `perfil_url: str` (via `url_perfil` global Jinja2) |

### Arquivos novos a criar

| Arquivo | Propósito |
|---|---|
| `templates/relatorio_professor.html` | Req 4 |
| `templates/perfil_professor.html` | Req 7 |
| `templates/perfil_coordenador.html` | Req 7 |
| `templates/perfil_empresa.html` | Req 7 |
| `static/avatars/` (diretório) | Req 6 |

### Arquivos a modificar

| Arquivo | Requisitos |
|---|---|
| `app/main.py` | 1, 2, 4, 6, 7, 8 |
| `app/models/user.py` | 6 |
| `templates/base_auth.html` | 5, 6 (macro), 7, 9, 10 |
| `templates/turmas.html` | 1 |
| `templates/tematicas.html` | 2 |
| `templates/equipe_detalhe.html` | 3 |
| `templates/relatorios.html` | 4 |
| `templates/dashboard.html` | 8 |
| `templates/perfil_aluno.html` | 6 |

---

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system — essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Filtro de turmas por ano — exatidão

*Para qualquer* conjunto de turmas com semestres variados e qualquer ano de filtro válido, todas as turmas retornadas pelo filtro devem ter o campo `semestre` iniciando com `"{ano}-"`, e nenhuma turma com semestre de outro ano deve aparecer no resultado.

**Validates: Requirements 1.2**

---

### Property 2: Extração de anos distintos — completude e unicidade

*Para qualquer* lista de turmas, o conjunto de anos extraídos deve conter exatamente os anos únicos presentes nos campos `semestre`, sem duplicatas e ordenados do mais recente ao mais antigo.

**Validates: Requirements 1.1**

---

### Property 3: Estado do filtro refletido no contexto — round-trip

*Para qualquer* ano válido submetido como parâmetro GET, o valor `ano_selecionado` retornado no contexto do template deve ser igual ao valor do parâmetro submetido.

**Validates: Requirements 1.5, 2.6**

---

### Property 4: Filtro de temáticas por professor — exatidão

*Para qualquer* conjunto de temáticas com `professor_id` variados e qualquer `professor_id` de filtro válido, todas as temáticas retornadas devem ter `professor_id` igual ao valor do filtro, e nenhuma temática de outro professor deve aparecer.

**Validates: Requirements 2.2**

---

### Property 5: Filtros compostos de temáticas — interseção correta

*Para qualquer* combinação de `filtro_turma` e `filtro_professor` ambos ativos, o resultado deve conter somente temáticas que satisfazem simultaneamente ambos os critérios (professor_id correto E turma_id correto).

**Validates: Requirements 2.3**

---

### Property 6: Pré-seleção de radio buttons de avaliação — correspondência exata

*Para qualquer* avaliação com qualquer combinação válida de conceitos nos 6 critérios, a lógica de renderização deve marcar como `checked` exatamente o radio button cujo `value` corresponde ao conceito salvo, e nenhum outro radio button do mesmo critério deve receber `checked`.

**Validates: Requirements 3.1, 3.2**

---

### Property 7: Round-trip de persistência de avaliação

*Para qualquer* conjunto de conceitos submetidos no formulário de avaliação, após a persistência bem-sucedida, a re-renderização da página deve exibir os mesmos conceitos recém-salvos como selecionados nos radio buttons correspondentes.

**Validates: Requirements 3.4**

---

### Property 8: Totais agregados do relatório de professor — invariância aritmética

*Para qualquer* professor com qualquer conjunto de temáticas e equipes, `total_equipes` deve ser igual à soma de `n_equipes` de cada temática, e `total_avaliacoes` deve ser igual à soma de `n_avaliacoes` de cada temática.

**Validates: Requirements 4.4**

---

### Property 9: Validação de upload de foto — rejeição de arquivos inválidos

*Para qualquer* arquivo cujo tipo MIME não seja `image/jpeg`, `image/png` ou `image/webp`, ou cujo tamanho exceda 2 MB, a rota de upload deve rejeitar o arquivo sem alterar o campo `foto_perfil` do usuário.

**Validates: Requirements 6.3**

---

### Property 10: URL de perfil correta por tipo de usuário

*Para qualquer* usuário com qualquer tipo válido (`ALUNO`, `PROFESSOR`, `COORDENADOR`, `ADMIN`, `EMPRESA`), a função `_url_perfil` deve retornar uma URL contendo o identificador do usuário e o path correspondente ao seu tipo.

**Validates: Requirements 7.1, 7.2, 7.3, 7.4**

---

### Property 11: Ações do FAB corretas por tipo de usuário

*Para qualquer* usuário de cada tipo, o menu do FAB deve conter exatamente as ações definidas para aquele tipo — nem mais, nem menos.

**Validates: Requirements 10.3, 10.4, 10.5, 10.6**

---

## Error Handling

### Erros de autenticação e autorização

| Situação | Comportamento |
|---|---|
| Usuário não autenticado acessa rota protegida | `RedirectResponse(url="/", status_code=303)` |
| Usuário sem permissão acessa rota restrita | `RedirectResponse(url="/dashboard", status_code=303)` |
| ALUNO acessa equipe da qual não faz parte | `RedirectResponse(url="/dashboard?erro=Sem+permissão", status_code=303)` |

### Erros de recursos não encontrados

| Situação | Comportamento |
|---|---|
| `professor_id` não existe ou não é PROFESSOR | `RedirectResponse(url="/relatorios?erro=Professor+não+encontrado", status_code=303)` |
| Turma, Temática ou Equipe não encontrada | Redirect para a listagem com `?erro=` correspondente |

### Erros de upload de foto

| Situação | Resposta |
|---|---|
| Tipo MIME inválido | Redirect para perfil com `?erro=Arquivo+inválido.+Envie+uma+imagem+JPEG%2C+PNG+ou+WebP+com+até+2+MB` |
| Arquivo > 2 MB | Idem acima |
| Diretório `static/avatars/` inexistente | Criar automaticamente no startup via `os.makedirs(..., exist_ok=True)` |

### Erros de filtro com parâmetros inválidos

| Situação | Comportamento |
|---|---|
| `filtro_professor` não é dígito ou ID inexistente | Ignorar silenciosamente, exibir todas as temáticas, `filtro_professor = ""` |
| `ano` não corresponde a nenhuma turma | Retorna lista vazia com mensagem de estado vazio no template |

### Erros de localStorage (Req 9)

Se `localStorage` não estiver disponível (modo privado, iframe, extensões), o JavaScript usa `try/catch` e mantém o comportamento funcional na sessão atual sem persistência — sidebar expande por padrão a cada carregamento de página.

### Fallback de avatar (Req 6)

Se `foto_perfil` for `None` ou a imagem não estiver acessível, o template exibe o avatar gerado por inicial (a macro `avatar()` não faz requisição HTTP extra — apenas verifica o campo do modelo).

---

## Testing Strategy

### Abordagem dual: testes unitários + testes baseados em propriedades

O projeto utiliza Python como linguagem principal. A biblioteca de property-based testing escolhida é **[Hypothesis](https://hypothesis.readthedocs.io/)**, integrada com pytest.

```
pip install hypothesis pytest
```

### Testes Unitários

Focados em comportamentos específicos, casos de borda e pontos de integração:

- **Req 3:** Verificar que sem avaliação prévia, todos os 6 critérios têm `BOM` como default
- **Req 4:** Verificar redirecionamento para `/relatorios?erro=...` quando professor não existe
- **Req 4:** Verificar redirecionamento para `/dashboard` quando usuário não é ADMIN/COORDENADOR
- **Req 5:** Verificar que o HTML renderizado de `base_auth.html` não contém o bloco inferior da sidebar
- **Req 8:** Verificar que equipe com `professor_id = None` exibe `—` na coluna Professor
- **Req 9:** Verificar que a classe `.collapsed` é adicionada/removida corretamente pelo JS
- **Req 10:** Verificar que clicar fora do FAB fecha o menu

### Testes Baseados em Propriedades (Property-Based Tests)

Cada propriedade deve ser implementada com **mínimo de 100 iterações**. Tag de referência: `# Feature: ui-improvements-and-new-features, Property {N}: {texto_resumido}`.

#### Property 1 — Filtro de turmas por ano

```python
from hypothesis import given, settings
import hypothesis.strategies as st

@given(
    turmas=st.lists(st.builds(
        Turma, semestre=st.from_regex(r'\d{4}-[12]')
    ), min_size=0, max_size=20),
    ano=st.from_regex(r'\d{4}')
)
@settings(max_examples=100)
def test_filtro_turmas_por_ano(turmas, ano):
    # Feature: ui-improvements-and-new-features, Property 1: filtro turmas por ano
    resultado = [t for t in turmas if t.semestre.startswith(f"{ano}-")]
    assert all(t.semestre.startswith(f"{ano}-") for t in resultado)
    assert not any(t for t in turmas if not t.semestre.startswith(f"{ano}-") and t in resultado)
```

#### Property 2 — Extração de anos distintos

```python
@given(semestres=st.lists(st.from_regex(r'\d{4}-[12]'), min_size=0, max_size=30))
@settings(max_examples=100)
def test_extracao_anos_distintos(semestres):
    # Feature: ui-improvements-and-new-features, Property 2: anos distintos
    anos = extrair_anos(semestres)  # função a testar
    assert len(anos) == len(set(anos))  # sem duplicatas
    assert anos == sorted(set(anos), reverse=True)  # ordenado descendente
```

#### Property 6 — Pré-seleção de radio buttons

```python
@given(
    conceitos=st.fixed_dictionaries({
        c: st.sampled_from(CONCEITOS) for c in [
            'conceito_conteudo', 'conceito_tecnica', 'conceito_apresentacao',
            'conceito_inovacao', 'conceito_equipe', 'conceito_final'
        ]
    })
)
@settings(max_examples=100)
def test_radio_button_selecao(conceitos):
    # Feature: ui-improvements-and-new-features, Property 6: radio buttons avaliação
    for criterio, valor_salvo in conceitos.items():
        for candidato in CONCEITOS:
            esperado = (candidato == valor_salvo)
            assert deve_estar_checked(candidato, valor_salvo) == esperado
```

#### Property 8 — Totais agregados do relatório

```python
@given(
    dados_tematicas=st.lists(
        st.fixed_dictionaries({
            "n_equipes": st.integers(min_value=0, max_value=20),
            "n_avaliacoes": st.integers(min_value=0, max_value=50),
        }),
        min_size=0, max_size=10
    )
)
@settings(max_examples=100)
def test_totais_agregados_relatorio(dados_tematicas):
    # Feature: ui-improvements-and-new-features, Property 8: totais agregados
    total_equipes = sum(d["n_equipes"] for d in dados_tematicas)
    total_avaliacoes = sum(d["n_avaliacoes"] for d in dados_tematicas)
    resultado = calcular_totais(dados_tematicas)
    assert resultado["total_equipes"] == total_equipes
    assert resultado["total_avaliacoes"] == total_avaliacoes
```

#### Property 10 — URL de perfil por tipo

```python
@given(
    tipo=st.sampled_from(["ALUNO", "PROFESSOR", "COORDENADOR", "ADMIN", "EMPRESA"]),
    user_id=st.integers(min_value=1, max_value=10000)
)
@settings(max_examples=100)
def test_url_perfil_por_tipo(tipo, user_id):
    # Feature: ui-improvements-and-new-features, Property 10: url_perfil por tipo
    usuario = User(id=user_id, tipo=tipo, nome="Test", email="t@t.com")
    url = _url_perfil(usuario)
    assert str(user_id) in url
    # Mapas esperados
    if tipo == "ALUNO":
        assert url == f"/alunos/{user_id}"
    elif tipo == "PROFESSOR":
        assert url == f"/perfil/professor/{user_id}"
    elif tipo in ("COORDENADOR", "ADMIN"):
        assert url == f"/perfil/coordenador/{user_id}"
    elif tipo == "EMPRESA":
        assert url == f"/perfil/empresa/{user_id}"
```

### Ordem de implementação e testes

| Prioridade | Requisito | Arquivos afetados |
|---|---|---|
| 1 | Req 3 — Fix avaliação | `equipe_detalhe.html` |
| 2 | Req 5 — Remover sidebar footer | `base_auth.html` |
| 3 | Req 8 — Professor nas equipes recentes | `main.py`, `dashboard.html` |
| 4 | Req 1 — Filtro por ano turmas | `main.py`, `turmas.html` |
| 5 | Req 2 — Filtro por professor temáticas | `main.py`, `tematicas.html` |
| 6 | Req 9 — Sidebar retrátil | `base_auth.html` |
| 7 | Req 10 — FAB ações rápidas | `base_auth.html` |
| 8 | Req 4 — Relatório professor | `main.py`, novo template |
| 9 | Req 6 — Fotos de perfil | `user.py`, `main.py`, templates |
| 10 | Req 7 — Perfis e redirecionamento | `main.py`, novos templates |
