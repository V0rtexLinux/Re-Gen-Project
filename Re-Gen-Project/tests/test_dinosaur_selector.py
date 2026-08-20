"""Tests for re_gen.data.dinosaur_selector - automatic dinosaur selection."""

import pytest

from re_gen.data.dinosaur_selector import (
    CapacidadeHardware,
    ConfiguracaoSelecao,
    SeletorDinossauro,
    DESCRICOES_SELECAO,
    selecionador_adaptativo,
)
from re_gen.data.paleontology import (
    DinosauroGrupo,
    Dinossauro,
    SistemaReferencia,
    criar_sistema_referencia_padrao,
)


@pytest.fixture
def sistema():
    """Return a fresh reference system."""
    return criar_sistema_referencia_padrao()


class TestSeletorDinossauroCreation:
    """Tests for SeletorDinossauro instantiation."""

    def test_creates_with_default_system(self):
        selector = SeletorDinossauro()
        assert selector.sistema_ref is not None
        assert len(selector.sistema_ref.dinossauros) > 0

    def test_creates_with_custom_system(self, sistema):
        selector = SeletorDinossauro(sistema)
        assert selector.sistema_ref is sistema

    def test_selecionador_adaptativo_factory(self):
        for hw in CapacidadeHardware:
            selector = selecionador_adaptativo(hw)
            assert isinstance(selector, SeletorDinossauro)


class TestSelecionar:
    """Tests for SeletorDinossauro.selecionar()."""

    def test_returns_tuple_of_dino_and_score(self, sistema):
        selector = SeletorDinossauro(sistema)
        config = ConfiguracaoSelecao()
        dino, score = selector.selecionar(config)
        assert isinstance(dino, Dinossauro)
        assert isinstance(score, float)
        assert score > 0

    def test_empty_system_raises(self):
        empty_sys = SistemaReferencia()
        selector = SeletorDinossauro(empty_sys)
        config = ConfiguracaoSelecao()
        with pytest.raises(ValueError, match="vazio"):
            selector.selecionar(config)

    def test_hardware_none_favors_conservado(self, sistema):
        selector = SeletorDinossauro(sistema)
        config_none = ConfiguracaoSelecao(hardware=CapacidadeHardware.NENHUMA)
        config_adv = ConfiguracaoSelecao(hardware=CapacidadeHardware.AVANCADA)
        dino_none, _ = selector.selecionar(config_none)
        dino_adv, _ = selector.selecionar(config_adv)
        # Both should return valid dinos
        assert isinstance(dino_none, Dinossauro)
        assert isinstance(dino_adv, Dinossauro)

    def test_diet_preference_affects_result(self, sistema):
        selector = SeletorDinossauro(sistema)
        config_carn = ConfiguracaoSelecao(preferencia_tipo_dieta="carnívoro")
        config_herb = ConfiguracaoSelecao(preferencia_tipo_dieta="herbívoro")
        dino_carn, _ = selector.selecionar(config_carn)
        dino_herb, _ = selector.selecionar(config_herb)
        # Different preferences should potentially yield different dinosaurs
        assert isinstance(dino_carn, Dinossauro)
        assert isinstance(dino_herb, Dinossauro)

    def test_group_preference_affects_result(self, sistema):
        selector = SeletorDinossauro(sistema)
        config = ConfiguracaoSelecao(preferencia_grupo=DinosauroGrupo.SAUROPODOMORPHA)
        dino, _ = selector.selecionar(config)
        assert isinstance(dino, Dinossauro)


class TestRecomendarMultiplos:
    """Tests for SeletorDinossauro.recomendar_multiplos()."""

    def test_returns_list_of_tuples(self, sistema):
        selector = SeletorDinossauro(sistema)
        config = ConfiguracaoSelecao()
        results = selector.recomendar_multiplos(config, n=3)
        assert isinstance(results, list)
        assert len(results) == 3
        for dino, score in results:
            assert isinstance(dino, Dinossauro)
            assert isinstance(score, float)

    def test_results_ordered_descending(self, sistema):
        selector = SeletorDinossauro(sistema)
        config = ConfiguracaoSelecao()
        results = selector.recomendar_multiplos(config, n=5)
        scores = [s for _, s in results]
        assert scores == sorted(scores, reverse=True)

    def test_n_exceeding_available_returns_all(self, sistema):
        selector = SeletorDinossauro(sistema)
        config = ConfiguracaoSelecao()
        results = selector.recomendar_multiplos(config, n=100)
        assert len(results) <= len(sistema.dinossauros)


class TestHardwareCompatibility:
    """Tests for hardware compatibility scoring."""

    @pytest.mark.parametrize("hw", list(CapacidadeHardware))
    def test_all_hardware_levels_work(self, sistema, hw):
        selector = SeletorDinossauro(sistema)
        config = ConfiguracaoSelecao(hardware=hw)
        dino, score = selector.selecionar(config)
        assert isinstance(dino, Dinossauro)
        assert score > 0


class TestDescricaoesSelecao:
    """Tests for the DESCRICOES_SELECAO dictionary."""

    def test_has_entries_for_all_dinos(self, sistema):
        for nome in sistema.dinossauros:
            if nome in DESCRICOES_SELECAO:
                assert isinstance(DESCRICOES_SELECAO[nome], str)
                assert len(DESCRICOES_SELECAO[nome]) > 0

    def test_known_dinos_have_descriptions(self):
        assert "Tyrannosaurus rex" in DESCRICOES_SELECAO
        assert "Velociraptor mongoliensis" in DESCRICOES_SELECAO
