# Requirements Document

## Introduction

Este documento descreve as melhorias de interface e novas funcionalidades a serem implementadas no **Observatório de Projetos Integradores (OPI)**, uma aplicação FastAPI com templates Jinja2/HTML, SQLAlchemy e SQLite. As melhorias abrangem filtros de navegação, correções de usabilidade, aprimoramentos visuais (fotos de perfil, nav-bar retrátil), expansão das páginas de relatórios e perfil, e um mecanismo de ações rápidas global.

---

## Glossary

- **OPI**: Observatório de Projetos Integradores — o sistema descrito neste documento.
- **Sistema**: A aplicação FastAPI/Jinja2 do OPI.
- **Usuário**: Qualquer pessoa autenticada no Sistema (ALUNO, PROFESSOR, COORDENADOR, ADMIN ou EMPRESA).
- **Aluno**: Usuário com tipo `ALUNO`.
- **Professor**: Usuário com tipo `PROFESSOR`.
- **Coordenador**: Usuário com tipo `COORDENADOR`.
- **Admin**: Usuário com tipo `ADMIN`.
- **Empresa**: Usuário com tipo `EMPRESA`.
- **Turma**: Entidade que agrupa temáticas por período letivo; possui campos `nome`, `semestre` e `ativa`.
- **Tematica**: Proposta de projeto vinculada a uma Turma e a um Professor responsável.
- **Equipe**: Grupo de alunos vinculado a uma Temática.
- **Avaliação**: Registro de conceito atribuído pelo Professor a uma Equipe.
- **Conceito**: Valor de avaliação (`INSUFICIENTE`, `REGULAR`, `BOM`, `OTIMO`, `EXCELENTE`).
- **Foto_de_Perfil**: Imagem associada ao cadastro de um Usuário, armazenada no servidor.
- **Nav-bar_Lateral**: Barra de navegação lateral (sidebar) exibida em todas as páginas autenticadas.
- **Nav-bar_Superior**: Barra de navegação horizontal fixa no topo das páginas autenticadas.
- **Botao_de_Acoes_Rapidas**: Elemento de UI flutuante fixo presente em todas as páginas autenticadas que oferece atalhos contextuais às operações mais frequentes.
- **Perfil_do_Usuário**: Página que exibe e permite editar os dados pessoais do Usuário logado ou de terceiros (conforme permissão).

---

## Requirements

### Requisito 1: Filtro por Ano na Listagem de Turmas

**User Story:** Como Coordenador ou Admin, quero filtrar as turmas por ano, para encontrar rapidamente as turmas de um período letivo específico sem precisar percorrer toda a lista.

#### Critérios de Aceitação

1. THE Sistema SHALL exibir, na página `/turmas`, um controle do tipo lista de seleção contendo a opção "Todos os anos" seguida dos anos distintos extraídos do campo `semestre` das Turmas cadastradas, onde o ano é o segmento de 4 dígitos localizado antes do separador `-` no valor do campo `semestre` (ex.: `"2025-1"` → `"2025"`), ordenados do mais recente ao mais antigo.
2. WHEN o Usuário seleciona um ano no controle de filtro e submete o formulário via requisição GET com o parâmetro `ano` contendo o ano selecionado, THE Sistema SHALL retornar somente as Turmas cujo campo `semestre` inicia com o valor do ano selecionado seguido do caractere `-`.
3. WHEN o Usuário submete o formulário com a opção "Todos os anos" selecionada, ou quando a página `/turmas` é acessada sem o parâmetro `ano` na requisição, THE Sistema SHALL exibir todas as Turmas cadastradas sem restrição de ano.
4. IF não existirem Turmas cadastradas para o ano selecionado, THEN THE Sistema SHALL exibir a mensagem "Nenhuma turma encontrada para o ano selecionado." na área de resultados, substituindo a tabela de turmas.
5. WHEN a página `/turmas` é retornada após a aplicação de um filtro por ano, THE Sistema SHALL exibir o ano correspondente ao filtro aplicado como a opção selecionada no controle de lista de seleção.

---

### Requisito 2: Filtro por Professor na Listagem de Temáticas

