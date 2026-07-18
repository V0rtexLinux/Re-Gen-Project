"""Tests for re_gen.data.paleontology - paleontological dinosaur database."""

import pytest

from re_gen.data.paleontology import (
    DinosauroGrupo,
    Dinossauro,
    Period,
    SistemaReferencia,
    criar_sistema_referencia_padrao,
    listar_dinossauros_recomendados,
    obter_sistema_referencia,
)


@pytest.fixture
def sistema_padrao():
    """Return a fresh default reference system."""
    return criar_sistema_referencia_padrao()


@pytest.fixture
def sistema_singleton():
    """Return the singleton reference system."""
    return obter_sistema_referencia()


class TestObterSistemaReferencia:
    """Tests for obter_sistema_referencia()."""

    def test_returns_sistema_referencia(self, sistema_singleton):
        assert isinstance(sistema_singleton, SistemaReferencia)

    def test_singleton_returns_same_instance(self):
        a = obter_sistema_referencia()
        b = obter_sistema_referencia()
        assert a is b

    def test_is_populated(self, sistema_singleton):
        assert len(sistema_singleton.dinossauros) > 0

    def test_contains_expected_groups(self, sistema_singleton):
        assert len(sistema_singleton.grupos_por_tipo) > 0


class TestCriarSistemaReferenciaPadrao:
    """Tests for criar_sistema_referencia_padrao()."""

    def test_returns_five_species(self, sistema_padrao):
        assert len(sistema_padrao.dinossauros) == 5

    def test_contains_trex(self, sistema_padrao):
        assert "Tyrannosaurus rex" in sistema_padrao.dinossauros

    def test_contains_velociraptor(self, sistema_padrao):
        assert "Velociraptor mongoliensis" in sistema_padrao.dinossauros

    def test_contains_archaeopteryx(self, sistema_padrao):
        assert "Archaeopteryx lithographica" in sistema_padrao.dinossauros

    def test_groups_populated(self, sistema_padrao):
        assert DinosauroGrupo.THEROPODA in sistema_padrao.grupos_por_tipo
        assert len(sistema_padrao.grupos_por_tipo[DinosauroGrupo.THEROPODA]) == 3

    def test_each_dino_has_required_fields(self, sistema_padrao):
        for dino in sistema_padrao.dinossauros.values():
            assert dino.nome_cientifico
            assert dino.nome_comum
            assert isinstance(dino.grupo, DinosauroGrupo)
            assert isinstance(dino.periodo, Period)
            assert dino.dieta in ("carnívoro", "herbívoro", "onívoro")
            assert dino.taxa_diferencacao_estimada >= 0


class TestBuscarPorNome:
    """Tests for SistemaReferencia.buscar_por_nome()."""

    def test_known_species_returns_dino(self, sistema_padrao):
        result = sistema_padrao.buscar_por_nome("Tyrannosaurus rex")
        assert result is not None
        assert isinstance(result, Dinossauro)
        assert result.nome_comum == "T-Rex"

    def test_unknown_species_returns_none(self, sistema_padrao):
        result = sistema_padrao.buscar_por_nome("Nonexistentus fakei")
        assert result is None

    def test_empty_string_returns_none(self, sistema_padrao):
        assert sistema_padrao.buscar_por_nome("") is None


class TestListarPorGrupo:
    """Tests for SistemaReferencia.listar_por_grupo()."""

    def test_theropoda_returns_three(self, sistema_padrao):
        theropods = sistema_padrao.listar_por_grupo(DinosauroGrupo.THEROPODA)
        assert len(theropods) == 3
        for dino in theropods:
            assert dino.grupo == DinosauroGrupo.THEROPODA

    def test_sauropodomorpha_returns_one(self, sistema_padrao):
        sauropods = sistema_padrao.listar_por_grupo(DinosauroGrupo.SAUROPODOMORPHA)
        assert len(sauropods) == 1
        assert sauropods[0].nome_cientifico == "Brachiosaurus altithorax"

    def test_ornithischia_returns_one(self, sistema_padrao):
        ornithischia = sistema_padrao.listar_por_grupo(DinosauroGrupo.ORNITHISCHIA)
        assert len(ornithischia) == 1
        assert ornithischia[0].nome_cientifico == "Triceratops horridus"


