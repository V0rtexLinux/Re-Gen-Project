#!/usr/bin/env python3
"""
incubator_device.py
=====================
Dispositivo de incubadora com conexão Arduino para Raspberry Pi Zero 2W.
"""

import logging

from re_gen.hardware.arduino_bridge import ArduinoBridge
from re_gen.hardware.device_base import DeviceBase


class IncubatorDevice(DeviceBase):
    """Dispositivo de incubadora conectado via Arduino."""

    def __init__(self, port: str = "/dev/ttyUSB0", baudrate: int = 9600):
        super().__init__("Incubator")
        self.bridge = ArduinoBridge(port=port, baudrate=baudrate)
        self.logger = logging.getLogger("Device:Incubator")

    def initialize(self) -> bool:
        if self.bridge.ping():
            self.initialized = True
            self.logger.info("Incubadora conectada e pronta")
            return True

        self.logger.error("Falha ao conectar com a incubadora")
        return False

    def notify_embryo_injected(self, timestamp: str, volume_ul: float) -> bool:
        self.logger.info("Notificando incubadora sobre injeção")
        return self.bridge.notify_embryo_injected(timestamp, volume_ul)

    def status(self) -> dict:
        base_status = super().status()
        report = self.bridge.get_incubator_status() or {}
        base_status.update(report)
        return base_status

    def shutdown(self) -> None:
        self.bridge.disconnect()
        super().shutdown()
