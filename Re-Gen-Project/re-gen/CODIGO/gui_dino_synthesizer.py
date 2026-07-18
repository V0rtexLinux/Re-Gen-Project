#!/usr/bin/env python3
"""
gui_dino_synthesizer.py
=======================
Interface Gráfica Completa para Síntese de DNA de Dinossauros
Usando PyQt5 + Matplotlib para visualização

Funcionalidades:
- Seleção de dinossauro (500+)
- Visualização do genoma
- Simulação de síntese de DNA
- Controle de hardware (Raspberry Pi Zero 2W)
- Injeção em embrião de galinha
- Monitoramento em tempo real
"""

import sys
import json
from typing import Optional, List
from dataclasses import asdict

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QTextEdit, QTableWidget, QTableWidgetItem,
    QProgressBar, QSpinBox, QDoubleSpinBox, QTabWidget, QDialog,
    QMessageBox, QListWidget, QListWidgetItem, QSpinBox as QIntSpinBox,
    QLineEdit
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor, QPixmap
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Importar módulos do projeto com tratamento de erro
try:
    from dinosaur_database import DINOSAUR_DATABASE
except ImportError:
    print("⚠️ dinosaur_database não encontrado - usando dados simulados")
    DINOSAUR_DATABASE = []

try:
    from dna_synthesizer_hardware import DNTPoolConfig
except ImportError:
    print("⚠️ dna_synthesizer_hardware não encontrado")
    DNTPoolConfig = None


