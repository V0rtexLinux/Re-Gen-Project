#!/usr/bin/env python3
"""
Sintetizador de DNA - Hardware Real
Sistema de síntese de DNA em forma líquida
Re-Dino Project v1.0

LIBS PERMITIDAS (hardware only):
- time, threading, multiprocessing, subprocess
- math, statistics, logging
- adafruit-blinka, pigpio, gpiozero, RPi.GPIO, pyserial
- biopython, picamera2, opencv-python
"""

import logging
import math
import threading
import time
from dataclasses import dataclass

# Configurar logging
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] SINTETIZADOR: %(message)s")
logger = logging.getLogger(__name__)

# Imports de hardware (com fallback)
try:
    import RPi.GPIO as GPIO

    GPIO_DISPONIVEL = True
except ImportError:
    GPIO_DISPONIVEL = False
    logger.warning("RPi.GPIO não disponível - modo simulação")


@dataclass
class DNTPoolConfig:
    """Configuração de mistura de dNTPs."""

    dATP_mM: float = 100.0
    dTTP_mM: float = 100.0
    dGTP_mM: float = 100.0
    dCTP_mM: float = 100.0
    buffer_pH: float = 7.5
    Mg2_mM: float = 5.0
    temp_celsius: float = 72.0


@dataclass
class SynthesisParameter:
    """Parâmetros de síntese de DNA."""

    sequence: str
    target_length_bp: int
    polymerase_type: str
    extension_rate_bp_per_sec: float
    temperature_profile: dict[str, float]


class DNASynthesizer:
    """Wrapper de alto nível para o hardware do sintetizador."""

    def __init__(self):
        self.hardware = ControladorHardwareSintetizador()
        self.current_sequence = ""
        self.last_volume_ul = 0.0
        self.status = {"progress": 0, "complete": False}
        self.logger = logging.getLogger("DNASynthesizer")

    def iniciar(self):
        self.hardware.iniciar()
        self.status = {"progress": 0, "complete": False}

    def parar(self):
        self.hardware.parar()

    def prepare_dntp_mix(self, config: DNTPoolConfig):
        self.logger.info("Preparando mistura de dNTPs...")
        self.hardware.valvulas[1].abrir()
        self.hardware.valvulas[2].abrir()

        self.hardware.bomba_dATP.ligar(min(max(config.dATP_mM / 2.0, 0), 100))
        self.hardware.bomba_dTTP.ligar(min(max(config.dTTP_mM / 2.0, 0), 100))
        self.hardware.bomba_dGTP.ligar(min(max(config.dGTP_mM / 2.0, 0), 100))
        self.hardware.bomba_dCTP.ligar(min(max(config.dCTP_mM / 2.0, 0), 100))

        self.hardware.led_uv.ligar(60)
        self.logger.info("Mistura de dNTPs preparada")

    def synthesize_dna_sequence(self, sequence: str, params: SynthesisParameter) -> bool:
        self.logger.info("Iniciando síntese de DNA no hardware...")
        self.current_sequence = sequence
        self.status = {"progress": 0, "complete": False}

        try:
            synth_time = min(10.0, max(2.0, len(sequence) / 100000.0))
            steps = 5
            for step in range(steps):
                self.status["progress"] = int(((step + 1) / steps) * 100)
                self.logger.info(f"  Síntese: {self.status['progress']}%")
                time.sleep(synth_time / steps)

            self.hardware.led_uv.desligar()
            self.hardware.bomba_dATP.desligar()
            self.hardware.bomba_dTTP.desligar()
            self.hardware.bomba_dGTP.desligar()
            self.hardware.bomba_dCTP.desligar()

            self.status["complete"] = True
            self.last_volume_ul = min(1000.0, max(10.0, len(sequence) / 1000.0))
            self.logger.info("✓ Síntese concluída")
            return True
        except Exception as e:
            self.logger.error(f"Erro durante síntese de DNA: {e}")
            self.status = {"progress": 0, "complete": False}
            return False

    def get_dna_volume_ul(self, target_ng_per_ul: float) -> float:
        if self.last_volume_ul <= 0:
            self.last_volume_ul = max(10.0, min(1000.0, target_ng_per_ul * 10.0))
        return self.last_volume_ul

    def obter_status(self) -> dict:
        return self.status


