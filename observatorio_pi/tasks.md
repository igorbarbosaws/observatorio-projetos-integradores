# Implementation Plan: UI Improvements and New Features

## Overview

Implementação incremental das 10 melhorias de UI e novas funcionalidades do Observatório PI. A sequência prioriza correções de bug e mudanças de baixo risco antes de funcionalidades novas complexas. Cada tarefa referencia os requisitos correspondentes e constrói sobre o estado deixado pela tarefa anterior.

A linguagem de implementação é **Python** (FastAPI/Jinja2/SQLAlchemy), alinhada ao stack existente do projeto.

---

## Tasks

- [ ] 1. Corrigir pré-seleção dos radio buttons de avaliação da equipe
  - [x] 1.1 Corrigir comparação string-a-string nos 6 critérios de avaliação em `equipe_detalhe.html`
    - Substituir a lógica de pré-seleção dos radio buttons de `conceito_conteudo`, `conceito_tecnica`, `conceito_apresentacao`, `conceito_inovacao`, `conceito_equipe` e `conceito_final` por comparação explícita `{% if avaliacao and avaliacao.<campo> == c %}checked{% elif not avaliacao and c == 'BOM' %}checked{% endif %}`
    - Garantir que exatamente um radio button por critério receba `checked` — nunca zero, nunca dois
    - _Requirements: 3.1, 3.2, 3.3_

  - [ ] 1.2 Escrever property test para pré-seleção dos radio buttons (Property 6)
    - **Property 6: Pré-seleção de radio buttons de avaliação — correspondência exata**
    - Para qualquer combinação de conceitos nos 6 critérios, a função `deve_estar_checked(candidato, valor_salvo)` deve retornar `True` exatamente quando `candidato == valor_salvo`
    - Criar arquivo `tests/test_properties.py` com `hypothesis` e pytest; mínimo de 100 exemplos
    - **Validates: Requirements 3.1, 3.2**

  - [ ] 1.3 Escrever teste unitário para round-trip de persistência de avaliação (Property 7)
    - Verificar que após POST `/equipes/{id}/avaliar` com conceitos específicos, o GET subsequente exibe os mesmos conceitos selecionados
    - **Validates: Requirements 3.4**

- [ ] 2. Checkpoint — Garantir que o formulário de avaliação esteja correto
  - Garantir que todos os testes passam. Verificar manualmente em `equipe_detalhe.html` que ao editar uma avaliação existente os conceitos salvos aparecem pré-selecionados. Perguntar ao usuário se há dúvidas antes de continuar.

- [ ] 3. Limpar sidebar e adicionar e-mail/badge na navbar superior
  - [ ] 3.1 Remover bloco de avatar/nome/e-mail do rodapé da sidebar em `base_auth.html`
    - Remover o `<div class="px-3 pt-3 border-top...">` que contém o avatar circular, nome e e-mail posicionados em `bottom:1rem`
    - _Requirements: 5.1_

  - [ ] 3.2 Adicionar e-mail truncado e badge de tipo na navbar superior em `base_auth.html`
    - Abaixo do `<span class="text-white">{{ usuario.nome }}</span>` existente, adicionar linha com e-mail truncado a 30 caracteres (`{{ usuario.email[:30] }}{% if usuario.email|length > 30 %}…{% endif %}`) e garantir exibição em telas ≥ 576px (`d-none d-sm-flex`)
    - O badge de tipo do usuário (`{{ usuario.tipo }}`) com `background:var(--senac-orange)` deve permanecer ao lado do nome
    - _Requirements: 5.2, 5.3, 5.4_

