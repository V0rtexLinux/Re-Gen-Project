"""Tests for re_gen.cli - command-line interface entry point."""

from unittest.mock import patch

import pytest


class TestCLIHelp:
    """Tests for --help flag."""

    def test_help_short_flag(self, capsys):
        from re_gen.cli import main

        with patch("sys.argv", ["re-gen", "-h"]):
            ret = main()
        assert ret == 0
        captured = capsys.readouterr()
        assert "re-gen" in captured.out
        assert "Usage:" in captured.out

    def test_help_long_flag(self, capsys):
        from re_gen.cli import main

        with patch("sys.argv", ["re-gen", "--help"]):
            ret = main()
        assert ret == 0
        captured = capsys.readouterr()
        assert "re-gen" in captured.out
        assert "--version" in captured.out


class TestCLIVersion:
    """Tests for --version flag."""

    def test_version_short_flag(self, capsys):
        from re_gen.cli import main

        with patch("sys.argv", ["re-gen", "-V"]):
            ret = main()
        assert ret == 0
        captured = capsys.readouterr()
        assert "re-gen" in captured.out
        assert "3.0.0" in captured.out

    def test_version_long_flag(self, capsys):
        from re_gen.cli import main

        with patch("sys.argv", ["re-gen", "--version"]):
            ret = main()
        assert ret == 0
        captured = capsys.readouterr()
        assert "3.0.0" in captured.out


class TestCLIDispatch:
    """Tests that the CLI forwards to the single unified pipeline."""

    def test_default_dispatches_to_unified_pipeline(self):
        from re_gen.cli import main

        argv = [
            "re-gen",
            "--email",
            "test@example.com",
            "--dinosaur",
            "Tyrannosaurus rex",
        ]
        with patch("sys.argv", argv), patch(
            "re_gen.pipeline.unified.main", return_value=0
        ) as mock_pipeline:
            ret = main()
        assert ret == 0
        mock_pipeline.assert_called_once()

    def test_lista_flag_lists_species_and_exits(self, capsys):
        """--lista must list species and exit 0 without requiring --email."""
        from re_gen.cli import main

        with patch("sys.argv", ["re-gen", "--lista"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "Tyrannosaurus rex" in captured.out

    def test_missing_email_is_a_usage_error(self):
        """Running the pipeline without --email must fail with a clear error."""
        from re_gen.cli import main

        with patch("sys.argv", ["re-gen"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
        assert exc_info.value.code != 0


class TestUnifiedPipelineParseArgs:
    """Tests for the unified pipeline's argument parser."""

    def test_parse_args_minimal(self):
        from re_gen.pipeline import unified

        test_args = ["--email", "test@example.com"]
        with patch("sys.argv", ["re-gen"] + test_args), patch.object(
            unified, "ReGenPipelineUnificado"
        ) as mock_pipeline_cls:
            mock_result = mock_pipeline_cls.return_value.executar.return_value
            mock_result.status_global = unified.PipelineStatus.CONCLUIDO
            mock_result.fases = []
            mock_result.dinossauro_selecionado.nome_cientifico = "Tyrannosaurus rex"
            mock_result.genoma_escala_completa = None
            mock_result.genoma_reconstruido = None
            mock_result.pacote_edicoes = None
            mock_result.diretorio_saida_final = "./re_gen_output"
            ret = unified.main()
        assert ret == 0
        _, kwargs = mock_pipeline_cls.call_args
        config = mock_pipeline_cls.call_args[0][0]
        assert config.ncbi_email == "test@example.com"
        assert config.hardware_disponivel is False
        assert config.fase_inicio == 0
        assert config.fase_fim == 8

    def test_parse_args_with_all_options(self):
        from re_gen.pipeline import unified

        test_args = [
            "--email", "user@test.com",
            "--api-key", "abc123",
            "--dinosaur", "Tyrannosaurus rex",
            "--hospedeiro", "Struthio camelus",
            "--hardware",
            "--sem-ia",
            "--output", "/tmp/re_gen_test",
            "--confianca", "0.75",
            "--fase-inicio", "0",
            "--fase-fim", "3",
        ]
        with patch("sys.argv", ["re-gen"] + test_args), patch.object(
            unified, "ReGenPipelineUnificado"
        ) as mock_pipeline_cls:
            mock_result = mock_pipeline_cls.return_value.executar.return_value
            mock_result.status_global = unified.PipelineStatus.CONCLUIDO
            mock_result.fases = []
            mock_result.dinossauro_selecionado.nome_cientifico = "Tyrannosaurus rex"
            mock_result.genoma_escala_completa = None
            mock_result.genoma_reconstruido = None
            mock_result.pacote_edicoes = None
            mock_result.diretorio_saida_final = "/tmp/re_gen_test"
            unified.main()

        config = mock_pipeline_cls.call_args[0][0]
        assert config.ncbi_api_key == "abc123"
        assert config.nome_dinossauro == "Tyrannosaurus rex"
        assert config.hospedeiro == "Struthio camelus"
        assert config.hardware_disponivel is True
        assert config.gerar_relatorio_ia is False
        assert config.diretorio_saida == "/tmp/re_gen_test"
        assert config.confianca_minima == 0.75
        assert config.fase_inicio == 0
        assert config.fase_fim == 3

    def test_fase_inicio_maior_que_fase_fim_e_erro(self):
        from re_gen.pipeline import unified

        test_args = [
            "--email", "test@example.com",
            "--fase-inicio", "5",
            "--fase-fim", "2",
        ]
        with patch("sys.argv", ["re-gen"] + test_args):
            with pytest.raises(SystemExit):
                unified.main()
