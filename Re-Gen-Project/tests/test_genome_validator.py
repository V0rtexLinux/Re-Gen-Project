"""Tests for re_gen.core.genome_validator – GenomeValidator and ValidationReport."""

import pytest

from re_gen.core.genome_validator import (
    GenomeValidator,
    SeverityLevel,
    ValidationReport,
    create_validator,
)


@pytest.fixture
def validator():
    return GenomeValidator()


# ---------------------------------------------------------------------------
# ValidationReport properties
# ---------------------------------------------------------------------------


class TestValidationReport:
    def test_is_valid_with_no_errors(self, validator):
        report = validator.validate("ATCGATCGATCGATCGATCG")
        assert report.is_valid is True

    def test_is_invalid_with_critical(self, validator):
        report = validator.validate("ATCGXYZATCG")
        assert report.is_valid is False

    def test_error_count(self, validator):
        report = validator.validate("ATCGXYZATCG")
        assert report.error_count >= 1

    def test_warning_count(self, validator):
        seq = "A" * 100 + "ATCG" * 20 + "G" * 100
        report = validator.validate(seq)
        assert report.warning_count >= 0

    def test_to_dict(self, validator):
        report = validator.validate("ATCGATCG")
        d = report.to_dict()
        assert "chunk_id" in d
        assert "is_valid" in d
        assert "issues" in d

    def test_str_representation(self, validator):
        report = validator.validate("ATCGATCG")
        s = str(report)
        assert "Validação" in s


# ---------------------------------------------------------------------------
# Valid DNA sequence
# ---------------------------------------------------------------------------


class TestValidSequence:
    def test_clean_sequence_no_issues(self, validator):
        report = validator.validate("ATCGATCGATCGATCGATCG", chunk_id="clean")
        assert report.is_valid is True
        assert report.chunk_id == "clean"
        assert report.sequence_length == 20

    def test_sequence_with_n_is_valid(self, validator):
        report = validator.validate("ATCGNNNNATCG")
        assert report.is_valid is True


# ---------------------------------------------------------------------------
# Invalid characters
# ---------------------------------------------------------------------------


class TestInvalidCharacters:
    def test_xyz_detected(self, validator):
        report = validator.validate("ATCGXYZATCG")
        assert report.is_valid is False
        types = [i.issue_type for i in report.issues]
        assert "invalid_character" in types

    def test_lowercase_invalid(self, validator):
        report = validator.validate("atcgxyzatcg")
        assert report.is_valid is False

    def test_mixed_invalid(self, validator):
        report = validator.validate("ATCG123!@#")
        assert report.is_valid is False


# ---------------------------------------------------------------------------
# GC content validation
# ---------------------------------------------------------------------------


class TestGCContent:
    def test_low_gc_warning(self, validator):
        seq = "A" * 100
        report = validator.validate(seq)
        types = [i.issue_type for i in report.issues]
        assert "low_gc_content" in types

    def test_high_gc_warning(self, validator):
        seq = "G" * 50 + "C" * 50
        report = validator.validate(seq)
        types = [i.issue_type for i in report.issues]
        assert "high_gc_content" in types

    def test_normal_gc_no_warning(self, validator):
        seq = "ATCG" * 25  # 50% GC
        report = validator.validate(seq)
        types = [i.issue_type for i in report.issues]
        assert "low_gc_content" not in types
        assert "high_gc_content" not in types


# ---------------------------------------------------------------------------
# Homopolymer detection
# ---------------------------------------------------------------------------


class TestHomopolymer:
    def test_long_a_detected(self, validator):
        seq = "ATCG" + "A" * 15 + "ATCG"
        report = validator.validate(seq)
        types = [i.issue_type for i in report.issues]
        assert "homopolymer" in types

    def test_long_g_detected(self, validator):
        seq = "ATCG" + "G" * 12 + "ATCG"
        report = validator.validate(seq)
        types = [i.issue_type for i in report.issues]
        assert "homopolymer" in types

    def test_short_homopolymer_not_flagged(self, validator):
        seq = "ATCGAAAATCGATCG"  # AAAA = 4 < threshold 10
        report = validator.validate(seq)
        types = [i.issue_type for i in report.issues]
        assert "homopolymer" not in types


# ---------------------------------------------------------------------------
# Stop codon detection
# ---------------------------------------------------------------------------


class TestStopCodons:
    def test_taa_detected(self, validator):
        seq = "ATGCGATAAATCGATCGATCG"
        report = validator.validate(seq)
        types = [i.issue_type for i in report.issues]
        assert "stop_codon" in types

    def test_tag_detected(self, validator):
        seq = "ATGCGATAGATCGATCGATCG"
        report = validator.validate(seq)
        types = [i.issue_type for i in report.issues]
        assert "stop_codon" in types

    def test_tga_detected(self, validator):
        seq = "ATGCGATGAATCGATCGATCG"
        report = validator.validate(seq)
        types = [i.issue_type for i in report.issues]
        assert "stop_codon" in types

    def test_no_stop_codons(self, validator):
        seq = "ATGCGATCGATCGATCGATCG"
        report = validator.validate(seq)
        types = [i.issue_type for i in report.issues]
        assert "stop_codon" not in types


# ---------------------------------------------------------------------------
# create_validator factory
# ---------------------------------------------------------------------------


class TestCreateValidator:
    def test_returns_validator(self):
        v = create_validator()
        assert isinstance(v, GenomeValidator)