class TestListarPorPeriodo:
    """Tests for SistemaReferencia.listar_por_periodo()."""

    def test_cretaceo_returns_three(self, sistema_padrao):
        cretaceo = sistema_padrao.listar_por_periodo(Period.CRETACEO)
        assert len(cretaceo) == 3

    def test_jurassico_returns_two(self, sistema_padrao):
        jurassico = sistema_padrao.listar_por_periodo(Period.JURASSICO)
        assert len(jurassico) == 2

    def test_triassico_returns_zero(self, sistema_padrao):
        triassico = sistema_padrao.listar_por_periodo(Period.TRIASSICO)
        assert len(triassico) == 0


class TestRegistrar:
    """Tests for SistemaReferencia.registrar()."""

    def test_adds_new_dino(self, sistema_padrao):
        custom = Dinossauro(
            nome_cientifico="Testus testi",
            nome_comum="Test Dino",
            grupo=DinosauroGrupo.THEROPODA,
            periodo=Period.CRETACEO,
            peso_estimado_kg=100,
            comprimento_estimado_m=2.0,
            altura_estimada_m=1.0,
            dieta="carnívoro",
            localizacao_geografica=["Testland"],
            descricao_paleontologica="A test dinosaur",
            caracteristicas_notaveis=["testing"],
            genes_conservados=["GENE1"],
            taxa_diferencacao_estimada=50.0,
            ancestrais_proximos=[],
            descendentes_vivos=[],
        )
        sistema_padrao.registrar(custom)
        assert sistema_padrao.buscar_por_nome("Testus testi") is custom

    def test_overwrites_existing_dino(self, sistema_padrao):
        original = sistema_padrao.buscar_por_nome("Tyrannosaurus rex")
        replacement = Dinossauro(
            nome_cientifico="Tyrannosaurus rex",
            nome_comum="New T-Rex",
            grupo=DinosauroGrupo.THEROPODA,
            periodo=Period.CRETACEO,
            peso_estimado_kg=1,
            comprimento_estimado_m=1,
            altura_estimada_m=1,
            dieta="herbívoro",
            localizacao_geografica=[],
            descricao_paleontologica="",
            caracteristicas_notaveis=[],
            genes_conservados=[],
            taxa_diferencacao_estimada=0,
            ancestrais_proximos=[],
            descendentes_vivos=[],
        )
        sistema_padrao.registrar(replacement)
        assert sistema_padrao.buscar_por_nome("Tyrannosaurus rex") is replacement
        assert sistema_padrao.buscar_por_nome("Tyrannosaurus rex") is not original


class TestListarDinossaurosRecomendados:
    """Tests for listar_dinossauros_recomendados()."""

    def test_returns_list_of_dinossauros(self):
        recomendados = listar_dinossauros_recomendados()
        assert isinstance(recomendados, list)
        assert len(recomendados) > 0
        assert all(isinstance(d, Dinossauro) for d in recomendados)

    def test_sorted_by_genes_then_weight(self):
        recomendados = listar_dinossauros_recomendados()
        for i in range(len(recomendados) - 1):
            a = recomendados[i]
            b = recomendados[i + 1]
            assert (-len(a.genes_conservados), -(a.peso_estimado_kg or 0)) <= (
                -len(b.genes_conservados),
                -(b.peso_estimado_kg or 0),
            )


class TestEnums:
    """Tests for DinosauroGrupo and Period enums."""

    def test_grupo_values(self):
        assert DinosauroGrupo.THEROPODA.value == "Theropoda"
        assert DinosauroGrupo.SAUROPODOMORPHA.value == "Sauropodomorpha"
        assert DinosauroGrupo.ORNITHISCHIA.value == "Ornithischia"

    def test_period_values(self):
        assert "Triássico" in Period.TRIASSICO.value
        assert "Jurássico" in Period.JURASSICO.value
        assert "Cretáceo" in Period.CRETACEO.value
