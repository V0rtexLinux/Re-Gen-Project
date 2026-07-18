#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hibridizador de DNA - Interface Gráfica PyQt5
Simula os dois monitores LCD de 10.1" com controles
Re-Dino Project v1.0
"""

import sys
import time
import json
from datetime import datetime
from threading import Thread
from typing import Optional

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QGridLayout, QPushButton, QLabel, QLCDNumber, QProgressBar,
    QTableWidget, QTableWidgetItem, QTabWidget, QSpinBox, QDoubleSpinBox,
    QComboBox, QTextEdit, QSlider, QDial
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject, QThread
from PyQt5.QtGui import QColor, QFont, QPixmap, QIcon
from PyQt5.QtChart import QChart, QChartView, QLineSeries
from PyQt5.QtCore import QPointF

from hibridizador_core import Hibridizador, HibridizadorState
from hibridizador_hardware import (
    ControladorHardware, CorLED, LEDRGB
)


class TrabalhadorHibridizacao(QObject):
    """Worker thread para atualizar dados em tempo real"""
    
    sinal_status_atualizado = pyqtSignal(dict)
    sinal_reacao_progresso = pyqtSignal(dict)
    
    def __init__(self, hibridizador: Hibridizador):
        super().__init__()
        self.hibridizador = hibridizador
        self.rodando = True
    
    def run(self):
        """Executar monitoramento contínuo"""
        while self.rodando:
            status = self.hibridizador.obter_status()
            self.sinal_status_atualizado.emit(status)
            
            if self.hibridizador.reacao_ativa:
                self.sinal_reacao_progresso.emit(
                    self.hibridizador.dados_reacao
                )
            
            time.sleep(0.5)
    
    def parar(self):
        """Parar thread"""
        self.rodando = False


class MonitorLCDEsquerdo(QWidget):
    """Monitor LCD Esquerdo - Monitoramento de Parâmetros"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Inicializar interface"""
        layout = QVBoxLayout()
        
        # Título
        titulo = QLabel("MONITOR 1: PARÂMETROS")
        titulo.setFont(QFont("Courier", 12, QFont.Bold))
        titulo.setStyleSheet("color: #00FF00; background-color: #000;")
        layout.addWidget(titulo)
        
        # Grid de parâmetros
        grid = QGridLayout()
        grid.setSpacing(10)
        
        # Temperatura
        self.lbl_temp_titulo = QLabel("TEMPERATURA:")
        self.lbl_temp_titulo.setStyleSheet("color: #00FF00; font-weight: bold;")
        self.lbl_temp_valor = QLCDNumber()
        self.lbl_temp_valor.setDigitCount(5)
        self.lbl_temp_valor.setSegmentStyle(QLCDNumber.Flat)
        self.lbl_temp_valor.setStyleSheet("color: #00FF00; background-color: #001100;")
        
        grid.addWidget(self.lbl_temp_titulo, 0, 0)
        grid.addWidget(self.lbl_temp_valor, 0, 1)
        grid.addWidget(QLabel("°C"), 0, 2)
        
        # pH
        self.lbl_ph_titulo = QLabel("pH:")
        self.lbl_ph_titulo.setStyleSheet("color: #00FF00; font-weight: bold;")
        self.lbl_ph_valor = QLCDNumber()
        self.lbl_ph_valor.setDigitCount(4)
        self.lbl_ph_valor.setSegmentStyle(QLCDNumber.Flat)
        self.lbl_ph_valor.setStyleSheet("color: #00FF00; background-color: #001100;")
        
        grid.addWidget(self.lbl_ph_titulo, 1, 0)
        grid.addWidget(self.lbl_ph_valor, 1, 1)
        
        # Condutividade
        self.lbl_cond_titulo = QLabel("CONDUTIVIDADE:")
        self.lbl_cond_titulo.setStyleSheet("color: #00FF00; font-weight: bold;")
        self.lbl_cond_valor = QLCDNumber()
        self.lbl_cond_valor.setDigitCount(5)
        self.lbl_cond_valor.setSegmentStyle(QLCDNumber.Flat)
        self.lbl_cond_valor.setStyleSheet("color: #00FF00; background-color: #001100;")
        
        grid.addWidget(self.lbl_cond_titulo, 2, 0)
        grid.addWidget(self.lbl_cond_valor, 2, 1)
        grid.addWidget(QLabel("mS/cm"), 2, 2)
        
        # Progresso
        self.lbl_prog_titulo = QLabel("PROGRESSO:")
        self.lbl_prog_titulo.setStyleSheet("color: #00FF00; font-weight: bold;")
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(
            "QProgressBar { background-color: #001100; border: 1px solid #00FF00; }"
            "QProgressBar::chunk { background-color: #00FF00; }"
        )
        
        grid.addWidget(self.lbl_prog_titulo, 3, 0)
        grid.addWidget(self.progress_bar, 3, 1, 1, 2)
        
        # Tempo decorrido
        self.lbl_tempo_titulo = QLabel("TEMPO DECORRIDO:")
        self.lbl_tempo_titulo.setStyleSheet("color: #00FF00; font-weight: bold;")
        self.lbl_tempo_valor = QLabel("00:00:00")
        self.lbl_tempo_valor.setStyleSheet("color: #00FF00; font-family: Courier;")
        
        grid.addWidget(self.lbl_tempo_titulo, 4, 0)
        grid.addWidget(self.lbl_tempo_valor, 4, 1)
        
        layout.addLayout(grid)
        layout.addStretch()
        
        self.setStyleSheet("background-color: #000; color: #00FF00;")
        self.setLayout(layout)
    
    def atualizar(self, status: dict):
        """Atualizar com novo status"""
        self.lbl_temp_valor.display(f"{status['temperatura']:.1f}")
        self.lbl_ph_valor.display(f"{status['pH']:.2f}")
        self.lbl_cond_valor.display(f"{status['condutividade']:.1f}")
        
        progresso = status['dados_reacao']['progresso_percentual']
        self.progress_bar.setValue(int(progresso))
        
        tempo_seg = int(status['dados_reacao']['tempo_decorrido'])
        horas = tempo_seg // 3600
        minutos = (tempo_seg % 3600) // 60
        segundos = tempo_seg % 60
        self.lbl_tempo_valor.setText(f"{horas:02d}:{minutos:02d}:{segundos:02d}")


