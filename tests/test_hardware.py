"""Tests for re_gen.hardware modules - DeviceBase, devices, scanner, orchestrator."""

import textwrap
from unittest.mock import MagicMock, patch

import pytest

from re_gen.hardware.device_base import DeviceBase


# ---------------------------------------------------------------------------
# DeviceBase tests (no hardware dependencies)
# ---------------------------------------------------------------------------


class TestDeviceBase:
    """Tests for the DeviceBase class."""

    def test_creation(self):
        dev = DeviceBase("TestDevice")
        assert dev.name == "TestDevice"
        assert dev.initialized is False

    def test_initialize_returns_true(self):
        dev = DeviceBase("TestDevice")
        assert dev.initialize() is True
        assert dev.initialized is True

    def test_shutdown_unsets_initialized(self):
        dev = DeviceBase("TestDevice")
        dev.initialize()
        assert dev.initialized is True
        dev.shutdown()
        assert dev.initialized is False

    def test_status_dict(self):
        dev = DeviceBase("TestDevice")
        status = dev.status()
        assert isinstance(status, dict)
        assert status["name"] == "TestDevice"
        assert status["initialized"] is False
        assert "updated_at" in status

    def test_status_after_initialize(self):
        dev = DeviceBase("TestDevice")
        dev.initialize()
        status = dev.status()
        assert status["initialized"] is True

    def test_shutdown_without_initialize(self):
        dev = DeviceBase("TestDevice")
        dev.shutdown()
        assert dev.initialized is False


# ---------------------------------------------------------------------------
# Hardware devices - build_hardware_devices
# ---------------------------------------------------------------------------


class TestBuildHardwareDevices:
    """Tests for hardware_devices.build_hardware_devices."""

    @pytest.fixture(autouse=True)
    def _mock_hardware_deps(self):
        """Mock all hardware-dependent constructors."""
        mock_bridge = MagicMock()
        mock_bridge.ping.return_value = True
        with (
            patch("re_gen.hardware.arduino_bridge.ArduinoBridge", mock_bridge),
            patch("re_gen.hardware.embryo_injector_device.EmbryoInjectionRobot"),
        ):
            yield

    def test_build_all_devices(self):
        """build_hardware_devices should create devices for all specs."""
        from re_gen.hardware.hardware_devices import (
            HARDWARE_DEVICE_SPECS,
            build_hardware_devices,
        )

        devices = build_hardware_devices()
        assert isinstance(devices, dict)
        assert len(devices) == len(HARDWARE_DEVICE_SPECS)

    def test_all_devices_are_device_base(self):
        from re_gen.hardware.hardware_devices import build_hardware_devices

        devices = build_hardware_devices()
        for key, dev in devices.items():
            assert isinstance(dev, DeviceBase), f"Device '{key}' is not a DeviceBase"

    def test_device_keys_match_specs(self):
        from re_gen.hardware.hardware_devices import HARDWARE_DEVICE_SPECS, build_hardware_devices

        devices = build_hardware_devices()
        assert set(devices.keys()) == set(HARDWARE_DEVICE_SPECS.keys())


class TestDefaultDeviceOrder:
    """Tests for get_default_device_order."""

    def test_returns_list(self):
        from re_gen.hardware.hardware_devices import get_default_device_order

        order = get_default_device_order()
        assert isinstance(order, list)
        assert len(order) > 0

    def test_returns_copy(self):
        from re_gen.hardware.hardware_devices import get_default_device_order

        a = get_default_device_order()
        b = get_default_device_order()
        assert a == b
        assert a is not b


class TestHardwareDeviceSpec:
    """Tests for HardwareDeviceSpec dataclass."""

    def test_all_specs_have_valid_class(self):
        from re_gen.hardware.hardware_devices import HARDWARE_DEVICE_SPECS

        for key, spec in HARDWARE_DEVICE_SPECS.items():
            assert isinstance(spec.name, str)
            assert issubclass(spec.cls, DeviceBase)


# ---------------------------------------------------------------------------
# ScannerInput tests (FASTQ / FASTA reading)
# ---------------------------------------------------------------------------