- [ ] 4. Exibir nome do professor nas equipes recentes do dashboard do aluno
  - [ ] 4.1 Adicionar `joinedload` na query de equipes recentes do aluno em `main.py`
    - Na rota `GET /dashboard`, no branch `usuario.tipo == "ALUNO"`, substituir `_equipes_do_aluno(db, usuario.id)[:5]` por uma query com `joinedload(Equipe.tematica).joinedload(Tematica.professor)` que retorne as equipes ordenadas por `Equipe.criado_em.desc()` e limitadas a 5
    - Importar `joinedload` de `sqlalchemy.orm`
    - _Requirements: 8.1_

  - [ ] 4.2 Adicionar coluna "Professor" na tabela "Equipes Recentes" em `dashboard.html`
    - Adicionar `<th>Professor</th>` no `<thead>` da tabela de equipes recentes
    - Para cada `eq`, exibir `{{ eq.tematica.professor.nome if eq.tematica and eq.tematica.professor else '—' }}` como texto simples (sem link/âncora) na célula correspondente
    - _Requirements: 8.1, 8.2, 8.3_

  - [ ] 4.3 Escrever teste unitário para exibição do "—" quando professor é nulo
    - Verificar que quando `professor_id` da Temática é `None`, o valor exibido é `—`
    - **Validates: Requirements 8.2**

- [ ] 5. Adicionar filtro por ano na listagem de turmas
  - [ ] 5.1 Atualizar rota `GET /turmas` em `main.py` para aceitar parâmetro `ano` e filtrar
    - Adicionar parâmetro `ano: str = ""` à rota `listar_turmas`
    - Extrair anos distintos de `t.semestre.split("-")[0]` para todas as turmas, ordenar em ordem decrescente
    - Aplicar `query.filter(Turma.semestre.startswith(f"{ano}-"))` quando `ano` não for vazio
    - Passar `anos_disponiveis` e `ano_selecionado` ao template
    - _Requirements: 1.1, 1.2, 1.3_

  - [ ] 5.2 Adicionar controle de filtro por ano em `turmas.html`
    - Adicionar `<form method="get" action="/turmas">` com `<select name="ano">` populado com `anos_disponiveis`, opção "Todos os anos" como primeira opção, e `selected` no ano correspondente a `ano_selecionado`
    - Exibir mensagem "Nenhuma turma encontrada para o ano selecionado." quando `turmas` estiver vazio e `ano_selecionado` estiver preenchido
    - _Requirements: 1.1, 1.4, 1.5_

  - [ ] 5.3 Escrever property test para filtro de turmas por ano (Property 1)
    - **Property 1: Filtro de turmas por ano — exatidão**
    - Para qualquer lista de turmas e qualquer ano de filtro, todas as turmas retornadas devem ter `semestre` iniciando com `"{ano}-"` e nenhuma turma de outro ano deve aparecer
    - **Validates: Requirements 1.2**

  - [ ] 5.4 Escrever property test para extração de anos distintos (Property 2)
    - **Property 2: Extração de anos distintos — completude e unicidade**
    - Para qualquer lista de semestres, os anos extraídos devem ser únicos e ordenados do mais recente ao mais antigo
    - **Validates: Requirements 1.1**

  - [ ] 5.5 Escrever property test para round-trip do estado do filtro (Property 3)
    - **Property 3: Estado do filtro refletido no contexto — round-trip**
    - Para qualquer ano válido submetido como parâmetro GET, `ano_selecionado` no contexto deve ser igual ao parâmetro
    - **Validates: Requirements 1.5**

