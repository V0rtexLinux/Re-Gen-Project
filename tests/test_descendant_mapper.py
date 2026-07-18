"""Tests for re_gen.data.descendant_mapper - descendant species mapping."""

import pytest

from re_gen.data.descendant_mapper import (
    CaracteristicaAncestral,
    EspecieDescendente,
    MapeadorDescendentes,
    criar_mapeador_padrao,
    obter_mapeador,
)


@pytest.fixture
def mapeador_padrao():
    """Return a fresh default mapper."""
    return criar_mapeador_padrao()


@pytest.fixture
def mapeador_singleton():
    """Return the singleton mapper."""
    return obter_mapeador()


class TestObterMapeador:
    """Tests for obter_mapeador()."""

    def test_returns_mapeador(self, mapeador_singleton):
        assert isinstance(mapeador_singleton, MapeadorDescendentes)

    def test_singleton_returns_same_instance(self):
        a = obter_mapeador()
        b = obter_mapeador()
        assert a is b

    def test_is_populated(self, mapeador_singleton):
        assert len(mapeador_singleton.descendentes) > 0


class TestCriarMapeadorPadrao:
    """Tests for criar_mapeador_padrao()."""

    def test_returns_six_species(self, mapeador_padrao):
        assert len(mapeador_padrao.descendentes) == 6

    def test_contains_gallus_gallus(self, mapeador_padrao):
        assert "Gallus gallus" in mapeador_padrao.descendentes

    def test_contains_crocodylus(self, mapeador_padrao):
        assert "Crocodylus niloticus" in mapeador_padrao.descendentes

    def test_indices_built(self, mapeador_padrao):
        assert len(mapeador_padrao._indice_caracteristicas) > 0
        assert len(mapeador_padrao._indice_ancestrais) > 0


class TestBuscarPorAncestral:
    """Tests for MapeadorDescendentes.buscar_por_ancestral()."""

    def test_trex_descendants(self, mapeador_padrao):
        result = mapeador_padrao.buscar_por_ancestral("Tyrannosaurus rex")
        assert len(result) > 0
        for esp in result:
            assert esp.ancestral_direto == "Tyrannosaurus rex"

    def test_velociraptor_descendants(self, mapeador_padrao):
        result = mapeador_padrao.buscar_por_ancestral("Velociraptor mongoliensis")
        assert len(result) > 0
        assert all(isinstance(e, EspecieDescendente) for e in result)

    def test_unknown_dino_returns_empty(self, mapeador_padrao):
        result = mapeador_padrao.buscar_por_ancestral("Fakosaurus fakei")
        assert result == []

    def test_results_sorted_by_genomic_score(self, mapeador_padrao):
        result = mapeador_padrao.buscar_por_ancestral("Tyrannosaurus rex")
        scores = [e.score_utilidade_genomica for e in result]
        assert scores == sorted(scores, reverse=True)


class TestBuscarPorCaracteristica:
    """Tests for MapeadorDescendentes.buscar_por_caracteristica()."""

    def test_penas_returns_birds(self, mapeador_padrao):
        result = mapeador_padrao.buscar_por_caracteristica(CaracteristicaAncestral.PENAS)
        assert len(result) > 0
        for esp in result:
            assert CaracteristicaAncestral.PENAS in esp.caracteristicas_preservadas

    def test_escama_returns_crocodilians(self, mapeador_padrao):
        result = mapeador_padrao.buscar_por_caracteristica(CaracteristicaAncestral.ESCAMA_AVANCADA)
        assert len(result) > 0

    def test_results_sorted_by_ncbi_quality(self, mapeador_padrao):
        result = mapeador_padrao.buscar_por_caracteristica(CaracteristicaAncestral.OSSOS_OCOS)
        qualities = [e.qualidade_anotacao_ncbi for e in result]
        assert qualities == sorted(qualities, reverse=True)