class TestScannerInput:
    """Tests for hardware.scanner_input."""

    def test_load_fastq(self, tmp_path):
        """Read a synthetic FASTQ file."""
        fastq = tmp_path / "test.fastq"
        seq = "ATCGATCGATCGATCG" * 4  # 64 chars
        qual = "I" * 64
        record = f"@read1\n{seq}\n+\n{qual}\n"
        fastq.write_text(record * 3)

        from re_gen.hardware.scanner_input import load_scanner_output

        reads = load_scanner_output(str(fastq), min_length=10)
        assert len(reads) == 3
        assert reads[0].length == 64

    def test_load_fasta(self, tmp_path):
        """Read a synthetic FASTA file."""
        fasta = tmp_path / "test.fasta"
        record = ">seq1 test sequence\nATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG\n"
        fasta.write_text(record * 2)

        from re_gen.hardware.scanner_input import load_scanner_output

        reads = load_scanner_output(str(fasta), min_length=10)
        assert len(reads) == 2
        assert reads[0].mean_quality is None  # FASTA has no quality

    def test_filter_short_reads(self, tmp_path):
        """Short reads below min_length are filtered."""
        fastq = tmp_path / "test.fastq"
        short_seq = "ATCG"
        short_qual = "IIII"
        long_seq = "ATCGATCGATCGATCG" * 4  # 64 chars
        long_qual = "I" * 64
        fastq.write_text(f"@read1\n{short_seq}\n+\n{short_qual}\n@read2\n{long_seq}\n+\n{long_qual}\n")

        from re_gen.hardware.scanner_input import load_scanner_output

        reads = load_scanner_output(str(fastq), min_length=10)
        assert len(reads) == 1
        assert reads[0].read_id == "read2"

    def test_filter_low_quality(self, tmp_path):
        """Reads below min_mean_quality are filtered in FASTQ."""
        fastq = tmp_path / "test.fastq"
        seq = "ATCGATCGATCGATCG" * 4  # 64 chars
        # Quality scores: '!' = 0, 'I' = 40
        bad_qual = "!" * 64
        good_qual = "I" * 64
        fastq.write_text(f"@bad_read\n{seq}\n+\n{bad_qual}\n@good_read\n{seq}\n+\n{good_qual}\n")

        from re_gen.hardware.scanner_input import load_scanner_output

        reads = load_scanner_output(str(fastq), min_length=10, min_mean_quality=7.0)
        assert len(reads) == 1
        assert reads[0].read_id == "good_read"

    def test_nonexistent_file_raises(self):
        from re_gen.hardware.scanner_input import ScannerInputError, load_scanner_output

        with pytest.raises(ScannerInputError, match="nao encontrado"):
            load_scanner_output("/nonexistent/file.fastq")

    def test_unsupported_format_raises(self, tmp_path):
        from re_gen.hardware.scanner_input import ScannerInputError, load_scanner_output

        bad_file = tmp_path / "test.xyz"
        bad_file.write_text("data")
        with pytest.raises(ScannerInputError, match="nao reconhecido"):
            load_scanner_output(str(bad_file))

    def test_all_reads_filtered_raises(self, tmp_path):
        from re_gen.hardware.scanner_input import ScannerInputError, load_scanner_output

        fastq = tmp_path / "test.fastq"
        fastq.write_text("@r1\nATCG\n+\nIIII\n")
        with pytest.raises(ScannerInputError, match="Nenhuma leitura"):
            load_scanner_output(str(fastq), min_length=100)

    def test_all_reads_low_quality_raises(self, tmp_path):
        from re_gen.hardware.scanner_input import ScannerInputError, load_scanner_output

        fastq = tmp_path / "test.fastq"
        seq = "ATCGATCGATCGATCG" * 4  # 64 chars
        bad_qual = "!" * 64  # all quality 0
        fastq.write_text(f"@r1\n{seq}\n+\n{bad_qual}\n")
        with pytest.raises(ScannerInputError, match="Nenhuma leitura"):
            load_scanner_output(str(fastq), min_length=10, min_mean_quality=7.0)


