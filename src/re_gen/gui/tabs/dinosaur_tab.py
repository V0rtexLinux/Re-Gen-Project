"""Dinosaur browser tab - explore the species database."""

from __future__ import annotations

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTableWidget, QTableWidgetItem, QComboBox, QPushButton,
    QHeaderView, QTextEdit, QSplitter, QFrame,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class DinosaurBrowserTab(QWidget):
    """Tab for browsing and filtering the dinosaur database."""

    def __init__(self) -> None:
        super().__init__()
        self._all_dinos: list = []
        self._setup_ui()
        self._load_data()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        # Filters
        filter_frame = QFrame()
        filter_frame.setStyleSheet("QFrame { background-color: #313244; border-radius: 6px; padding: 8px; }")
        filter_layout = QHBoxLayout(filter_frame)

        filter_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type species name...")
        self.search_input.textChanged.connect(self._filter_table)
        filter_layout.addWidget(self.search_input)

        filter_layout.addWidget(QLabel("Period:"))
        self.period_filter = QComboBox()
        self.period_filter.addItems(["All", "Triassic", "Jurassic", "Cretaceous"])
        self.period_filter.currentTextChanged.connect(self._filter_table)
        filter_layout.addWidget(self.period_filter)

        filter_layout.addWidget(QLabel("Diet:"))
        self.diet_filter = QComboBox()
        self.diet_filter.addItems(["All", "Herbivore", "Carnivore", "Omnivore"])
        self.diet_filter.currentTextChanged.connect(self._filter_table)
        filter_layout.addWidget(self.diet_filter)

        layout.addWidget(filter_frame)

        # Main content splitter
        splitter = QSplitter(Qt.Horizontal)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["Scientific Name", "Common Name", "Period", "Diet", "Length (m)", "Weight (kg)"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget { alternate-background-color: #1e1e2e; }
            QTableWidget::item { padding: 4px; }
        """)
        self.table.currentCellChanged.connect(self._on_select)
        splitter.addWidget(self.table)

        # Detail panel
        detail_widget = QWidget()
        detail_layout = QVBoxLayout(detail_widget)
        self.detail_title = QLabel("Select a species")
        self.detail_title.setFont(QFont("sans-serif", 16, QFont.Bold))
        self.detail_title.setStyleSheet("color: #f5c2e7;")
        detail_layout.addWidget(self.detail_title)

        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        detail_layout.addWidget(self.detail_text)

        self.run_btn = QPushButton("Run Pipeline for This Species")
        self.run_btn.setMinimumHeight(40)
        detail_layout.addWidget(self.run_btn)

        splitter.addWidget(detail_widget)
        splitter.setSizes([700, 400])

        layout.addWidget(splitter)

        # Count
        self.count_label = QLabel()
        self.count_label.setStyleSheet("color: #6c7086;")
        layout.addWidget(self.count_label)

    def _load_data(self) -> None:
        try:
            from re_gen.data.dinosaur_database import DINOSAUR_DATABASE
            self._all_dinos = list(DINOSAUR_DATABASE)
        except Exception:
            self._all_dinos = []
        self._populate_table(self._all_dinos)

    def _populate_table(self, dinos: list) -> None:
        self.table.setRowCount(len(dinos))
        for row, d in enumerate(dinos):
            name = getattr(d, "scientific_name", "")
            common = getattr(d, "common_name", "")
            period = getattr(d, "period", "")
            if hasattr(period, "value"):
                period = period.value
            diet = getattr(d, "diet", "")
            if hasattr(diet, "value"):
                diet = diet.value
            length = getattr(d, "length_meters", 0)
            weight = getattr(d, "weight_kg", 0)

            self.table.setItem(row, 0, QTableWidgetItem(str(name)))
            self.table.setItem(row, 1, QTableWidgetItem(str(common)))
            self.table.setItem(row, 2, QTableWidgetItem(str(period)))
            self.table.setItem(row, 3, QTableWidgetItem(str(diet)))
            self.table.setItem(row, 4, QTableWidgetItem(f"{length:.1f}"))
            self.table.setItem(row, 5, QTableWidgetItem(f"{weight:,.0f}"))

        self.count_label.setText(f"Showing {len(dinos)} of {len(self._all_dinos)} species")

    def _filter_table(self) -> None:
        text = self.search_input.text().lower()
        period = self.period_filter.currentText().lower()
        diet = self.diet_filter.currentText().lower()

        filtered = []
        for d in self._all_dinos:
            name = str(getattr(d, "scientific_name", "")).lower()
            common = str(getattr(d, "common_name", "")).lower()
            if text and text not in name and text not in common:
                continue
            p = str(getattr(d, "period", "")).lower()
            if period != "all" and period not in p:
                continue
            dt = str(getattr(d, "diet", "")).lower()
            if diet != "all" and diet not in dt:
                continue
            filtered.append(d)
        self._populate_table(filtered)

    def _on_select(self, row: int, _col: int, _prev: int, _prev_col: int) -> None:
        if row < 0:
            return
        name_item = self.table.item(row, 0)
        if not name_item:
            return
        name = name_item.text()

        dino = None
        for d in self._all_dinos:
            if getattr(d, "scientific_name", "") == name:
                dino = d
                break
        if not dino:
            return

        self.detail_title.setText(getattr(dino, "common_name", name))
        lines = [
            f"<b>Scientific name:</b> {getattr(dino, 'scientific_name', '')}",
            f"<b>Period:</b> {getattr(dino, 'period', '')}",
            f"<b>Diet:</b> {getattr(dino, 'diet', '')}",
            f"<b>Length:</b> {getattr(dino, 'length_meters', 0):.1f} m",
            f"<b>Height:</b> {getattr(dino, 'height_meters', 0):.1f} m",
            f"<b>Weight:</b> {getattr(dino, 'weight_kg', 0):,.0f} kg",
            f"<b>Genome size:</b> {getattr(dino, 'genome_size_bp', 0):,} bp",
        ]
        if hasattr(dino, "description") and dino.description:
            lines.append(f"\n<b>Description:</b> {dino.description}")
        self.detail_text.setHtml("<br>".join(lines))