**User Story:** Como Coordenador ou Admin, quero filtrar as temáticas por professor responsável, para visualizar rapidamente o conjunto de projetos sob responsabilidade de cada docente.

#### Critérios de Aceitação

1. THE Sistema SHALL exibir, na página `/tematicas`, um controle do tipo lista de seleção populado com os Usuários ativos do tipo `PROFESSOR`, ordenados por nome, contendo a opção inicial "Todos os professores", disponível exclusivamente para Usuários com tipo `ADMIN` ou `COORDENADOR`.
2. WHEN um Usuário do tipo `ADMIN` ou `COORDENADOR` seleciona um Professor no filtro e submete o formulário, THE Sistema SHALL retornar somente as Temáticas cujo `professor_id` corresponde ao Professor selecionado, excluindo Temáticas com `professor_id` nulo.
3. WHEN os filtros de turma e professor estão ambos ativos na requisição, THE Sistema SHALL aplicar os dois critérios de forma cumulativa (interseção), retornando somente Temáticas que satisfazem simultaneamente ambos os filtros.
4. WHEN o Usuário submete o formulário com a opção "Todos os professores" selecionada, ou quando a página `/tematicas` é acessada sem o parâmetro `filtro_professor`, THE Sistema SHALL exibir todas as Temáticas sem restrição de professor.
5. IF não existirem Temáticas para o Professor selecionado com os demais filtros ativos, THEN THE Sistema SHALL exibir a mensagem "Nenhuma temática encontrada." na área de resultados.
6. IF a página `/tematicas` é retornada após submissão do filtro de professor com um `filtro_professor` válido, THEN THE Sistema SHALL exibir o Professor correspondente como a opção selecionada no controle de lista de seleção.
7. IF a página `/tematicas` recebe o parâmetro `filtro_professor` com um valor inexistente ou inválido, THEN THE Sistema SHALL ignorar o parâmetro e retornar todas as Temáticas sem restrição de professor, exibindo "Todos os professores" como opção selecionada.

---

### Requisito 3: Correção da Seleção de Conceito na Avaliação Geral da Equipe

**User Story:** Como Professor, quero que o conceito previamente salvo de cada critério apareça corretamente selecionado ao abrir o formulário de avaliação, para não precisar reatribuir manualmente os conceitos ao atualizar uma avaliação.

#### Critérios de Aceitação

1. WHEN o Professor acessa a página `/equipes/{equipe_id}` e já existe uma Avaliação registrada para a Equipe, THE Sistema SHALL pré-selecionar, para cada critério de avaliação (`conceito_conteudo`, `conceito_tecnica`, `conceito_apresentacao`, `conceito_inovacao`, `conceito_equipe`, `conceito_final`), o radio button cujo atributo `value` corresponde exatamente ao valor do Conceito salvo na Avaliação.
2. IF o valor renderizado do atributo `value` de um radio button para um critério não corresponder exatamente ao Conceito armazenado na Avaliação, THEN THE Sistema SHALL NÃO renderizar o atributo `checked` para esse radio button, garantindo que apenas um radio button por critério receba o atributo `checked`.
3. WHEN o Professor acessa a página `/equipes/{equipe_id}` e não existe Avaliação prévia registrada para a Equipe, THE Sistema SHALL pré-selecionar o radio button correspondente ao Conceito `BOM` para todos os critérios de avaliação.
4. WHEN o Professor submete o formulário de avaliação com novos valores e a submissão é processada com sucesso, THE Sistema SHALL persistir os novos Conceitos e, ao renderizar novamente a página `/equipes/{equipe_id}`, SHALL exibir os radio buttons correspondentes aos Conceitos recém-salvos com o atributo `checked`.

---

### Requisito 4: Página de Detalhes do Professor nos Relatórios

**User Story:** Como Coordenador ou Admin, quero clicar no nome de um professor na seção de relatórios e ver as temáticas pelas quais ele é responsável junto com os dados agregados dessas temáticas, para acompanhar a carga de orientação de cada docente.

#### Critérios de Aceitação