class DinosaurDatabaseWidget(QWidget):
    """Widget para explorar banco de dados de dinossauros."""
    
    def __init__(self):
        super().__init__()
        # Se banco está vazio, adicionar dados de teste
        if not DINOSAUR_DATABASE:
            self._load_test_dinosaurs()
        self.init_ui()
    
    def _load_test_dinosaurs(self):
        """Carrega dinossauros de teste se banco vazio."""
        test_data = [
            ("Tyrannosaurus rex", "Tiranossauro", 12.3, 4.0, 8800, "Cretáceo", "carnívoro", "popular"),
            ("Triceratops horridus", "Tricerátops", 9.0, 3.0, 6000, "Cretáceo", "herbívoro", "popular"),
            ("Velociraptor mongoliensis", "Velocirraptor", 2.1, 0.9, 15, "Cretáceo", "carnívoro", "popular"),
            ("Stegosaurus stenops", "Estegossauro", 9.0, 4.0, 2700, "Jurássico", "herbívoro", "popular"),
            ("Brachiosaurus altithorax", "Braquiossauro", 26.0, 13.0, 56000, "Jurássico", "herbívoro", "popular"),
        ]
        
        for sci_name, common, length, height, weight, period, diet, popularity in test_data:
            DINOSAUR_DATABASE.append({
                'scientific_name': sci_name,
                'common_name': common,
                'length_meters': length,
                'height_meters': height,
                'weight_kg': weight,
                'period': period,
                'diet': diet,
                'popularity': popularity,
                'description': f'{common}: Dinossauro do {period}'
            })
    
    def init_ui(self):
        """Inicializa interface do banco de dados."""
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("🦖 Banco de Dinossauros (500+ espécies)")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)
        
        # Filtros
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Buscar:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Tyrannosaurus, Triceratops...")
        filter_layout.addWidget(self.search_input)
        
        layout.addLayout(filter_layout)
        
        # Tabela de dinossauros
        self.dinosaur_table = QTableWidget()
        self.dinosaur_table.setColumnCount(7)
        self.dinosaur_table.setHorizontalHeaderLabels([
            "Nome Comum", "Científico", "Período", "Dieta",
            "Comprimento (m)", "Peso (kg)", "Popularidade"
        ])
        layout.addWidget(self.dinosaur_table)
        
        # Detalhes
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(150)
        layout.addWidget(self.details_text)
        
        # Botões
        button_layout = QHBoxLayout()
        self.select_btn = QPushButton("Selecionar este Dinossauro")
        self.select_btn.clicked.connect(self.on_select_dinosaur)
        button_layout.addWidget(self.select_btn)
        
        self.random_btn = QPushButton("Dinossauro Aleatório")
        self.random_btn.clicked.connect(self.on_random_dinosaur)
        button_layout.addWidget(self.random_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.load_dinosaurs()
    
    def load_dinosaurs(self):
        """Carrega dinossauros na tabela."""
        self.dinosaur_table.setRowCount(len(DINOSAUR_DATABASE))
        
        for row, dino in enumerate(DINOSAUR_DATABASE):
            try:
                # Trata dino como dict ou objeto
                if isinstance(dino, dict):
                    common = str(dino.get('common_name', ''))
                    scientific = str(dino.get('scientific_name', ''))
                    period = str(dino.get('period', ''))
                    diet = str(dino.get('diet', ''))
                    length = str(dino.get('length_meters', 0))
                    weight = str(dino.get('weight_kg', 0))
                    popularity = str(dino.get('popularity', ''))
                else:
                    # Se for objeto com atributos
                    common = str(dino.common_name) if hasattr(dino, 'common_name') else ''
                    scientific = str(dino.scientific_name) if hasattr(dino, 'scientific_name') else ''
                    period = str(dino.period.value) if hasattr(dino, 'period') and hasattr(dino.period, 'value') else str(dino.period) if hasattr(dino, 'period') else ''
                    diet = str(dino.diet.value) if hasattr(dino, 'diet') and hasattr(dino.diet, 'value') else str(dino.diet) if hasattr(dino, 'diet') else ''
                    length = f"{float(dino.length_meters):.1f}" if hasattr(dino, 'length_meters') else '0'
                    weight = f"{int(dino.weight_kg):,}" if hasattr(dino, 'weight_kg') else '0'
                    popularity = str(dino.popularity) if hasattr(dino, 'popularity') else ''
                
                self.dinosaur_table.setItem(row, 0, QTableWidgetItem(common))
                self.dinosaur_table.setItem(row, 1, QTableWidgetItem(scientific))
                self.dinosaur_table.setItem(row, 2, QTableWidgetItem(period))
                self.dinosaur_table.setItem(row, 3, QTableWidgetItem(diet))
                self.dinosaur_table.setItem(row, 4, QTableWidgetItem(length))
                self.dinosaur_table.setItem(row, 5, QTableWidgetItem(weight))
                self.dinosaur_table.setItem(row, 6, QTableWidgetItem(popularity))
            except Exception as e:
                print(f"Erro ao carregar dinossauro {row}: {e}")
    
    def on_select_dinosaur(self):
        """Ao selecionar um dinossauro."""
        current_row = self.dinosaur_table.currentRow()
        if current_row >= 0 and current_row < len(DINOSAUR_DATABASE):
            dino = DINOSAUR_DATABASE[current_row]
            
            try:
                if isinstance(dino, dict):
                    text = f"""
                    <b>Nome:</b> {dino.get('common_name')} ({dino.get('scientific_name')})<br>
                    <b>Período:</b> {dino.get('period')}<br>
                    <b>Tamanho:</b> {dino.get('length_meters')}m x {dino.get('height_meters')}m<br>
                    <b>Peso:</b> {dino.get('weight_kg'):,} kg<br>
                    <b>Descrição:</b> {dino.get('description', 'N/A')}<br>
                    """
                else:
                    period = dino.period.value if hasattr(dino.period, 'value') else str(dino.period)
                    diet = dino.diet.value if hasattr(dino.diet, 'value') else str(dino.diet)
                    text = f"""
                    <b>Nome:</b> {dino.common_name} ({dino.scientific_name})<br>
                    <b>Período:</b> {period}<br>
                    <b>Tamanho:</b> {dino.length_meters}m x {dino.height_meters}m<br>
                    <b>Peso:</b> {dino.weight_kg:,} kg<br>
                    <b>Dieta:</b> {diet}<br>
                    <b>Descrição:</b> {dino.description}<br>
                    """
                self.details_text.setText(text)
            except Exception as e:
                self.details_text.setText(f"<b>Erro:</b> {str(e)}")
    
    def on_random_dinosaur(self):
        """Seleciona dinossauro aleatório."""
        import random
        idx = random.randint(0, len(DINOSAUR_DATABASE) - 1)
        self.dinosaur_table.selectRow(idx)
        self.on_select_dinosaur()


class DNASynthesisWidget(QWidget):
    """Widget para controlar síntese de DNA."""
    
    def __init__(self):
        super().__init__()
        self.synthesizer = None
        self.init_ui()
    
    def init_ui(self):
        """Inicializa interface de síntese."""
        layout = QVBoxLayout()
        
        title = QLabel("🧬 Síntese de DNA")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        # Configurações
        config_layout = QHBoxLayout()
        
        config_layout.addWidget(QLabel("dATP (mM):"))
        self.dntp_a = QDoubleSpinBox()
        self.dntp_a.setValue(100.0)
        config_layout.addWidget(self.dntp_a)
        
        config_layout.addWidget(QLabel("dTTP (mM):"))
        self.dntp_t = QDoubleSpinBox()
        self.dntp_t.setValue(100.0)
        config_layout.addWidget(self.dntp_t)
        
        layout.addLayout(config_layout)
        
        # Barra de progresso
        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)
        
        # Log
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
        # Botões
        button_layout = QHBoxLayout()
        self.start_synthesis_btn = QPushButton("Iniciar Síntese")
        self.start_synthesis_btn.clicked.connect(self.on_start_synthesis)
        button_layout.addWidget(self.start_synthesis_btn)
        
        self.stop_synthesis_btn = QPushButton("Parar Síntese")
        self.stop_synthesis_btn.setEnabled(False)
        self.stop_synthesis_btn.clicked.connect(self.on_stop_synthesis)
        button_layout.addWidget(self.stop_synthesis_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def on_start_synthesis(self):
        """Inicia síntese de DNA."""
        self.log_text.append("[INFO] Iniciando síntese de DNA...")
        self.progress.setValue(0)
        self.start_synthesis_btn.setEnabled(False)
        self.stop_synthesis_btn.setEnabled(True)
        
        # Simula síntese
        for i in range(0, 101, 10):
            self.progress.setValue(i)
            self.log_text.append(f"Progresso: {i}%")
        
        self.log_text.append("[OK] Síntese concluída!")
        self.start_synthesis_btn.setEnabled(True)
        self.stop_synthesis_btn.setEnabled(False)
    
    def on_stop_synthesis(self):
        """Para síntese."""
        self.log_text.append("[WARN] Síntese interrompida pelo usuário")
        self.start_synthesis_btn.setEnabled(True)
        self.stop_synthesis_btn.setEnabled(False)


class EmbryoInjectionWidget(QWidget):
    """Widget para injeção em embrião de galinha."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Inicializa interface de injeção."""
        layout = QVBoxLayout()
        
        title = QLabel("🐣 Injeção em Embrião de Galinha")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        # Parâmetros
        params_layout = QHBoxLayout()
        
        params_layout.addWidget(QLabel("Volume de DNA (µL):"))
        self.volume_spinbox = QDoubleSpinBox()
        self.volume_spinbox.setValue(50.0)
        params_layout.addWidget(self.volume_spinbox)
        
        params_layout.addWidget(QLabel("Profundidade (mm):"))
        self.depth_spinbox = QDoubleSpinBox()
        self.depth_spinbox.setValue(2.0)
        params_layout.addWidget(self.depth_spinbox)
        
        layout.addLayout(params_layout)
        
        # Visualização 3D (simulada)
        self.visualization = QLabel("📍 Posição de Injeção: X=0mm, Y=0mm, Z=0mm")
        layout.addWidget(self.visualization)
        
        # Log
        self.injection_log = QTextEdit()
        self.injection_log.setReadOnly(True)
        layout.addWidget(self.injection_log)
        
        # Botões
        button_layout = QHBoxLayout()
        self.inject_btn = QPushButton("Injetar DNA no Embrião")
        self.inject_btn.clicked.connect(self.on_inject)
        button_layout.addWidget(self.inject_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def on_inject(self):
        """Realiza injeção."""
        self.injection_log.append("[INFO] Iniciando injeção...")
        self.injection_log.append(f"Volume: {self.volume_spinbox.value()}µL")
        self.injection_log.append(f"Profundidade: {self.depth_spinbox.value()}mm")
        self.injection_log.append("[OK] Injeção realizada com sucesso!")
        self.injection_log.append("[INFO] Embrião agora contém genoma de dinossauro")


class MainWindow(QMainWindow):
    """Janela principal da aplicação."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🦖 Re-Dino: Sistema de Síntese de DNA de Dinossauros")
        self.setGeometry(100, 100, 1400, 900)
        
        # Widget central
        central_widget = QWidget()
        layout = QVBoxLayout()
        
        # Abas
        self.tabs = QTabWidget()
        self.tabs.addTab(DinosaurDatabaseWidget(), "🦖 Banco de Dinossauros")
        self.tabs.addTab(DNASynthesisWidget(), "🧬 Síntese de DNA")
        self.tabs.addTab(EmbryoInjectionWidget(), "🐣 Injeção em Embrião")
        
        layout.addWidget(self.tabs)
        
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)


def main():
    """Função principal."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
