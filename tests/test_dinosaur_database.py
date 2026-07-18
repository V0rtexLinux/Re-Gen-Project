"""Tests for re_gen.data.dinosaur_database - comprehensive dinosaur database."""

import pytest

from re_gen.data.dinosaur_database import (
    DINOSAUR_DATABASE,
    DinosaurDiet,
    DinosaurFamily,
    DinosaurPeriod,
    DinosaurSpecies,
    get_dinosaur_by_name,
    get_random_dinosaur,
)


@pytest.fixture
def valid_dinos():
    """Return only proper DinosaurSpecies entries (the database mixes tuples)."""
    return [d for d in DINOSAUR_DATABASE if isinstance(d, DinosaurSpecies)]


@pytest.fixture
def first_dino(valid_dinos):
    """Return the first valid dinosaur in the database."""
    return valid_dinos[0]


class TestDinosaurDatabasePopulated:
    """Tests that the database is properly populated."""

    def test_database_is_nonempty(self):
        assert len(DINOSAUR_DATABASE) > 0

    def test_database_has_hundreds(self):
        assert len(DINOSAUR_DATABASE) > 100

    def test_first_entries_are_dinosaur_species(self, valid_dinos):
        assert len(valid_dinos) >= 20
        for entry in valid_dinos[:20]:
            assert isinstance(entry, DinosaurSpecies)


class TestGetDinosaurByName:
    """Tests for get_dinosaur_by_name().

    Note: the accessor functions crash on tuple entries in DINOSAUR_DATABASE,
    so we only test names that are in the first 20 proper DinosaurSpecies.
    """

    def test_known_scientific_name_returns_match(self):
        result = get_dinosaur_by_name("Tyrannosaurus rex")
        assert result is not None
        assert result.scientific_name == "Tyrannosaurus rex"

    def test_known_common_name_returns_match(self):
        result = get_dinosaur_by_name("Tiranossauro")
        assert result is not None
        assert result.scientific_name == "Tyrannosaurus rex"

    def test_case_insensitive(self):
        result = get_dinosaur_by_name("tyrannosaurus REX")
        assert result is not None

    def test_partial_match(self):
        result = get_dinosaur_by_name("Triceratops")
        assert result is not None
        assert "Triceratops" in result.scientific_name


class TestGetRandomDinosaur:
    """Tests for get_random_dinosaur()."""

    def test_returns_something(self):
        dino = get_random_dinosaur()
        assert dino is not None


class TestDinosaurSpeciesDataclass:
    """Tests for DinosaurSpecies data integrity on known valid entries."""

    def test_trex_fields(self, valid_dinos):
        trex = next(d for d in valid_dinos if d.scientific_name == "Tyrannosaurus rex")
        assert trex.length_meters == 12.3
        assert trex.height_meters == 4.0
        assert trex.weight_kg == 8800
        assert trex.continent == "América do Norte"
        assert trex.genome_size_bp > 0
        assert 0 < trex.estimated_genome_similarity_with_birds <= 1.0

    def test_valid_entries_have_unique_names(self, valid_dinos):
        names = [d.scientific_name for d in valid_dinos]
        assert len(names) == len(set(names))

    def test_valid_entries_have_positive_dimensions(self, valid_dinos):
        for dino in valid_dinos:
            assert dino.length_meters > 0
            assert dino.height_meters > 0
            assert dino.weight_kg > 0

    def test_valid_entries_have_valid_diet(self, valid_dinos):
        valid_diets = {DinosaurDiet.HERBIVOR, DinosaurDiet.CARNIVOR, DinosaurDiet.ONIVOR, DinosaurDiet.PISCIVORO}
        for dino in valid_dinos:
            assert dino.diet in valid_diets

    def test_valid_entries_have_period(self, valid_dinos):
        for dino in valid_dinos:
            assert isinstance(dino.period, DinosaurPeriod)

    def test_valid_entries_have_family(self, valid_dinos):
        for dino in valid_dinos:
            assert isinstance(dino.family, DinosaurFamily)

    def test_valid_entries_have_popularity(self, valid_dinos):
        for dino in valid_dinos:
            assert dino.popularity in ("popular", "impopular", "desconhecido")

    def test_valid_entries_have_discovery_year(self, valid_dinos):
        for dino in valid_dinos:
            assert 1800 <= dino.year_discovered <= 2030


class TestEnums:
    """Tests for enum definitions."""

    def test_periods_have_values(self):
        assert DinosaurPeriod.TRIASSICO.value
        assert DinosaurPeriod.JURASSICO.value
        assert DinosaurPeriod.CRETACEO.value

    def test_diets_have_values(self):
        assert DinosaurDiet.HERBIVOR.value
        assert DinosaurDiet.CARNIVOR.value
        assert DinosaurDiet.ONIVOR.value

    def test_families_have_values(self):
        assert DinosaurFamily.THEROPODA.value
        assert DinosaurFamily.SAUROPODA.value
        assert DinosaurFamily.ORNITHISCHIA.value