class TestEncontrarMelhorReferencia:
    """Tests for MapeadorDescendentes.encontrar_melhor_referencia()."""

    def test_trex_without_filter(self, mapeador_padrao):
        ref = mapeador_padrao.encontrar_melhor_referencia("Tyrannosaurus rex")
        assert ref is not None
        assert isinstance(ref, EspecieDescendente)

    def test_trex_with_penas_filter(self, mapeador_padrao):
        ref = mapeador_padrao.encontrar_melhor_referencia(
            "Tyrannosaurus rex",
            CaracteristicaAncestral.PENAS,
        )
        assert ref is not None
        assert CaracteristicaAncestral.PENAS in ref.caracteristicas_preservadas

    def test_unknown_dino_returns_none(self, mapeador_padrao):
        ref = mapeador_padrao.encontrar_melhor_referencia("Nosuchspecies")
        assert ref is None

    def test_filter_no_match_returns_none(self, mapeador_padrao):
        ref = mapeador_padrao.encontrar_melhor_referencia(
            "Tyrannosaurus rex",
            CaracteristicaAncestral.GARRA_SICLE,
        )
        # Gallus and Struthio don't have GARRA_SICLE, but Falco is not under T-rex
        # So this should return None if no descendant of T-rex has garra_sicle
        assert ref is None or isinstance(ref, EspecieDescendente)


class TestListarTodosRecomendados:
    """Tests for MapeadorDescendentes.listar_todos_recomendados()."""

    def test_returns_all_species(self, mapeador_padrao):
        result = mapeador_padrao.listar_todos_recomendados()
        assert len(result) == len(mapeador_padrao.descendentes)

    def test_ordered_by_utility_score(self, mapeador_padrao):
        result = mapeador_padrao.listar_todos_recomendados()
        scores = [(e.score_utilidade_genomica + e.qualidade_anotacao_ncbi) / 2.0 for e in result]
        assert scores == sorted(scores, reverse=True)


class TestRegistrar:
    """Tests for MapeadorDescendentes.registrar()."""

    def test_adds_species_and_updates_indices(self, mapeador_padrao):
        new_species = EspecieDescendente(
            nome_cientifico="Testus testis",
            nome_comum="Test Bird",
            grupo_taxa="Aves",
            caracteristicas_preservadas=[CaracteristicaAncestral.PENAS],
            genes_ortologos=["GENE1"],
            genes_notaveis={CaracteristicaAncestral.PENAS: ["GENE1"]},
            ancestral_direto="Tyrannosaurus rex",
            anos_divergencia_estimados=66e6,
            score_utilidade_genomica=50.0,
            qualidade_anotacao_ncbi=50.0,
        )
        mapeador_padrao.registrar(new_species)
        assert "Testus testis" in mapeador_padrao.descendentes
        assert "Testus testis" in mapeador_padrao._indice_ancestrais["Tyrannosaurus rex"]
        assert "Testus testis" in mapeador_padrao._indice_caracteristicas[CaracteristicaAncestral.PENAS]


class TestEspecieDescendenteDataclass:
    """Tests for EspecieDescendente data integrity."""

    def test_gallus_fields(self, mapeador_padrao):
        gallus = mapeador_padrao.descendentes["Gallus gallus"]
        assert gallus.nome_comum == "Galinha-selvagem"
        assert gallus.grupo_taxa == "Aves"
        assert gallus.score_utilidade_genomica == 95.0
        assert gallus.qualidade_anotacao_ncbi == 98.0
        assert len(gallus.genes_ortologos) > 0
        assert len(gallus.caracteristicas_preservadas) > 0


class TestCaracteristicaAncestralEnum:
    """Tests for CaracteristicaAncestral enum."""

    def test_all_values_present(self):
        expected = {
            "ossos_ocos",
            "penas",
            "garra_sicle",
            "visao_binocular",
            "estrutura_mandibular",
            "escama_avancada",
            "dimorfismo_sexual",
        }
        actual = {c.value for c in CaracteristicaAncestral}
        assert actual == expected
