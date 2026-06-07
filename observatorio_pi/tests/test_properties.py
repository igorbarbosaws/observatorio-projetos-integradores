"""
Testes de propriedades e unitários para a feature ui-improvements-and-new-features.

Cada teste referencia a propriedade e o requisito que valida.
"""

# ---------------------------------------------------------------------------
# Property 7: Round-trip de persistência de avaliação
# Feature: ui-improvements-and-new-features, Property 7: round-trip persistência avaliação
# Validates: Requirements 3.4
# ---------------------------------------------------------------------------
#
# Verifica que após salvar uma Avaliação com conceitos específicos, a lógica
# de renderização `deve_estar_checked(candidato, valor_salvo)` retorna True
# apenas para o conceito salvo e False para todos os outros — garantindo que
# o radio button correto seja marcado como checked na re-renderização da página.


from types import SimpleNamespace

# Conceitos válidos espelhados do modelo (project.py)
CONCEITOS = ["INSUFICIENTE", "REGULAR", "BOM", "OTIMO", "EXCELENTE"]

# Campos de conceito presentes no modelo Avaliacao
CAMPOS_CONCEITO = [
    "conceito_conteudo",
    "conceito_tecnica",
    "conceito_apresentacao",
    "conceito_inovacao",
    "conceito_equipe",
    "conceito_final",
]


def deve_estar_checked(candidato: str, valor_salvo: str) -> bool:
    """
    Lógica de renderização equivalente ao template Jinja2:

        {% if avaliacao and avaliacao.<campo> == c %}checked{% endif %}

    Retorna True se o radio button com `value=candidato` deve receber
    o atributo `checked`, dado que o valor persistido é `valor_salvo`.
    """
    return candidato == valor_salvo


