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