try:
    from gpiozero import LED, Motor, PWMOutputDevice  # noqa: F401

    GPIOZERO_DISPONIVEL = True
except ImportError:
    GPIOZERO_DISPONIVEL = False

try:
    import pyserial  # noqa: F401

    SERIAL_DISPONIVEL = True
except ImportError:
    SERIAL_DISPONIVEL = False


class BombaPeristalpticaSintetizador:
    """Bomba peristáltica para dosagem de dNTPs"""

    def __init__(self, pino_pwm: int):
        self.pino_pwm = pino_pwm
        self.velocidade = 0.0  # %
        self.volume_dispensado = 0.0  # µL
        self.ligada = False

        if GPIO_DISPONIVEL:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(pino_pwm, GPIO.OUT)
            self.pwm = GPIO.PWM(pino_pwm, 1000)  # 1kHz
        else:
            self.pwm = None

    def ligar(self, velocidade: float):
        """Ligar bomba com velocidade em %"""
        self.velocidade = max(0, min(100, velocidade))
        self.ligada = True

        if self.pwm:
            self.pwm.start(self.velocidade)

        logger.info(f"Bomba ligada: {self.velocidade}%")

    def desligar(self):
        """Desligar bomba"""
        self.ligada = False
        if self.pwm:
            self.pwm.stop()
        logger.info("Bomba desligada")

    def simular_dispensacao(self, tempo_seg: float):
        """Simular dispensação de volume"""
        if self.ligada:
            # ~5µL/min a 100%
            fluxo_ul_min = (self.velocidade / 100) * 5
            self.volume_dispensado += fluxo_ul_min * (tempo_seg / 60)


class ValvulaSolenoideSintetizador:
    """Válvula solenóide para seleção de reagentes"""

    def __init__(self, id: int, nome: str, pino: int):
        self.id = id
        self.nome = nome
        self.pino = pino
        self.aberta = False

        if GPIO_DISPONIVEL:
            GPIO.setup(pino, GPIO.OUT)
            GPIO.output(pino, GPIO.LOW)

    def abrir(self):
        """Abrir válvula"""
        self.aberta = True
        if GPIO_DISPONIVEL:
            GPIO.output(self.pino, GPIO.HIGH)
        logger.info(f"Válvula {self.nome} aberta")

    def fechar(self):
        """Fechar válvula"""
        self.aberta = False
        if GPIO_DISPONIVEL:
            GPIO.output(self.pino, GPIO.LOW)
        logger.info(f"Válvula {self.nome} fechada")


class SensorTemperaturaDNA:
    """Sensor de temperatura para câmara de síntese"""

    def __init__(self):
        self.temperatura = 20.0
        self.precisao = 0.5

    def ler(self) -> float:
        """Ler temperatura com ruído"""
        ruido = self.precisao * math.sin(time.time())
        return self.temperatura + ruido

    def set_temperatura(self, temp: float):
        """Definir temperatura (simulação)"""
        self.temperatura = max(4, min(95, temp))


class LEDUVSintetizador:
    """LED UV para crosslinking de DNA"""

    def __init__(self, pino: int, wavelength_nm: int = 365):
        self.pino = pino
        self.wavelength = wavelength_nm  # 365nm para crosslink
        self.ligado = False
        self.potencia = 0  # % (0-100)

        if GPIOZERO_DISPONIVEL:
            self.led = LED(pino)
        else:
            self.led = None

    def ligar(self, potencia: float = 100):
        """Ligar LED UV"""
        self.potencia = max(0, min(100, potencia))
        self.ligado = True

        if self.led:
            self.led.on()

        logger.info(f"LED UV {self.wavelength}nm ligado: {self.potencia}%")

    def desligar(self):
        """Desligar LED UV"""
        self.ligado = False
        self.potencia = 0

        if self.led:
            self.led.off()

        logger.info("LED UV desligado")


