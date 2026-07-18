#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Robô de Síntese de DNA
Sistema robótico para síntese in vitro de genomas
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
from typing import Dict, Optional, List
from dataclasses import dataclass
from enum import Enum

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] ROBO_SINTESE: %(message)s'
)
logger = logging.getLogger(__name__)

# Hardware
try:
    from gpiozero import Motor, Servo, Motor
    GPIOZERO_DISPONIVEL = True
except ImportError:
    GPIOZERO_DISPONIVEL = False

try:
    import RPi.GPIO as GPIO
    GPIO_DISPONIVEL = True
except ImportError:
    GPIO_DISPONIVEL = False


class BracoRobotico:
    """Braço robótico para movimentação de reagentes"""
    
    def __init__(self):
        self.joint1 = 0.0  # Graus
        self.joint2 = 0.0
        self.joint3 = 0.0
        
        # Limites de movimento
        self.joint1_min, self.joint1_max = -180, 180
        self.joint2_min, self.joint2_max = -90, 90
        self.joint3_min, self.joint3_max = 0, 180
        
        # Velocidade angular: ~20 graus/s
        self.velocidade_angular = 20.0
    
    def mover_para_angulo(self, j1: float, j2: float, j3: float) -> float:
        """
        Mover braço para posição angular
        
        Returns:
            Tempo em segundos
        """
        # Limitar ângulos
        j1 = max(self.joint1_min, min(self.joint1_max, j1))
        j2 = max(self.joint2_min, min(self.joint2_max, j2))
        j3 = max(self.joint3_min, min(self.joint3_max, j3))
        
        # Calcular movimento máximo
        delta_j1 = abs(j1 - self.joint1)
        delta_j2 = abs(j2 - self.joint2)
        delta_j3 = abs(j3 - self.joint3)
        delta_max = max(delta_j1, delta_j2, delta_j3)
        
        tempo = delta_max / self.velocidade_angular if self.velocidade_angular > 0 else 0
        
        self.joint1 = j1
        self.joint2 = j2
        self.joint3 = j3
        
        logger.info(f"Braço movido para ({j1:.1f}°, {j2:.1f}°, {j3:.1f}°) em {tempo:.2f}s")
        return tempo
    
    def obter_posicao(self) -> tuple:
        """Obter posição angular atual"""
        return (self.joint1, self.joint2, self.joint3)


class Garra:
    """Garra para pegar tubos/placas"""
    
    def __init__(self):
        self.aberta = True
        self.item_seguro = None
    
    def abrir(self):
        """Abrir garra"""
        self.aberta = True
        self.item_seguro = None
        logger.info("Garra aberta")
    
    def fechar(self):
        """Fechar garra"""
        self.aberta = False
        logger.info("Garra fechada")
    
    def pegar_item(self, item_id: str) -> bool:
        """Pegar item"""
        if self.aberta:
            self.fechar()
            self.item_seguro = item_id
            logger.info(f"Item '{item_id}' pego")
            return True
        return False
    
    def largar_item(self) -> Optional[str]:
        """Largar item"""
        item = self.item_seguro
        self.abrir()
        return item


class EstacaoDeTrabalhoDNA:
    """Estação de trabalho para síntese de DNA"""
    
    def __init__(self, id: str):
        self.id = id
        self.tipo = "dNTP"  # Tipo de reagente
        self.volume_ml = 1.0
        self.temperatura = 20.0
        self.ocupada = False
    
    def carregar_reagente(self, tipo: str, volume: float):
        """Carregar reagente"""
        self.tipo = tipo
        self.volume_ml = volume
        self.ocupada = True
        logger.info(f"Estação {self.id} carregada com {volume}mL de {tipo}")
    
    def dispensar(self, volume_ul: float) -> bool:
        """Dispensar volume"""
        if self.volume_ml * 1000 < volume_ul:
            logger.error(f"Volume insuficiente em {self.id}")
            return False
        
        self.volume_ml -= volume_ul / 1000
        logger.info(f"Dispensado {volume_ul}µL de {self.id}")
        return True