- [ ] 6. Adicionar filtro por professor na listagem de temáticas
  - [ ] 6.1 Atualizar rota `GET /tematicas` em `main.py` para aceitar parâmetro `filtro_professor`
    - Adicionar parâmetro `filtro_professor: str = ""` à rota `listar_tematicas`
    - Buscar professores ativos: `db.query(User).filter(User.tipo == "PROFESSOR", User.ativo == True).order_by(User.nome).all()`
    - Aplicar filtro por `professor_id` somente quando `usuario.tipo in ("ADMIN", "COORDENADOR")` e `filtro_professor` não for vazio e for um ID válido (dígitos e registro existente); ignorar silenciosamente se inválido
    - Aplicar filtros de turma e professor de forma cumulativa (ambos ativos = interseção)
    - Passar `professores` e `filtro_professor` ao template
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.7_

  - [ ] 6.2 Adicionar controle de filtro por professor em `tematicas.html`
    - Dentro do bloco de filtro `<form method="get" action="/tematicas">` existente, adicionar `<select name="filtro_professor">` com "Todos os professores" como primeira opção e os professores de `professores`, marcando `selected` no professor correspondente a `filtro_professor`
    - Exibir o select apenas para `{% if usuario.tipo in ('ADMIN', 'COORDENADOR') %}`
    - _Requirements: 2.1, 2.6_

  - [ ] 6.3 Escrever property test para filtro de temáticas por professor (Property 4)
    - **Property 4: Filtro de temáticas por professor — exatidão**
    - Para qualquer conjunto de temáticas e qualquer `professor_id` válido, todas as retornadas devem ter `professor_id` igual ao filtro
    - **Validates: Requirements 2.2**

  - [ ] 6.4 Escrever property test para filtros compostos de temáticas (Property 5)
    - **Property 5: Filtros compostos de temáticas — interseção correta**
    - Para qualquer combinação de `filtro_turma` e `filtro_professor` ambos ativos, o resultado deve satisfazer simultaneamente ambos os critérios
    - **Validates: Requirements 2.3**

- [ ] 7. Checkpoint — Garantir que filtros e dashboard estejam corretos
  - Garantir que todos os testes passam. Verificar que filtros de turma, temática e professor funcionam isolados e combinados. Perguntar ao usuário se há dúvidas antes de continuar.

- [ ] 8. Implementar sidebar retrátil com localStorage
  - [ ] 8.1 Adicionar CSS da sidebar retrátil em `base_auth.html`
    - Definir variáveis `--sidebar-width` (16.666%) e `--sidebar-collapsed` (60px)
    - Adicionar regra `.sidebar.collapsed` que: define `width: var(--sidebar-collapsed)`, oculta `.nav-link-text` via `display:none` e oculta `.sidebar-section-label`
    - Adicionar `transition: width 250ms ease` à `.sidebar`
    - Ajustar `.main-content` para usar `width: calc(100% - var(--sidebar-width))` e transição correspondente; quando sidebar recolhida, `width: calc(100% - var(--sidebar-collapsed))`
    - _Requirements: 9.2, 9.3, 9.6, 9.7_

  - [ ] 8.2 Adicionar botão hamburger e envolver textos dos links em `base_auth.html`
    - Adicionar botão `<button id="sidebarToggle">` com ícone `bi-list` na navbar superior (antes do bloco de nome do usuário)
    - Envolver o texto de cada item de menu da sidebar em `<span class="nav-link-text">texto</span>`, mantendo os ícones `<i>` fora do span
    - Envolver os labels de seção (`.sidebar-section-label`) em elemento com classe que possa ser ocultado com `.collapsed`
    - _Requirements: 9.1_

  - [ ] 8.3 Adicionar JavaScript de toggle da sidebar com persistência em `localStorage` em `base_auth.html`
    - Implementar IIFE que: lê `localStorage.getItem('opi_sidebar_collapsed')` na inicialização, aplica estado (collapsed ou não), adiciona listener no `#sidebarToggle` e persiste estado via `try/catch` para não quebrar em modo privado
    - _Requirements: 9.4, 9.5_

- [ ] 9. Implementar botão de ações rápidas fixo (FAB)
  - [ ] 9.1 Adicionar HTML e CSS do FAB em `base_auth.html`
    - Adicionar container `position:fixed;bottom:24px;right:24px;z-index:1050` antes de `</body>` com botão principal `#fabBtn` (ícone `bi-plus-lg`) e container de itens `#fabMenu` com `display:none` por padrão
    - Cada item do FAB deve ser um `<a>` com ícone e label renderizado via condicional Jinja2 `{% if usuario.tipo == 'ALUNO' %}...{% elif usuario.tipo == 'PROFESSOR' %}...` etc., conforme as ações definidas nos Req 10.3–10.6
    - Estilizar o botão principal como circular (48x48px), com `background:var(--senac-blue)` e cor branca
    - _Requirements: 10.1, 10.3, 10.4, 10.5, 10.6_

  - [ ] 9.2 Adicionar JavaScript do FAB em `base_auth.html`
    - Toggle de abertura/fechamento: ao clicar em `#fabBtn`, alternar `display` do `#fabMenu` e trocar o ícone entre `bi-plus-lg` e `bi-x-lg`
    - Fechar ao clicar fora: adicionar listener `document.addEventListener('click', ...)` que fecha o menu quando o clique ocorre fora do container do FAB
    - _Requirements: 10.2, 10.7_

  - [ ] 9.3 Escrever property test para ações do FAB por tipo de usuário (Property 11)
    - **Property 11: Ações do FAB corretas por tipo de usuário**
    - Para cada tipo de usuário, verificar que o HTML renderizado do FAB contém exatamente as ações definidas — nem mais, nem menos
    - **Validates: Requirements 10.3, 10.4, 10.5, 10.6**

