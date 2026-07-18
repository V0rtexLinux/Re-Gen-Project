#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Incubadora - Monitor de Aplicação
Sistema de monitoramento de incubação de embrião
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
from typing import Dict, Optional
from dataclasses import dataclass
from enum import Enum

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] INCUBADORA: %(message)s'
)
logger = logging.getLogger(__name__)

# Hardware
try:
    from gpiozero import Motor, LED, TempSensor
    GPIOZERO_DISPONIVEL = True
except ImportError:
    GPIOZERO_DISPONIVEL = False

try:
    import RPi.GPIO as GPIO
    GPIO_DISPONIVEL = True
except ImportError:
    GPIO_DISPONIVEL = False


class EstadoIncubacao(Enum):
    """Estados da incubação"""
    DESLIGADA = "desligada"
    AQUECENDO = "aquecendo"
    ESTABILIZADA = "estabilizada"
    INCUBANDO = "incubando"
    ECLOSAO = "eclosão"
    COMPLETO = "completo"
    ERRO = "erro"


@dataclass
class ParametrosIncubacao:
    """Parâmetros de incubação"""
    temperatura_alvo: float = 37.8  # °C (incubação de galinha)
    umidade_alvo: float = 55.0  # % (ótima para galinha)
    duracao_dias: int = 21  # Dias de incubação
    periodo_viragem: int = 24  # Horas entre viragens


class ControladorTemperatura:
    """Controlador de temperatura"""
    
    def __init__(self):
        self.temperatura_alvo = 37.8  # °C
        self.temperatura_atual = 20.0
        self.resistencia_ligada = False
        self.ventilador_ligado = False
        self.potencia_resistencia = 500  # Watts
    
    def ligar_aquecimento(self, temp_alvo: float):
        """Ligar aquecimento"""
        self.temperatura_alvo = max(30, min(42, temp_alvo))
        self.resistencia_ligada = True
        logger.info(f"Aquecimento ligado: {self.temperatura_alvo}°C")
    
    def desligar_aquecimento(self):
        """Desligar aquecimento"""
        self.resistencia_ligada = False
        logger.info("Aquecimento desligado")
    
    def simular_aquecimento(self, tempo_seg: float):
        """Simular aquecimento gradual"""
        if self.resistencia_ligada:
            # ~2°C/min de aquecimento
            taxa = (self.potencia_resistencia / 1000) * 0.03
            self.temperatura_atual += taxa * (tempo_seg / 60)
            
            if self.temperatura_atual > self.temperatura_alvo:
                self.temperatura_atual = self.temperatura_alvo
        else:
            # Resfriamento natural
            self.temperatura_atual -= 0.01 * tempo_seg


class ControladorUmidade:
    """Controlador de umidade"""
    
    def __init__(self):
        self.umidade_alvo = 55.0  # %
        self.umidade_atual = 45.0
        self.nebulizador_ligado = False
        self.ventilador_ligado = False
    
    def ligar_nebulizador(self):
        """Ligar nebulizador"""
        self.nebulizador_ligado = True
        logger.info("Nebulizador ligado")
    
    def desligar_nebulizador(self):
        """Desligar nebulizador"""
        self.nebulizador_ligado = False
        logger.info("Nebulizador desligado")
    
    def simular_umidade(self, tempo_seg: float):
        """Simular mudança de umidade"""
        if self.nebulizador_ligado:
            # Aumentar umidade
            self.umidade_atual += 0.1 * (tempo_seg / 60)
            if self.umidade_atual > self.umidade_alvo:
                self.umidade_atual = self.umidade_alvo
        else:
            # Diminuir umidade naturalmente
            self.umidade_atual -= 0.05 * (tempo_seg / 60)
            if self.umidade_atual < 30:
                self.umidade_atual = 30


class SensorTemperatura:
    """Sensor de temperatura"""
    
    def __init__(self):
        self.temperatura = 20.0
    
    def ler(self) -> float:
        """Ler temperatura"""
        ruido = 0.2 * math.sin(time.time())
        return self.temperatura + ruido


class SensorUmidade:
    """Sensor de umidade"""
    
    def __init__(self):
        self.umidade = 50.0
    
    def ler(self) -> float:
        """Ler umidade"""
        ruido = 0.5 * math.sin(time.time())
        return self.umidade + ruido


