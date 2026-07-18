#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fossil_cleaner_device.py
===========================
Dispositivo de limpeza de fósseis para remover detritos e preparar amostras.
"""

import logging
import time
from typing import Dict

from device_base import DeviceBase

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False


class FossilCleanerDevice(DeviceBase):
    """Dispositivo responsável pela limpeza de fósseis."""

    BRUSH_PIN = 23
    AIR_BLOWER_PIN = 24

    def __init__(self):
        super().__init__("Fossil Cleaner")
        self.logger = logging.getLogger("Device:Fossil Cleaner")
        self.brush_active = False
        self.air_active = False

    def initialize(self) -> bool:
        if GPIO_AVAILABLE:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.BRUSH_PIN, GPIO.OUT)
            GPIO.setup(self.AIR_BLOWER_PIN, GPIO.OUT)
            GPIO.output(self.BRUSH_PIN, GPIO.LOW)
            GPIO.output(self.AIR_BLOWER_PIN, GPIO.LOW)
        self.initialized = True
        self.logger.info("Dispositivo de limpeza de fósseis inicializado")
        return True

    def clean_surface(self, sample_name: str, mode: str = "delicate", duration_sec: float = 10.0) -> bool:
        self.logger.info(f"Iniciando limpeza do fóssil: {sample_name} (modo {mode})")
        self.brush_active = True
        self.air_active = True
        if GPIO_AVAILABLE:
            GPIO.output(self.BRUSH_PIN, GPIO.HIGH)
            GPIO.output(self.AIR_BLOWER_PIN, GPIO.HIGH)
        time.sleep(duration_sec)
        if GPIO_AVAILABLE:
            GPIO.output(self.BRUSH_PIN, GPIO.LOW)
            GPIO.output(self.AIR_BLOWER_PIN, GPIO.LOW)
        self.brush_active = False
        self.air_active = False
        self.logger.info(f"Limpeza de {sample_name} concluída")
        return True

    def status(self) -> Dict:
        base_status = super().status()
        base_status.update({
            "brush_active": self.brush_active,
            "air_active": self.air_active,
        })
        return base_status

    def shutdown(self) -> None:
        if GPIO_AVAILABLE:
            GPIO.output(self.BRUSH_PIN, GPIO.LOW)
            GPIO.output(self.AIR_BLOWER_PIN, GPIO.LOW)
        super().shutdown()
