"""Tests for re_gen.core.gene_edit_package – build_edit_package and CSV export."""

import csv
from pathlib import Path

import pytest

from re_gen.core.gene_edit_package import (
    EditPackage,
    GeneEdit,
    build_edit_package,
    export_edit_package_csv,
)
from re_gen.core.reconstruct import ReconstructionResult


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def reconstruction_result():
    return ReconstructionResult(
        consensus_sequence="ATCGATCGATCGATCGATCG",
        per_base_confidence=[
            0.95,
            0.95,
            0.95,
            0.95,
            0.95,
            0.95,
            0.95,
            0.95,
            0.95,
            0.95,
            0.95,
            0.95,
            0.95,
            0.95,
            0.95,
            0.95,
            0.95,
            0.95,
            0.95,
            0.95,
        ],
        mean_confidence=0.95,
        n_references_used=3,
        reference_species=["Gallus", "Crocodylus", "Chelonia"],
        gc_content=50.0,
    )


@pytest.fixture
def reconstruction_with_low_confidence():
    return ReconstructionResult(
        consensus_sequence="ATCGATCGATCGATCGATCG",
        per_base_confidence=[
            0.95,
            0.95,
            0.3,
            0.95,
            0.95,
            0.95,
            0.95,
            0.95,
            0.95,
            0.95,
            0.95,
            0.95,
            0.95,
            0.95,
            0.95,
            0.95,
            0.95,
            0.95,
            0.95,
            0.95,
        ],
        mean_confidence=0.91,
        n_references_used=3,
        reference_species=["Gallus", "Crocodylus", "Chelonia"],
        gc_content=50.0,
    )


# ---------------------------------------------------------------------------
# build_edit_package
# ---------------------------------------------------------------------------


class TestBuildEditPackage:
    def test_identical_sequences_no_edits(self, reconstruction_result):
        pkg = build_edit_package(
            reconstruction_result,
            host_sequence="ATCGATCGATCGATCGATCG",
            host_species="Gallus gallus",
            target_species_label="T. rex",
        )
        assert isinstance(pkg, EditPackage)
        assert pkg.n_total_edits == 0
        assert pkg.pct_genome_identity == 100.0

    def test_different_sequences_produce_edits(self, reconstruction_result):
        pkg = build_edit_package(
            reconstruction_result,
            host_sequence="TTTTTTTTTTTTTTTTTTTT",
            host_species="Gallus gallus",
            target_species_label="T. rex",
        )
        assert pkg.n_total_edits > 0
        assert all(isinstance(e, GeneEdit) for e in pkg.edits)

    def test_low_confidence_positions_skipped(self, reconstruction_with_low_confidence):
        pkg = build_edit_package(
            reconstruction_with_low_confidence,
            host_sequence="TTTTTTTTTTTTTTTTTTTT",
            host_species="Gallus gallus",
            target_species_label="T. rex",
        )
        # Position 2 has 0.3 confidence — should be skipped if different
        edit_positions = [e.position for e in pkg.edits]
        assert 2 not in edit_positions

    def test_pct_identity(self, reconstruction_result):
        pkg = build_edit_package(
            reconstruction_result,
            host_sequence="ATCGATCGATCGATCGATCG",
            host_species="Gallus gallus",
            target_species_label="T. rex",
        )
        assert pkg.pct_genome_identity == 100.0

    def test_species_labels(self, reconstruction_result):
        pkg = build_edit_package(
            reconstruction_result,
            host_sequence="TTTTTTTTTTTTTTTTTTTT",
            host_species="Gallus gallus",
            target_species_label="T. rex",
        )
        assert pkg.host_species == "Gallus gallus"
        assert pkg.target_species_label == "T. rex"

    def test_min_confidence_threshold(self, reconstruction_result):
        pkg = build_edit_package(
            reconstruction_result,
            host_sequence="TTTTTTTTTTTTTTTTTTTT",
            host_species="Gallus gallus",
            target_species_label="T. rex",
            min_confidence_to_edit=0.99,
        )
        # All confidences are 0.95 < 0.99, so no edits
        assert pkg.n_total_edits == 0

    def test_edit_type_is_substitution(self, reconstruction_result):
        pkg = build_edit_package(
            reconstruction_result,
            host_sequence="TTTTTTTTTTTTTTTTTTTT",
            host_species="Gallus gallus",
            target_species_label="T. rex",
        )
        assert all(e.edit_type == "substituicao" for e in pkg.edits)

    def test_short_host_sequence(self, reconstruction_result):
        pkg = build_edit_package(
            reconstruction_result,
            host_sequence="ATCG",
            host_species="Gallus gallus",
            target_species_label="T. rex",
        )
        assert pkg.n_total_edits == 0
        assert pkg.pct_genome_identity == 100.0


# ---------------------------------------------------------------------------
# CSV export
# ---------------------------------------------------------------------------


class TestExportCSV:
    def test_creates_csv_file(self, reconstruction_result, tmp_path):
        pkg = build_edit_package(
            reconstruction_result,
            host_sequence="TTTTTTTTTTTTTTTTTTTT",
            host_species="Gallus gallus",
            target_species_label="T. rex",
        )
        csv_path = str(tmp_path / "edits.csv")
        export_edit_package_csv(pkg, csv_path)
        assert Path(csv_path).exists()

    def test_csv_has_header(self, reconstruction_result, tmp_path):
        pkg = build_edit_package(
            reconstruction_result,
            host_sequence="TTTTTTTTTTTTTTTTTTTT",
            host_species="Gallus gallus",
            target_species_label="T. rex",
        )
        csv_path = str(tmp_path / "edits.csv")
        export_edit_package_csv(pkg, csv_path)
        with open(csv_path) as f:
            reader = csv.reader(f)
            header = next(reader)
        assert header == ["position", "host_base", "target_base", "edit_type", "confidence"]

    def test_csv_row_count_matches_edits(self, reconstruction_result, tmp_path):
        pkg = build_edit_package(
            reconstruction_result,
            host_sequence="TTTTTTTTTTTTTTTTTTTT",
            host_species="Gallus gallus",
            target_species_label="T. rex",
        )
        csv_path = str(tmp_path / "edits.csv")
        export_edit_package_csv(pkg, csv_path)
        with open(csv_path) as f:
            rows = list(csv.reader(f))
        # header + data rows
        assert len(rows) - 1 == pkg.n_total_edits

    def test_empty_edit_package_csv(self, reconstruction_result, tmp_path):
        pkg = build_edit_package(
            reconstruction_result,
            host_sequence="ATCGATCGATCGATCGATCG",
            host_species="Gallus gallus",
            target_species_label="T. rex",
        )
        csv_path = str(tmp_path / "empty.csv")
        export_edit_package_csv(pkg, csv_path)
        with open(csv_path) as f:
            rows = list(csv.reader(f))
        assert len(rows) == 1  # header only
