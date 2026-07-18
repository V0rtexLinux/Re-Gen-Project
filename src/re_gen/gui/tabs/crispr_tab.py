"""CRISPR design tab - design guide RNAs interactively."""

from __future__ import annotations

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QSpinBox, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QFormLayout, QGroupBox, QSplitter,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class CRISPRDesignTab(QWidget):
    """Tab for interactive CRISPR gRNA design."""

    def __init__(self) -> None:
        super().__init__()
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        splitter = QSplitter(Qt.Vertical)

        # Input section
        input_frame = QFrame()
        input_layout = QVBoxLayout(input_frame)

        input_title = QLabel("CRISPR gRNA Designer")
        input_title.setFont(QFont("sans-serif", 16, QFont.Bold))
        input_title.setStyleSheet("color: #f5c2e7;")
        input_layout.addWidget(input_title)

        form = QFormLayout()
        self.variant_combo = QComboBox()
        self.variant_combo.addItems(["SpCas9 (NGG)", "Cpf1/Cas12a (TTN)", "FnCas9 (YG)"])
        form.addRow("Cas9 Variant:", self.variant_combo)

        self.num_grnas_spin = QSpinBox()
        self.num_grnas_spin.setRange(1, 50)
        self.num_grnas_spin.setValue(10)
        form.addRow("Number of gRNAs:", self.num_grnas_spin)

        self.start_spin = QSpinBox()
        self.start_spin.setRange(0, 999999)
        form.addRow("Region Start:", self.start_spin)

        self.end_spin = QSpinBox()
        self.end_spin.setRange(0, 999999)
        self.end_spin.setValue(1000)
        form.addRow("Region End:", self.end_spin)
        input_layout.addLayout(form)

        input_layout.addWidget(QLabel("Target Sequence (DNA):"))
        self.seq_input = QTextEdit()
        self.seq_input.setMaximumHeight(100)
        self.seq_input.setPlaceholderText("Paste DNA sequence here (ATCG only)...")
        input_layout.addWidget(self.seq_input)

        btn_layout = QHBoxLayout()
        self.design_btn = QPushButton("Design gRNAs")
        self.design_btn.setMinimumHeight(36)
        self.design_btn.clicked.connect(self._design)
        btn_layout.addWidget(self.design_btn)
        btn_layout.addStretch()
        input_layout.addLayout(btn_layout)

        splitter.addWidget(input_frame)

        # Results
        results_frame = QFrame()
        results_layout = QVBoxLayout(results_frame)

        results_title = QLabel("Results")
        results_title.setFont(QFont("sans-serif", 14, QFont.Bold))
        results_title.setStyleSheet("color: #89b4fa;")
        results_layout.addWidget(results_title)

        self.results_table = QTableWidget()
        self.results_table.setColumnCount(8)
        self.results_table.setHorizontalHeaderLabels([
            "#", "Sequence (20bp)", "PAM", "Position", "GC%", "Specificity", "Efficiency", "Quality"
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.results_table.setAlternatingRowColors(True)
        results_layout.addWidget(self.results_table)

        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setMaximumHeight(120)
        results_layout.addWidget(self.detail_text)

        splitter.addWidget(results_frame)
        splitter.setSizes([300, 400])

        layout.addWidget(splitter)

    def _design(self) -> None:
        sequence = self.seq_input.toPlainText().strip().upper()
        if not sequence:
            self.detail_text.setText("Please enter a DNA sequence.")
            return

        # Map combo to variant
        variant_map = {
            0: "SPCAS9",
            1: "CPFCAS9",
            2: "FNCAS9",
        }
        from re_gen.core.crispr_engine import CRISPRDesigner, Cas9Variant

        variant_name = variant_map.get(self.variant_combo.currentIndex(), "SPCAS9")
        variant = Cas9Variant[variant_name]
        designer = CRISPRDesigner(variant=variant)

        region_start = self.start_spin.value()
        region_end = min(self.end_spin.value(), len(sequence))
        num = self.num_grnas_spin.value()

        grnas = designer.find_grnas(
            sequence,
            region_start=region_start,
            region_end=region_end,
            num_grnas=num,
        )

        self.results_table.setRowCount(len(grnas))
        for row, g in enumerate(grnas):
            self.results_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.results_table.setItem(row, 1, QTableWidgetItem(g.sequence))
            self.results_table.setItem(row, 2, QTableWidgetItem(g.pam))
            self.results_table.setItem(row, 3, QTableWidgetItem(str(g.position)))
            self.results_table.setItem(row, 4, QTableWidgetItem(f"{g.gc_content:.1f}"))
            self.results_table.setItem(row, 5, QTableWidgetItem(f"{g.specificity_score:.1f}"))
            self.results_table.setItem(row, 6, QTableWidgetItem(f"{g.efficiency_score:.1f}"))
            quality = "GOOD" if g.is_good else "FAIR"
            self.results_table.setItem(row, 7, QTableWidgetItem(quality))

        good = sum(1 for g in grnas if g.is_good)
        self.detail_text.setText(
            f"Found {len(grnas)} gRNAs ({good} good quality). "
            f"Using {variant.value[1]} with PAM: {variant.value[0]}"
        )