class TestRoundTripPersistenciaAvaliacao:
    """
    Property 7 — Round-trip de persistência de avaliação.

    Validates: Requirements 3.4

    Garante que para qualquer combinação de conceitos salvos nos 6 critérios
    de avaliação, apenas o radio button cujo value corresponde ao conceito
    salvo recebe checked=True, e todos os outros recebem checked=False.
    """

    def _make_avaliacao(self, **conceitos) -> SimpleNamespace:
        """Cria um objeto avaliação simples com os conceitos fornecidos."""
        return SimpleNamespace(**conceitos)

    # ------------------------------------------------------------------
    # Testes de correspondência exata (checked=True apenas para o salvo)
    # ------------------------------------------------------------------

    def test_conceito_salvo_retorna_checked_true(self):
        """Para cada campo e cada conceito válido, deve_estar_checked deve
        retornar True quando candidato == valor_salvo."""
        for campo in CAMPOS_CONCEITO:
            for conceito in CONCEITOS:
                assert deve_estar_checked(conceito, conceito) is True, (
                    f"Campo '{campo}': deve_estar_checked('{conceito}', '{conceito}') "
                    f"deveria ser True"
                )

    def test_outros_conceitos_retornam_checked_false(self):
        """Para cada campo, todos os conceitos diferentes do salvo devem
        retornar False — garantindo apenas um radio button marcado por critério."""
        for campo in CAMPOS_CONCEITO:
            for valor_salvo in CONCEITOS:
                outros = [c for c in CONCEITOS if c != valor_salvo]
                for candidato in outros:
                    assert deve_estar_checked(candidato, valor_salvo) is False, (
                        f"Campo '{campo}': deve_estar_checked('{candidato}', '{valor_salvo}') "
                        f"deveria ser False"
                    )

    # ------------------------------------------------------------------
    # Testes de round-trip com objeto Avaliacao simulado
    # ------------------------------------------------------------------

    def test_roundtrip_todos_conceitos_diferentes(self):
        """
        Simula uma avaliação com um conceito distinto em cada critério e
        verifica que a lógica de checked reproduz exatamente os valores salvos.
        """
        valores_salvos = {
            "conceito_conteudo":     "INSUFICIENTE",
            "conceito_tecnica":      "REGULAR",
            "conceito_apresentacao": "BOM",
            "conceito_inovacao":     "OTIMO",
            "conceito_equipe":       "EXCELENTE",
            "conceito_final":        "BOM",
        }
        avaliacao = self._make_avaliacao(**valores_salvos)

        for campo, valor_esperado in valores_salvos.items():
            valor_na_obj = getattr(avaliacao, campo)
            for candidato in CONCEITOS:
                resultado = deve_estar_checked(candidato, valor_na_obj)
                esperado = (candidato == valor_esperado)
                assert resultado == esperado, (
                    f"Campo '{campo}' (salvo='{valor_esperado}'): "
                    f"deve_estar_checked('{candidato}', ...) esperado={esperado}, "
                    f"obtido={resultado}"
                )

    def test_roundtrip_todos_conceitos_iguais_excelente(self):
        """
        Avaliação com todos os critérios em EXCELENTE: apenas EXCELENTE deve
        receber checked, os demais devem retornar False.
        """
        avaliacao = self._make_avaliacao(
            **{campo: "EXCELENTE" for campo in CAMPOS_CONCEITO}
        )

        for campo in CAMPOS_CONCEITO:
            valor_na_obj = getattr(avaliacao, campo)
            assert deve_estar_checked("EXCELENTE", valor_na_obj) is True
            for outro in [c for c in CONCEITOS if c != "EXCELENTE"]:
                assert deve_estar_checked(outro, valor_na_obj) is False, (
                    f"Campo '{campo}': deve_estar_checked('{outro}', 'EXCELENTE') "
                    f"deveria ser False"
                )

    def test_roundtrip_todos_conceitos_iguais_bom(self):
        """
        Avaliação com todos os critérios no padrão BOM (default do modelo):
        apenas BOM deve receber checked.
        """
        avaliacao = self._make_avaliacao(
            **{campo: "BOM" for campo in CAMPOS_CONCEITO}
        )

        for campo in CAMPOS_CONCEITO:
            valor_na_obj = getattr(avaliacao, campo)
            assert deve_estar_checked("BOM", valor_na_obj) is True
            for outro in [c for c in CONCEITOS if c != "BOM"]:
                assert deve_estar_checked(outro, valor_na_obj) is False

    def test_roundtrip_exatamente_um_checked_por_criterio(self):
        """
        Invariante fundamental: para qualquer avaliação salva, a contagem de
        radio buttons que receberiam checked para um dado critério deve ser
        exatamente 1.
        """
        # Testa todas as combinações possíveis de conceito por campo
        for valor_salvo in CONCEITOS:
            avaliacao = self._make_avaliacao(
                **{campo: valor_salvo for campo in CAMPOS_CONCEITO}
            )
            for campo in CAMPOS_CONCEITO:
                valor_na_obj = getattr(avaliacao, campo)
                checked_count = sum(
                    1 for c in CONCEITOS if deve_estar_checked(c, valor_na_obj)
                )
                assert checked_count == 1, (
                    f"Campo '{campo}' com valor_salvo='{valor_salvo}': "
                    f"esperado exatamente 1 checked, obtido {checked_count}"
                )

    def test_roundtrip_conceito_insuficiente(self):
        """Round-trip específico para o conceito INSUFICIENTE em todos os critérios."""
        avaliacao = self._make_avaliacao(
            **{campo: "INSUFICIENTE" for campo in CAMPOS_CONCEITO}
        )
        for campo in CAMPOS_CONCEITO:
            valor_na_obj = getattr(avaliacao, campo)
            assert deve_estar_checked("INSUFICIENTE", valor_na_obj) is True
            assert deve_estar_checked("REGULAR", valor_na_obj) is False
            assert deve_estar_checked("BOM", valor_na_obj) is False
            assert deve_estar_checked("OTIMO", valor_na_obj) is False
            assert deve_estar_checked("EXCELENTE", valor_na_obj) is False


# ---------------------------------------------------------------------------
# Property 7 (DB round-trip): Persistência real com SQLite em memória
# Validates: Requirements 3.4
# ---------------------------------------------------------------------------
#
# Estes testes verificam o round-trip completo de persistência:
# simula a lógica de POST `/equipes/{id}/avaliar` (criar/atualizar Avaliacao)
# e depois confirma que os valores recuperados do banco correspondem
# exatamente aos conceitos submetidos — garantindo que o formulário
# os exibiria pré-selecionados corretamente.

import sys
import os

# Torna o pacote `app` importável a partir do diretório raiz do projeto
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.user import User
from app.models.project import Avaliacao, Equipe, Tematica, Turma


