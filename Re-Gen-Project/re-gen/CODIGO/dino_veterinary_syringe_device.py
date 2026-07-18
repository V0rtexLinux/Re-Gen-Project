#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dino_veterinary_syringe_device.py
=================================
Siringa veterinária para grandes dinossauros, com agulha reforçada para amostras de sangue.
"""

import logging
import time
from typing import Dict, Optional

from device_base import DeviceBase

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False


class DinoVeterinarySyringeDevice(DeviceBase):
    """Dispositivo veterinário com seringa de alta força."""

    SYRINGE_PIN = 12
    NEEDLE_SERVO_PIN = 13

    def __init__(self):
        super().__init__("Dino Veterinary Syringe")
        self.logger = logging.getLogger("Device:Dino Veterinary Syringe")
        self.current_volume_ml = 0.0
        self.needle_depth_mm = 0.0
        self.prepared = False

    def initialize(self) -> bool:
        if GPIO_AVAILABLE:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.SYRINGE_PIN, GPIO.OUT)
            GPIO.setup(self.NEEDLE_SERVO_PIN, GPIO.OUT)
        self.initialized = True
        self.logger.info("Siringa veterinária inicializada")
        return True

    def prepare_needle(self) -> bool:
        self.logger.info("Preparando agulha reforçada")
        self.prepared = True
        time.sleep(1.0)
        return True

    def penetrate_skin(self, thickness_mm: float) -> bool:
        if not self.prepared:
            self.logger.warning("Agulha não preparada; preparando agora")
            self.prepare_needle()
        self.needle_depth_mm = thickness_mm
        self.logger.info(f"Penetrando pele até {thickness_mm}mm")
        time.sleep(min(3.0, thickness_mm / 10.0))
        return True

    def extract_blood_sample(self, species_name: str, volume_ml: float = 5.0) -> Optional[float]:
        self.logger.info(f"Extraindo amostra de sangue de {species_name}: {volume_ml:.1f}mL")
        if not self.prepared:
            self.prepare_needle()
        if volume_ml <= 0:
            self.logger.error("Volume de sangue inválido")
            return None
        self.penetrate_skin(thickness_mm=25.0)
        time.sleep(2.0)
        self.current_volume_ml = volume_ml
        self.logger.info(f"Amostra de {volume_ml:.1f}mL coletada")
        return self.current_volume_ml

    def inject_medication(self, species_name: str, volume_ml: float = 2.0) -> bool:
        self.logger.info(f"Injetando medicação em {species_name}: {volume_ml:.1f}mL")
        self.penetrate_skin(thickness_mm=20.0)
        time.sleep(1.5)
        self.logger.info("Medicação injetada")
        return True

    def status(self) -> Dict:
        base_status = super().status()
        base_status.update({
            "needle_prepared": self.prepared,
            "needle_depth_mm": self.needle_depth_mm,
            "last_volume_ml": self.current_volume_ml,
        })
        return base_status

    def shutdown(self) -> None:
        self.prepared = False
        self.needle_depth_mm = 0.0
        super().shutdown()
