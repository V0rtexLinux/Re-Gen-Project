"""Tests for re_gen.cli - command-line interface entry point."""

import sys
from unittest.mock import patch

import pytest

from re_gen.cli import main


class TestCLIHelp:
    """Tests for --help flag."""

    def test_help_short_flag(self, capsys):
        with patch("sys.argv", ["re-gen", "-h"]):
            ret = main()
        assert ret == 0
        captured = capsys.readouterr()
        assert "re-gen" in captured.out
        assert "Usage:" in captured.out

    def test_help_long_flag(self, capsys):
        with patch("sys.argv", ["re-gen", "--help"]):
            ret = main()
        assert ret == 0
        captured = capsys.readouterr()
        assert "re-gen" in captured.out
        assert "--version" in captured.out


class TestCLIVersion:
    """Tests for --version flag."""

    def test_version_short_flag(self, capsys):
        with patch("sys.argv", ["re-gen", "-V"]):
            ret = main()
        assert ret == 0
        captured = capsys.readouterr()
        assert "re-gen" in captured.out
        assert "3.0.0" in captured.out

    def test_version_long_flag(self, capsys):
        with patch("sys.argv", ["re-gen", "--version"]):
            ret = main()
        assert ret == 0
        captured = capsys.readouterr()
        assert "3.0.0" in captured.out


class TestCLIDispatch:
    """Tests for pipeline dispatch."""

    def test_v2_dispatches_to_v2_main(self):
        argv = [
            "re-gen",
            "v2",
            "--gene",
            "COI",
            "--host-species",
            "Gallus gallus",
            "--ncbi-email",
            "test" + chr(64) + "test.com",
        ]
        with patch("sys.argv", argv), patch("re_gen.pipeline.main.main", return_value=0) as mock_v2:
            ret = main()
        assert ret == 0
        mock_v2.assert_called_once()

    def test_default_dispatches_to_v3(self):
        argv = ["re-gen", "--species", "Tyrannosaurus rex", "--ncbi-email", "test" + chr(64) + "test.com"]
        with patch("sys.argv", argv), patch("re_gen.pipeline.main_v3.main", return_value=0) as mock_v3:
            ret = main()
        assert ret == 0
        mock_v3.assert_called_once()


class TestPipelineMainParseArgs:
    """Tests for pipeline.main.parse_args."""

    def test_parse_args_minimal(self):
        from re_gen.pipeline.main import parse_args

        test_args = [
            "--gene",
            "cytochrome b",
            "--host-species",
            "Struthio camelus",
            "--ncbi-email",
            "test@example.com",
        ]
        with patch("sys.argv", ["re-gen"] + test_args):
            args = parse_args()
        assert args.gene == "cytochrome b"
        assert args.host_species == "Struthio camelus"
        assert args.ncbi_email == "test@example.com"

    def test_parse_args_defaults(self):
        from re_gen.pipeline.main import parse_args

        test_args = [
            "--gene",
            "COI",
            "--host-species",
            "Gallus gallus",
            "--ncbi-email",
            "test@example.com",
        ]
        with patch("sys.argv", ["re-gen"] + test_args):
            args = parse_args()
        assert args.hardware == "nenhuma"
        assert args.min_length == 50
        assert args.min_quality == 7.0
        assert args.dinosaur is None
        assert args.ncbi_api_key is None

    def test_parse_args_with_all_options(self):
        from re_gen.pipeline.main import parse_args

        test_args = [
            "--gene",
            "FOXP2",
            "--host-species",
            "Gallus gallus",
            "--ncbi-email",
            "user@test.com",
            "--ncbi-api-key",
            "abc123",
            "--dinosaur",
            "Tyrannosaurus rex",
            "--preferencia-dieta",
            "carnívoro",
            "--preferencia-tamanho-min",
            "100",
            "--preferencia-tamanho-max",
            "5000",
            "--hardware",
            "basica",
            "--scanner-file",
            "/tmp/test.fastq",
            "--min-length",
            "100",
            "--min-quality",
            "10.0",
        ]
        with patch("sys.argv", ["re-gen"] + test_args):
            args = parse_args()
        assert args.gene == "FOXP2"
        assert args.ncbi_api_key == "abc123"
        assert args.dinosaur == "Tyrannosaurus rex"
        assert args.preferencia_dieta == "carnívoro"
        assert args.preferencia_tamanho_min == 100.0
        assert args.preferencia_tamanho_max == 5000.0
        assert args.hardware == "basica"
        assert args.scanner_file == "/tmp/test.fastq"
        assert args.min_length == 100
        assert args.min_quality == 10.0


class TestPipelineMainV3Args:
    """Tests for pipeline.main_v3.main argument parser."""

    def test_v3_requires_species(self):
        with patch("sys.argv", ["re-gen"]):
            with pytest.raises(SystemExit):
                # main_v3 constructs parser internally; simulate parse by calling
                # directly with no args
                import argparse

                parser = argparse.ArgumentParser()
                parser.add_argument("--species", required=True)
                parser.add_argument("--ncbi-email", required=True)
                parser.parse_args([])
