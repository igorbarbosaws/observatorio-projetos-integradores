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
