#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
environmental_monitor_device.py
================================
Dispositivo de monitoramento ambiental do laboratório para Raspberry Pi Zero 2W.
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


class EnvironmentalMonitorDevice(DeviceBase):
    """Dispositivo que monitora condições ambientais do laboratório."""

    TEMP_SENSOR_PIN = 4
    HUMIDITY_SENSOR_PIN = 17

    def __init__(self):
        super().__init__("Environmental Monitor")
        self.logger = logging.getLogger("Device:Environmental Monitor")
        self.temperature_c = 22.0
        self.humidity_pct = 50.0
        self.air_quality_index = 20

    def initialize(self) -> bool:
        if GPIO_AVAILABLE:
            GPIO.setmode(GPIO.BCM)
        self.initialized = True
        self.logger.info("Monitor ambiental inicializado")
        return True

    def measure_conditions(self) -> Dict:
        self.temperature_c += 0.1
        self.humidity_pct += 0.2
        self.air_quality_index = max(0, min(100, self.air_quality_index + 1))
        self.logger.info(f"Condições ambientais: {self.temperature_c:.1f}°C, {self.humidity_pct:.0f}% umidade")
        return {
            "temperature_c": round(self.temperature_c, 1),
            "humidity_pct": round(self.humidity_pct, 1),
            "air_quality_index": self.air_quality_index,
        }

    def status(self) -> Dict:
        base_status = super().status()
        base_status.update(self.measure_conditions())
        return base_status

    def shutdown(self) -> None:
        super().shutdown()
