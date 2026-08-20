#!/usr/bin/env python3
"""
device_base.py
===============
Base comum para dispositivos de hardware no Re-Gen Project.
"""

import logging
from datetime import datetime


class DeviceBase:
    """Classe base para dispositivos de hardware."""

    def __init__(self, name: str):
        self.name = name
        self.initialized = False
        self.logger = logging.getLogger(f"Device:{name}")

    def initialize(self) -> bool:
        """Inicializa o dispositivo."""
        self.logger.info(f"Inicializando dispositivo {self.name}")
        self.initialized = True
        return True

    def shutdown(self) -> None:
        """Desliga o dispositivo e libera recursos."""
        self.logger.info(f"Desligando dispositivo {self.name}")
        self.initialized = False

    def status(self) -> dict:
        """Retorna o estado atual do dispositivo."""
        return {
            "name": self.name,
            "initialized": self.initialized,
            "updated_at": datetime.now().isoformat(),
        }