class RoboSinteseDNA:
    """Robô principal de síntese de DNA"""
    
    def __init__(self):
        self.braco = BracoRobotico()
        self.garra = Garra()
        
        # Estações de trabalho
        self.estacoes = {
            "dNTP_A": EstacaoDeTrabalhoDNA("dNTP_A"),
            "dNTP_G": EstacaoDeTrabalhoDNA("dNTP_G"),
            "dNTP_C": EstacaoDeTrabalhoDNA("dNTP_C"),
            "dNTP_T": EstacaoDeTrabalhoDNA("dNTP_T"),
            "polimerase": EstacaoDeTrabalhoDNA("polimerase"),
            "buffer": EstacaoDeTrabalhoDNA("buffer"),
            "saida": EstacaoDeTrabalhoDNA("saida"),
        }
        
        # Estado
        self.sinteses_completas = 0
        self.ativo = False
    
    def preparar_sistema(self) -> bool:
        """Preparar sistema"""
        logger.info("Preparando sistema de síntese")
        
        # Carregar estações
        self.estacoes["dNTP_A"].carregar_reagente("dATP", 1.0)
        self.estacoes["dNTP_G"].carregar_reagente("dGTP", 1.0)
        self.estacoes["dNTP_C"].carregar_reagente("dCTP", 1.0)
        self.estacoes["dNTP_T"].carregar_reagente("dTTP", 1.0)
        self.estacoes["polimerase"].carregar_reagente("DNA Polimerase", 0.5)
        self.estacoes["buffer"].carregar_reagente("Buffer TE", 2.0)
        
        logger.info("Sistema pronto")
        return True
    
    def sintetizar_dna(self, sequencia: str) -> Optional[float]:
        """
        Sintetizar DNA de acordo com sequência
        
        Args:
            sequencia: String com ACGT
            
        Returns:
            Quantidade em ng se bem-sucedido, None se falhou
        """
        logger.info(f"Sintetizando: {sequencia}")
        
        tempo_total = 0.0
        
        # 1. Mover para estação de preparação
        tempo_total += self.braco.mover_para_angulo(0, 0, 0)
        
        # 2. Preparar mistura (simular)
        tempo_total += 60  # 1 minuto de preparação
        
        # 3. Processar sequência
        for nucleotideo in sequencia:
            if nucleotideo == 'A':
                tempo_total += self.braco.mover_para_angulo(45, 30, 90)
                self.estacoes["dNTP_A"].dispensar(1.0)  # 1µL
            elif nucleotideo == 'G':
                tempo_total += self.braco.mover_para_angulo(90, 30, 90)
                self.estacoes["dNTP_G"].dispensar(1.0)
            elif nucleotideo == 'C':
                tempo_total += self.braco.mover_para_angulo(135, 30, 90)
                self.estacoes["dNTP_C"].dispensar(1.0)
            elif nucleotideo == 'T':
                tempo_total += self.braco.mover_para_angulo(180, 30, 90)
                self.estacoes["dNTP_T"].dispensar(1.0)
            
            # Esperar polimerase processar
            tempo_total += 2  # 2 segundos por nucleotideo
        
        # 4. Recolher resultado
        tempo_total += self.braco.mover_para_angulo(-45, -45, 0)
        
        # Calcular quantidade de DNA sintetizado
        # Aproximadamente 330 g/mol por nucleotideo (MW médio)
        num_nucleotideos = len(sequencia)
        peso_molecular_total = num_nucleotideos * 330  # g/mol
        
        # ~50-100 ng por síntese bem-sucedida
        dna_sintetizado = 75.0 * (num_nucleotideos / 1000)  # ng
        
        self.sinteses_completas += 1
        logger.info(f"Síntese completa: {dna_sintetizado:.2f}ng em {tempo_total:.2f}s")
        
        return dna_sintetizado
    
    def obter_status(self) -> Dict:
        """Obter status do robô"""
        return {
            "braco_posicao": self.braco.obter_posicao(),
            "garra_aberta": self.garra.aberta,
            "item_seguro": self.garra.item_seguro,
            "sinteses_completas": self.sinteses_completas,
            "estacoes_status": {
                estacao_id: {
                    "volume_ml": estacao.volume_ml,
                    "tipo": estacao.tipo,
                    "ocupada": estacao.ocupada
                }
                for estacao_id, estacao in self.estacoes.items()
            }
        }


if __name__ == "__main__":
    robo = RoboSinteseDNA()
    robo.preparar_sistema()
    
    # Sintetizar alguns genomas curtos
    sequencias = [
        "ACGTACGTACGT",
        "AAATTTGGGCCC",
        "ACGTACGT",
    ]
    
    dna_total = 0.0
    for seq in sequencias:
        dna = robo.sintetizar_dna(seq)
        if dna:
            dna_total += dna
    
    print(f"\nTotal de DNA sintetizado: {dna_total:.2f}ng")
    print(f"Sínteses realizadas: {robo.sinteses_completas}")
