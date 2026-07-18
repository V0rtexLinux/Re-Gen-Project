"""Tests for re_gen.core.enzyme_library – EnzymeLibrary, enzyme lookup, synthesis recipes."""

import pytest

from re_gen.core.enzyme_library import (
    EnzymeClass,
    EnzymeLibrary,
    get_enzyme_library,
)


@pytest.fixture
def library():
    return EnzymeLibrary()


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------


class TestSingleton:
    def test_get_enzyme_library_returns_instance(self):
        lib = get_enzyme_library()
        assert isinstance(lib, EnzymeLibrary)

    def test_singleton_same_instance(self):
        a = get_enzyme_library()
        b = get_enzyme_library()
        assert a is b


# ---------------------------------------------------------------------------
# Getting known enzymes
# ---------------------------------------------------------------------------


class TestGetEnzymes:
    def test_ecori(self, library):
        eco = library.get_enzyme("EcoRI")
        assert eco is not None
        assert eco.enzyme_class == EnzymeClass.RESTRICTION
        assert eco.recognition_site.recognition_sequence == "GAATTC"

    def test_hindiii(self, library):
        hind = library.get_enzyme("HindIII")
        assert hind is not None
        assert hind.recognition_site.recognition_sequence == "AAGCTT"

    def test_bamhi(self, library):
        bam = library.get_enzyme("BamHI")
        assert bam is not None
        assert bam.recognition_site.recognition_sequence == "GGATCC"

    def test_psti(self, library):
        pst = library.get_enzyme("PstI")
        assert pst is not None
        assert pst.recognition_site.recognition_sequence == "CTGCAG"

    def test_nonexistent_returns_none(self, library):
        assert library.get_enzyme("FakeEnzyme") is None

    def test_t4_ligase(self, library):
        lig = library.get_enzyme("T4 DNA Ligase")
        assert lig is not None
        assert lig.enzyme_class == EnzymeClass.LIGASE

    def test_taq_polymerase(self, library):
        taq = library.get_enzyme("Taq Polymerase")
        assert taq is not None
        assert taq.enzyme_class == EnzymeClass.POLYMERASE


# ---------------------------------------------------------------------------
# Enzyme class filtering
# ---------------------------------------------------------------------------


class TestEnzymeFiltering:
    def test_restriction_enzymes(self, library):
        restriction = library.get_restriction_enzymes()
        assert len(restriction) >= 4
        names = [e.name for e in restriction]
        assert "EcoRI" in names
        assert "HindIII" in names

    def test_ligases(self, library):
        ligases = library.get_ligases()
        assert len(ligases) >= 2
        names = [e.name for e in ligases]
        assert "T4 DNA Ligase" in names

    def test_polymerases(self, library):
        pols = library.get_polymerases()
        assert len(pols) >= 3
        names = [e.name for e in pols]
        assert "Taq Polymerase" in names
        assert "Pfu Polymerase" in names
        assert "Phusion Polymerase" in names


# ---------------------------------------------------------------------------
# Synthesis recipe generation
# ---------------------------------------------------------------------------


class TestSynthesisRecipe:
    def test_recipe_structure(self, library):
        recipe = library.get_synthesis_recipe(10_000)
        assert "fragment_size_bp" in recipe
        assert "recommended_enzymes" in recipe
        assert "total_cost_usd" in recipe
        assert recipe["fragment_size_bp"] == 10_000

    def test_recipe_has_enzymes(self, library):
        recipe = library.get_synthesis_recipe(5_000)
        assert len(recipe["recommended_enzymes"]) >= 3

    def test_recipe_cost_positive(self, library):
        recipe = library.get_synthesis_recipe(1_000)
        assert recipe["total_cost_usd"] > 0

    def test_recipe_steps(self, library):
        recipe = library.get_synthesis_recipe(10_000)
        steps = [e["step"] for e in recipe["recommended_enzymes"]]
        assert "PCR amplification" in steps
        assert "Ligation" in steps


# ---------------------------------------------------------------------------
# Find restriction enzyme for sequence
# ---------------------------------------------------------------------------


class TestFindRestrictionEnzymeForSequence:
    def test_ecori_site_found(self, library):
        seq = "ATCGGAATTCGATCG"
        results = library.find_restriction_enzyme_for_sequence(seq)
        names = [name for name, _ in results]
        assert "EcoRI" in names

    def test_bamhi_site_found(self, library):
        seq = "ATCGGGATCCGATCG"
        results = library.find_restriction_enzyme_for_sequence(seq)
        names = [name for name, _ in results]
        assert "BamHI" in names

    def test_no_sites(self, library):
        seq = "ATCGATCGATCGATCG"
        results = library.find_restriction_enzyme_for_sequence(seq)
        # No standard sites → empty or no EcoRI/BamHI
        names = [name for name, _ in results]
        assert "EcoRI" not in names

    def test_multiple_sites(self, library):
        seq = "GAATTCATCGGGATCC"
        results = library.find_restriction_enzyme_for_sequence(seq)
        names = [name for name, _ in results]
        assert "EcoRI" in names
        assert "BamHI" in names


# ---------------------------------------------------------------------------
# Add custom enzyme
# ---------------------------------------------------------------------------


class TestAddEnzyme:
    def test_add_and_retrieve(self, library):
        from re_gen.core.enzyme_library import Enzyme

        custom = Enzyme(
            name="CustomEnz",
            systematic_name="Custom",
            enzyme_class=EnzymeClass.RESTRICTION,
            organism_source="Lab",
            activity_unit="U",
            price_per_unit_usd=10.0,
            optimal_temperature_c=37,
            optimal_ph=7.5,
            buffer_composition="TE",
        )
        library.add_enzyme(custom)
        assert library.get_enzyme("CustomEnz") is custom