- [ ] 10. Implementar página de relatório por professor
  - [ ] 10.1 Criar rota `GET /relatorios/professor/{professor_id}` em `main.py`
    - Adicionar rota com verificação de tipo (`ADMIN`/`COORDENADOR`), busca do professor, cálculo de `dados_tematicas`, `total_tematicas`, `total_equipes`, `total_avaliacoes` conforme o design
    - Redirecionar para `/relatorios?erro=Professor+não+encontrado` se professor inexistente ou tipo incorreto
    - Redirecionar para `/dashboard` se usuário logado não for ADMIN/COORDENADOR
    - _Requirements: 4.1, 4.5, 4.7_

  - [ ] 10.2 Criar template `relatorio_professor.html`
    - Estender `base_auth.html`; exibir nome e e-mail do professor no topo
    - Exibir cards de totais (Temáticas, Equipes, Avaliações)
    - Exibir tabela com colunas: Temática, Turma, Status, Nº Equipes, Nº Avaliações
    - Exibir mensagem "Nenhuma temática associada a este professor." quando lista vazia; manter totais como zero
    - _Requirements: 4.2, 4.3, 4.4, 4.6_

  - [ ] 10.3 Adicionar link no nome do professor em `relatorios.html`
    - Atualizar a query `top_professores` em `main.py` para retornar `(professor.id, professor.nome, total)` em vez de `(nome, total)`
    - Em `relatorios.html`, na tabela "Professores mais ativos", envolver o nome do professor em `<a href="/relatorios/professor/{{ prof_id }}">` usando o id retornado
    - _Requirements: 4.1_

  - [ ] 10.4 Escrever property test para totais agregados do relatório (Property 8)
    - **Property 8: Totais agregados do relatório de professor — invariância aritmética**
    - Para qualquer lista de `dados_tematicas` com `n_equipes` e `n_avaliacoes`, `total_equipes` deve ser a soma de todos os `n_equipes` e `total_avaliacoes` a soma de todos os `n_avaliacoes`
    - **Validates: Requirements 4.4**

- [ ] 11. Checkpoint — Garantir que relatório de professor esteja correto
  - Garantir que todos os testes passam. Verificar que o link na tabela de professores navega para `/relatorios/professor/{id}` corretamente e que a página exibe os dados esperados. Perguntar ao usuário se há dúvidas antes de continuar.