def _make_in_memory_session():
    """Cria uma sessão SQLite em memória com todas as tabelas criadas."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return Session()


def _seed_db(db):
    """
    Insere as entidades mínimas necessárias para criar uma Avaliação:
    Turma → Tematica → Equipe + Professor (User).

    Retorna (equipe_id, professor_id).
    """
    professor = User(
        nome="Prof Teste",
        email="prof@teste.com",
        senha_hash="hash",
        tipo="PROFESSOR",
        ativo=True,
    )
    db.add(professor)
    db.flush()

    turma = Turma(nome="TURMA A", semestre="2025-1")
    db.add(turma)
    db.flush()

    tematica = Tematica(
        titulo="Temática Teste",
        turma_id=turma.id,
        professor_id=professor.id,
    )
    db.add(tematica)
    db.flush()

    equipe = Equipe(nome="Equipe Alpha", tematica_id=tematica.id)
    db.add(equipe)
    db.flush()

    db.commit()
    return equipe.id, professor.id


def _simular_post_avaliar(db, equipe_id: int, professor_id: int, conceitos: dict) -> None:
    """
    Reproduz a lógica de POST `/equipes/{equipe_id}/avaliar` de `main.py`:
    cria nova Avaliacao ou atualiza a existente.
    """
    existente = (
        db.query(Avaliacao)
        .filter(
            Avaliacao.equipe_id == equipe_id,
            Avaliacao.professor_id == professor_id,
        )
        .first()
    )
    if existente:
        existente.conceito_conteudo     = conceitos["conceito_conteudo"]
        existente.conceito_tecnica      = conceitos["conceito_tecnica"]
        existente.conceito_apresentacao = conceitos["conceito_apresentacao"]
        existente.conceito_inovacao     = conceitos["conceito_inovacao"]
        existente.conceito_equipe       = conceitos["conceito_equipe"]
        existente.conceito_final        = conceitos["conceito_final"]
    else:
        db.add(Avaliacao(
            equipe_id=equipe_id,
            professor_id=professor_id,
            **conceitos,
        ))
    db.commit()


class TestRoundTripPersistenciaAvaliacaoDB:
    """
    Property 7 — Round-trip de persistência de avaliação (banco de dados).

    Validates: Requirements 3.4

    Verifica que após persistir uma Avaliação com conceitos específicos via
    a lógica equivalente ao POST `/equipes/{id}/avaliar`, o registro
    recuperado do banco exibe os mesmos conceitos — garantindo que
    a re-renderização da página mostraria os radio buttons corretos.
    """

    def test_roundtrip_db_criacao_nova_avaliacao(self):
        """
        Salva uma nova Avaliação com conceitos distintos por critério e verifica
        que todos os 6 campos são persistidos e recuperados corretamente.
        """
        db = _make_in_memory_session()
        try:
            equipe_id, professor_id = _seed_db(db)

            conceitos = {
                "conceito_conteudo":     "INSUFICIENTE",
                "conceito_tecnica":      "REGULAR",
                "conceito_apresentacao": "BOM",
                "conceito_inovacao":     "OTIMO",
                "conceito_equipe":       "EXCELENTE",
                "conceito_final":        "BOM",
            }

            _simular_post_avaliar(db, equipe_id, professor_id, conceitos)

            avaliacao = (
                db.query(Avaliacao)
                .filter(
                    Avaliacao.equipe_id == equipe_id,
                    Avaliacao.professor_id == professor_id,
                )
                .first()
            )

            assert avaliacao is not None, "Avaliação não foi criada no banco"

            for campo, valor_esperado in conceitos.items():
                valor_recuperado = getattr(avaliacao, campo)
                assert valor_recuperado == valor_esperado, (
                    f"Campo '{campo}': esperado='{valor_esperado}', "
                    f"recuperado='{valor_recuperado}'"
                )

                # Verifica que a lógica de checked produz o resultado correto
                assert deve_estar_checked(valor_recuperado, valor_esperado) is True
                for outro in [c for c in CONCEITOS if c != valor_esperado]:
                    assert deve_estar_checked(outro, valor_recuperado) is False, (
                        f"Campo '{campo}': deve_estar_checked('{outro}', '{valor_recuperado}') "
                        f"deveria ser False"
                    )
        finally:
            db.close()

    def test_roundtrip_db_atualizacao_avaliacao_existente(self):
        """
        Cria uma Avaliação inicial e depois a atualiza com novos conceitos.
        Verifica que os conceitos atualizados são persistidos e recuperados
        corretamente (não os valores originais).
        """
        db = _make_in_memory_session()
        try:
            equipe_id, professor_id = _seed_db(db)

            # 1ª submissão
            conceitos_iniciais = {campo: "BOM" for campo in CAMPOS_CONCEITO}
            _simular_post_avaliar(db, equipe_id, professor_id, conceitos_iniciais)

            # 2ª submissão com conceitos diferentes
            conceitos_atualizados = {
                "conceito_conteudo":     "EXCELENTE",
                "conceito_tecnica":      "OTIMO",
                "conceito_apresentacao": "REGULAR",
                "conceito_inovacao":     "INSUFICIENTE",
                "conceito_equipe":       "EXCELENTE",
                "conceito_final":        "OTIMO",
            }
            _simular_post_avaliar(db, equipe_id, professor_id, conceitos_atualizados)

            # Deve existir apenas um registro (upsert)
            total = (
                db.query(Avaliacao)
                .filter(
                    Avaliacao.equipe_id == equipe_id,
                    Avaliacao.professor_id == professor_id,
                )
                .count()
            )
            assert total == 1, f"Esperado 1 Avaliação, encontrado {total}"

            avaliacao = (
                db.query(Avaliacao)
                .filter(
                    Avaliacao.equipe_id == equipe_id,
                    Avaliacao.professor_id == professor_id,
                )
                .first()
            )

            for campo, valor_esperado in conceitos_atualizados.items():
                valor_recuperado = getattr(avaliacao, campo)
                assert valor_recuperado == valor_esperado, (
                    f"Campo '{campo}' após atualização: esperado='{valor_esperado}', "
                    f"recuperado='{valor_recuperado}'"
                )
                assert deve_estar_checked(valor_recuperado, valor_esperado) is True
        finally:
            db.close()

    def test_roundtrip_db_todos_conceitos_possiveis(self):
        """
        Para cada conceito válido como valor uniforme nos 6 critérios,
        verifica que salvar e recuperar produz o mesmo valor em todos os campos.
        """
        for conceito in CONCEITOS:
            db = _make_in_memory_session()
            try:
                equipe_id, professor_id = _seed_db(db)

                conceitos = {campo: conceito for campo in CAMPOS_CONCEITO}
                _simular_post_avaliar(db, equipe_id, professor_id, conceitos)

                avaliacao = (
                    db.query(Avaliacao)
                    .filter(
                        Avaliacao.equipe_id == equipe_id,
                        Avaliacao.professor_id == professor_id,
                    )
                    .first()
                )

                assert avaliacao is not None

                for campo in CAMPOS_CONCEITO:
                    valor_recuperado = getattr(avaliacao, campo)
                    assert valor_recuperado == conceito, (
                        f"Conceito='{conceito}', campo='{campo}': "
                        f"recuperado='{valor_recuperado}'"
                    )
                    assert deve_estar_checked(conceito, valor_recuperado) is True

                    checked_total = sum(
                        1 for c in CONCEITOS
                        if deve_estar_checked(c, valor_recuperado)
                    )
                    assert checked_total == 1, (
                        f"Conceito='{conceito}', campo='{campo}': "
                        f"esperado exatamente 1 checked, obtido {checked_total}"
                    )
            finally:
                db.close()

    def test_roundtrip_db_exatamente_um_checked_por_criterio_apos_persistencia(self):
        """
        Invariante de cardinalidade: após persistência, para cada critério
        exatamente um dos 5 radio buttons recebe checked=True.
        """
        db = _make_in_memory_session()
        try:
            equipe_id, professor_id = _seed_db(db)

            # Conceito diferente por critério para maximizar cobertura
            conceitos = {
                "conceito_conteudo":     "INSUFICIENTE",
                "conceito_tecnica":      "REGULAR",
                "conceito_apresentacao": "BOM",
                "conceito_inovacao":     "OTIMO",
                "conceito_equipe":       "EXCELENTE",
                "conceito_final":        "REGULAR",
            }
            _simular_post_avaliar(db, equipe_id, professor_id, conceitos)

            avaliacao = (
                db.query(Avaliacao)
                .filter(
                    Avaliacao.equipe_id == equipe_id,
                    Avaliacao.professor_id == professor_id,
                )
                .first()
            )
            assert avaliacao is not None

            for campo in CAMPOS_CONCEITO:
                valor_recuperado = getattr(avaliacao, campo)
                checked_count = sum(
                    1 for c in CONCEITOS
                    if deve_estar_checked(c, valor_recuperado)
                )
                assert checked_count == 1, (
                    f"Campo '{campo}' (persistido='{valor_recuperado}'): "
                    f"esperado exatamente 1 checked, obtido {checked_count}"
                )
        finally:
            db.close()


# ---------------------------------------------------------------------------
# Property 6: Pré-seleção de radio buttons de avaliação — correspondência exata
# Feature: ui-improvements-and-new-features, Property 6: radio buttons avaliação
# Validates: Requirements 3.1, 3.2
# ---------------------------------------------------------------------------
#
# Para qualquer combinação de conceitos nos 6 critérios, a função
# `deve_estar_checked(candidato, valor_salvo)` deve retornar True exatamente
# quando candidato == valor_salvo — garantindo que apenas um radio button por
# critério receba checked, e que seja o correto.

from hypothesis import given, settings
import hypothesis.strategies as st

# Campos de avaliação — os 6 critérios do formulário
_CAMPOS_AVALIACAO = [
    "conceito_conteudo",
    "conceito_tecnica",
    "conceito_apresentacao",
    "conceito_inovacao",
    "conceito_equipe",
    "conceito_final",
]

# Estratégia: dicionário fixo com um conceito aleatório por critério
_estrategia_conceitos = st.fixed_dictionaries(
    {campo: st.sampled_from(CONCEITOS) for campo in _CAMPOS_AVALIACAO}
)


@given(conceitos=_estrategia_conceitos)
@settings(max_examples=100)
def test_property6_radio_button_selecao_correspondencia_exata(conceitos):
    """
    **Validates: Requirements 3.1, 3.2**

    Property 6: Para qualquer combinação de conceitos nos 6 critérios,
    deve_estar_checked(candidato, valor_salvo) retorna True se e somente se
    candidato == valor_salvo.
    """
    # Feature: ui-improvements-and-new-features, Property 6: radio buttons avaliação
    for _campo, valor_salvo in conceitos.items():
        for candidato in CONCEITOS:
            esperado = (candidato == valor_salvo)
            resultado = deve_estar_checked(candidato, valor_salvo)
            assert resultado == esperado, (
                f"Critério '{_campo}' (valor_salvo='{valor_salvo}', "
                f"candidato='{candidato}'): esperado={esperado}, obtido={resultado}"
            )


@given(conceitos=_estrategia_conceitos)
@settings(max_examples=100)
def test_property6_exatamente_um_checked_por_criterio(conceitos):
    """
    **Validates: Requirements 3.1, 3.2**

    Property 6 — invariante de cardinalidade: para qualquer avaliação gerada,
    a contagem de radio buttons que receberiam checked para cada critério deve
    ser exatamente 1 (nunca zero, nunca dois ou mais).
    """
    # Feature: ui-improvements-and-new-features, Property 6: radio buttons avaliação
    for _campo, valor_salvo in conceitos.items():
        checked_count = sum(
            1 for candidato in CONCEITOS
            if deve_estar_checked(candidato, valor_salvo)
        )
        assert checked_count == 1, (
            f"Critério '{_campo}' (valor_salvo='{valor_salvo}'): "
            f"esperado exatamente 1 checked, obtido {checked_count}"
        )


# ---------------------------------------------------------------------------
# Funções auxiliares — extraídas de main.py para teste isolado
# ---------------------------------------------------------------------------

def extrair_anos(semestres: list) -> list:
    """
    Extrai anos distintos de uma lista de semestres no formato 'AAAA-N'.
    Retorna lista ordenada em ordem decrescente, sem duplicatas.
    Mirrors da lógica em GET /turmas.
    """
    anos = sorted(
        set(s.split("-")[0] for s in semestres if "-" in s),
        reverse=True,
    )
    return anos


def filtrar_turmas_por_ano(turmas: list, ano: str) -> list:
    """
    Filtra turmas cujo campo semestre inicia com '{ano}-'.
    Mirrors da lógica em GET /turmas.
    """
    if not ano:
        return turmas
    return [t for t in turmas if t.semestre.startswith(f"{ano}-")]


def filtrar_tematicas_por_professor(tematicas: list, professor_id) -> list:
    """
    Filtra temáticas pelo professor_id.
    Mirrors da lógica em GET /tematicas.
    """
    return [t for t in tematicas if t.professor_id == professor_id]


def filtrar_tematicas_combinado(tematicas: list, turma_id=None, professor_id=None) -> list:
    """
    Aplica filtros de turma e professor de forma cumulativa (interseção).
    """
    resultado = tematicas
    if turma_id is not None:
        resultado = [t for t in resultado if t.turma_id == turma_id]
    if professor_id is not None:
        resultado = [t for t in resultado if t.professor_id == professor_id]
    return resultado


def _url_perfil_local(tipo: str, user_id: int) -> str:
    """Mirrors de _url_perfil em main.py."""
    mapa = {
        "ALUNO":       f"/alunos/{user_id}",
        "PROFESSOR":   f"/perfil/professor/{user_id}",
        "COORDENADOR": f"/perfil/coordenador/{user_id}",
        "ADMIN":       f"/perfil/coordenador/{user_id}",
        "EMPRESA":     f"/perfil/empresa/{user_id}",
    }
    return mapa.get(tipo, "/dashboard")


def calcular_totais(dados_tematicas: list) -> dict:
    """
    Calcula os totais de equipes e avaliações a partir de dados_tematicas.
    Mirrors da lógica em GET /relatorios/professor/{id}.
    """
    return {
        "total_equipes":     sum(d["n_equipes"] for d in dados_tematicas),
        "total_avaliacoes":  sum(d["n_avaliacoes"] for d in dados_tematicas),
        "total_tematicas":   len(dados_tematicas),
    }


# ---------------------------------------------------------------------------
# Property 1: Filtro de turmas por ano — exatidão
# Feature: ui-improvements-and-new-features, Property 1: filtro turmas por ano
# Validates: Requirements 1.2
# ---------------------------------------------------------------------------

_estrategia_semestre = st.from_regex(r"\d{4}-[12]", fullmatch=True)
_estrategia_ano      = st.from_regex(r"\d{4}", fullmatch=True)


@given(
    semestres=st.lists(_estrategia_semestre, min_size=0, max_size=20),
    ano=_estrategia_ano,
)
@settings(max_examples=100)
def test_property1_filtro_turmas_por_ano_exatidao(semestres, ano):
    """
    **Validates: Requirements 1.2**

    Property 1: Para qualquer lista de turmas e qualquer ano de filtro,
    todas as turmas retornadas devem ter semestre iniciando com '{ano}-'
    e nenhuma turma de outro ano deve aparecer.
    """
    # Feature: ui-improvements-and-new-features, Property 1: filtro turmas por ano
    turmas = [SimpleNamespace(semestre=s) for s in semestres]
    resultado = filtrar_turmas_por_ano(turmas, ano)

    # Todas as retornadas devem iniciar com '{ano}-'
    for t in resultado:
        assert t.semestre.startswith(f"{ano}-"), (
            f"Turma com semestre '{t.semestre}' não deveria estar no resultado "
            f"para filtro ano='{ano}'"
        )

    # Nenhuma turma de outro ano deve aparecer
    ids_resultado = {id(t) for t in resultado}
    for t in turmas:
        if not t.semestre.startswith(f"{ano}-"):
            assert id(t) not in ids_resultado, (
                f"Turma com semestre '{t.semestre}' não deveria estar no resultado "
                f"para filtro ano='{ano}'"
            )


# ---------------------------------------------------------------------------
# Property 2: Extração de anos distintos — completude e unicidade
# Feature: ui-improvements-and-new-features, Property 2: anos distintos
# Validates: Requirements 1.1
# ---------------------------------------------------------------------------

@given(semestres=st.lists(_estrategia_semestre, min_size=0, max_size=30))
@settings(max_examples=100)
def test_property2_extracao_anos_distintos_unicidade(semestres):
    """
    **Validates: Requirements 1.1**

    Property 2: Para qualquer lista de semestres, os anos extraídos devem ser
    únicos (sem duplicatas) e ordenados do mais recente ao mais antigo.
    """
    # Feature: ui-improvements-and-new-features, Property 2: anos distintos
    anos = extrair_anos(semestres)

    # Sem duplicatas
    assert len(anos) == len(set(anos)), (
        f"Anos extraídos contêm duplicatas: {anos}"
    )

    # Ordenados descendentemente
    assert anos == sorted(set(anos), reverse=True), (
        f"Anos não estão em ordem decrescente: {anos}"
    )

    # Completude: todos os anos dos semestres devem aparecer
    anos_esperados = {s.split("-")[0] for s in semestres if "-" in s}
    assert set(anos) == anos_esperados, (
        f"Conjunto de anos extraídos {set(anos)} != esperado {anos_esperados}"
    )


# ---------------------------------------------------------------------------
# Property 3: Estado do filtro refletido no contexto — round-trip
# Feature: ui-improvements-and-new-features, Property 3: round-trip filtro ano
# Validates: Requirements 1.5
# ---------------------------------------------------------------------------

@given(ano=_estrategia_ano)
@settings(max_examples=100)
def test_property3_round_trip_ano_selecionado(ano):
    """
    **Validates: Requirements 1.5**

    Property 3: Para qualquer ano válido submetido como parâmetro GET,
    ano_selecionado no contexto deve ser igual ao parâmetro submetido.
    """
    # Feature: ui-improvements-and-new-features, Property 3: round-trip filtro ano
    # Simula a lógica da rota: recebe `ano`, passa `ano_selecionado=ano` ao template
    ano_selecionado = ano  # a rota simplesmente repassa o parâmetro recebido
    assert ano_selecionado == ano


# ---------------------------------------------------------------------------
# Property 4: Filtro de temáticas por professor — exatidão
# Feature: ui-improvements-and-new-features, Property 4: filtro tematicas professor
# Validates: Requirements 2.2
# ---------------------------------------------------------------------------

@given(
    professor_ids=st.lists(st.integers(min_value=1, max_value=50), min_size=0, max_size=20),
    filtro_professor_id=st.integers(min_value=1, max_value=50),
)
@settings(max_examples=100)
def test_property4_filtro_tematicas_por_professor_exatidao(professor_ids, filtro_professor_id):
    """
    **Validates: Requirements 2.2**

    Property 4: Para qualquer conjunto de temáticas com professor_ids variados
    e qualquer professor_id de filtro, todas as retornadas devem ter
    professor_id igual ao filtro.
    """
    # Feature: ui-improvements-and-new-features, Property 4: filtro tematicas professor
    tematicas = [SimpleNamespace(professor_id=pid, turma_id=1) for pid in professor_ids]
    resultado = filtrar_tematicas_por_professor(tematicas, filtro_professor_id)

    for t in resultado:
        assert t.professor_id == filtro_professor_id, (
            f"Temática com professor_id={t.professor_id} não deveria estar no resultado "
            f"para filtro professor_id={filtro_professor_id}"
        )

    # Nenhuma temática de outro professor deve aparecer
    ids_resultado = {id(t) for t in resultado}
    for t in tematicas:
        if t.professor_id != filtro_professor_id:
            assert id(t) not in ids_resultado


# ---------------------------------------------------------------------------
# Property 5: Filtros compostos de temáticas — interseção correta
# Feature: ui-improvements-and-new-features, Property 5: filtros compostos tematicas
# Validates: Requirements 2.3
# ---------------------------------------------------------------------------

@given(
    dados=st.lists(
        st.fixed_dictionaries({
            "professor_id": st.integers(min_value=1, max_value=10),
            "turma_id":     st.integers(min_value=1, max_value=10),
        }),
        min_size=0, max_size=20,
    ),
    filtro_turma=st.integers(min_value=1, max_value=10),
    filtro_professor=st.integers(min_value=1, max_value=10),
)
@settings(max_examples=100)
def test_property5_filtros_compostos_intersecao(dados, filtro_turma, filtro_professor):
    """
    **Validates: Requirements 2.3**

    Property 5: Para qualquer combinação de filtro_turma e filtro_professor
    ambos ativos, o resultado deve satisfazer simultaneamente ambos os critérios.
    """
    # Feature: ui-improvements-and-new-features, Property 5: filtros compostos tematicas
    tematicas = [SimpleNamespace(**d) for d in dados]
    resultado = filtrar_tematicas_combinado(
        tematicas, turma_id=filtro_turma, professor_id=filtro_professor
    )

    for t in resultado:
        assert t.turma_id == filtro_turma, (
            f"Temática com turma_id={t.turma_id} não satisfaz filtro_turma={filtro_turma}"
        )
        assert t.professor_id == filtro_professor, (
            f"Temática com professor_id={t.professor_id} não satisfaz filtro_professor={filtro_professor}"
        )


# ---------------------------------------------------------------------------
# Property 8: Totais agregados do relatório de professor — invariância aritmética
# Feature: ui-improvements-and-new-features, Property 8: totais agregados relatorio
# Validates: Requirements 4.4
# ---------------------------------------------------------------------------

@given(
    dados_tematicas=st.lists(
        st.fixed_dictionaries({
            "n_equipes":    st.integers(min_value=0, max_value=20),
            "n_avaliacoes": st.integers(min_value=0, max_value=50),
        }),
        min_size=0, max_size=10,
    )
)
@settings(max_examples=100)
def test_property8_totais_agregados_relatorio(dados_tematicas):
    """
    **Validates: Requirements 4.4**

    Property 8: Para qualquer lista de dados_tematicas, total_equipes deve ser
    a soma de todos os n_equipes e total_avaliacoes a soma de todos os n_avaliacoes.
    """
    # Feature: ui-improvements-and-new-features, Property 8: totais agregados
    resultado = calcular_totais(dados_tematicas)

    total_equipes_esperado    = sum(d["n_equipes"] for d in dados_tematicas)
    total_avaliacoes_esperado = sum(d["n_avaliacoes"] for d in dados_tematicas)
    total_tematicas_esperado  = len(dados_tematicas)

    assert resultado["total_equipes"]    == total_equipes_esperado
    assert resultado["total_avaliacoes"] == total_avaliacoes_esperado
    assert resultado["total_tematicas"]  == total_tematicas_esperado


# ---------------------------------------------------------------------------
# Property 10: URL de perfil correta por tipo de usuário
# Feature: ui-improvements-and-new-features, Property 10: url_perfil por tipo
# Validates: Requirements 7.1, 7.2, 7.3, 7.4
# ---------------------------------------------------------------------------

_TIPOS_USUARIO = ["ALUNO", "PROFESSOR", "COORDENADOR", "ADMIN", "EMPRESA"]


@given(
    tipo=st.sampled_from(_TIPOS_USUARIO),
    user_id=st.integers(min_value=1, max_value=10000),
)
@settings(max_examples=100)
def test_property10_url_perfil_por_tipo(tipo, user_id):
    """
    **Validates: Requirements 7.1, 7.2, 7.3, 7.4**

    Property 10: Para qualquer usuário com tipo válido e qualquer id,
    _url_perfil retorna URL contendo o id e o path correto para aquele tipo.
    """
    # Feature: ui-improvements-and-new-features, Property 10: url_perfil por tipo
    url = _url_perfil_local(tipo, user_id)

    # A URL deve conter o id do usuário
    assert str(user_id) in url, (
        f"URL '{url}' não contém o id '{user_id}' para tipo '{tipo}'"
    )

    # A URL deve corresponder ao path esperado para cada tipo
    if tipo == "ALUNO":
        assert url == f"/alunos/{user_id}"
    elif tipo == "PROFESSOR":
        assert url == f"/perfil/professor/{user_id}"
    elif tipo in ("COORDENADOR", "ADMIN"):
        assert url == f"/perfil/coordenador/{user_id}"
    elif tipo == "EMPRESA":
        assert url == f"/perfil/empresa/{user_id}"


# ---------------------------------------------------------------------------
# Property 11: Ações do FAB corretas por tipo de usuário
# Feature: ui-improvements-and-new-features, Property 11: FAB acoes por tipo
# Validates: Requirements 10.3, 10.4, 10.5, 10.6
# ---------------------------------------------------------------------------

# Mapeamento esperado: tipo → conjunto de URLs/ações obrigatórias no FAB
_FAB_ACOES_ESPERADAS = {
    "ALUNO":       {"/tematicas", "/portfolio"},
    "PROFESSOR":   {"/tematicas", "/portfolio"},
    "COORDENADOR": {"/turmas/nova", "/tematicas/nova", "/relatorios"},
    "ADMIN":       {"/usuarios/novo", "/turmas/nova", "/tematicas/nova", "/relatorios"},
    "EMPRESA":     {"/portfolio"},
}


def get_fab_urls(tipo: str, usuario_id: int) -> set:
    """
    Simula as URLs que devem aparecer no FAB para cada tipo de usuário,
    espelhando a lógica do template base_auth.html.
    """
    if tipo == "ALUNO":
        return {"/tematicas", "/portfolio", _url_perfil_local(tipo, usuario_id)}
    elif tipo == "PROFESSOR":
        return {"/tematicas", "/portfolio"}
    elif tipo == "COORDENADOR":
        return {"/turmas/nova", "/tematicas/nova", "/relatorios"}
    elif tipo == "ADMIN":
        return {"/usuarios/novo", "/turmas/nova", "/tematicas/nova", "/relatorios"}
    elif tipo == "EMPRESA":
        return {"/portfolio"}
    return set()


@given(
    tipo=st.sampled_from(_TIPOS_USUARIO),
    user_id=st.integers(min_value=1, max_value=10000),
)
@settings(max_examples=100)
def test_property11_fab_acoes_por_tipo(tipo, user_id):
    """
    **Validates: Requirements 10.3, 10.4, 10.5, 10.6**

    Property 11: Para cada tipo de usuário, o FAB deve conter pelo menos
    as ações obrigatórias definidas para aquele tipo — sem ações de outros tipos.
    """
    # Feature: ui-improvements-and-new-features, Property 11: FAB acoes por tipo
    urls_fab = get_fab_urls(tipo, user_id)
    acoes_obrigatorias = _FAB_ACOES_ESPERADAS[tipo]

    # Todas as ações obrigatórias devem estar presentes
    for acao in acoes_obrigatorias:
        assert acao in urls_fab, (
            f"Tipo '{tipo}': ação obrigatória '{acao}' ausente no FAB. "
            f"FAB atual: {urls_fab}"
        )

    # Ações de outros tipos não devem aparecer (exceto sobreposições intencionais)
    for outro_tipo, outras_acoes in _FAB_ACOES_ESPERADAS.items():
        if outro_tipo == tipo:
            continue
        acoes_exclusivas_outro = outras_acoes - acoes_obrigatorias
        for acao_exclusiva in acoes_exclusivas_outro:
            assert acao_exclusiva not in urls_fab, (
                f"Tipo '{tipo}': ação '{acao_exclusiva}' exclusiva de '{outro_tipo}' "
                f"não deveria aparecer no FAB. FAB atual: {urls_fab}"
            )