1. WHEN o Usuário clica no nome de um Professor na tabela "Professores mais ativos" da página `/relatorios`, THE Sistema SHALL redirecionar o Usuário para a página `/relatorios/professor/{professor_id}`.
2. THE Sistema SHALL exibir, na página `/relatorios/professor/{professor_id}`, o nome completo e o e-mail do Professor.
3. THE Sistema SHALL exibir, na página `/relatorios/professor/{professor_id}`, a lista de Temáticas pelas quais o Professor é responsável, contendo para cada Temática: título, nome da Turma vinculada, status da Temática, número de Equipes vinculadas à Temática e número de registros de `Avaliacao` (avaliação coletiva de equipe) onde o `professor_id` corresponde ao Professor e cuja `equipe_id` pertence à Temática.
4. THE Sistema SHALL exibir, na página `/relatorios/professor/{professor_id}`, os seguintes totais agregados: soma total de Temáticas pelas quais o Professor é responsável, soma total de Equipes vinculadas a essas Temáticas e soma total de registros de `Avaliacao` realizados pelo Professor nessas Equipes.
5. IF o Professor com o `professor_id` informado não for encontrado no banco de dados ou não possuir tipo `PROFESSOR`, THEN THE Sistema SHALL redirecionar o Usuário para `/relatorios?erro=Professor+não+encontrado`.
6. IF o Professor não possuir Temáticas associadas, THEN THE Sistema SHALL exibir a mensagem "Nenhuma temática associada a este professor." no lugar da lista de Temáticas, e exibir zero nos totais agregados.
7. IF o Usuário que acessa `/relatorios/professor/{professor_id}` não possuir tipo `ADMIN` ou `COORDENADOR`, THEN THE Sistema SHALL redirecionar o Usuário para `/dashboard`.

---

### Requisito 5: Remoção das Informações de Usuário do Rodapé da Nav-bar Lateral

**User Story:** Como Usuário autenticado, quero que meu nome e e-mail não apareçam no canto inferior esquerdo da nav-bar lateral, para que a interface fique mais limpa e as informações de identidade fiquem centralizadas no canto superior direito.

#### Critérios de Aceitação

1. THE Sistema SHALL remover da Nav-bar_Lateral o bloco de conteúdo que exibe o nome e o avatar do Usuário na posição inferior da sidebar, de modo que nenhum nome, e-mail ou avatar do Usuário seja exibido na Nav-bar_Lateral.
2. WHILE o Usuário está autenticado e acessa qualquer página em telas com largura mínima de 576px, THE Sistema SHALL exibir o nome completo do Usuário logado no canto superior direito da Nav-bar_Superior.
3. WHILE o Usuário está autenticado e acessa qualquer página em telas com largura mínima de 576px, THE Sistema SHALL exibir o e-mail do Usuário logado abaixo do nome na Nav-bar_Superior, truncando o endereço com reticências (`…`) se o comprimento exceder 30 caracteres visíveis.
4. WHILE o Usuário está autenticado e acessa qualquer página em telas com largura mínima de 576px, THE Sistema SHALL exibir o badge de tipo do Usuário (`ALUNO`, `PROFESSOR`, `COORDENADOR`, `ADMIN` ou `EMPRESA`) ao lado do nome na Nav-bar_Superior.

---

### Requisito 6: Fotos de Perfil para Usuários

**User Story:** Como Usuário autenticado, quero poder fazer upload de uma foto de perfil, para personalizar minha identidade visual no sistema e substituir o avatar gerado por inicial.

#### Critérios de Aceitação

1. THE Sistema SHALL disponibilizar, nas páginas de edição de perfil dos tipos `ALUNO`, `PROFESSOR`, `COORDENADOR` e `EMPRESA`, um campo de upload de imagem para foto de perfil.
2. WHEN o Usuário seleciona e submete um arquivo de imagem com formato JPEG, PNG ou WebP e tamanho até 2 MB na página de edição do seu perfil, THE Sistema SHALL salvar o arquivo com um nome único vinculado ao identificador do Usuário e associar o caminho do arquivo ao registro do Usuário no banco de dados.
3. IF o Usuário submete um arquivo cujo tamanho excede 2 MB ou cujo tipo MIME não é `image/jpeg`, `image/png` ou `image/webp`, THEN THE Sistema SHALL exibir a mensagem "Arquivo inválido. Envie uma imagem JPEG, PNG ou WebP com até 2 MB." e não alterar a foto de perfil existente.
4. WHEN o registro do Usuário possui uma foto de perfil associada, THE Sistema SHALL substituir o avatar gerado por inicial pela foto de perfil do Usuário em todos os locais onde avatares de Usuário são exibidos (incluindo: Nav-bar_Superior, cards de membros de equipe, seção de equipes recentes no dashboard do aluno e páginas de perfil).
5. WHILE o registro do Usuário não possui foto de perfil associada, THE Sistema SHALL exibir o avatar gerado por inicial como fallback em todos os locais onde avatares são exibidos.
6. WHEN o Usuário submete uma nova foto de perfil com sucesso, THE Sistema SHALL substituir a foto de perfil anterior, mantendo apenas a imagem mais recente associada ao Usuário.

