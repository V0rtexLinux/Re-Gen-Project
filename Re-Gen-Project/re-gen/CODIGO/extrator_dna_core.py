#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrator de DNA - Motor Principal
Sistema de extração de DNA de amostras biológicas
Re-Dino Project v1.0
"""

import json
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
from enum import Enum


class ExtratorState(Enum):
    """Estados do extrator de DNA"""
    DESLIGADO = "desligado"
    PRONTO = "pronto"
    PREPARANDO = "preparando"
    LISANDO = "lisando"
    PRECIPITANDO = "precipitando"
    CENTRIFUGANDO = "centrifugando"
    LAVANDO = "lavando"
    SECANDO = "secando"
    RECOLHENDO = "recolhendo"
    COMPLETO = "completo"
    ERRO = "erro"


@dataclass
class AmostraBiologica:
    """Amostra biológica para extração"""
    id: str
    tipo: str  # "sangue", "tecido", "saliva", "pluma"
    volume_ml: float  # mL
    quantidade_celulas: int  # células estimadas
    timestamp_coleta: str


@dataclass
class ParametroExtracao:
    """Parâmetros da extração de DNA"""
    temperatura_lise: float = 65.0  # °C
    tempo_lise: int = 300  # segundos (5 min)
    rpm_centrifugacao: int = 10000  # RPM
    tempo_centrifugacao: int = 120  # segundos (2 min)
    volume_buffer_lise: int = 200  # µL
    volume_etanol: int = 300  # µL
    temperatura_secagem: float = 55.0  # °C
    tempo_secagem: int = 600  # segundos (10 min)


@dataclass
class LeituraSensor:
    """Leitura de sensores durante extração"""
    temperatura: float  # °C
    rpg: float  # RPM
    absorbancia_260: float  # UV absorbância
    absorbancia_280: float  # UV absorbância
    turbidez: float  # NTU
    timestamp: str


class ModeloExtracao:
    """Modelo matemático da extração de DNA"""
    
    def __init__(self):
        # Constantes de eficiência
        self.eficiencia_lise = 0.85  # 85% de lise celular
        self.eficiencia_precipitacao = 0.90  # 90% de precipitação
        self.eficiencia_centrifugacao = 0.95  # 95% de separação
        self.eficiencia_lavagem = 0.88  # 88% de pureza mantida
        
        # Constantes cinéticas
        self.taxa_lise = 0.003  # s⁻¹
        self.taxa_precipitacao = 0.0015  # s⁻¹
        self.taxa_denaturacao = 0.0001  # s⁻¹ (proteínas)
    
    def calcular_dna_extraido(self, amostra: AmostraBiologica, parametros: ParametroExtracao) -> Tuple[float, float]:
        """
        Calcular quantidade de DNA extraído
        
        Args:
            amostra: Amostra biológica
            parametros: Parâmetros da extração
            
        Returns:
            (dna_total_ng, pureza_260_280)
        """
        # Estimativa: 6 pg de DNA por célula humana
        dna_por_celula = 6e-12  # gramas
        dna_inicial = amostra.quantidade_celulas * dna_por_celula * 1e9  # ng
        
        # Aplicar eficiências
        dna_apos_lise = dna_inicial * self.eficiencia_lise
        dna_apos_precipitacao = dna_apos_lise * self.eficiencia_precipitacao
        dna_apos_centrifugacao = dna_apos_precipitacao * self.eficiencia_centrifugacao
        dna_final = dna_apos_centrifugacao * self.eficiencia_lavagem
        
        # Calcular pureza (A260/A280)
        # Ideal: 1.8-2.0 (DNA puro)
        # Com proteínas: <1.8
        # Com RNA: >2.0
        pureza = 1.85 + (0.05 * self.eficiencia_lavagem)
        
        return dna_final, pureza
    
    def estimar_tempo_total(self, parametros: ParametroExtracao) -> int:
        """
        Estimar tempo total da extração
        
        Returns:
            Tempo em segundos
        """
        tempo = (
            60 +  # Preparação inicial
            parametros.tempo_lise +
            60 +  # Precipitação
            parametros.tempo_centrifugacao +
            60 +  # Transferência
            parametros.tempo_centrifugacao +  # Segunda centrifugação (lavagem)
            parametros.tempo_secagem +
            60    # Recolhimento
        )
        return tempo


class ExtratorDNA:
    """Controlador principal do extrator de DNA"""
    
    def __init__(self):
        self.estado = ExtratorState.DESLIGADO
        self.modelo_extracao = ModeloExtracao()
        
        # Hardware (será injetado)
        self.hardware = None
        
        # Estado interno
        self.amostra_atual: Optional[AmostraBiologica] = None
        self.parametros_extracao = ParametroExtracao()
        
        self.temperatura_atual = 20.0
        self.rpm_atual = 0
        self.absorbancia_260 = 0.0
        self.absorbancia_280 = 0.0
        self.turbidez_atual = 0.0
        
        self.historico_leituras: List[LeituraSensor] = []
        
        # Resultado
        self.resultado_extracao = None
        self.dna_extraido_ng = 0.0
        self.pureza_260_280 = 0.0
    
    def set_hardware(self, hardware):
        """Injetar controlador de hardware"""
        self.hardware = hardware
    
    def ligar(self) -> bool:
        """Ligar o extrator"""
        try:
            if self.estado == ExtratorState.DESLIGADO:
                self.estado = ExtratorState.PRONTO
                self.temperatura_atual = 20.0
                print("[EXTRATOR] Sistema ligado e pronto")
                return True
        except Exception as e:
            self.estado = ExtratorState.ERRO
            print(f"[ERRO] Falha ao ligar: {e}")
            return False
    
    def desligar(self) -> bool:
        """Desligar o extrator"""
        try:
            self.estado = ExtratorState.DESLIGADO
            print("[EXTRATOR] Sistema desligado")
            return True
        except Exception as e:
            print(f"[ERRO] Falha ao desligar: {e}")
            return False
    
    def carregar_amostra(self, amostra: AmostraBiologica) -> bool:
        """Carregar amostra para extração"""
        try:
            if self.estado != ExtratorState.PRONTO:
                print(f"[ERRO] Sistema não está pronto. Estado: {self.estado.value}")
                return False
            
            self.amostra_atual = amostra
            self.estado = ExtratorState.PREPARANDO
            print(f"[AMOSTRA] Carregada: {amostra.tipo} ({amostra.volume_ml}mL)")
            return True
        except Exception as e:
            print(f"[ERRO] Falha ao carregar amostra: {e}")
            return False
    
    def configurar_parametros(self, parametros: Dict) -> bool:
        """Configurar parâmetros da extração"""
        try:
            if parametros.get("temperatura_lise"):
                self.parametros_extracao.temperatura_lise = parametros["temperatura_lise"]
            if parametros.get("tempo_lise"):
                self.parametros_extracao.tempo_lise = parametros["tempo_lise"]
            if parametros.get("rpm_centrifugacao"):
                self.parametros_extracao.rpm_centrifugacao = parametros["rpm_centrifugacao"]
            
            print(f"[CONFIG] Parâmetros atualizados")
            return True
        except Exception as e:
            print(f"[ERRO] Falha ao configurar: {e}")
            return False
    
    def iniciar_extracao(self) -> bool:
        """Iniciar processo de extração"""
        try:
            if self.estado != ExtratorState.PREPARANDO:
                print(f"[ERRO] Não pronto para extrair. Estado: {self.estado.value}")
                return False
            
            if not self.amostra_atual:
                print("[ERRO] Nenhuma amostra carregada")
                return False
            
            print(f"[EXTRAÇÃO] Iniciada para {self.amostra_atual.tipo}")
            
            # Simular etapas
            self._executar_lise()
            self._executar_precipitacao()
            self._executar_centrifugacao()
            self._executar_lavagem()
            self._executar_secagem()
            self._recolher_dna()
            
            # Calcular resultado
            self.dna_extraido_ng, self.pureza_260_280 = self.modelo_extracao.calcular_dna_extraido(
                self.amostra_atual,
                self.parametros_extracao
            )
            
            self.resultado_extracao = {
                "status": "sucesso",
                "amostra": asdict(self.amostra_atual),
                "dna_extraido_ng": self.dna_extraido_ng,
                "pureza_260_280": self.pureza_260_280,
                "concentracao_ng_ul": self.dna_extraido_ng / 50,  # Volume final ~50µL
                "timestamp": datetime.now().isoformat()
            }
            
            self.estado = ExtratorState.COMPLETO
            print(f"[SUCESSO] DNA extraído: {self.dna_extraido_ng:.2f} ng")
            return True
        except Exception as e:
            self.estado = ExtratorState.ERRO
            print(f"[ERRO] Falha na extração: {e}")
            return False
    
    def _executar_lise(self):
        """Executar etapa de lise celular"""
        self.estado = ExtratorState.LISANDO
        print(f"[LISE] Aquecendo para {self.parametros_extracao.temperatura_lise}°C")
        self.temperatura_atual = self.parametros_extracao.temperatura_lise
        print(f"[LISE] Incubando por {self.parametros_extracao.tempo_lise}s")
    
    def _executar_precipitacao(self):
        """Executar precipitação de DNA"""
        self.estado = ExtratorState.PRECIPITANDO
        print(f"[PRECIPITAÇÃO] Adicionando etanol")
    
    def _executar_centrifugacao(self):
        """Executar centrifugação"""
        self.estado = ExtratorState.CENTRIFUGANDO
        print(f"[CENTRIFUGAÇÃO] {self.parametros_extracao.rpm_centrifugacao} RPM por {self.parametros_extracao.tempo_centrifugacao}s")
        self.rpm_atual = self.parametros_extracao.rpm_centrifugacao
    
    def _executar_lavagem(self):
        """Executar lavagem"""
        self.estado = ExtratorState.LAVANDO
        print(f"[LAVAGEM] Etapa 1 - Etanol 70%")
        print(f"[LAVAGEM] Etapa 2 - Etanol 100%")
    
    def _executar_secagem(self):
        """Executar secagem"""
        self.estado = ExtratorState.SECANDO
        print(f"[SECAGEM] Aquecendo para {self.parametros_extracao.temperatura_secagem}°C por {self.parametros_extracao.tempo_secagem}s")
        self.temperatura_atual = self.parametros_extracao.temperatura_secagem
    
    def _recolher_dna(self):
        """Recolher DNA final"""
        self.estado = ExtratorState.RECOLHENDO
        print("[RECOLHIMENTO] Adicionando buffer TE 50µL")
        print("[RECOLHIMENTO] DNA armazenado em tubo estéril")
    
    def obter_status(self) -> Dict:
        """Obter status completo do sistema"""
        return {
            "estado": self.estado.value,
            "temperatura": round(self.temperatura_atual, 2),
            "rpm": self.rpm_atual,
            "absorbancia_260": round(self.absorbancia_260, 3),
            "absorbancia_280": round(self.absorbancia_280, 3),
            "turbidez": round(self.turbidez_atual, 2),
            "dna_extraido_ng": round(self.dna_extraido_ng, 2),
            "pureza": round(self.pureza_260_280, 2),
            "timestamp": datetime.now().isoformat()
        }
    
    def exportar_dados_extracao(self) -> Dict:
        """Exportar dados completos da extração"""
        return {
            "timestamp": datetime.now().isoformat(),
            "parametros": asdict(self.parametros_extracao),
            "resultado": self.resultado_extracao,
            "historico_sensores": [asdict(l) for l in self.historico_leituras],
        }


if __name__ == "__main__":
    # Exemplo de uso
    extrator = ExtratorDNA()
    extrator.ligar()
    
    # Criar amostra
    amostra = AmostraBiologica(
        id="AMOSTRA_001",
        tipo="sangue",
        volume_ml=5.0,
        quantidade_celulas=50000000,  # 50 milhões de células
        timestamp_coleta=datetime.now().isoformat()
    )
    
    # Carregar e extrair
    extrator.carregar_amostra(amostra)
    extrator.iniciar_extracao()
    
    # Resultado
    status = extrator.obter_status()
    print(f"\nRESULTADO:")
    print(f"DNA: {status['dna_extraido_ng']} ng")
    print(f"Pureza: {status['pureza']}")
    
    extrator.desligar()