class TestSummarizeReads:
    """Tests for summarize_reads."""

    def test_summary_fields(self, tmp_path):
        from re_gen.hardware.scanner_input import load_scanner_output, summarize_reads

        fastq = tmp_path / "test.fastq"
        seq = "ATCGATCGATCGATCG" * 3 + "ATCG"  # 52 chars
        qual = "I" * 52
        record = f"@r1\n{seq}\n+\n{qual}\n"
        fastq.write_text(record * 3)
        reads = load_scanner_output(str(fastq), min_length=10)
        summary = summarize_reads(reads)
        assert summary["n_reads"] == 3
        assert summary["total_bases"] == 3 * 52
        assert summary["avg_length"] > 0
        assert summary["avg_quality"] is not None

    def test_summary_no_quality(self, tmp_path):
        from re_gen.hardware.scanner_input import load_scanner_output, summarize_reads

        fasta = tmp_path / "test.fasta"
        fasta.write_text(">s1\nATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG\n")
        reads = load_scanner_output(str(fasta), min_length=10)
        summary = summarize_reads(reads)
        assert summary["avg_quality"] is None


# ---------------------------------------------------------------------------
# HardwareOrchestrator tests
# ---------------------------------------------------------------------------


class TestHardwareOrchestrator:
    """Tests for HardwareOrchestrator creation and state."""

    def test_creation(self):
        from re_gen.hardware.hardware_orchestrator import HardwareOrchestrator, HardwareState

        orch = HardwareOrchestrator()
        assert orch.state == HardwareState.IDLE
        assert orch.devices == {}
        assert orch.last_error is None

    def test_custom_port(self):
        from re_gen.hardware.hardware_orchestrator import HardwareOrchestrator

        orch = HardwareOrchestrator(arduino_port="/dev/ttyACM0", arduino_baudrate=115200)
        assert orch.arduino_port == "/dev/ttyACM0"
        assert orch.arduino_baudrate == 115200

    def test_initial_status(self):
        from re_gen.hardware.hardware_orchestrator import HardwareOrchestrator, HardwareState

        orch = HardwareOrchestrator()
        status = orch.get_status()
        assert isinstance(status, dict)
        assert status["state"] == HardwareState.IDLE.value
        assert status["synthesizer_ready"] is False
        assert status["injector_ready"] is False
        assert status["incubator_ready"] is False
        assert status["current_job"] is None
        assert status["last_error"] is None

    def test_device_order_populated(self):
        from re_gen.hardware.hardware_orchestrator import HardwareOrchestrator

        orch = HardwareOrchestrator()
        assert len(orch.device_order) > 0

    def test_get_device_returns_none_when_empty(self):
        from re_gen.hardware.hardware_orchestrator import HardwareOrchestrator

        orch = HardwareOrchestrator()
        assert orch.get_device("synthesizer") is None

    def test_job_id_format(self):
        from re_gen.hardware.hardware_orchestrator import OrchestrationJob

        job = OrchestrationJob(job_id="test_123", species_name="Testus")
        assert job.job_id == "test_123"
        assert job.species_name == "Testus"
        assert job.state.value == "idle"
        assert job.events == []

    def test_job_log_event(self):
        from re_gen.hardware.hardware_orchestrator import OrchestrationJob

        job = OrchestrationJob(job_id="test", species_name="Testus")
        job.log_event("TEST", "test message")
        assert len(job.events) == 1
        assert job.events[0]["type"] == "TEST"
        assert job.events[0]["message"] == "test message"
        assert "timestamp" in job.events[0]


class TestHardwareState:
    """Tests for HardwareState enum."""

    def test_all_states_unique(self):
        from re_gen.hardware.hardware_orchestrator import HardwareState

        values = [s.value for s in HardwareState]
        assert len(values) == len(set(values))

    def test_expected_states_exist(self):
        from re_gen.hardware.hardware_orchestrator import HardwareState

        expected = {"idle", "ready", "synthesizing", "injecting", "incubating", "error", "emergency_stop"}
        actual = {s.value for s in HardwareState}
        assert expected.issubset(actual)


class TestInjectionStatus:
    """Tests for InjectionStatus enum."""

    def test_all_statuses_unique(self):
        from re_gen.hardware.hardware_orchestrator import InjectionStatus

        values = [s.value for s in InjectionStatus]
        assert len(values) == len(set(values))