- [ ] 12. Implementar upload e exibição de fotos de perfil
  - [ ] 12.1 Adicionar campo `foto_perfil` ao modelo `User` em `models/user.py`
    - Adicionar `foto_perfil = Column(String, nullable=True, default=None)` ao final dos campos da classe `User`
    - Criar script de migração manual em comentário ou arquivo separado: `ALTER TABLE users ADD COLUMN foto_perfil TEXT;`
    - _Requirements: 6.1, 6.2_

  - [ ] 12.2 Criar diretório `static/avatars/` e registrar arquivos estáticos em `main.py`
    - Criar diretório `observatorio_pi/app/static/avatars/` (com arquivo `.gitkeep` para persistência no git)
    - Adicionar `app.mount("/static", StaticFiles(directory=...), name="static")` em `main.py` com `os.makedirs(..., exist_ok=True)` no startup
    - Importar `StaticFiles` de `fastapi.staticfiles`
    - _Requirements: 6.2_

  - [ ] 12.3 Criar rota `POST /meu-perfil/foto` em `main.py` ou `user_router.py`
    - Aceitar `UploadFile` via `multipart/form-data`
    - Validar tipo MIME (`image/jpeg`, `image/png`, `image/webp`) e tamanho ≤ 2 MB; em caso de falha, redirecionar com `?erro=Arquivo+inválido.+Envie+uma+imagem+JPEG%2C+PNG+ou+WebP+com+até+2+MB`
    - Salvar arquivo como `avatar_{usuario.id}.{ext}` em `static/avatars/`; atualizar `usuario.foto_perfil` com o caminho relativo
    - _Requirements: 6.2, 6.3, 6.6_

  - [ ] 12.4 Criar macro `avatar(u, size=32)` em `base_auth.html`
    - Se `u.foto_perfil` existir: renderizar `<img src="/static/{{ u.foto_perfil }}" style="width:{{ size }}px;height:{{ size }}px;border-radius:50%;object-fit:cover;">`
    - Caso contrário: renderizar `<div>` circular com inicial colorida (lógica existente em `perfil_aluno.html`)
    - _Requirements: 6.4, 6.5_

  - [ ] 12.5 Aplicar macro `avatar` nos locais onde avatares são exibidos
    - `base_auth.html` navbar superior: substituir o avatar de inicial pelo `{{ avatar(usuario, 28) }}`
    - `equipe_detalhe.html` lista de membros: substituir os divs de inicial pelo `{{ avatar(membro, 28) }}`
    - `perfil_aluno.html` card de perfil: substituir div de avatar pelo `{{ avatar(perfil, 80) }}`
    - _Requirements: 6.4, 6.5_

  - [ ] 12.6 Adicionar campo de upload de foto no formulário de edição de perfil do aluno em `perfil_aluno.html`
    - No modal `#modalEditarPerfil`, adicionar campo `<input type="file" name="foto" accept="image/jpeg,image/png,image/webp">` com enctype `multipart/form-data` no formulário
    - Exibir preview da foto atual se existir
    - _Requirements: 6.1_

  - [ ] 12.7 Escrever property test para validação de upload de foto (Property 9)
    - **Property 9: Validação de upload de foto — rejeição de arquivos inválidos**
    - Para qualquer arquivo com tipo MIME fora do conjunto permitido ou tamanho > 2 MB, a rota de upload deve rejeitar sem alterar `foto_perfil`
    - **Validates: Requirements 6.3**

  - [ ] 12.8 Escrever property test para URL de perfil por tipo de usuário (Property 10)
    - **Property 10: URL de perfil correta por tipo de usuário**
    - Para qualquer usuário com tipo válido e qualquer `id`, `_url_perfil(usuario)` deve retornar URL contendo o `id` e o path correto para aquele tipo
    - **Validates: Requirements 7.1, 7.2, 7.3, 7.4**