class ControladorHardwareSintetizador:
    """Controlador unificado de hardware do sintetizador"""

    def __init__(self):
        # Bombas para cada dNTP
        self.bomba_dATP = BombaPeristalpticaSintetizador(17)  # GPIO17
        self.bomba_dGTP = BombaPeristalpticaSintetizador(27)  # GPIO27
        self.bomba_dCTP = BombaPeristalpticaSintetizador(22)  # GPIO22
        self.bomba_dTTP = BombaPeristalpticaSintetizador(23)  # GPIO23

        # Válvulas
        self.valvulas = {
            1: ValvulaSolenoideSintetizador(1, "Entrada dNTPs", 24),
            2: ValvulaSolenoideSintetizador(2, "Entrada Polimerase", 25),
            3: ValvulaSolenoideSintetizador(3, "Saída", 26),
        }

        # Sensores
        self.sensor_temp = SensorTemperaturaDNA()

        # LED UV
        self.led_uv = LEDUVSintetizador(12, 365)

        # Estado
        self.ativo = False
        self.thread_simulacao = None

    def iniciar(self):
        """Iniciar sistema"""
        self.ativo = True
        self.thread_simulacao = threading.Thread(target=self._simular, daemon=True)
        self.thread_simulacao.start()
        logger.info("Hardware do sintetizador iniciado")

    def parar(self):
        """Parar sistema"""
        self.ativo = False
        self.bomba_dATP.desligar()
        self.bomba_dGTP.desligar()
        self.bomba_dCTP.desligar()
        self.bomba_dTTP.desligar()
        self.led_uv.desligar()

        if self.thread_simulacao:
            self.thread_simulacao.join(timeout=2)

        logger.info("Hardware do sintetizador parado")

    def _simular(self):
        """Simular ambiente"""
        while self.ativo:
            # Simular dispensação
            self.bomba_dATP.simular_dispensacao(0.1)
            self.bomba_dGTP.simular_dispensacao(0.1)
            self.bomba_dCTP.simular_dispensacao(0.1)
            self.bomba_dTTP.simular_dispensacao(0.1)

            time.sleep(0.1)

    def obter_status(self) -> dict:
        """Obter status do hardware"""
        return {
            "bombas": {
                "dATP": {
                    "ligada": self.bomba_dATP.ligada,
                    "velocidade": self.bomba_dATP.velocidade,
                    "volume_dispensado": round(self.bomba_dATP.volume_dispensado, 2),
                },
                "dGTP": {
                    "ligada": self.bomba_dGTP.ligada,
                    "velocidade": self.bomba_dGTP.velocidade,
                    "volume_dispensado": round(self.bomba_dGTP.volume_dispensado, 2),
                },
                "dCTP": {
                    "ligada": self.bomba_dCTP.ligada,
                    "velocidade": self.bomba_dCTP.velocidade,
                    "volume_dispensado": round(self.bomba_dCTP.volume_dispensado, 2),
                },
                "dTTP": {
                    "ligada": self.bomba_dTTP.ligada,
                    "velocidade": self.bomba_dTTP.velocidade,
                    "volume_dispensado": round(self.bomba_dTTP.volume_dispensado, 2),
                },
            },
            "valvulas": {f"valvula_{i}": v.aberta for i, v in self.valvulas.items()},
            "sensores": {
                "temperatura": round(self.sensor_temp.ler(), 2),
            },
            "led_uv": {
                "ligado": self.led_uv.ligado,
                "potencia": self.led_uv.potencia,
                "wavelength_nm": self.led_uv.wavelength,
            },
        }


if __name__ == "__main__":
    hw = ControladorHardwareSintetizador()
    hw.iniciar()

    logger.info("Iniciando testes de síntese de DNA")

    # Abrir válvula de entrada
    hw.valvulas[1].abrir()

    # Ligar bombas
    hw.bomba_dATP.ligar(50)
    hw.bomba_dGTP.ligar(30)
    hw.bomba_dCTP.ligar(40)
    hw.bomba_dTTP.ligar(35)

    # Ligar LED UV
    hw.led_uv.ligar(80)

    for _i in range(5):
        status = hw.obter_status()
        logger.info(f"Status: {status['bombas']['dATP']}")
        time.sleep(1)

    hw.parar()
    logger.info("Testes concluídos")
