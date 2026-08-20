"""Tests for re_gen.exceptions - custom exception hierarchy."""

import pytest

from re_gen.exceptions import (
    ConfigurationError,
    CRISPRError,
    HardwareError,
    ReGenError,
    ReconstructionError,
    ReferenceSearchError,
    SequenceError,
    SimulationOnlyError,
    ValidationError,
)


class TestExceptionInheritance:
    """Tests for exception inheritance relationships."""

    def test_all_base_classes_inherit_from_regen_error(self):
        base_exceptions = [
            SequenceError,
            ReconstructionError,
            ReferenceSearchError,
            ValidationError,
            CRISPRError,
            HardwareError,
            ConfigurationError,
        ]
        for exc_class in base_exceptions:
            assert issubclass(exc_class, ReGenError)

    def test_regen_error_inherits_from_exception(self):
        assert issubclass(ReGenError, Exception)

    def test_simulation_only_error_inherits_from_hardware_error(self):
        assert issubclass(SimulationOnlyError, HardwareError)

    def test_simulation_only_error_also_inherits_regen_error(self):
        assert issubclass(SimulationOnlyError, ReGenError)

    def test_simulation_only_error_inherits_exception(self):
        assert issubclass(SimulationOnlyError, Exception)


class TestExceptionCanbeRaisedAndCaught:
    """Tests that all exception classes can be raised and caught."""

    @pytest.mark.parametrize(
        "exc_class",
        [
            ReGenError,
            SequenceError,
            ReconstructionError,
            ReferenceSearchError,
            ValidationError,
            CRISPRError,
            HardwareError,
            SimulationOnlyError,
            ConfigurationError,
        ],
    )
    def test_can_be_raised(self, exc_class):
        with pytest.raises(exc_class):
            raise exc_class("test message")

    @pytest.mark.parametrize(
        "exc_class",
        [
            ReGenError,
            SequenceError,
            ReconstructionError,
            ReferenceSearchError,
            ValidationError,
            CRISPRError,
            HardwareError,
            SimulationOnlyError,
            ConfigurationError,
        ],
    )
    def test_can_be_caught_as_regen_error(self, exc_class):
        with pytest.raises(ReGenError):
            raise exc_class("test message")

    @pytest.mark.parametrize(
        "exc_class",
        [
            ReGenError,
            SequenceError,
            ReconstructionError,
            ReferenceSearchError,
            ValidationError,
            CRISPRError,
            HardwareError,
            SimulationOnlyError,
            ConfigurationError,
        ],
    )
    def test_can_be_caught_as_exception(self, exc_class):
        with pytest.raises(Exception):
            raise exc_class("test message")


class TestSimulationOnlyErrorHierarchy:
    """Tests that SimulationOnlyError is correctly in the hierarchy."""

    def test_catch_as_hardware_error(self):
        with pytest.raises(HardwareError):
            raise SimulationOnlyError("no real hardware")

    def test_catch_as_regen_error(self):
        with pytest.raises(ReGenError):
            raise SimulationOnlyError("no real hardware")

    def test_not_catchable_as_sequence_error(self):
        with pytest.raises(HardwareError):
            with pytest.raises(SequenceError):
                raise SimulationOnlyError("no real hardware")


class TestExceptionMessages:
    """Tests that exceptions preserve messages."""

    @pytest.mark.parametrize(
        "exc_class",
        [
            SequenceError,
            ReconstructionError,
            ReferenceSearchError,
            ValidationError,
            CRISPRError,
            HardwareError,
            SimulationOnlyError,
            ConfigurationError,
        ],
    )
    def test_message_preserved(self, exc_class):
        msg = "Something went wrong"
        try:
            raise exc_class(msg)
        except exc_class as e:
            assert str(e) == msg