class ControladorIncubadora:
    """Controlador principal da incubadora"""
    
    def __init__(self):
        self.estado = EstadoIncubacao.DESLIGADA
        self.parametros = ParametrosIncubacao()
        
        # Controladores
        self.controle_temp = ControladorTemperatura()
        self.controle_umidade = ControladorUmidade()
        
        # Sensores
        self.sensor_temp = SensorTemperatura()
        self.sensor_umidade = SensorUmidade()
        
        # Tempo de incubação
        self.tempo_inicio = None
        self.tempo_decorrido = 0
        
        # Thread de simulação
        self.thread_simulacao = None
        self.ativo = False
    
    def iniciar_incubacao(self) -> bool:
        """Iniciar processo de incubação"""
        try:
            self.estado = EstadoIncubacao.AQUECENDO
            self.tempo_inicio = time.time()
            self.ativo = True
            
            # Iniciar thread
            self.thread_simulacao = threading.Thread(
                target=self._simular_incubacao, daemon=True
            )
            self.thread_simulacao.start()
            
            # Ligar aquecimento
            self.controle_temp.ligar_aquecimento(self.parametros.temperatura_alvo)
            self.controle_umidade.ligar_nebulizador()
            
            logger.info("Incubação iniciada")
            return True
        except Exception as e:
            self.estado = EstadoIncubacao.ERRO
            logger.error(f"Erro ao iniciar incubação: {e}")
            return False
    
    def parar_incubacao(self):
        """Parar incubação"""
        self.ativo = False
        self.controle_temp.desligar_aquecimento()
        self.controle_umidade.desligar_nebulizador()
        self.estado = EstadoIncubacao.DESLIGADA
        
        if self.thread_simulacao:
            self.thread_simulacao.join(timeout=2)
        
        logger.info("Incubação parada")
    
    def _simular_incubacao(self):
        """Simular processo de incubação"""
        while self.ativo:
            # Atualizar tempo
            self.tempo_decorrido = (time.time() - self.tempo_inicio) / 3600 / 24  # Dias
            
            # Simular temperatura
            self.controle_temp.simular_aquecimento(0.1)
            self.sensor_temp.temperatura = self.controle_temp.temperatura_atual
            
            # Simular umidade
            self.controle_umidade.simular_umidade(0.1)
            self.sensor_umidade.umidade = self.controle_umidade.umidade_atual
            
            # Verificar estado
            if self.controle_temp.temperatura_atual > self.parametros.temperatura_alvo - 0.5:
                self.estado = EstadoIncubacao.ESTABILIZADA
            
            if self.tempo_decorrido > 20:
                self.estado = EstadoIncubacao.ECLOSAO
                logger.info("Período de eclósão iniciado!")
            
            if self.tempo_decorrido > self.parametros.duracao_dias:
                self.estado = EstadoIncubacao.COMPLETO
                self.ativo = False
                logger.info("Incubação concluída com sucesso!")
            
            time.sleep(0.1)
    
    def obter_status(self) -> Dict:
        """Obter status completo"""
        return {
            "estado": self.estado.value,
            "temperatura_atual": round(self.sensor_temp.ler(), 2),
            "temperatura_alvo": self.parametros.temperatura_alvo,
            "umidade_atual": round(self.sensor_umidade.ler(), 1),
            "umidade_alvo": self.parametros.umidade_alvo,
            "tempo_decorrido_dias": round(self.tempo_decorrido, 1),
            "resistencia_ligada": self.controle_temp.resistencia_ligada,
            "nebulizador_ligado": self.controle_umidade.nebulizador_ligado,
        }


if __name__ == "__main__":
    incubadora = ControladorIncubadora()
    incubadora.iniciar_incubacao()
    
    for i in range(10):
        status = incubadora.obter_status()
        print(f"[{i}] Estado: {status['estado']} | "
              f"Temp: {status['temperatura_atual']}°C | "
              f"Umidade: {status['umidade_atual']}% | "
              f"Dias: {status['tempo_decorrido_dias']}")
        time.sleep(1)
    
    incubadora.parar_incubacao()
