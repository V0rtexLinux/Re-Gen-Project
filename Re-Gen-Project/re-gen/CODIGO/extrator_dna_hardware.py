#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrator de DNA - Simulador de Hardware
Simulação de sensores, atuadores e componentes físicos
Re-Dino Project v1.0
"""

import time
import threading
import math
import logging
from typing import Dict, Optional, Callable
from dataclasses import dataclass
from enum import Enum


# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


class SensorTemperatura:
    """Sensor de temperatura para incubadora"""
    
    def __init__(self):
        self.valor_atual: float = 20.0
        self.precisao: float = 0.5
    
    def ler(self) -> float:
        """Ler temperatura"""
        ruido = (self.precisao * 0.1) * math.sin(time.time())
        return self.valor_atual + ruido
    
    def set_valor(self, valor: float):
        """Definir valor (simulação)"""
        self.valor_atual = max(-10, min(100, valor))


class SensorAbsorbancia:
    """Sensor de absorbância (espectrofotômetro)"""
    
    def __init__(self):
        self.valor_260: float = 0.0  # DNA máximo em 260nm
        self.valor_280: float = 0.0  # Proteínas em 280nm
    
    def ler(self) -> tuple:
        """Retornar (A260, A280)"""
        return self.valor_260, self.valor_280
    
    def set_valor(self, a260: float, a280: float):
        """Definir valores"""
        self.valor_260 = max(0, min(4, a260))
        self.valor_280 = max(0, min(4, a280))


class Centrifuga:
    """Centrifuga de laboratório"""
    
    def __init__(self):
        self.rpm_alvo: int = 0
        self.rpm_atual: int = 0
        self.ligada: bool = False
    
    def ligar(self, rpm: int):
        """Ligar centrifuga"""
        self.rpm_alvo = max(100, min(15000, rpm))
        self.ligada = True
        logger.info(f"Centrifuga ligada: {self.rpm_alvo} RPM")
    
    def desligar(self):
        """Desligar centrifuga"""
        self.ligada = False
        self.rpm_alvo = 0
        logger.info("Centrifuga desligada")
    
    def simular_aceleracao(self, tempo_seg: float):
        """Simular aceleração gradual"""
        if self.ligada:
            # Aceleração: ~1000 RPM/s
            delta = min(1000 * tempo_seg, self.rpm_alvo - self.rpm_atual)
            self.rpm_atual += delta
        else:
            # Desaceleração: ~500 RPM/s
            delta = max(-500 * tempo_seg, -self.rpm_atual)
            self.rpm_atual += delta


class Aquecedor:
    """Aquecedor para incubação"""
    
    def __init__(self):
        self.temperatura_alvo: float = 20.0
        self.temperatura_atual: float = 20.0
        self.ligado: bool = False
        self.potencia_watts: float = 200.0
    
    def ligar(self, temperatura_alvo: float):
        """Ligar aquecedor"""
        self.temperatura_alvo = max(20, min(100, temperatura_alvo))
        self.ligado = True
        logger.info(f"Aquecedor ligado: {self.temperatura_alvo}°C")
    
    def desligar(self):
        """Desligar aquecedor"""
        self.ligado = False
        logger.info("Aquecedor desligado")
    
    def simular_aquecimento(self, tempo_seg: float):
        """Simular aquecimento gradual"""
        if self.ligado:
            # Taxa de aquecimento: ~2°C/min
            taxa = (self.potencia_watts / 1000) * 0.03
            self.temperatura_atual += taxa * (tempo_seg / 60)
            
            if self.temperatura_atual > self.temperatura_alvo:
                self.temperatura_atual = self.temperatura_alvo
        else:
            # Resfriamento natural: ~0.5°C/min
            self.temperatura_atual -= 0.008 * tempo_seg


class Agitador:
    """Agitador para homogeneização"""
    
    def __init__(self):
        self.rpm_alvo: int = 0
        self.rpm_atual: int = 0
        self.ligado: bool = False
    
    def ligar(self, rpm: int):
        """Ligar agitador"""
        self.rpm_alvo = max(100, min(3000, rpm))
        self.ligado = True
        logger.info(f"Agitador ligado: {self.rpm_alvo} RPM")
    
    def desligar(self):
        """Desligar agitador"""
        self.ligado = False
        self.rpm_alvo = 0
        logger.info("Agitador desligado")


class BombaPeristaltica:
    """Bomba peristáltica para dosagem"""
    
    def __init__(self):
        self.velocidade: float = 0.0  # %
        self.fluxo_ml_min: float = 0.0
        self.ligada: bool = False
    
    def ligar(self, velocidade: float):
        """Ligar bomba"""
        self.velocidade = max(0, min(100, velocidade))
        self.fluxo_ml_min = (self.velocidade / 100) * 10  # Máximo 10 mL/min
        self.ligada = True
        logger.info(f"Bomba ligada: {self.velocidade}% ({self.fluxo_ml_min:.1f} mL/min)")
    
    def desligar(self):
        """Desligar bomba"""
        self.ligada = False
        logger.info("Bomba desligada")


class LEDIndicador:
    """LED indicador de status"""
    
    def __init__(self, cor: str = "verde"):
        self.cor = cor
        self.ligado = False
        self.piscando = False
    
    def ligar(self):
        """Ligar LED"""
        self.ligado = True
    
    def desligar(self):
        """Desligar LED"""
        self.ligado = False
    
    def piscar(self):
        """Ativar piscagem"""
        self.piscando = True
    
    def parar_piscagem(self):
        """Parar piscagem"""
        self.piscando = False


class ControladorHardwareExtrator:
    """Controlador unificado de hardware do extrator"""
    
    def __init__(self):
        # Sensores
        self.temp_sensor = SensorTemperatura()
        self.absorbancia_sensor = SensorAbsorbancia()
        
        # Atuadores
        self.centrifuga = Centrifuga()
        self.aquecedor = Aquecedor()
        self.agitador = Agitador()
        self.bomba = BombaPeristaltica()
        
        # LEDs indicadores
        self.led_ligado = LEDIndicador("verde")
        self.led_processando = LEDIndicador("amarelo")
        self.led_erro = LEDIndicador("vermelho")
        
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
        logger.info("Simulador de hardware iniciado")
    
    def parar(self):
        """Parar simulação"""
        self.ativo = False
        if self.thread_simulacao:
            self.thread_simulacao.join(timeout=2)
        logger.info("Simulador de hardware parado")
    
    def _simular_ambiente(self):
        """Simular ambiente de hardware (thread contínua)"""
        while self.ativo:
            # Atualizar centrifuga
            self.centrifuga.simular_aceleracao(0.1)
            
            # Atualizar aquecedor
            self.aquecedor.simular_aquecimento(0.1)
            
            # Atualizar sensores baseado em atuadores
            self.temp_sensor.set_valor(self.aquecedor.temperatura_atual)
            
            time.sleep(0.1)
    
    def obter_status_completo(self) -> Dict:
        """Obter status completo do hardware"""
        a260, a280 = self.absorbancia_sensor.ler()
        
        return {
            "sensores": {
                "temperatura": round(self.temp_sensor.ler(), 2),
                "absorbancia_260": round(a260, 3),
                "absorbancia_280": round(a280, 3),
                "pureza_260_280": round(a260 / a280 if a280 > 0 else 0, 2),
            },
            "centrifuga": {
                "ligada": self.centrifuga.ligada,
                "rpm_alvo": self.centrifuga.rpm_alvo,
                "rpm_atual": int(self.centrifuga.rpm_atual),
            },
            "aquecedor": {
                "ligado": self.aquecedor.ligado,
                "temperatura_alvo": self.aquecedor.temperatura_alvo,
                "temperatura_atual": round(self.aquecedor.temperatura_atual, 2),
            },
            "agitador": {
                "ligado": self.agitador.ligado,
                "rpm_alvo": self.agitador.rpm_alvo,
            },
            "bomba": {
                "ligada": self.bomba.ligada,
                "velocidade_pct": self.bomba.velocidade,
                "fluxo_ml_min": round(self.bomba.fluxo_ml_min, 2),
            },
            "leds": {
                "ligado": self.led_ligado.ligado,
                "processando": self.led_processando.ligado,
                "erro": self.led_erro.ligado,
            }
        }
    
    # Métodos de controle
    def ligar_centrifuga(self, rpm: int):
        """Ligar centrifuga"""
        self.centrifuga.ligar(rpm)
    
    def desligar_centrifuga(self):
        """Desligar centrifuga"""
        self.centrifuga.desligar()
    
    def ligar_aquecedor(self, temperatura: float):
        """Ligar aquecedor"""
        self.aquecedor.ligar(temperatura)
    
    def desligar_aquecedor(self):
        """Desligar aquecedor"""
        self.aquecedor.desligar()
    
    def ligar_agitador(self, rpm: int):
        """Ligar agitador"""
        self.agitador.ligar(rpm)
    
    def desligar_agitador(self):
        """Desligar agitador"""
        self.agitador.desligar()
    
    def ligar_bomba(self, velocidade: float):
        """Ligar bomba"""
        self.bomba.ligar(velocidade)
    
    def desligar_bomba(self):
        """Desligar bomba"""
        self.bomba.desligar()
    
    def set_absorbancia(self, a260: float, a280: float):
        """Definir valores de absorbância (simulação)"""
        self.absorbancia_sensor.set_valor(a260, a280)
    
    def led_status(self, tipo: str, ligado: bool):
        """Controlar LED de status"""
        if tipo == "ligado":
            if ligado:
                self.led_ligado.ligar()
            else:
                self.led_ligado.desligar()
        elif tipo == "processando":
            if ligado:
                self.led_processando.ligar()
            else:
                self.led_processando.desligar()
        elif tipo == "erro":
            if ligado:
                self.led_erro.ligar()
            else:
                self.led_erro.desligar()


if __name__ == "__main__":
    hw = ControladorHardwareExtrator()
    hw.iniciar()
    
    # Teste
    hw.ligar_centrifuga(10000)
    hw.ligar_aquecedor(65)
    hw.ligar_bomba(50)
    
    for i in range(10):
        status = hw.obter_status_completo()
        print(f"\n[{i}] Temp: {status['sensores']['temperatura']}°C | "
              f"RPM: {status['centrifuga']['rpm_atual']} | "
              f"Bomba: {status['bomba']['fluxo_ml_min']} mL/min")
        time.sleep(1)
    
    hw.parar()
