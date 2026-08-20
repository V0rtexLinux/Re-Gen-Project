#!/usr/bin/env python3
"""
fossil_grinder_device.py
========================
Dispositivo de moagem de fósseis para extração de amostras pré-genômicas.
"""

import logging
import time

from re_gen.hardware.device_base import DeviceBase

try:
    import RPi.GPIO as GPIO

    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False


class FossilGrinderDevice(DeviceBase):
    """Dispositivo responsável pela moagem de fósseis."""

    GRINDER_PIN = 18
    PWM_FREQUENCY = 1000

    def __init__(self):
        super().__init__("Fossil Grinder")
        self.motor_speed = 0
        self.logger = logging.getLogger("Device:Fossil Grinder")
        self.pwm = None

    def initialize(self) -> bool:
        if GPIO_AVAILABLE:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.GRINDER_PIN, GPIO.OUT)
            self.pwm = GPIO.PWM(self.GRINDER_PIN, self.PWM_FREQUENCY)
            self.pwm.start(0)
        self.initialized = True
        self.logger.info("Dispositivo de moagem de fósseis inicializado")
        return True

    def grind_sample(self, sample_name: str, duration_sec: float = 15.0, speed_percent: float = 70.0) -> bool:
        self.logger.info(f"Iniciando moagem do fóssil: {sample_name}")
        self.motor_speed = max(10.0, min(100.0, speed_percent))
        if GPIO_AVAILABLE and self.pwm:
            self.pwm.ChangeDutyCycle(self.motor_speed)
        self.logger.info(f"Moendo a {self.motor_speed:.0f}% de potência")
        time.sleep(duration_sec)
        if GPIO_AVAILABLE and self.pwm:
            self.pwm.ChangeDutyCycle(0)
        self.logger.info(f"Moagem de {sample_name} concluída")
        return True

    def status(self) -> dict:
        base_status = super().status()
        base_status.update({"motor_speed": self.motor_speed, "grinding": False})
        return base_status

    def shutdown(self) -> None:
        if GPIO_AVAILABLE and self.pwm:
            self.pwm.stop()
        super().shutdown()