- [ ] 13. Implementar perfis por tipo de usuário e redirecionamento pelo nome/foto
  - [ ] 13.1 Adicionar função `_url_perfil` e registrá-la como global Jinja2 em `main.py`
    - Implementar `_url_perfil(usuario: User) -> str` com mapeamento por tipo (ALUNO → `/alunos/{id}`, PROFESSOR → `/perfil/professor/{id}`, COORDENADOR/ADMIN → `/perfil/coordenador/{id}`, EMPRESA → `/perfil/empresa/{id}`)
    - Registrar em `templates.env.globals["url_perfil"] = _url_perfil`
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

  - [ ] 13.2 Tornar o bloco de nome/foto da navbar superior clicável em `base_auth.html`
    - Envolver o bloco `<span class="text-white-50 small d-none d-sm-flex...">` em `<a href="{{ url_perfil(usuario) }}" class="text-decoration-none">` com estilos adequados para manter a aparência atual
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

  - [ ] 13.3 Remover item "Meu Perfil" da sidebar em `base_auth.html`
    - Remover o bloco `{% if usuario.tipo == 'ALUNO' %}<li class="nav-item"><a ... href="/meu-perfil">Meu Perfil</a></li>{% endif %}` da sidebar
    - _Requirements: 7.6_

  - [ ] 13.4 Criar rota `GET /perfil/professor/{professor_id}` e template `perfil_professor.html`
    - Rota em `main.py`: buscar professor, detectar se `usuario.id == professor_id` para habilitar edição, retornar template com `perfil`, `eh_proprio`, `active_page="tematicas"`
    - Template: estender `base_auth.html`; exibir nome, e-mail, badge de tipo; se `eh_proprio`, exibir botão/modal de edição dos campos de perfil permitidos para professor (bio, cidade, telefone); modo somente leitura para outros usuários
    - _Requirements: 7.2, 7.5, 7.7_

  - [ ] 13.5 Criar rota `GET /perfil/coordenador/{coordenador_id}` e template `perfil_coordenador.html`
    - Semelhante à rota do professor; tipos COORDENADOR e ADMIN compartilham este perfil (conforme `_url_perfil`)
    - Template: exibir nome, e-mail, badge de tipo; formulário de edição quando `eh_proprio`
    - _Requirements: 7.3, 7.5, 7.7_

  - [ ] 13.6 Criar rota `GET /perfil/empresa/{empresa_id}` e template `perfil_empresa.html`
    - Rota e template análogos; tipo EMPRESA compartilha campos de perfil adequados (nome, cidade, bio, telefone, linkedin)
    - _Requirements: 7.4, 7.5, 7.7_

  - [ ] 13.7 Adicionar campo de upload de foto nos novos templates de perfil (professor, coordenador, empresa)
    - Em cada novo template de perfil, no formulário de edição (modo `eh_proprio`), adicionar campo de upload de foto com `accept="image/jpeg,image/png,image/webp"` e `enctype="multipart/form-data"`
    - _Requirements: 6.1_

- [ ] 14. Checkpoint final — Garantir que todos os testes passam
  - Garantir que todos os testes passam. Verificar que o redirecionamento pelo clique no nome/foto funciona para todos os tipos de usuário. Verificar que o upload de foto funciona e que o avatar aparece nos locais corretos. Perguntar ao usuário se há dúvidas antes de finalizar.

---

## Notes

- Tasks marcadas com `*` são opcionais e podem ser puladas para uma entrega mais rápida
- Cada task referencia os requisitos específicos para rastreabilidade
- Os checkpoints garantem validação incremental antes de avançar para funcionalidades mais complexas
- Os property tests devem ser criados em `tests/test_properties.py` com `hypothesis` e pytest; instalar via `pip install hypothesis pytest`
- O script de migração SQL (`ALTER TABLE users ADD COLUMN foto_perfil TEXT;`) deve ser executado manualmente em bancos existentes antes de rodar a aplicação após a task 12.1
- As property tests validam invariantes matemáticas e de filtragem que são difíceis de cobrir com exemplos unitários

---

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1"] },
    { "id": 1, "tasks": ["1.2", "1.3", "3.1", "3.2"] },
    { "id": 2, "tasks": ["4.1"] },
    { "id": 3, "tasks": ["4.2", "4.3", "5.1"] },
    { "id": 4, "tasks": ["5.2", "5.3", "5.4", "5.5", "6.1"] },
    { "id": 5, "tasks": ["6.2", "6.3", "6.4", "8.1"] },
    { "id": 6, "tasks": ["8.2", "9.1"] },
    { "id": 7, "tasks": ["8.3", "9.2", "9.3", "10.1"] },
    { "id": 8, "tasks": ["10.2", "10.3"] },
    { "id": 9, "tasks": ["10.4", "12.1"] },
    { "id": 10, "tasks": ["12.2", "12.3"] },
    { "id": 11, "tasks": ["12.4"] },
    { "id": 12, "tasks": ["12.5", "12.6", "12.7", "13.1"] },
    { "id": 13, "tasks": ["12.8", "13.2", "13.3", "13.4"] },
    { "id": 14, "tasks": ["13.5", "13.6"] },
    { "id": 15, "tasks": ["13.7"] }
  ]
}
```
