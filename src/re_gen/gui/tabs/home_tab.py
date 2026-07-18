"""Home tab - Dashboard with project overview and quick actions."""

from __future__ import annotations

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGridLayout, QSizePolicy,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from re_gen import __version__


class _StatCard(QFrame):
    """A styled statistic card."""

    def __init__(self, title: str, value: str, subtitle: str = "") -> None:
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: #313244; border-radius: 8px;
                padding: 16px; margin: 4px;
            }
        """)
        layout = QVBoxLayout(self)
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #6c7086; font-size: 12px; border: none;")
        value_label = QLabel(value)
        value_label.setStyleSheet("color: #f5c2e7; font-size: 28px; font-weight: bold; border: none;")
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        if subtitle:
            sub = QLabel(subtitle)
            sub.setStyleSheet("color: #a6adc8; font-size: 11px; border: none;")
            layout.addWidget(sub)


class HomeTab(QWidget):
    """Home dashboard tab."""

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # Title
        title = QLabel(f"Re-Gen v{__version__}")
        title.setFont(QFont("sans-serif", 24, QFont.Bold))
        title.setStyleSheet("color: #f5c2e7;")
        subtitle = QLabel("Paleontological Genome Reconstruction Pipeline")
        subtitle.setStyleSheet("color: #a6adc8; font-size: 14px;")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        # Stats row
        stats_layout = QHBoxLayout()
        try:
            from re_gen.data.dinosaur_database import DINOSAUR_DATABASE
            n_dinos = len(DINOSAUR_DATABASE)
        except Exception:
            n_dinos = 530

        stats_layout.addWidget(_StatCard("Species in Database", str(n_dinos)))
        stats_layout.addWidget(_StatCard("Pipeline Version", "v3"))
        stats_layout.addWidget(_StatCard("CRISPR Variants", "5"))
        stats_layout.addWidget(_StatCard("Hardware Devices", "11"))
        layout.addLayout(stats_layout)

        # Quick actions
        actions_frame = QFrame()
        actions_frame.setFrameShape(QFrame.StyledPanel)
        actions_frame.setStyleSheet("QFrame { background-color: #313244; border-radius: 8px; padding: 16px; }")
        actions_layout = QVBoxLayout(actions_frame)

        actions_title = QLabel("Quick Actions")
        actions_title.setFont(QFont("sans-serif", 14, QFont.Bold))
        actions_title.setStyleSheet("color: #89b4fa; border: none;")
        actions_layout.addWidget(actions_title)

        btn_layout = QHBoxLayout()
        for text, tooltip in [
            ("Browse Dinosaurs", "Explore the species database"),
            ("Run Pipeline", "Start genome reconstruction"),
            ("Design gRNAs", "CRISPR guide RNA design"),
            ("Hardware Status", "Check connected devices"),
        ]:
            btn = QPushButton(text)
            btn.setToolTip(tooltip)
            btn.setMinimumHeight(40)
            btn_layout.addWidget(btn)
        actions_layout.addLayout(btn_layout)

        layout.addWidget(actions_frame)

        # Info
        info = QLabel(
            "All hardware modules run in simulation mode when devices are not connected. "
            "Install optional dependencies for full functionality:\n"
            "  pip install re-gen[hardware,ai,gui]"
        )
        info.setStyleSheet("color: #6c7086; font-size: 11px; padding: 8px;")
        info.setWordWrap(True)
        layout.addWidget(info)

        layout.addStretch()
