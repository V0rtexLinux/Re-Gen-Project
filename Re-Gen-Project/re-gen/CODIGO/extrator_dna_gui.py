#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrator de DNA - Interface Gráfica
Re-Dino Project v1.0
"""

import sys
import time
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QProgressBar, QTextEdit, QComboBox,
    QSpinBox, QDoubleSpinBox, QTabWidget, QTableWidget, QTableWidgetItem
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor

from extrator_dna_core import ExtratorDNA, ExtratorState, AmostraBiologica, ParametroExtracao
from extrator_dna_hardware import ControladorHardwareExtrator


class JanelaExtratorDNA(QMainWindow):
    """Janela principal do interface do extrator"""
    
    def __init__(self):
        super().__init__()
        
        # Backend
        self.extrator = ExtratorDNA()
        self.hardware = ControladorHardwareExtrator()
        self.extrator.set_hardware(self.hardware)
        
        self.init_ui()
        self.setup_conexoes()
        self.iniciar_atualizacoes()
        
        # Iniciar sistemas
        self.hardware.iniciar()
        self.extrator.ligar()
    
    def init_ui(self):
        """Inicializar interface"""
        self.setWindowTitle("🧬 EXTRATOR DE DNA - Sistema de Extração")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("background-color: #f0f0f0;")
        
        # Widget central com abas
        tabs = QTabWidget()
        
        # Aba 1: Controle
        tab_controle = self.criar_aba_controle()
        tabs.addTab(tab_controle, "Controle")
        
        # Aba 2: Monitoramento
        tab_monitor = self.criar_aba_monitoramento()
        tabs.addTab(tab_monitor, "Monitoramento")
        
        # Aba 3: Dados
        tab_dados = self.criar_aba_dados()
        tabs.addTab(tab_dados, "Dados")
        
        self.setCentralWidget(tabs)
    
    def criar_aba_controle(self) -> QWidget:
        """Criar aba de controle"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Seleção de amostra
        layout.addWidget(QLabel("TIPO DE AMOSTRA"))
        self.combo_amostra = QComboBox()
        self.combo_amostra.addItems(["sangue", "tecido", "saliva", "pluma"])
        layout.addWidget(self.combo_amostra)
        
        # Volume
        layout.addWidget(QLabel("VOLUME (mL)"))
        self.spin_volume = QDoubleSpinBox()
        self.spin_volume.setValue(5.0)
        self.spin_volume.setMinimum(0.1)
        self.spin_volume.setMaximum(50.0)
        layout.addWidget(self.spin_volume)
        
        # Quantidade de células
        layout.addWidget(QLabel("QUANTIDADE DE CÉLULAS"))
        self.spin_celulas = QSpinBox()
        self.spin_celulas.setValue(50000000)
        self.spin_celulas.setMaximum(1000000000)
        layout.addWidget(self.spin_celulas)
        
        # Temperatura de lise
        layout.addWidget(QLabel("TEMPERATURA LISE (°C)"))
        self.spin_temp_lise = QDoubleSpinBox()
        self.spin_temp_lise.setValue(65.0)
        self.spin_temp_lise.setMinimum(20.0)
        self.spin_temp_lise.setMaximum(95.0)
        layout.addWidget(self.spin_temp_lise)
        
        # RPM centrifugação
        layout.addWidget(QLabel("RPM CENTRIFUGAÇÃO"))
        self.spin_rpm = QSpinBox()
        self.spin_rpm.setValue(10000)
        self.spin_rpm.setMinimum(1000)
        self.spin_rpm.setMaximum(15000)
        layout.addWidget(self.spin_rpm)
        
        # Botões
        self.btn_carregar = QPushButton("CARREGAR AMOSTRA")
        self.btn_carregar.clicked.connect(self.carregar_amostra)
        layout.addWidget(self.btn_carregar)
        
        self.btn_iniciar = QPushButton("INICIAR EXTRAÇÃO")
        self.btn_iniciar.setStyleSheet("background-color: #4CAF50; color: white;")
        self.btn_iniciar.clicked.connect(self.iniciar_extracao)
        layout.addWidget(self.btn_iniciar)
        
        widget.setLayout(layout)
        return widget
    
    def criar_aba_monitoramento(self) -> QWidget:
        """Criar aba de monitoramento"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Status geral
        layout.addWidget(QLabel("STATUS DO SISTEMA"))
        self.label_estado = QLabel("Pronto")
        self.label_estado.setFont(QFont("Courier", 12, QFont.Bold))
        self.label_estado.setStyleSheet("color: green;")
        layout.addWidget(self.label_estado)
        
        # Progress
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        
        # Sensores
        layout.addWidget(QLabel("SENSORES"))
        self.label_temp = QLabel("Temperatura: --")
        self.label_absorbancia = QLabel("A260: -- | A280: -- | Pureza: --")
        layout.addWidget(self.label_temp)
        layout.addWidget(self.label_absorbancia)
        
        # Atuadores
        layout.addWidget(QLabel("ATUADORES"))
        self.label_centrifuga = QLabel("Centrifuga: Parada")
        self.label_aquecedor = QLabel("Aquecedor: Desligado")
        self.label_bomba = QLabel("Bomba: Parada")
        layout.addWidget(self.label_centrifuga)
        layout.addWidget(self.label_aquecedor)
        layout.addWidget(self.label_bomba)
        
        # Log
        layout.addWidget(QLabel("LOG"))
        self.text_log = QTextEdit()
        self.text_log.setReadOnly(True)
        self.text_log.setMaximumHeight(150)
        layout.addWidget(self.text_log)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def criar_aba_dados(self) -> QWidget:
        """Criar aba de dados de resultado"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("RESULTADO DA EXTRAÇÃO"))
        
        self.label_dna_ng = QLabel("DNA extraído: -- ng")
        self.label_dna_ng.setFont(QFont("Courier", 14, QFont.Bold))
        self.label_dna_ng.setStyleSheet("color: #2196F3;")
        layout.addWidget(self.label_dna_ng)
        
        self.label_concentracao = QLabel("Concentração: -- ng/µL")
        layout.addWidget(self.label_concentracao)
        
        self.label_pureza = QLabel("Pureza (A260/A280): --")
        layout.addWidget(self.label_pureza)
        
        # Tabela de resultados
        layout.addWidget(QLabel("HISTÓRICO"))
        self.table_resultados = QTableWidget()
        self.table_resultados.setColumnCount(4)
        self.table_resultados.setHorizontalHeaderLabels([
            "Amostra", "DNA (ng)", "Concentração (ng/µL)", "Pureza"
        ])
        layout.addWidget(self.table_resultados)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def setup_conexoes(self):
        """Setup de conexões"""
        pass
    
    def iniciar_atualizacoes(self):
        """Iniciar timer de atualizações"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.atualizar_interface)
        self.timer.start(500)
    
    def atualizar_interface(self):
        """Atualizar interface com dados do extrator"""
        status = self.extrator.obter_status()
        hw_status = self.hardware.obter_status_completo()
        
        # Atualizar estado
        estado_texto = status['estado'].upper()
        self.label_estado.setText(f"Estado: {estado_texto}")
        
        # Cores por estado
        if status['estado'] == 'completo':
            self.label_estado.setStyleSheet("color: green; font-weight: bold;")
        elif status['estado'] == 'erro':
            self.label_estado.setStyleSheet("color: red; font-weight: bold;")
        else:
            self.label_estado.setStyleSheet("color: orange; font-weight: bold;")
        
        # Sensores
        self.label_temp.setText(
            f"Temperatura: {hw_status['sensores']['temperatura']:.1f}°C"
        )
        self.label_absorbancia.setText(
            f"A260: {hw_status['sensores']['absorbancia_260']:.3f} | "
            f"A280: {hw_status['sensores']['absorbancia_280']:.3f} | "
            f"Pureza: {hw_status['sensores']['pureza_260_280']:.2f}"
        )
        
        # Atuadores
        cent_status = "Ligada" if hw_status['centrifuga']['ligada'] else "Parada"
        self.label_centrifuga.setText(
            f"Centrifuga: {cent_status} ({hw_status['centrifuga']['rpm_atual']} RPM)"
        )
        
        aq_status = "Aquecendo" if hw_status['aquecedor']['ligado'] else "Desligado"
        self.label_aquecedor.setText(
            f"Aquecedor: {aq_status} ({hw_status['aquecedor']['temperatura_atual']:.1f}°C)"
        )
        
        bomba_status = "Bombeando" if hw_status['bomba']['ligada'] else "Parada"
        self.label_bomba.setText(
            f"Bomba: {bomba_status} ({hw_status['bomba']['fluxo_ml_min']:.1f} mL/min)"
        )
        
        # Resultado
        if status['dna_extraido_ng'] > 0:
            self.label_dna_ng.setText(f"DNA extraído: {status['dna_extraido_ng']:.2f} ng")
            conc = status['dna_extraido_ng'] / 50  # 50µL volume final
            self.label_concentracao.setText(f"Concentração: {conc:.2f} ng/µL")
            self.label_pureza.setText(f"Pureza (A260/A280): {status['pureza']:.2f}")
    
    def carregar_amostra(self):
        """Carregar amostra"""
        tipo = self.combo_amostra.currentText()
        volume = self.spin_volume.value()
        celulas = self.spin_celulas.value()
        
        amostra = AmostraBiologica(
            id=f"AMOSTRA_{int(time.time())}",
            tipo=tipo,
            volume_ml=volume,
            quantidade_celulas=celulas,
            timestamp_coleta=time.strftime("%Y-%m-%d %H:%M:%S")
        )
        
        self.extrator.carregar_amostra(amostra)
        self.text_log.append(f"✓ Amostra carregada: {tipo} ({volume}mL)")
    
    def iniciar_extracao(self):
        """Iniciar extração"""
        # Configurar parâmetros
        parametros = {
            "temperatura_lise": self.spin_temp_lise.value(),
            "rpm_centrifugacao": self.spin_rpm.value(),
        }
        self.extrator.configurar_parametros(parametros)
        
        # Iniciar
        self.extrator.iniciar_extracao()
        self.text_log.append("✓ Extração iniciada")
    
    def closeEvent(self, event):
        """Evento de fechamento"""
        self.extrator.desligar()
        self.hardware.parar()
        event.accept()


def main():
    """Função principal"""
    app = QApplication(sys.argv)
    
    janela = JanelaExtratorDNA()
    janela.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
