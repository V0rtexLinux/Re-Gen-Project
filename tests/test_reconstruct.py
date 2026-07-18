"""Tests for re_gen.core.reconstruct – reconstruct_ancestral_sequence and helpers."""

import pytest

from re_gen.ncbi.ncbi_reference import ReferenceSequenceDeep
from re_gen.core.reconstruct import (
    ReconstructionResult,
    ReconstructedPosition,
    low_confidence_regions,
    reconstruct_ancestral_sequence,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_ref(species: str, sequence: str, weight: float = 1.0) -> ReferenceSequenceDeep:
    return ReferenceSequenceDeep(
        species=species,
        accession=f"REF_{species.replace(' ', '_')}",
        gene_name="cytb",
        sequence=sequence,
        length=len(sequence),
        phylogenetic_distance=weight,
    )


# ---------------------------------------------------------------------------
# reconstruct_ancestral_sequence
# ---------------------------------------------------------------------------


class TestReconstructAncestralSequence:
    def test_identical_sequences(self):
        refs = [_make_ref("Gallus gallus", "ATCGATCGATCG")]
        result = reconstruct_ancestral_sequence("ATCGATCGATCG", refs)
        assert isinstance(result, ReconstructionResult)
        assert result.consensus_sequence == "ATCGATCGATCG"
        assert result.mean_confidence == pytest.approx(1.0)
        assert result.n_references_used == 1

    def test_two_references_consensus(self):
        refs = [
            _make_ref("Gallus", "ATCGATCG"),
            _make_ref("Crocodylus", "ATCGATCA"),
        ]
        result = reconstruct_ancestral_sequence("ATCGATCG", refs)
        assert len(result.consensus_sequence) > 0
        assert result.n_references_used == 2
        assert result.mean_confidence > 0.0

    def test_gc_content_calculated(self):
        refs = [_make_ref("Species A", "GCGCGCGCGC")]
        result = reconstruct_ancestral_sequence("GCGCGCGCGC", refs)
        assert result.gc_content == pytest.approx(100.0)

    def test_empty_fragment_raises(self):
        refs = [_make_ref("Species A", "ATCG")]
        with pytest.raises(ValueError, match="scanned_fragment"):
            reconstruct_ancestral_sequence("", refs)

    def test_empty_panel_raises(self):
        with pytest.raises(ValueError, match="reference_panel"):
            reconstruct_ancestral_sequence("ATCG", [])

    def test_per_base_confidence_length(self):
        refs = [_make_ref("Gallus", "ATCGATCGATCG")]
        result = reconstruct_ancestral_sequence("ATCGATCGATCG", refs)
        assert len(result.per_base_confidence) == len(result.consensus_sequence)

    def test_reference_species_listed(self):
        refs = [
            _make_ref("Gallus gallus", "ATCG"),
            _make_ref("Crocodylus", "ATCG"),
        ]
        result = reconstruct_ancestral_sequence("ATCG", refs)
        assert "Gallus gallus" in result.reference_species
        assert "Crocodylus" in result.reference_species

    def test_single_sequence_still_works(self):
        refs = [_make_ref("Lonchura", "ATCGATCGATCGATCG")]
        result = reconstruct_ancestral_sequence("ATCGATCGATCGATCG", refs)
        assert result.consensus_sequence == "ATCGATCGATCGATCG"


# ---------------------------------------------------------------------------
# low_confidence_regions
# ---------------------------------------------------------------------------


class TestLowConfidenceRegions:
    def test_all_high_confidence(self):
        result = ReconstructionResult(
            consensus_sequence="ATCG",
            per_base_confidence=[0.9, 0.8, 0.9, 0.95],
            mean_confidence=0.89,
            n_references_used=2,
            reference_species=["A", "B"],
            gc_content=50.0,
        )
        regions = low_confidence_regions(result, threshold=0.6)
        assert regions == []

    def test_low_confidence_region_detected(self):
        result = ReconstructionResult(
            consensus_sequence="ATCGATCG",
            per_base_confidence=[0.9, 0.9, 0.3, 0.2, 0.9, 0.9, 0.9, 0.9],
            mean_confidence=0.725,
            n_references_used=2,
            reference_species=["A", "B"],
            gc_content=50.0,
        )
        regions = low_confidence_regions(result, threshold=0.6)
        assert len(regions) >= 1
        assert regions[0] == (2, 4)

    def test_low_confidence_at_end(self):
        result = ReconstructionResult(
            consensus_sequence="ATCG",
            per_base_confidence=[0.9, 0.9, 0.3, 0.1],
            mean_confidence=0.525,
            n_references_used=1,
            reference_species=["A"],
            gc_content=50.0,
        )
        regions = low_confidence_regions(result, threshold=0.6)
        assert len(regions) >= 1
        assert regions[-1][1] == 4
