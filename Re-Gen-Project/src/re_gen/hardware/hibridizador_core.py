#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hibridizador de DNA - Motor Principal de Controle
Sistema de hibridização de DNA para síntese de genomas híbridos
Re-Dino Project v1.0
"""

import json
import time
import math
import threading
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
from enum import Enum
import numpy as np
from scipy.integrate import odeint


class HibridizadorState(Enum):
    """Estados do hibridizador"""
    DESLIGADO = "desligado"
    PRONTO = "pronto"
    AQUECENDO = "aquecendo"
    RESFRIANDO = "resfriando"
    EM_REACAO = "em_reacao"
    CICLO_LIMPEZA = "ciclo_limpeza"
    ERRO = "erro"


@dataclass
class SensorLeitura:
    """Leitura de sensores"""
    temperatura: float  # °C
    ph: float  # Unidades pH
    condutividade: float  # mS/cm
    turbidez: float  # NTU
    timestamp: str


@dataclass
class ParametroReacao:
    """Parâmetros da reação de hibridização"""
    temperatura_alvo: float = 37.5  # °C
    duracao_reacao: int = 14400  # 4 horas em segundos
    velocidade_bomba: float = 75.0  # % (0-100)
    volume_dna_a: int = 500  # µL
    volume_dna_b: int = 500  # µL
    volume_buffer: int = 1000  # µL
    modo_automatico: bool = True


class ModeloReacao:
    """Modelo matemático da reação de hibridização"""
    
    def __init__(self):
        self.k1 = 0.001  # Taxa de associação DNA-A
        self.k2 = 0.0005  # Taxa de associação DNA-B
        self.k_desnaturacao = 0.0002  # Taxa de desnaturação
        self.k_renaturacao = 0.00015  # Taxa de renaturação
        
    def derivadas(self, y: List[float], t: float, temp: float) -> List[float]:
        """
        Calcula derivadas temporais da reação
        y = [DNA_A_livre, DNA_B_livre, Complexo_AB, DNA_hibridizado]
        """
        DNA_A_livre, DNA_B_livre, Complexo_AB, DNA_hibridizado = y
        
        # Ajuste da taxa com temperatura (Arrhenius)
        fator_temp = math.exp(-5000 * (1/(temp + 273) - 1/310.15))
        
        # Equações diferenciais
        d_DNA_A = -self.k1 * fator_temp * DNA_A_livre * DNA_B_livre + self.k_desnaturacao * Complexo_AB
        d_DNA_B = d_DNA_A  # Mesmo que DNA_A
        d_Complexo = self.k1 * fator_temp * DNA_A_livre * DNA_B_livre - self.k_desnaturacao * Complexo_AB - 0.1 * Complexo_AB
        d_Hibridizado = 0.1 * Complexo_AB
        
        return [d_DNA_A, d_DNA_B, d_Complexo, d_Hibridizado]
    
    def simular_reacao(self, temperatura: float, duracao: int, condicoes_iniciais: Tuple) -> Tuple[np.ndarray, np.ndarray]:
        """
        Simula a reação de hibridização
        
        Args:
            temperatura: Temperatura em °C
            duracao: Duração em segundos
            condicoes_iniciais: (DNA_A, DNA_B, Complexo, Hibridizado)
        
        Returns:
            (tempo, concentrações)
        """
        t = np.linspace(0, duracao, duracao // 60)  # Ponto a cada minuto
        
        y0 = list(condicoes_iniciais)
        solucao = odeint(self.derivadas, y0, t, args=(temperatura,))
        
        return t, solucao


class Hibridizador:
    """Controlador principal do hibridizador"""
    
    def __init__(self):
        self.estado = HibridizadorState.DESLIGADO
        self.modelo_reacao = ModeloReacao()
        
        # Hardware (será injetado)
        self.hardware = None
        
        # Estado interno
        self.temperatura_atual = 20.0
        self.ph_atual = 7.4
        self.condutividade_atual = 10.0
        self.turbidez_atual = 0.0
        
        self.historico_leituras: List[SensorLeitura] = []
        self.parametros_reacao = ParametroReacao()
        
        # Controle de processo
        self.reacao_ativa = False
        self.tempo_inicio_reacao = None
        self.thread_reacao = None
        self.thread_monitoramento = None
        
        # Dados da reação
        self.dados_reacao = {
            "DNA_A_livre": 100.0,
            "DNA_B_livre": 100.0,
            "Complexo_AB": 0.0,
            "DNA_hibridizado": 0.0,
            "progresso_percentual": 0.0,
            "tempo_decorrido": 0,
        }
        
        self.resultado_final = None
        
    def set_hardware(self, hardware):
        """Injetar controlador de hardware"""
        self.hardware = hardware
        
    def ligar(self) -> bool:
        """Ligar o hibridizador"""
        try:
            if self.estado == HibridizadorState.DESLIGADO:
                self.estado = HibridizadorState.AQUECENDO
                self.temperatura_atual = 20.0
                
                # Iniciar thread de monitoramento
                self.thread_monitoramento = threading.Thread(
                    target=self._thread_monitoramento, daemon=True
                )
                self.thread_monitoramento.start()
                
                print("[HIBRIDIZADOR] Sistema ligado. Aquecendo...")
                return True
        except Exception as e:
            self.estado = HibridizadorState.ERRO
            print(f"[ERRO] Falha ao ligar: {e}")
            return False
            
    def desligar(self) -> bool:
        """Desligar o hibridizador"""
        try:
            self.reacao_ativa = False
            if self.thread_reacao:
                self.thread_reacao.join(timeout=5)
            
            self.estado = HibridizadorState.DESLIGADO
            self.temperatura_atual = 20.0
            print("[HIBRIDIZADOR] Sistema desligado")
            return True
        except Exception as e:
            print(f"[ERRO] Falha ao desligar: {e}")
            return False
    
    def configurar_parametros(self, parametros: Dict) -> bool:
        """Configurar parâmetros da reação"""
        try:
            if parametros.get("temperatura_alvo"):
                self.parametros_reacao.temperatura_alvo = parametros["temperatura_alvo"]
            if parametros.get("duracao_reacao"):
                self.parametros_reacao.duracao_reacao = parametros["duracao_reacao"]
            if parametros.get("velocidade_bomba"):
                self.parametros_reacao.velocidade_bomba = parametros["velocidade_bomba"]
            
            print(f"[CONFIG] Parâmetros atualizados: {self.parametros_reacao}")
            return True
        except Exception as e:
            print(f"[ERRO] Falha ao configurar: {e}")
            return False
    
    def iniciar_reacao(self) -> bool:
        """Iniciar reação de hibridização"""
        try:
            if self.estado not in [HibridizadorState.PRONTO, HibridizadorState.RESFRIANDO]:
                print(f"[ERRO] Não é possível iniciar. Estado: {self.estado.value}")
                return False
            
            self.reacao_ativa = True
            self.tempo_inicio_reacao = time.time()
            self.estado = HibridizadorState.EM_REACAO
            
            # Thread da reação
            self.thread_reacao = threading.Thread(
                target=self._thread_reacao, daemon=True
            )
            self.thread_reacao.start()
            
            print("[REAÇÃO] Iniciada!")
            return True
        except Exception as e:
            self.estado = HibridizadorState.ERRO
            print(f"[ERRO] Falha ao iniciar reação: {e}")
            return False
    
    def pausar_reacao(self) -> bool:
        """Pausar reação (não implementado nesta versão)"""
        print("[PAUSA] Reação pausada")
        return True
    
    def parar_reacao(self) -> bool:
        """Parar reação"""
        self.reacao_ativa = False
        self.estado = HibridizadorState.RESFRIANDO
        print("[PARADA] Reação parada, resfriando...")
        return True
    
    def resetar_sistema(self) -> bool:
        """Resetar e limpar o sistema"""
        try:
            self.reacao_ativa = False
            self.estado = HibridizadorState.AQUECENDO  # Aquecimento de limpeza
            
            # Aquecedor a 95°C por 5 minutos
            print("[LIMPEZA] Iniciando ciclo de esterilização (95°C por 5 min)...")
            time.sleep(2)  # Simulação
            
            # Resfriamento
            print("[LIMPEZA] Resfriando para 20°C...")
            time.sleep(2)  # Simulação
            
            self.dados_reacao = {
                "DNA_A_livre": 100.0,
                "DNA_B_livre": 100.0,
                "Complexo_AB": 0.0,
                "DNA_hibridizado": 0.0,
                "progresso_percentual": 0.0,
                "tempo_decorrido": 0,
            }
            self.historico_leituras = []
            self.resultado_final = None
            
            self.estado = HibridizadorState.PRONTO
            print("[LIMPEZA] Concluída. Sistema pronto.")
            return True
        except Exception as e:
            print(f"[ERRO] Falha ao resetar: {e}")
            return False
    
    def obter_leitura_sensores(self) -> SensorLeitura:
        """Obter leitura atual dos sensores"""
        leitura = SensorLeitura(
            temperatura=self.temperatura_atual,
            ph=self.ph_atual,
            condutividade=self.condutividade_atual,
            turbidez=self.turbidez_atual,
            timestamp=datetime.now().isoformat()
        )
        self.historico_leituras.append(leitura)
        return leitura
    
    def exportar_dados_reacao(self) -> Dict:
        """Exportar dados da reação completa"""
        return {
            "timestamp": datetime.now().isoformat(),
            "parametros": asdict(self.parametros_reacao),
            "resultado_final": self.resultado_final,
            "historico_sensores": [asdict(l) for l in self.historico_leituras[-100:]],  # Últimas 100
            "dados_reacao_final": self.dados_reacao
        }
    
    def _thread_monitoramento(self):
        """Thread de monitoramento contínuo dos sensores"""
        while self.estado != HibridizadorState.DESLIGADO:
            # Simular leituras (em produção, seria de sensores reais)
            if self.estado == HibridizadorState.AQUECENDO:
                # Aquecendo até temperatura alvo
                delta = self.parametros_reacao.temperatura_alvo - self.temperatura_atual
                self.temperatura_atual += delta * 0.05  # 5% de aproximação por ciclo
                
                if abs(delta) < 0.2:
                    self.estado = HibridizadorState.PRONTO
                    print(f"[AQUECEDOR] Temperatura estabilizada em {self.temperatura_atual:.1f}°C")
            
            elif self.estado == HibridizadorState.RESFRIANDO:
                # Resfriando até 20°C
                delta = 20.0 - self.temperatura_atual
                self.temperatura_atual += delta * 0.1  # 10% de aproximação
                
                if abs(delta) < 0.2:
                    self.estado = HibridizadorState.PRONTO
                    self.temperatura_atual = 20.0
            
            # Simulação de valores normais (sem reação)
            self.ph_atual = 7.4 + np.random.normal(0, 0.05)
            self.condutividade_atual = 10.0 + np.random.normal(0, 0.2)
            self.turbidez_atual = 0.1 + np.random.normal(0, 0.05)
            
            # Registrar leitura
            self.obter_leitura_sensores()
            
            time.sleep(1)  # Atualizar a cada segundo
    
    def _thread_reacao(self):
        """Thread de reação de hibridização"""
        tempo_total = self.parametros_reacao.duracao_reacao
        tempo_inicio = time.time()
        
        # Condições iniciais (µM)
        condicoes_iniciais = (
            self.parametros_reacao.volume_dna_a / 100.0,  # DNA_A_livre
            self.parametros_reacao.volume_dna_b / 100.0,  # DNA_B_livre
            0.0,  # Complexo_AB
            0.0   # DNA_hibridizado
        )
        
        # Simular reação
        t, solucao = self.modelo_reacao.simular_reacao(
            self.parametros_reacao.temperatura_alvo,
            tempo_total,
            condicoes_iniciais
        )
        
        idx = 0
        tempo_ultimo_ponto = tempo_inicio
        
        while self.reacao_ativa and idx < len(solucao) - 1:
            tempo_decorrido = time.time() - tempo_inicio
            
            # Encontrar ponto mais próximo do tempo decorrido
            idx = int((tempo_decorrido / tempo_total) * len(solucao))
            idx = min(idx, len(solucao) - 1)
            
            # Atualizar dados da reação
            self.dados_reacao = {
                "DNA_A_livre": float(solucao[idx][0]),
                "DNA_B_livre": float(solucao[idx][1]),
                "Complexo_AB": float(solucao[idx][2]),
                "DNA_hibridizado": float(solucao[idx][3]),
                "progresso_percentual": (tempo_decorrido / tempo_total) * 100,
                "tempo_decorrido": int(tempo_decorrido),
            }
            
            # Simulação de variação de sensores durante reação
            self.ph_atual = 7.4 + 0.3 * (idx / len(solucao)) + np.random.normal(0, 0.02)
            self.turbidez_atual = 0.1 + 2.0 * (idx / len(solucao)) + np.random.normal(0, 0.1)
            
            # Registrar leitura
            self.obter_leitura_sensores()
            
            # Log periódico
            if time.time() - tempo_ultimo_ponto > 60:  # A cada minuto
                print(f"[REAÇÃO] {self.dados_reacao['progresso_percentual']:.1f}% - "
                      f"DNA_H: {solucao[idx][3]:.2f} µM")
                tempo_ultimo_ponto = time.time()
            
            time.sleep(0.1)  # Atualizar 10x por segundo
        
        # Reação concluída
        if not self.reacao_ativa:
            print("[REAÇÃO] Parada pelo usuário")
        else:
            print("[REAÇÃO] Concluída com sucesso!")
            self.resultado_final = {
                "status": "sucesso",
                "DNA_hibridizado_final": float(solucao[-1][3]),
                "DNA_A_restante": float(solucao[-1][0]),
                "DNA_B_restante": float(solucao[-1][1]),
                "temperatura_media": np.mean([l.temperatura for l in self.historico_leituras[-300:]]),
                "pH_final": self.ph_atual,
                "timestamp_conclusao": datetime.now().isoformat()
            }
            self.estado = HibridizadorState.RESFRIANDO
    
    def obter_status(self) -> Dict:
        """Obter status completo do sistema"""
        return {
            "estado": self.estado.value,
            "temperatura": round(self.temperatura_atual, 2),
            "pH": round(self.ph_atual, 2),
            "condutividade": round(self.condutividade_atual, 2),
            "turbidez": round(self.turbidez_atual, 2),
            "reacao_ativa": self.reacao_ativa,
            "dados_reacao": self.dados_reacao,
            "timestamp": datetime.now().isoformat()
        }


if __name__ == "__main__":
    # Exemplo de uso
    hibridizador = Hibridizador()
    hibridizador.ligar()
    
    time.sleep(3)
    
    # Configurar parâmetros
    hibridizador.configurar_parametros({
        "temperatura_alvo": 37.5,
        "duracao_reacao": 600,  # 10 minutos para teste
        "velocidade_bomba": 75.0
    })
    
    # Iniciar reação
    hibridizador.iniciar_reacao()
    
    # Monitorar por 15 segundos
    for i in range(15):
        status = hibridizador.obter_status()
        print(f"\n[STATUS {i}] {status['estado']} - "
              f"Temp: {status['temperatura']}°C - "
              f"Progresso: {status['dados_reacao']['progresso_percentual']:.1f}%")
        time.sleep(1)
    
    hibridizador.desligar()
