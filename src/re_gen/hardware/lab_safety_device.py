#!/usr/bin/env python3
"""
lab_safety_device.py
====================
Dispositivo de segurança do laboratório para Raspberry Pi Zero 2W.
"""

from re_gen.hardware.device_base import DeviceBase


class LabSafetyDevice(DeviceBase):
    """Dispositivo de segurança geral do laboratório."""

    def __init__(self):
        super().__init__("Lab Safety")
        self.safe_mode = True

    def initialize(self) -> bool:
        self.safe_mode = True
        self.initialized = True
        return True

    def status(self) -> dict:
        base_status = super().status()
        base_status["safe_mode"] = self.safe_mode
        return base_status

    def shutdown(self) -> None:
        self.safe_mode = False
        super().shutdown()
