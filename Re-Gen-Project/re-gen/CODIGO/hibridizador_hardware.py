#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hibridizador de DNA - Simulador de Hardware
Simulação de sensores, atuadores e componentes físicos
Re-Dino Project v1.0

Libs para Hardware (Raspberry Pi / GPIO):
- time, threading, multiprocessing, subprocess
- math, statistics, logging
- adafruit-blinka, pigpio, gpiozero, RPi.GPIO
- pyserial, biopython, picamera2, opencv-python
"""

import time
import threading
import multiprocessing
import subprocess
import math
import statistics
import logging
import numpy as np
from typing import Dict, Optional, Callable
from dataclasses import dataclass
from enum import Enum

# Hardware libs (com try/except para desenvolvimento)
try:
    import board
    import digitalio
    from adafruit_blinka.microcontroller.bcm283x import pins
    BLINKA_DISPONIVEL = True
except ImportError:
    BLINKA_DISPONIVEL = False

try:
    import pigpio
    PIGPIO_DISPONIVEL = True
except ImportError:
    PIGPIO_DISPONIVEL = False

try:
    from gpiozero import LED, Motor, DistanceSensor
    GPIOZERO_DISPONIVEL = True
except ImportError:
    GPIOZERO_DISPONIVEL = False

try:
    import RPi.GPIO as GPIO
    GPIO_DISPONIVEL = True
except ImportError:
    GPIO_DISPONIVEL = False

try:
    import serial
    SERIAL_DISPONIVEL = True
except ImportError:
    SERIAL_DISPONIVEL = False

try:
    from Bio import SeqIO
    from Bio.SeqUtils import gc_fraction
    BIOPYTHON_DISPONIVEL = True
except ImportError:
    BIOPYTHON_DISPONIVEL = False

try:
    from picamera2 import Picamera2
    PICAMERA_DISPONIVEL = True
except ImportError:
    PICAMERA_DISPONIVEL = False

try:
    import cv2
    OPENCV_DISPONIVEL = True
except ImportError:
    OPENCV_DISPONIVEL = False

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(name)s - %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


class CorLED(Enum):
    """Cores do LED RGB"""
    OFF = (0, 0, 0)
    VERMELHO = (255, 0, 0)
    VERDE = (0, 255, 0)
    AZUL = (0, 0, 255)
    ROXO = (255, 0, 255)
    AMARELO = (255, 255, 0)
    CYAN = (0, 255, 255)
    BRANCO = (255, 255, 255)
    LARANJA = (255, 165, 0)
    PINK = (255, 192, 203)


class EstadoBotao(Enum):
    """Estado do botão"""
    SOLTO = 0
    PRESSIONADO = 1
    PRESSIONADO_LONGO = 2


@dataclass
class BotaoRGB:
    """Botão com LED RGB integrado"""
    id: int
    nome: str
    cor_atual: CorLED = CorLED.OFF
    pressionado: bool = False
    callback: Optional[Callable] = None
    
    def atualizar_cor(self, cor: CorLED):
        """Atualizar cor do LED"""
        self.cor_atual = cor
    
    def pressionar(self):
        """Simular pressão"""
        self.pressionado = True
        if self.callback:
            self.callback()
    
    def soltar(self):
        """Simular soltura"""
        self.pressionado = False


@dataclass
class SensorTemperatura:
    """Sensor de temperatura DS18B20"""
    valor_atual: float = 20.0
    precisao: float = 0.5  # ±0.5°C
    
    def ler(self) -> float:
        """Ler temperatura com ruído"""
        ruido = np.random.normal(0, self.precisao * 0.1)
        return self.valor_atual + ruido
    
    def set_valor(self, valor: float):
        """Definir valor (para simulação)"""
        self.valor_atual = max(-10, min(50, valor))  # Limitar 0-50°C


@dataclass
class SensorPH:
    """Sensor de pH digital"""
    valor_atual: float = 7.4
    precisao: float = 0.1
    
    def ler(self) -> float:
        """Ler pH com ruído"""
        ruido = np.random.normal(0, self.precisao * 0.1)
        return self.valor_atual + ruido
    
    def set_valor(self, valor: float):
        """Definir valor (para simulação)"""
        self.valor_atual = max(0, min(14, valor))  # pH 0-14


@dataclass
class SensorCondutividade:
    """Sensor de condutividade"""
    valor_atual: float = 10.0  # mS/cm
    precisao: float = 0.5
    
    def ler(self) -> float:
        """Ler condutividade com ruído"""
        ruido = np.random.normal(0, self.precisao * 0.1)
        return self.valor_atual + ruido
    
    def set_valor(self, valor: float):
        """Definir valor"""
        self.valor_atual = max(0, min(20, valor))  # 0-20 mS/cm


@dataclass
class SensorTurbidez:
    """Sensor óptico de turbidez"""
    valor_atual: float = 0.1  # NTU
    precisao: float = 1.0
    
    def ler(self) -> float:
        """Ler turbidez com ruído"""
        ruido = np.random.normal(0, self.precisao * 0.1)
        return max(0, self.valor_atual + ruido)
    
    def set_valor(self, valor: float):
        """Definir valor"""
        self.valor_atual = max(0, min(1000, valor))  # 0-1000 NTU


class BombaPeristaltica:
    """Bomba peristáltica controlada"""
    
    def __init__(self):
        self.velocidade: float = 0.0  # % (0-100)
        self.fluxo_atual: float = 0.0  # mL/min
        self.volume_dispensado: float = 0.0  # mL
        self.funcionando: bool = False
    
    def setvelocidade(self, velocidade: float):
        """Definir velocidade (0-100%)"""
        self.velocidade = max(0, min(100, velocidade))
        self.fluxo_atual = (self.velocidade / 100) * 50  # Máximo 50 mL/min
    
    def ligar(self):
        """Ligar bomba"""
        self.funcionando = True
    
    def desligar(self):
        """Desligar bomba"""
        self.funcionando = False
        self.fluxo_atual = 0.0
    
    def simular_dispensacao(self, tempo_segundos: float):
        """Simular dispensação (calcular volume dispensado)"""
        if self.funcionando:
            tempo_minutos = tempo_segundos / 60
            self.volume_dispensado += self.fluxo_atual * tempo_minutos


class Aquecedor:
    """Resistência de aquecimento controlada"""
    
    def __init__(self, potencia_watts: float = 500):
        self.potencia = potencia_watts
        self.temperatura_alvo: float = 20.0
        self.ligado: bool = False
        self.temperatura_atual: float = 20.0
    
    def ligar(self, temperatura_alvo: float):
        """Ligar aquecedor"""
        self.temperatura_alvo = max(20, min(45, temperatura_alvo))  # 20-45°C
        self.ligado = True
    
    def desligar(self):
        """Desligar aquecedor"""
        self.ligado = False
    
    def simular_aquecimento(self, tempo_segundos: float):
        """Simular aquecimento gradual"""
        if self.ligado:
            # Taxa de aquecimento: ~1°C por minuto
            delta = (self.temperatura_alvo - self.temperatura_atual)
            taxa_aquecimento = (self.potencia / 1000) * 0.1  # Proporcional à potência
            self.temperatura_atual += taxa_aquecimento * (tempo_segundos / 60)
            
            # Limitar temperatura máxima
            if self.temperatura_atual > self.temperatura_alvo:
                self.temperatura_atual = self.temperatura_alvo
        else:
            # Resfriamento natural
            self.temperatura_atual -= 0.02 * tempo_segundos


class Resfriador:
    """Ventilador de resfriamento"""
    
    def __init__(self):
        self.ligado: bool = False
        self.velocidade: float = 0.0  # % (0-100)
    
    def ligar(self, velocidade: float = 100):
        """Ligar resfriador"""
        self.ligado = True
        self.velocidade = max(0, min(100, velocidade))
    
    def desligar(self):
        """Desligar resfriador"""
        self.ligado = False
        self.velocidade = 0.0
    
    def simular_resfriamento(self, temperatura_atual: float) -> float:
        """Simular resfriamento (retorna nova temperatura)"""
        if self.ligado:
            # Taxa de resfriamento proporcional à velocidade
            taxa_resfriamento = (self.velocidade / 100) * 0.05  # °C/s
            return temperatura_atual - taxa_resfriamento
        return temperatura_atual


class ValvulaSolenoide:
    """Válvula solenóide 2/2"""
    
    def __init__(self, id: int, nome: str):
        self.id = id
        self.nome = nome
        self.aberta: bool = False
    
    def abrir(self):
        """Abrir válvula"""
        self.aberta = True
    
    def fechar(self):
        """Fechar válvula"""
        self.aberta = False
    
    def toggle(self):
        """Alternar estado"""
        self.aberta = not self.aberta


class LEDRGB:
    """LED RGB 10W ajustável"""
    
    def __init__(self):
        self.cor_atual: CorLED = CorLED.OFF
        self.brilho: float = 0.0  # 0-100%
        self.modo_pulsacao: bool = False
        self.frequencia_pulsacao: float = 1.0  # Hz
    
    def setcor(self, cor: CorLED, brilho: float = 100):
        """Definir cor e brilho"""
        self.cor_atual = cor
        self.brilho = max(0, min(100, brilho))
    
    def modo_pulsacao_ativar(self, frequencia: float = 1.0):
        """Ativar modo pulsação"""
        self.modo_pulsacao = True
        self.frequencia_pulsacao = frequencia
    
    def modo_pulsacao_desativar(self):
        """Desativar modo pulsação"""
        self.modo_pulsacao = False


class EncoderRotativo:
    """Encoder rotativo para controle contínuo"""
    
    def __init__(self, id: int, nome: str, minimo: float = 0, maximo: float = 100):
        self.id = id
        self.nome = nome
        self.valor: float = (minimo + maximo) / 2
        self.minimo = minimo
        self.maximo = maximo
    
    def girar_horario(self, passos: float = 1):
        """Girar no sentido horário"""
        self.valor = min(self.maximo, self.valor + passos)
    
    def girar_antihorario(self, passos: float = 1):
        """Girar no sentido anti-horário"""
        self.valor = max(self.minimo, self.valor - passos)
    
    def set_valor(self, valor: float):
        """Definir valor direto"""
        self.valor = max(self.minimo, min(self.maximo, valor))


class ControladorHardware:
    """Simulador completo de hardware"""
    
    def __init__(self):
        # Sensores
        self.temp_sensor = SensorTemperatura()
        self.ph_sensor = SensorPH()
        self.cond_sensor = SensorCondutividade()
        self.turb_sensor = SensorTurbidez()
        
        # Atuadores
        self.bomba = BombaPeristaltica()
        self.aquecedor = Aquecedor()
        self.resfriador = Resfriador()
        
        # Válvulas
        self.valvulas = {
            1: ValvulaSolenoide(1, "Entrada DNA-A"),
            2: ValvulaSolenoide(2, "Entrada DNA-B"),
            3: ValvulaSolenoide(3, "Entrada Reagentes"),
            4: ValvulaSolenoide(4, "Saída Hibridizado"),
            5: ValvulaSolenoide(5, "Overflow"),
        }
        
        # LED RGB
        self.led_rgb = LEDRGB()
        
        # Botões RGB (4x4)
        self.botoes = {}
        nomes_botoes = [
            "Liga/Desliga", "Iniciar", "Pausa", "Reset",
            "Temp↑", "Temp↓", "Veloc↑", "Veloc↓",
            "Manual", "Auto", "Calibrar", "Diagnóstico",
            "Salvar", "Carregar", "Exportar", "Menu"
        ]
        
        for i in range(16):
            self.botoes[i] = BotaoRGB(
                id=i,
                nome=nomes_botoes[i],
                cor_atual=CorLED.OFF
            )
        
        # Encoders
        self.encoder_temperatura = EncoderRotativo(1, "Temperatura", 20, 45)
        self.encoder_velocidade = EncoderRotativo(2, "Velocidade", 0, 100)
        
        # Potenciômetros
        self.pot_brilho = 50.0  # 0-100%
        self.pot_alarme = 70.0  # 0-100%
        
        # Thread de simulação
        self.thread_simulacao = None
        self.ativo = False
    
    def iniciar(self):
        """Iniciar simulação de hardware"""
        self.ativo = True
        self.thread_simulacao = threading.Thread(
            target=self._simular_ambiente, daemon=True
        )
        self.thread_simulacao.start()
        print("[HW] Simulador de hardware iniciado")
    
    def parar(self):
        """Parar simulação"""
        self.ativo = False
        if self.thread_simulacao:
            self.thread_simulacao.join(timeout=2)
        print("[HW] Simulador de hardware parado")
    
    def _simular_ambiente(self):
        """Simular ambiente de hardware (thread contínua)"""
        while self.ativo:
            # Atualizar sensores baseado em atuadores
            self.temp_sensor.set_valor(self.temp_sensor.valor_atual)
            
            # Aquecimento/Resfriamento
            if self.aquecedor.ligado:
                self.aquecedor.simular_aquecimento(1.0)
                self.temp_sensor.valor_atual = self.aquecedor.temperatura_atual
            
            if self.resfriador.ligado:
                novo_temp = self.resfriador.simular_resfriamento(
                    self.temp_sensor.valor_atual
                )
                self.temp_sensor.valor_atual = novo_temp
            
            # Bomba
            self.bomba.simular_dispensacao(1.0)
            
            time.sleep(1.0)
    
    def obter_status_completo(self) -> Dict:
        """Obter status completo do hardware"""
        return {
            "sensores": {
                "temperatura": self.temp_sensor.ler(),
                "pH": self.ph_sensor.ler(),
                "condutividade": self.cond_sensor.ler(),
                "turbidez": self.turb_sensor.ler(),
            },
            "atuadores": {
                "bomba": {
                    "velocidade": self.bomba.velocidade,
                    "fluxo": self.bomba.fluxo_atual,
                    "volume_dispensado": round(self.bomba.volume_dispensado, 2),
                    "funcionando": self.bomba.funcionando,
                },
                "aquecedor": {
                    "ligado": self.aquecedor.ligado,
                    "temperatura_alvo": self.aquecedor.temperatura_alvo,
                    "temperatura_atual": round(self.aquecedor.temperatura_atual, 2),
                },
                "resfriador": {
                    "ligado": self.resfriador.ligado,
                    "velocidade": self.resfriador.velocidade,
                },
            },
            "valvulas": {
                f"valvula_{i}": v.aberta for i, v in self.valvulas.items()
            },
            "led_rgb": {
                "cor": self.led_rgb.cor_atual.name,
                "brilho": self.led_rgb.brilho,
                "modo_pulsacao": self.led_rgb.modo_pulsacao,
            },
            "controles": {
                "temperatura_encoder": self.encoder_temperatura.valor,
                "velocidade_encoder": self.encoder_velocidade.valor,
                "brilho_potenciometro": self.pot_brilho,
                "alarme_potenciometro": self.pot_alarme,
            }
        }
    
    # Métodos de controle de botões
    def pressionar_botao(self, id_botao: int, callback=None):
        """Pressionar botão"""
        if id_botao in self.botoes:
            if callback:
                self.botoes[id_botao].callback = callback
            self.botoes[id_botao].pressionar()
    
    # Métodos de controle de válvulas
    def abrir_valvula(self, id_valvula: int) -> bool:
        """Abrir válvula"""
        if id_valvula in self.valvulas:
            self.valvulas[id_valvula].abrir()
            return True
        return False
    
    def fechar_valvula(self, id_valvula: int) -> bool:
        """Fechar válvula"""
        if id_valvula in self.valvulas:
            self.valvulas[id_valvula].fechar()
            return True
        return False
    
    # Métodos de controle de LED RGB
    def set_cor_led(self, cor: CorLED, brilho: float = 100):
        """Definir cor do LED RGB"""
        self.led_rgb.setcor(cor, brilho)
    
    # Métodos de controle de bomba
    def set_velocidade_bomba(self, velocidade: float):
        """Definir velocidade da bomba"""
        self.bomba.setvelocidade(velocidade)
    
    def ligar_bomba(self):
        """Ligar bomba"""
        self.bomba.ligar()
    
    def desligar_bomba(self):
        """Desligar bomba"""
        self.bomba.desligar()
    
    # Métodos de controle de aquecimento
    def ligar_aquecedor(self, temperatura_alvo: float):
        """Ligar aquecedor"""
        self.aquecedor.ligar(temperatura_alvo)
    
    def desligar_aquecedor(self):
        """Desligar aquecedor"""
        self.aquecedor.desligar()
    
    # Métodos de controle de resfriamento
    def ligar_resfriador(self, velocidade: float = 100):
        """Ligar resfriador"""
        self.resfriador.ligar(velocidade)
    
    def desligar_resfriador(self):
        """Desligar resfriador"""
        self.resfriador.desligar()


if __name__ == "__main__":
    hw = ControladorHardware()
    hw.iniciar()
    
    # Teste
    hw.ligar_aquecedor(37.5)
    hw.set_velocidade_bomba(75)
    hw.ligar_bomba()
    hw.set_cor_led(CorLED.AZUL, 100)
    
    for i in range(10):
        status = hw.obter_status_completo()
        print(f"\n[HW STATUS {i}]")
        print(f"  Temp: {status['sensores']['temperatura']:.1f}°C")
        print(f"  pH: {status['sensores']['pH']:.2f}")
        print(f"  Bomba: {status['atuadores']['bomba']['fluxo']:.1f} mL/min")
        time.sleep(2)
    
    hw.parar()
