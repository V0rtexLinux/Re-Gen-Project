"""Custom exception hierarchy for Re-Gen."""


class ReGenError(Exception):
    """Base exception for all Re-Gen errors."""


class SequenceError(ReGenError):
    """Invalid or malformed DNA sequence."""


class ReconstructionError(ReGenError):
    """Ancestral sequence reconstruction failed."""


class ReferenceSearchError(ReGenError):
    """NCBI/reference search failed."""


class ValidationError(ReGenError):
    """Sequence validation failed."""


class CRISPRError(ReGenError):
    """CRISPR design error."""


class HardwareError(ReGenError):
    """Hardware communication error."""


class SimulationOnlyError(HardwareError):
    """Operation requires real hardware but only simulation is available."""


class ConfigurationError(ReGenError):
    """Invalid configuration."""