---

### Requisito 7: Redirecionamento ao Perfil pelo Clique no Nome/Foto do Usuário na Nav-bar Superior

**User Story:** Como Usuário autenticado, quero que clicar no meu nome ou foto no canto superior direito me redirecione para minha página de perfil, para acessar e editar meus dados sem precisar de uma aba dedicada "Meu Perfil" na nav-bar lateral.

#### Critérios de Aceitação

1. WHEN o Usuário do tipo `ALUNO` clica no seu nome ou foto na Nav-bar_Superior, THE Sistema SHALL redirecionar o Usuário para a página de perfil de aluno correspondente ao seu identificador.
2. WHEN o Usuário do tipo `PROFESSOR` clica no seu nome ou foto na Nav-bar_Superior, THE Sistema SHALL redirecionar o Usuário para a página de perfil de professor correspondente ao seu identificador.
3. WHEN o Usuário do tipo `COORDENADOR` ou `ADMIN` clica no seu nome ou foto na Nav-bar_Superior, THE Sistema SHALL redirecionar o Usuário para a página de perfil de coordenador correspondente ao seu identificador.
4. WHEN o Usuário do tipo `EMPRESA` clica no seu nome ou foto na Nav-bar_Superior, THE Sistema SHALL redirecionar o Usuário para a página de perfil de empresa correspondente ao seu identificador.
5. THE Sistema SHALL criar páginas de perfil dedicadas para os tipos `PROFESSOR`, `COORDENADOR` e `EMPRESA`, exibindo os dados pessoais do respectivo Usuário e disponibilizando edição dos campos permitidos para cada tipo.
6. IF o item "Meu Perfil" existir na Nav-bar_Lateral, THEN THE Sistema SHALL remover esse item da navegação, uma vez que o acesso ao perfil passa a ser realizado exclusivamente pelo clique no nome ou foto na Nav-bar_Superior.
7. WHEN um Usuário autenticado tenta acessar diretamente a URL de perfil de outro Usuário de tipo diferente do seu, THE Sistema SHALL exibir os dados do perfil solicitado em modo somente leitura, sem disponibilizar edição.

---

### Requisito 8: Nome do Professor nas Equipes Recentes do Dashboard do Aluno

**User Story:** Como Aluno, quero ver o nome do professor responsável pela temática nas equipes exibidas na seção "Equipes Recentes" do meu dashboard, para identificar rapidamente quem orienta cada projeto.

#### Critérios de Aceitação

1. WHEN o Usuário do tipo `ALUNO` acessa o dashboard e a seção "Equipes Recentes" exibe ao menos uma Equipe, THE Sistema SHALL exibir uma coluna com o cabeçalho "Professor" contendo o nome completo do Professor responsável pela Temática de cada Equipe, com as equipes ordenadas pela data de criação em ordem decrescente.
2. IF o campo `professor_id` da Temática vinculada a uma Equipe for nulo, ou se a Temática da Equipe não estiver associada a nenhum Professor, THEN THE Sistema SHALL exibir o caractere "—" na coluna "Professor" da linha correspondente à Equipe.
3. THE Sistema SHALL exibir o nome do Professor como texto simples de leitura, sem elemento âncora ou link, nas linhas da tabela "Equipes Recentes" do dashboard do Aluno.

---

### Requisito 9: Nav-bar Lateral Retrátil

