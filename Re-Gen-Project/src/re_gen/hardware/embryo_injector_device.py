#!/usr/bin/env python3
"""
embryo_injector_device.py
===========================
Dispositivo de injeção de embrião para Raspberry Pi Zero 2W.
"""

import logging

from re_gen.hardware.device_base import DeviceBase
from re_gen.hardware.embryo_injection_robot import EmbryoInjectionRobot, InjectionTarget


class EmbryoInjectorDevice(DeviceBase):
    """Dispositivo de injeção em embrião."""

    def __init__(self):
        super().__init__("Embryo Injector")
        self.injector = EmbryoInjectionRobot()
        self.last_target: InjectionTarget | None = None
        self.last_success = False
        self.logger = logging.getLogger("Device:Embryo Injector")

    def initialize(self) -> bool:
        self.injector.calibrate()
        self.initialized = True
        self.logger.info("Embryo Injector calibrado e pronto")
        return True

    def prepare_injection(self) -> bool:
        self.logger.info("Preparando sistema de injeção")
        self.injector.stage.home()
        self.injector.syringe.refill()
        self.logger.info("Sistema de injeção preparado")
        return True

    def detect_embryo_target(self, image=None) -> InjectionTarget | None:
        self.logger.info("Detectando alvo de injeção")
        target = self.injector.find_embryo_nucleus(image)
        if target:
            self.logger.info(f"Alvo detectado em ({target.x_mm}, {target.y_mm}, {target.z_mm}) mm")
        return target

    def inject_dna(self, sequence: str, target: InjectionTarget, dna_concentration_ng_ul: float = 50.0) -> bool:
        self.logger.info("Executando injeção de DNA")
        self.last_target = target
        self.last_success = self.injector.inject_dna(sequence, target, dna_concentration_ng_ul)
        if self.last_success:
            self.logger.info("Injeção realizada com sucesso")
        else:
            self.logger.error("Falha na injeção")
        return self.last_success

    def status(self) -> dict:
        base_status = super().status()
        base_status.update(
            {
                "target": {
                    "x_mm": getattr(self.last_target, "x_mm", None),
                    "y_mm": getattr(self.last_target, "y_mm", None),
                    "z_mm": getattr(self.last_target, "z_mm", None),
                    "volume_nl": getattr(self.last_target, "volume_nl", None),
                },
                "last_success": self.last_success,
            }
        )
        return base_status

    def shutdown(self) -> None:
        self.injector.cleanup()
        super().shutdown()
