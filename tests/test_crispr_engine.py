"""Tests for re_gen.core.crispr_engine – CRISPRDesigner, GuideRNA, CRISPREditingPlan."""

import pytest

from re_gen.core.crispr_engine import (
    CRISPRDesigner,
    CRISPREditingPlan,
    Cas9Variant,
    GuideRNA,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def designer():
    return CRISPRDesigner(variant=Cas9Variant.SPCAS9)


@pytest.fixture
def cpf_designer():
    return CRISPRDesigner(variant=Cas9Variant.CPFCAS9)


@pytest.fixture
def long_sequence():
    """A 100-bp sequence rich with NGG PAM sites for SpCas9."""
    return "ATGCGATCGATCGTAGCTAGCTAGCTGATCGATCGATCGATCGTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGC"


# ---------------------------------------------------------------------------
# GuideRNA dataclass
# ---------------------------------------------------------------------------


class TestGuideRNAProperties:
    def test_combined_score(self):
        grna = GuideRNA(
            sequence="A" * 20,
            pam="AGG",
            position=0,
            specificity_score=80.0,
            efficiency_score=60.0,
        )
        assert grna.combined_score == pytest.approx(70.0)

    def test_is_good_when_all_criteria_met(self):
        grna = GuideRNA(
            sequence="ATCGATCGATCGATCGATCG",
            pam="AGG",
            position=0,
            gc_content=50.0,
            specificity_score=80.0,
            efficiency_score=80.0,
            off_targets_count=2,
            homopolymer_count=0,
        )
        assert grna.is_good is True

    def test_is_bad_when_high_off_targets(self):
        grna = GuideRNA(
            sequence="ATCGATCGATCGATCGATCG",
            pam="AGG",
            position=0,
            gc_content=50.0,
            specificity_score=80.0,
            efficiency_score=80.0,
            off_targets_count=10,
            homopolymer_count=0,
        )
        assert grna.is_good is False

    def test_is_bad_when_low_gc(self):
        grna = GuideRNA(
            sequence="AAAAAAAAAAAAAAAAAAAA",
            pam="AGG",
            position=0,
            gc_content=5.0,
            specificity_score=80.0,
            efficiency_score=80.0,
            off_targets_count=0,
            homopolymer_count=0,
        )
        assert grna.is_good is False

    def test_is_bad_when_homopolymer_present(self):
        grna = GuideRNA(
            sequence="ATCGATCGATCGATCGATCG",
            pam="AGG",
            position=0,
            gc_content=50.0,
            specificity_score=80.0,
            efficiency_score=80.0,
            off_targets_count=0,
            homopolymer_count=1,
        )
        assert grna.is_good is False

    def test_is_bad_when_low_score(self):
        grna = GuideRNA(
            sequence="ATCGATCGATCGATCGATCG",
            pam="AGG",
            position=0,
            gc_content=50.0,
            specificity_score=40.0,
            efficiency_score=40.0,
            off_targets_count=0,
            homopolymer_count=0,
        )
        assert grna.is_good is False


# ---------------------------------------------------------------------------
# CRISPRDesigner – GC content
# ---------------------------------------------------------------------------


class TestGCCContent:
    def test_all_gc(self, designer):
        assert designer._calculate_gc_content("GCGCGC") == pytest.approx(100.0)

    def test_no_gc(self, designer):
        assert designer._calculate_gc_content("ATATAT") == pytest.approx(0.0)

    def test_mixed(self, designer):
        assert designer._calculate_gc_content("ATCG") == pytest.approx(50.0)

    def test_empty(self, designer):
        assert designer._calculate_gc_content("") == 0.0


# ---------------------------------------------------------------------------
# CRISPRDesigner – Homopolymer counting
# ---------------------------------------------------------------------------


class TestHomopolymerCount:
    def test_no_homopolymer(self, designer):
        assert designer._count_homopolymers("ATCGATCGATCG") == 0

    def test_one_homopolymer(self, designer):
        assert designer._count_homopolymers("AAAATCGATCG") == 1

    def test_multiple_homopolymers(self, designer):
        seq = "AAAATTTTCCCC"
        count = designer._count_homopolymers(seq)
        assert count >= 3

    def test_short_homopolymer_ignored(self, designer):
        assert designer._count_homopolymers("AAATCGATCG") == 0


# ---------------------------------------------------------------------------
# CRISPRDesigner – Specificity / Efficiency scoring
# ---------------------------------------------------------------------------


class TestScoring:
    def test_specificity_range(self, designer):
        for seq in ["ATCGATCGATCGATCGATCG", "GCGCGCGCGCGCGCGCGCGC", "AAAAAAAAAAAAAAAAAAAA"]:
            score = designer._score_specificity(seq)
            assert 0.0 <= score <= 100.0

    def test_efficiency_range(self, designer):
        for seq in ["ATCGATCGATCGATCGATCG", "GCGCGCGCGCGCGCGCGCGC", "AAAAAAAAAAAAAAAAAAAA"]:
            score = designer._score_efficiency(seq)
            assert 0.0 <= score <= 100.0


# ---------------------------------------------------------------------------
# CRISPRDesigner – PAM finding
# ---------------------------------------------------------------------------


class TestPAMFinding:
    def test_finds_ngg_pams(self, designer):
        # NGG = [ATCG]GG: AGG at 2, CGG at 11, TGG at 14
        seq = "AAAGGGTTTCCCTGGAGG"
        pams = designer._find_pams(seq)
        assert len(pams) >= 3

    def test_no_pams_in_at_only(self, designer):
        pams = designer._find_pams("ATAAATAAATAAAATAAAA")
        assert len(pams) == 0

    def test_cpf_finds_ttn_pams(self, cpf_designer):
        seq = "TTAGCTTAGCTTAGC"
        pams = cpf_designer._find_pams(seq)
        assert len(pams) >= 1


# ---------------------------------------------------------------------------
# CRISPRDesigner – find_grnas
# ---------------------------------------------------------------------------


class TestFindGRNAs:
    def test_returns_grnas(self, designer, long_sequence):
        grnas = designer.find_grnas(long_sequence, num_grnas=5)
        assert len(grnas) <= 5
        assert all(isinstance(g, GuideRNA) for g in grnas)

    def test_grnas_sorted_by_score(self, designer, long_sequence):
        grnas = designer.find_grnas(long_sequence, num_grnas=5)
        scores = [g.combined_score for g in grnas]
        assert scores == sorted(scores, reverse=True)

    def test_region_filter(self, designer, long_sequence):
        grnas = designer.find_grnas(
            long_sequence,
            region_start=10,
            region_end=30,
            num_grnas=10,
        )
        for g in grnas:
            assert 10 <= g.position < 30

    def test_empty_sequence(self, designer):
        grnas = designer.find_grnas("", num_grnas=5)
        assert grnas == []

    def test_sequence_with_no_pams(self, designer):
        grnas = designer.find_grnas("A" * 40, num_grnas=5)
        assert grnas == []

    def test_sequence_too_short(self, designer):
        grnas = designer.find_grnas("ATGC", num_grnas=5)
        assert grnas == []


# ---------------------------------------------------------------------------
# CRISPRDesigner – design_edit_plan
# ---------------------------------------------------------------------------


class TestDesignEditPlan:
    def test_plan_is_valid(self, designer, long_sequence):
        plan = designer.design_edit_plan(
            long_sequence,
            target_start=10,
            target_end=40,
            desired_change="deletion",
        )
        assert isinstance(plan, CRISPREditingPlan)
        assert plan.desired_change == "deletion"
        assert plan.target_start == 10
        assert plan.target_end == 40

    def test_plan_has_grnas(self, designer):
        # Build a sequence with frequent NGG PAMs in the search window
        seq = "ATCGATCGATCGAGGATCGATCGATCGAGGATCGATCGATCGAGG" * 5
        plan = designer.design_edit_plan(
            seq,
            target_start=50,
            target_end=100,
            desired_change="substitution",
            desired_sequence="AAAA",
        )
        assert len(plan.grnas) > 0

    def test_plan_efficiency_positive(self, designer, long_sequence):
        plan = designer.design_edit_plan(
            long_sequence,
            target_start=10,
            target_end=40,
            desired_change="insertion",
        )
        assert plan.expected_efficiency >= 0.0


# ---------------------------------------------------------------------------
# CRISPRDesigner – Risk identification
# ---------------------------------------------------------------------------


class TestRiskIdentification:
    def test_no_grnas_yields_risk(self, designer):
        risks = designer._identify_risks([], "ATCGATCG")
        assert any("Nenhum gRNA" in r for r in risks)

    def test_low_efficiency_risk(self, designer):
        grnas = [
            GuideRNA("A" * 20, "AGG", 0, efficiency_score=30.0),
        ]
        risks = designer._identify_risks(grnas, "ATCGATCG")
        assert any("Eficiência" in r for r in risks)

    def test_homopolymer_risk(self, designer):
        grnas = [
            GuideRNA(
                "ATCGATCGATCGATCGATCG",
                "AGG",
                0,
                gc_content=50.0,
                efficiency_score=80.0,
                homopolymer_count=1,
            ),
        ]
        risks = designer._identify_risks(grnas, "ATCGATCG")
        assert any("homopolímeros" in r for r in risks)


# ---------------------------------------------------------------------------
# Cas9 Variant enum
# ---------------------------------------------------------------------------


class TestCas9Variant:
    def test_spCas9_pam(self):
        assert Cas9Variant.SPCAS9.value[0] == "NGG"

    def test_cpf_pam(self):
        assert Cas9Variant.CPFCAS9.value[0] == "TTN"

    def test_designer_uses_variant_pam(self, cpf_designer):
        assert cpf_designer.pam_pattern == "TTN"
