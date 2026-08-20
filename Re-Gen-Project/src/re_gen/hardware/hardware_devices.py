#!/usr/bin/env python3
"""
hardware_devices.py
===================

Fábrica e registro dos dispositivos de hardware do Re-Gen Project.
Este módulo representa a arquitetura de dispositivos como um catálogo
de componentes e define a ordem de inicialização usada pelo orquestrador.
"""

import logging
from dataclasses import dataclass, field

from re_gen.hardware.device_base import DeviceBase
from re_gen.hardware.dino_veterinary_syringe_device import DinoVeterinarySyringeDevice
from re_gen.hardware.dna_synthesizer_device import DNASynthesizerDevice
from re_gen.hardware.embryo_injector_device import EmbryoInjectorDevice
from re_gen.hardware.environmental_monitor_device import EnvironmentalMonitorDevice
from re_gen.hardware.fossil_cleaner_device import FossilCleanerDevice
from re_gen.hardware.fossil_grinder_device import FossilGrinderDevice
from re_gen.hardware.incubator_device import IncubatorDevice
from re_gen.hardware.lab_safety_device import LabSafetyDevice

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class HardwareDeviceSpec:
    """Especificação de um dispositivo de hardware."""

    name: str
    cls: type[DeviceBase]
    init_kwargs: dict = field(default_factory=dict)


DEFAULT_HARDWARE_DEVICE_ORDER: list[str] = [
    "synthesizer",
    "injector",
    "incubator",
    "fossil_grinder",
    "fossil_cleaner",
    "vet_syringe",
    "environment_monitor",
    "safety_device",
]

HARDWARE_DEVICE_SPECS: dict[str, HardwareDeviceSpec] = {
    "synthesizer": HardwareDeviceSpec("DNA Synthesizer", DNASynthesizerDevice),
    "injector": HardwareDeviceSpec("Embryo Injector", EmbryoInjectorDevice),
    "incubator": HardwareDeviceSpec("Incubator", IncubatorDevice),
    "fossil_grinder": HardwareDeviceSpec("Fossil Grinder", FossilGrinderDevice),
    "fossil_cleaner": HardwareDeviceSpec("Fossil Cleaner", FossilCleanerDevice),
    "vet_syringe": HardwareDeviceSpec("Dino Veterinary Syringe", DinoVeterinarySyringeDevice),
    "environment_monitor": HardwareDeviceSpec("Environmental Monitor", EnvironmentalMonitorDevice),
    "safety_device": HardwareDeviceSpec("Lab Safety", LabSafetyDevice),
}


def build_hardware_devices(arduino_port: str = "/dev/ttyUSB0", baudrate: int = 9600) -> dict[str, DeviceBase]:
    """Cria instâncias de todos os dispositivos do sistema."""
    devices: dict[str, DeviceBase] = {}

    for key, spec in HARDWARE_DEVICE_SPECS.items():
        kwargs = dict(spec.init_kwargs)
        if key == "incubator":
            kwargs.update({"port": arduino_port, "baudrate": baudrate})

        logger.debug(f"Criando dispositivo '{key}' ({spec.name})")
        devices[key] = spec.cls(**kwargs)

    return devices


def get_default_device_order() -> list[str]:
    """Retorna a ordem padrão de inicialização dos dispositivos."""
    return list(DEFAULT_HARDWARE_DEVICE_ORDER)


__all__ = [
    "DEFAULT_HARDWARE_DEVICE_ORDER",
    "HARDWARE_DEVICE_SPECS",
    "HardwareDeviceSpec",
    "build_hardware_devices",
    "get_default_device_order",
]
