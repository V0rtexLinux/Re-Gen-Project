#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dna_synthesizer_device.py
===========================
Dispositivo de sintetizador de DNA para Raspberry Pi Zero 2W.
"""

import logging
from typing import Dict, Optional

from device_base import DeviceBase
from dna_synthesizer_hardware import DNASynthesizer, DNTPoolConfig, SynthesisParameter


class DNASynthesizerDevice(DeviceBase):
    """Dispositivo de sintetização de DNA."""

    def __init__(self):
        super().__init__("DNA Synthesizer")
        self.synthesizer = DNASynthesizer()
        self.config: Optional[DNTPoolConfig] = None
        self.last_volume_ul: float = 0.0
        self.logger = logging.getLogger("Device:DNA Synthesizer")

    def initialize(self) -> bool:
        self.synthesizer.iniciar()
        self.initialized = True
        self.logger.info("DNA Synthesizer inicializado")
        return True

    def prepare_mix(self, config: DNTPoolConfig) -> None:
        self.config = config
        self.synthesizer.prepare_dntp_mix(config)
        self.logger.info("Mistura de dNTPs preparada")

    def synthesize(self, sequence: str, params: SynthesisParameter) -> Optional[float]:
        self.logger.info("Iniciando síntese de DNA")
        success = self.synthesizer.synthesize_dna_sequence(sequence, params)
        if not success:
            self.logger.error("Falha na síntese de DNA")
            return None

        self.last_volume_ul = self.synthesizer.get_dna_volume_ul(50.0)
        self.logger.info(f"DNA sintetizado com volume {self.last_volume_ul:.2f}µL")
        return self.last_volume_ul

    def status(self) -> Dict:
        status = self.synthesizer.obter_status()
        base_status = super().status()
        base_status.update({
            "dna_progress": status.get("progress", 0),
            "dna_complete": status.get("complete", False),
            "volume_ul": self.last_volume_ul,
        })
        return base_status

    def shutdown(self) -> None:
        self.synthesizer.parar()
        super().shutdown()
