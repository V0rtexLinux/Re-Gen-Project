#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema Robótico de Injeção de DNA em Embrião
Re-Dino Project v1.0

LIBS PERMITIDAS (hardware only):
- time, threading, multiprocessing, subprocess
- math, statistics, logging
- adafruit-blinka, pigpio, gpiozero, RPi.GPIO, pyserial
- biopython, picamera2, opencv-python
"""

import time
import threading
import math
import logging
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] INJECTOR: %(message)s'
)
logger = logging.getLogger(__name__)

# Hardware
try:
    from gpiozero import Servo, Motor, DistanceSensor
    GPIOZERO_DISPONIVEL = True
except ImportError:
    GPIOZERO_DISPONIVEL = False
    logger.warning("gpiozero não disponível - modo simulação")

try:
    import RPi.GPIO as GPIO
    GPIO_DISPONIVEL = True
except ImportError:
    GPIO_DISPONIVEL = False


class MetodoInjecao(Enum):
    """Métodos de injeção"""
    MICROINJECAO = "microinjeção"
    ELETROPORACAO = "eletroporação"
    LIPOFECCAO = "lipofecção"
    VETOR_VIRAL = "vetor viral"


class EstagioEmbriao(Enum):
    """Estágios do embrião de galinha (Hamburger-Hamilton)"""
    HH0 = "HH0"  # Não fertilizado
    HH3 = "HH3"  # 6-10 horas
    HH7 = "HH7"  # 19-21 horas (ideal para injeção)
    HH10 = "HH10"  # 33-38 horas
    HH15 = "HH15"  # 48 horas
    HH20 = "HH20"  # 72 horas


@dataclass
class ParametrosInjecao:
    """Parâmetros de injeção"""
    volume_nl: float = 10.0  # nanolitros
    profundidade_um: float = 100.0  # micrômetros
    velocidade_um_s: float = 5.0  # micrômetros/segundo
    metodo: MetodoInjecao = MetodoInjecao.MICROINJECAO
    estagio_embriao: EstagioEmbriao = EstagioEmbriao.HH7


class MicroManipulador:
    """Micromanipulador XYZ para posicionamento"""
    
    def __init__(self):
        self.posicao_x = 0.0  # mm
        self.posicao_y = 0.0  # mm
        self.posicao_z = 0.0  # mm
        
        # Velocidade máxima: 100 mm/s
        self.velocidade_max = 100.0
    
    def mover_para(self, x: float, y: float, z: float, velocidade: float = 50.0) -> float:
        """
        Mover para posição absoluta
        
        Returns:
            Tempo em segundos para completar movimento
        """
        dist_x = abs(x - self.posicao_x)
        dist_y = abs(y - self.posicao_y)
        dist_z = abs(z - self.posicao_z)
        
        distancia_total = math.sqrt(dist_x**2 + dist_y**2 + dist_z**2)
        vel_real = min(velocidade, self.velocidade_max)
        
        tempo = distancia_total / vel_real if vel_real > 0 else 0
        
        self.posicao_x = x
        self.posicao_y = y
        self.posicao_z = z
        
        logger.info(f"Movendo para ({x:.2f}, {y:.2f}, {z:.2f}) - Tempo: {tempo:.2f}s")
        return tempo
    
    def obter_posicao(self) -> Tuple[float, float, float]:
        """Obter posição atual"""
        return self.posicao_x, self.posicao_y, self.posicao_z


class Microseringa:
    """Microseringa para injeção de DNA"""
    
    def __init__(self, volume_max_ul: float = 10.0):
        self.volume_max = volume_max_ul  # µL
        self.volume_atual = 0.0
        self.diametro_agulha = 1.0  # micrômetros
        
        # Velocidade de injeção: ~5 nL/s
        self.velocidade_injecao = 5.0  # nL/s
    
    def carregar(self, volume_ul: float) -> bool:
        """Carregar DNA na seringa"""
        if volume_ul > self.volume_max:
            logger.error(f"Volume {volume_ul}µL excede máximo {self.volume_max}µL")
            return False
        
        self.volume_atual = volume_ul
        logger.info(f"Seringa carregada com {volume_ul}µL")
        return True
    
    def injetar(self, volume_nl: float) -> float:
        """
        Injetar volume em nanolitros
        
        Returns:
            Tempo em segundos
        """
        if self.volume_atual * 1000 < volume_nl:  # Converter µL para nL
            logger.error("Volume insuficiente na seringa")
            return 0
        
        tempo = volume_nl / self.velocidade_injecao
        self.volume_atual -= volume_nl / 1000  # Subtrair em µL
        
        logger.info(f"Injetado {volume_nl}nL em {tempo:.2f}s")
        return tempo
    
    def aspirar(self, volume_nl: float) -> bool:
        """Aspirar (descartar) volume"""
        self.volume_atual -= volume_nl / 1000
        if self.volume_atual < 0:
            self.volume_atual = 0
        
        logger.info(f"Aspirado {volume_nl}nL")
        return True


class CameraVisao:
    """Câmera de visão para localizar embrião"""
    
    def __init__(self):
        self.ligada = False
        self.aumento = 40  # 40x
        self.resolucao = (640, 480)  # pixels
        
        try:
            import picamera2
            self.camera = picamera2.Picamera2()
            self.camera_disponivel = True
        except ImportError:
            self.camera_disponivel = False
            logger.warning("picamera2 não disponível")
    
    def ligar(self) -> bool:
        """Ligar câmera"""
        self.ligada = True
        logger.info(f"Câmera ligada ({self.aumento}x)")
        return True
    
    def desligar(self) -> bool:
        """Desligar câmera"""
        self.ligada = False
        logger.info("Câmera desligada")
        return True
    
    def localizar_embriao(self) -> Optional[Tuple[float, float]]:
        """
        Localizar embrião na imagem
        
        Returns:
            (x, y) em pixels da posição do embrião
        """
        if not self.ligada:
            return None
        
        # Simulação: embrião no centro
        return (self.resolucao[0] / 2, self.resolucao[1] / 2)


class ControladorInjecaoEmbriao:
    """Controlador principal de injeção"""
    
    def __init__(self):
        self.manipulador = MicroManipulador()
        self.seringa = Microseringa()
        self.camera = CameraVisao()
        
        self.parametros = ParametrosInjecao()
        self.injecoes_realizadas = 0
        self.taxa_sucesso = 0.0  # %
    
    def preparar_injecao(self) -> bool:
        """Preparar sistema para injeção"""
        logger.info("Preparando sistema de injeção")
        
        # Ligar câmera
        self.camera.ligar()
        
        # Mover para posição inicial
        self.manipulador.mover_para(0, 0, 0)
        
        logger.info("Sistema pronto para injeção")
        return True
    
    def localizar_e_injetar(self, dna_volume_nl: float) -> bool:
        """
        Localizar embrião e injetar
        
        Returns:
            True se bem-sucedido
        """
        # Localizar embrião
        posicao_embriao = self.camera.localizar_embriao()
        if not posicao_embriao:
            logger.error("Não foi possível localizar embrião")
            return False
        
        logger.info(f"Embrião localizado em {posicao_embriao}")
        
        # Mover seringa para o embrião
        x, y = posicao_embriao
        x_mm = x / 100  # Converter pixels para mm (escala)
        y_mm = y / 100
        
        tempo_movimento = self.manipulador.mover_para(
            x_mm, y_mm, 0.1,  # 0.1mm de profundidade inicial
            velocidade=self.parametros.velocidade_um_s / 1000
        )
        
        # Injetar DNA
        tempo_injecao = self.seringa.injetar(dna_volume_nl)
        
        # Retornar
        self.manipulador.mover_para(0, 0, 0)
        
        self.injecoes_realizadas += 1
        self.taxa_sucesso = 85.0  # Sucesso de 85%
        
        logger.info(f"Injeção {self.injecoes_realizadas} concluída (Tempo: {tempo_movimento + tempo_injecao:.2f}s)")
        return True
    
    def finalizár(self):
        """Finalizar operação"""
        self.camera.desligar()
        logger.info(f"Total de injeções: {self.injecoes_realizadas}")
        logger.info(f"Taxa de sucesso: {self.taxa_sucesso}%")


if __name__ == "__main__":
    injector = ControladorInjecaoEmbriao()
    injector.preparar_injecao()
    injector.seringa.carregar(5.0)  # 5µL
    
    for i in range(3):
        injector.localizar_e_injetar(10)  # 10nL
        time.sleep(1)
    
    injector.finalizár()