**User Story:** Como Usuário autenticado, quero poder recolher e expandir a nav-bar lateral por meio de um botão com ícone de três traços, para ganhar mais espaço horizontal no conteúdo principal quando necessário.

#### Critérios de Aceitação

1. WHILE o Usuário está autenticado e visualiza qualquer página, THE Sistema SHALL exibir um botão com ícone de três traços (hamburger) na Nav-bar_Superior, visível em todas as páginas autenticadas.
2. WHEN o Usuário clica no botão hamburger e a Nav-bar_Lateral está expandida, THE Sistema SHALL recolher a Nav-bar_Lateral, ocultando os textos dos itens de menu e exibindo apenas os ícones.
3. WHEN o Usuário clica no botão hamburger e a Nav-bar_Lateral está recolhida, THE Sistema SHALL expandir a Nav-bar_Lateral, restaurando a exibição completa dos textos dos itens de menu.
4. WHEN a página é carregada, THE Sistema SHALL verificar o `localStorage` do navegador em busca do estado salvo da Nav-bar_Lateral e aplicar o estado salvo (expandido ou recolhido); IF nenhum valor estiver salvo no `localStorage`, THEN THE Sistema SHALL exibir a Nav-bar_Lateral no estado expandido por padrão.
5. IF o `localStorage` do navegador não estiver disponível, THEN THE Sistema SHALL manter o estado da Nav-bar_Lateral funcional durante a sessão atual sem persistência entre páginas, exibindo a Nav-bar_Lateral como expandida ao carregar cada página.
6. WHILE a Nav-bar_Lateral está recolhida, THE Sistema SHALL expandir a área de conteúdo principal para ocupar 100% do espaço horizontal disponível excluindo a largura da Nav-bar_Lateral recolhida.
7. WHEN o botão hamburger é acionado para expandir ou recolher a Nav-bar_Lateral, THE Sistema SHALL animar a transição com duração entre 200ms e 300ms.

---

### Requisito 10: Botão de Ações Rápidas Fixo Global

**User Story:** Como Usuário autenticado, quero ter um botão de ações rápidas fixo (floating action button) em todas as páginas do sistema, para acessar as operações mais frequentes sem precisar rolar a página ou navegar até o dashboard.

#### Critérios de Aceitação

1. THE Sistema SHALL exibir um Botao_de_Acoes_Rapidas com posição fixa no canto inferior direito da viewport em todas as páginas autenticadas, mantendo margem mínima de 16px em relação às bordas inferior e direita da viewport.
2. WHEN o Usuário clica no Botao_de_Acoes_Rapidas enquanto o menu está fechado, THE Sistema SHALL expandir um menu contendo as ações definidas para o tipo do Usuário logado, com no máximo 5 itens de ação visíveis; WHEN o Usuário clica no Botao_de_Acoes_Rapidas enquanto o menu está aberto, THE Sistema SHALL fechar o menu.
3. IF o Usuário logado possuir tipo `ALUNO`, THEN THE Sistema SHALL exibir no menu as ações: navegar para a listagem de temáticas, navegar para o portfólio e navegar para o perfil do aluno logado.
4. IF o Usuário logado possuir tipo `PROFESSOR`, THEN THE Sistema SHALL exibir no menu as ações: navegar para a listagem de temáticas e navegar para o portfólio.
5. IF o Usuário logado possuir tipo `COORDENADOR`, THEN THE Sistema SHALL exibir no menu as ações: criar nova turma, criar nova temática e navegar para relatórios. IF o Usuário logado possuir tipo `ADMIN`, THEN THE Sistema SHALL exibir as mesmas ações do `COORDENADOR` acrescidas da ação de criar novo usuário.
6. IF o Usuário logado possuir tipo `EMPRESA`, THEN THE Sistema SHALL exibir no menu a ação: navegar para o portfólio.
7. WHEN o Usuário clica em qualquer área da página fora do menu expandido do Botao_de_Acoes_Rapidas, THE Sistema SHALL fechar o menu sem executar nenhuma ação de navegação.
8. WHILE o menu do Botao_de_Acoes_Rapidas está aberto ou fechado, THE Sistema SHALL garantir que o botão e seu menu não sobreponham nenhum elemento focalizável ou clicável renderizado pela página, recalculando a posição se necessário.
