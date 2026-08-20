"""Hardware abstraction layer with automatic simulation fallback."""

from re_gen.hardware.arduino_bridge import ArduinoBridge
from re_gen.hardware.device_base import DeviceBase
from re_gen.hardware.dino_veterinary_syringe_device import DinoVeterinarySyringeDevice
from re_gen.hardware.dna_storage_media_writer import (
    DNAStorageMediaWriter,
    ReedSolomonEncoder,
    StorageMetadata,
)
from re_gen.hardware.dna_synthesizer_device import DNASynthesizerDevice
from re_gen.hardware.dna_synthesizer_hardware import (
    ControladorHardwareSintetizador,
    DNASynthesizer,
    DNTPoolConfig,
    SynthesisParameter,
)
from re_gen.hardware.embryo_injection_robot import (
    EmbryoInjectionRobot,
    InjectionTarget,
    ServoMotor,
    SyringeController,
    XYZStage,
)
from re_gen.hardware.embryo_injector_device import EmbryoInjectorDevice
from re_gen.hardware.environmental_monitor_device import EnvironmentalMonitorDevice
from re_gen.hardware.extrator_dna_core import ExtratorDNA, ExtratorState
from re_gen.hardware.fossil_cleaner_device import FossilCleanerDevice
from re_gen.hardware.fossil_grinder_device import FossilGrinderDevice
from re_gen.hardware.hardware_devices import build_hardware_devices, get_default_device_order
from re_gen.hardware.hardware_orchestrator import (
    HardwareOrchestrator,
    HardwareState,
    InjectionStatus,
    OrchestrationJob,
)
from re_gen.hardware.hibridizador_core import Hibridizador, HibridizadorState
from re_gen.hardware.incubator_device import IncubatorDevice
from re_gen.hardware.lab_safety_device import LabSafetyDevice
from re_gen.hardware.scanner_input import (
    ScannedRead,
    ScannerInputError,
    load_scanner_output,
    summarize_reads,
)
from re_gen.hardware.utero_ovo_controller import (
    FaseUteroOvo,
    LeituraSensores,
    ParametrosProtocolo,
    UteroOvoController,
)

__all__ = [
    "ArduinoBridge",
    "ControladorHardwareSintetizador",
    "DeviceBase",
    "DinoVeterinarySyringeDevice",
    "DNASynthesizer",
    "DNASynthesizerDevice",
    "DNAStorageMediaWriter",
    "DNTPoolConfig",
    "EmbryoInjectionRobot",
    "EmbryoInjectorDevice",
    "EnvironmentalMonitorDevice",
    "ExtratorDNA",
    "ExtratorState",
    "FaseUteroOvo",
    "FossilCleanerDevice",
    "FossilGrinderDevice",
    "HardwareOrchestrator",
    "HardwareState",
    "Hibridizador",
    "HibridizadorState",
    "IncubatorDevice",
    "InjectionStatus",
    "InjectionTarget",
    "LabSafetyDevice",
    "LeituraSensores",
    "OrchestrationJob",
    "ParametrosProtocolo",
    "ReedSolomonEncoder",
    "ScannedRead",
    "ScannerInputError",
    "ServoMotor",
    "StorageMetadata",
    "SynthesisParameter",
    "SyringeController",
    "UteroOvoController",
    "XYZStage",
    "build_hardware_devices",
    "get_default_device_order",
    "load_scanner_output",
    "summarize_reads",
]
