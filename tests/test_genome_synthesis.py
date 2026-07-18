"""Tests for re_gen.core.genome_synthesis – ChunkStatus, GenomeSynthesisJob, GenomeSynthesizer."""

import json
from pathlib import Path

import pytest

from re_gen.core.genome_synthesis import (
    ChunkStatus,
    GenomeSynthesisJob,
    GenomeSynthesizer,
    create_test_genome_job,
)


# ---------------------------------------------------------------------------
# ChunkStatus enum
# ---------------------------------------------------------------------------


class TestChunkStatus:
    def test_all_values(self):
        expected = {"pending", "processing", "validated", "failed", "written"}
        assert {s.value for s in ChunkStatus} == expected

    def test_pending(self):
        assert ChunkStatus.PENDING.value == "pending"

    def test_processing(self):
        assert ChunkStatus.PROCESSING.value == "processing"

    def test_validated(self):
        assert ChunkStatus.VALIDATED.value == "validated"

    def test_failed(self):
        assert ChunkStatus.FAILED.value == "failed"

    def test_written(self):
        assert ChunkStatus.WRITTEN.value == "written"


# ---------------------------------------------------------------------------
# GenomeSynthesisJob
# ---------------------------------------------------------------------------


class TestGenomeSynthesisJob:
    def test_expected_chunks_exact(self):
        job = GenomeSynthesisJob(
            job_id="j1",
            target_species="T. rex",
            target_genome_size_bp=200_000,
            chunk_size_bp=100_000,
        )
        assert job.expected_chunks == 2

    def test_expected_chunks_rounds_up(self):
        job = GenomeSynthesisJob(
            job_id="j1",
            target_species="T. rex",
            target_genome_size_bp=250_000,
            chunk_size_bp=100_000,
        )
        assert job.expected_chunks == 3

    def test_expected_chunks_one_chunk(self):
        job = GenomeSynthesisJob(
            job_id="j1",
            target_species="T. rex",
            target_genome_size_bp=50_000,
            chunk_size_bp=100_000,
        )
        assert job.expected_chunks == 1

    def test_default_values(self):
        job = GenomeSynthesisJob(
            job_id="j1",
            target_species="T. rex",
            target_genome_size_bp=1_000_000,
        )
        assert job.chunk_size_bp == 100_000


# ---------------------------------------------------------------------------
# create_test_genome_job helper
# ---------------------------------------------------------------------------


class TestCreateTestGenomeJob:
    def test_defaults(self):
        job = create_test_genome_job()
        assert job.target_species == "Tyrannosaurus rex"
        assert job.target_genome_size_bp == 1_000_000
        assert "test_Tyrannosaurus_rex" == job.job_id

    def test_custom_species(self):
        job = create_test_genome_job(species="Velociraptor mongoliensis", size_bp=500_000)
        assert job.target_species == "Velociraptor mongoliensis"
        assert job.target_genome_size_bp == 500_000


# ---------------------------------------------------------------------------
# GenomeSynthesizer checkpoint save/load
# ---------------------------------------------------------------------------


class TestGenomeSynthesizerCheckpoint:
    def test_save_and_load(self, tmp_path):
        job = GenomeSynthesisJob(
            job_id="cp_test",
            target_species="T. rex",
            target_genome_size_bp=1_000_000,
            output_dir=tmp_path,
        )
        synth = GenomeSynthesizer(job)
        saved_path = synth.save_checkpoint()
        assert saved_path.exists()

        loaded = synth.load_checkpoint(str(saved_path))
        assert loaded["job_id"] == "cp_test"
        assert loaded["species"] == "T. rex"
        assert loaded["target_bp"] == 1_000_000
        assert "timestamp" in loaded

    def test_output_dir_created(self, tmp_path):
        out = tmp_path / "nested" / "output"
        job = GenomeSynthesisJob(
            job_id="j1",
            target_species="T. rex",
            target_genome_size_bp=1_000,
            output_dir=out,
        )
        synth = GenomeSynthesizer(job)
        assert synth.output_dir.exists()