class MonitorLCDDireito(QWidget):
    """Monitor LCD Direito - Análise e Controle"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.series_hibridizado = QLineSeries()
        self.series_complexo = QLineSeries()
        self.init_ui()
    
    def init_ui(self):
        """Inicializar interface"""
        layout = QVBoxLayout()
        
        # Título
        titulo = QLabel("MONITOR 2: ANÁLISE DE DNA")
        titulo.setFont(QFont("Courier", 12, QFont.Bold))
        titulo.setStyleSheet("color: #0080FF; background-color: #000;")
        layout.addWidget(titulo)
        
        # Gráfico
        chart = QChart()
        chart.setTitle("Concentração de DNA (µM)")
        chart.setBackgroundBrush(QColor("#000"))
        chart.setTitleBrush(QColor("#0080FF"))
        
        self.series_hibridizado.setName("DNA Hibridizado")
        self.series_complexo.setName("Complexo AB")
        
        chart.addSeries(self.series_hibridizado)
        chart.addSeries(self.series_complexo)
        chart.createDefaultAxes()
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(chart_view.Antialiasing)
        chart_view.setStyleSheet("background-color: #001133;")
        
        layout.addWidget(chart_view)
        
        # Info de reação
        info_layout = QGridLayout()
        
        self.lbl_dna_a = QLabel("DNA-A livre: --")
        self.lbl_dna_a.setStyleSheet("color: #0080FF;")
        self.lbl_dna_b = QLabel("DNA-B livre: --")
        self.lbl_dna_b.setStyleSheet("color: #0080FF;")
        self.lbl_complexo = QLabel("Complexo AB: --")
        self.lbl_complexo.setStyleSheet("color: #00FF00;")
        self.lbl_hibridizado = QLabel("Hibridizado: --")
        self.lbl_hibridizado.setStyleSheet("color: #FF0000; font-weight: bold;")
        
        info_layout.addWidget(self.lbl_dna_a, 0, 0)
        info_layout.addWidget(self.lbl_dna_b, 0, 1)
        info_layout.addWidget(self.lbl_complexo, 1, 0)
        info_layout.addWidget(self.lbl_hibridizado, 1, 1)
        
        layout.addLayout(info_layout)
        
        self.setStyleSheet("background-color: #000; color: #0080FF;")
        self.setLayout(layout)
    
    def atualizar(self, dados_reacao: dict):
        """Atualizar com dados de reação"""
        self.lbl_dna_a.setText(f"DNA-A livre: {dados_reacao['DNA_A_livre']:.2f} µM")
        self.lbl_dna_b.setText(f"DNA-B livre: {dados_reacao['DNA_B_livre']:.2f} µM")
        self.lbl_complexo.setText(f"Complexo AB: {dados_reacao['Complexo_AB']:.2f} µM")
        self.lbl_hibridizado.setText(f"Hibridizado: {dados_reacao['DNA_hibridizado']:.2f} µM")
        
        # Atualizar gráfico (a cada 10 pontos)
        if len(self.series_hibridizado) < 100:
            self.series_hibridizado.append(
                QPointF(len(self.series_hibridizado), 
                       dados_reacao['DNA_hibridizado'])
            )
            self.series_complexo.append(
                QPointF(len(self.series_complexo), 
                       dados_reacao['Complexo_AB'])
            )


class PainelControles(QWidget):
    """Painel de controles com botões RGB (4x4)"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.botoes_callbacks = {}
        self.init_ui()
    
    def init_ui(self):
        """Inicializar painel de botões"""
        layout = QVBoxLayout()
        
        # Título
        titulo = QLabel("PAINEL DE CONTROLE (4x4)")
        titulo.setFont(QFont("Courier", 10, QFont.Bold))
        titulo.setStyleSheet("color: #FFFF00; background-color: #000;")
        layout.addWidget(titulo)
        
        # Grid de botões
        grid = QGridLayout()
        grid.setSpacing(5)
        
        nomes_botoes = [
            "Liga/Desliga", "Iniciar", "Pausa", "Reset",
            "Temp↑", "Temp↓", "Veloc↑", "Veloc↓",
            "Manual", "Auto", "Calibrar", "Diagnóstico",
            "Salvar", "Carregar", "Exportar", "Menu"
        ]
        
        cores = [
            "#FF0000", "#0000FF", "#FFFF00", "#FF0000",
            "#FFA500", "#00FFFF", "#FF00FF", "#FFC0CB",
            "#00FF00", "#0000FF", "#FFFF00", "#FFFFFF",
            "#00FF00", "#0000FF", "#FFFF00", "#FF00FF"
        ]
        
        self.botoes = {}
        
        for i in range(16):
            linha = i // 4
            coluna = i % 4
            
            btn = QPushButton(nomes_botoes[i])
            btn.setMinimumHeight(60)
            btn.setMinimumWidth(80)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {cores[i]};
                    color: #000;
                    font-weight: bold;
                    border-radius: 5px;
                    border: 2px solid #333;
                }}
                QPushButton:hover {{
                    background-color: {cores[i]};
                    border: 2px solid #FFF;
                }}
                QPushButton:pressed {{
                    background-color: #666;
                }}
            """)
            
            self.botoes[i] = btn
            grid.addWidget(btn, linha, coluna)
        
        layout.addLayout(grid)
        
        self.setStyleSheet("background-color: #000;")
        self.setLayout(layout)
    
    def conectar_botao(self, id_botao: int, callback):
        """Conectar callback a um botão"""
        if id_botao in self.botoes:
            self.botoes[id_botao].clicked.connect(callback)


class JanelaHibridizador(QMainWindow):
    """Janela principal da interface do hibridizador"""
    
    def __init__(self):
        super().__init__()
        
        # Backend
        self.hibridizador = Hibridizador()
        self.hardware = ControladorHardware()
        self.hibridizador.set_hardware(self.hardware)
        
        self.init_ui()
        self.setup_conexoes()
        self.iniciar_atualizacoes()
        
        # Iniciar sistemas
        self.hardware.iniciar()
        self.hibridizador.ligar()
    
    def init_ui(self):
        """Inicializar interface"""
        self.setWindowTitle("🧬 HIBRIDIZADOR DNA 3000 - Sistema de Hibridização")
        self.setGeometry(0, 0, 1920, 1080)
        self.setStyleSheet("background-color: #000; color: #FFF;")
        
        # Widget central
        central = QWidget()
        layout = QHBoxLayout()
        
        # Monitor 1 (Esquerdo)
        self.monitor_esquerdo = MonitorLCDEsquerdo()
        self.monitor_esquerdo.setMinimumWidth(500)
        self.monitor_esquerdo.setMaximumWidth(700)
        layout.addWidget(self.monitor_esquerdo)
        
        # Painel central (câmara + separador)
        painel_central = QVBoxLayout()
        
        camera_label = QLabel("═══ CÂMARA DE REAÇÃO CENTRAL ═══")
        camera_label.setAlignment(Qt.AlignCenter)
        camera_label.setFont(QFont("Courier", 14, QFont.Bold))
        camera_label.setStyleSheet("color: #FF00FF;")
        painel_central.addWidget(camera_label)
        
        # Simulação visual da câmara
        self.camera_display = QLabel()
        self.camera_display.setMinimumSize(300, 300)
        self.camera_display.setAlignment(Qt.AlignCenter)
        self.camera_display.setStyleSheet("""
            background-color: #001100;
            border: 3px solid #00FF00;
            border-radius: 150px;
        """)
        self.camera_display.setText("CÂMARA\nPRÉPARA")
        painel_central.addWidget(self.camera_display)
        
        layout.addLayout(painel_central)
        
        # Monitor 2 (Direito)
        self.monitor_direito = MonitorLCDDireito()
        self.monitor_direito.setMinimumWidth(500)
        self.monitor_direito.setMaximumWidth(700)
        layout.addWidget(self.monitor_direito)
        
        central.setLayout(layout)
        self.setCentralWidget(central)
        
        # Painel de controles (inferior via dock)
        dock = QWidget()
        dock_layout = QVBoxLayout()
        self.painel_controles = PainelControles()
        dock_layout.addWidget(self.painel_controles)
        dock.setLayout(dock_layout)
        dock.setMaximumHeight(300)
        
        # Adicionar como widget inferior
        layout_main = QVBoxLayout()
        layout_main.addLayout(layout)
        layout_main.addWidget(dock)
        
        central_main = QWidget()
        central_main.setLayout(layout_main)
        self.setCentralWidget(central_main)
    
    def setup_conexoes(self):
        """Conectar botões aos callbacks"""
        self.painel_controles.conectar_botao(0, self.ligar_desligar)
        self.painel_controles.conectar_botao(1, self.iniciar_reacao)
        self.painel_controles.conectar_botao(2, self.pausar_reacao)
        self.painel_controles.conectar_botao(3, self.resetar_sistema)
    
    def iniciar_atualizacoes(self):
        """Iniciar thread de atualizações"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.atualizar_interface)
        self.timer.start(500)  # Atualizar a cada 500ms
    
    def atualizar_interface(self):
        """Atualizar interface com dados do hibridizador"""
        status = self.hibridizador.obter_status()
        
        self.monitor_esquerdo.atualizar(status)
        self.monitor_direito.atualizar(status['dados_reacao'])
        
        # Atualizar cor da câmara baseado no estado
        estado = self.hibridizador.estado.value
        if estado == "pronto":
            self.camera_display.setStyleSheet("""
                background-color: #001100;
                border: 3px solid #00FF00;
                border-radius: 150px;
            """)
            self.camera_display.setText("PRONTO\n✓")
            self.hardware.set_cor_led(CorLED.VERDE, 80)
        elif estado == "em_reacao":
            self.camera_display.setStyleSheet("""
                background-color: #000055;
                border: 3px solid #0000FF;
                border-radius: 150px;
            """)
            self.camera_display.setText("REAÇÃO\nEM PROGRESSO")
            self.hardware.set_cor_led(CorLED.AZUL, 100)
        elif estado == "erro":
            self.camera_display.setStyleSheet("""
                background-color: #550000;
                border: 3px solid #FF0000;
                border-radius: 150px;
            """)
            self.camera_display.setText("ERRO\n⚠")
            self.hardware.set_cor_led(CorLED.VERMELHO, 100)
    
    def ligar_desligar(self):
        """Toggle liga/desliga"""
        if self.hibridizador.estado == HibridizadorState.DESLIGADO:
            self.hibridizador.ligar()
        else:
            self.hibridizador.desligar()
    
    def iniciar_reacao(self):
        """Iniciar reação"""
        self.hibridizador.iniciar_reacao()
    
    def pausar_reacao(self):
        """Pausar reação"""
        self.hibridizador.pausar_reacao()
    
    def resetar_sistema(self):
        """Resetar sistema"""
        self.hibridizador.resetar_sistema()
    
    def closeEvent(self, event):
        """Evento de fechamento"""
        self.hibridizador.desligar()
        self.hardware.parar()
        event.accept()


def main():
    """Função principal"""
    app = QApplication(sys.argv)
    
    janela = JanelaHibridizador()
    janela.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
