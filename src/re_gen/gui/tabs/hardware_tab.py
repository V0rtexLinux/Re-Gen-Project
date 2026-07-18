"""Hardware monitor tab - display device status and controls."""

from __future__ import annotations

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGridLayout, QProgressBar, QGroupBox, QPlainTextEdit,
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont


class _DeviceCard(QFrame):
    """Card showing status of a single hardware device."""

    def __init__(self, name: str, device_type: str) -> None:
        super().__init__()
        self.device_name = name
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: #313244; border-radius: 8px;
                padding: 12px; margin: 4px;
            }
        """)
        layout = QVBoxLayout(self)

        title = QLabel(name)
        title.setFont(QFont("sans-serif", 12, QFont.Bold))
        title.setStyleSheet("color: #cdd6f4; border: none;")
        layout.addWidget(title)

        self.type_label = QLabel(device_type)
        self.type_label.setStyleSheet("color: #6c7086; font-size: 11px; border: none;")
        layout.addWidget(self.type_label)

        self.status_label = QLabel("Unknown")
        self.status_label.setStyleSheet("color: #f9e2af; font-weight: bold; border: none;")
        layout.addWidget(self.status_label)

        self.sim_label = QLabel("")
        self.sim_label.setStyleSheet("color: #a6adc8; font-size: 10px; border: none;")
        layout.addWidget(self.sim_label)


class HardwareMonitorTab(QWidget):
    """Tab for monitoring hardware device status."""

    def __init__(self) -> None:
        super().__init__()
        self._cards: dict[str, _DeviceCard] = {}
        self._setup_ui()
        self._refresh_status()

        # Auto-refresh every 5 seconds
        self._timer = QTimer()
        self._timer.timeout.connect(self._refresh_status)
        self._timer.start(5000)

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        # Header
        header = QHBoxLayout()
        title = QLabel("Hardware Monitor")
        title.setFont(QFont("sans-serif", 18, QFont.Bold))
        title.setStyleSheet("color: #f5c2e7;")
        header.addWidget(title)
        header.addStretch()

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._refresh_status)
        header.addWidget(refresh_btn)

        stop_btn = QPushButton("Emergency Stop")
        stop_btn.setStyleSheet("QPushButton { background-color: #f38ba8; color: #1e1e2e; }")
        stop_btn.clicked.connect(self._emergency_stop)
        header.addWidget(stop_btn)
        layout.addLayout(header)

        # Mode indicator
        self.mode_label = QLabel("Mode: Simulation (no hardware detected)")
        self.mode_label.setStyleSheet("color: #a6e3a1; font-size: 13px; padding: 8px;")
        layout.addWidget(self.mode_label)

        # Device grid
        self.grid = QGridLayout()
        self.grid.setSpacing(8)

        devices = [
            ("DNA Synthesizer", "RPi PWM + Pumps", "dna_synth"),
            ("Embryo Injection", "RPi Servos XYZ", "embryo_inject"),
            ("Embryo Inject System", "gpiozero + picamera", "embryo_sys"),
            ("Incubator", "Arduino Serial", "incubator"),
            ("Environmental Monitor", "RPi GPIO Sensors", "env_monitor"),
            ("Fossil Grinder", "RPi PWM Motor", "fossil_grind"),
            ("Fossil Cleaner", "RPi GPIO Actuators", "fossil_clean"),
            ("Lab Safety", "Software Only", "lab_safety"),
            ("Vet Syringe", "RPi Servo + Pump", "vet_syringe"),
            ("Arduino Bridge", "USB Serial", "arduino"),
            ("Scanner Input", "File I/O (FASTQ)", "scanner"),
        ]

        for i, (name, dtype, key) in enumerate(devices):
            card = _DeviceCard(name, dtype)
            self._cards[key] = card
            self.grid.addWidget(card, i // 3, i % 3)

        layout.addLayout(self.grid)

        # Log
        log_group = QGroupBox("Device Log")
        log_layout = QVBoxLayout(log_group)
        self.log_text = QPlainTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        log_layout.addWidget(self.log_text)
        layout.addWidget(log_group)

    def _refresh_status(self) -> None:
        has_gpio = False
        has_serial = False
        try:
            import RPi.GPIO  # noqa: F401
            has_gpio = True
        except ImportError:
            pass
        try:
            import serial  # noqa: F401
            has_serial = True
        except ImportError:
            pass

        if has_gpio or has_serial:
            self.mode_label.setText("Mode: Hardware Detected")
            self.mode_label.setStyleSheet("color: #f9e2af; font-size: 13px; padding: 8px;")
        else:
            self.mode_label.setText("Mode: Simulation (no hardware detected)")
            self.mode_label.setStyleSheet("color: #a6e3a1; font-size: 13px; padding: 8px;")

        statuses = {
            "dna_synth": ("Simulation", has_gpio),
            "embryo_inject": ("Requires GPIO", has_gpio),
            "embryo_sys": ("Simulation OK", True),
            "incubator": ("Simulation OK", True),
            "env_monitor": ("Simulation OK", True),
            "fossil_grind": ("Simulation OK", True),
            "fossil_clean": ("Simulation OK", True),
            "lab_safety": ("Always OK", True),
            "vet_syringe": ("Simulation OK", True),
            "arduino": ("Simulation OK", True),
            "scanner": ("Always OK", True),
        }

        for key, card in self._cards.items():
            label, ok = statuses.get(key, ("Unknown", False))
            card.status_label.setText("ACTIVE" if ok else "INACTIVE")
            card.status_label.setStyleSheet(
                f"color: {'#a6e3a1' if ok else '#f38ba8'}; font-weight: bold; border: none;"
            )
            card.sim_label.setText(f"Simulated: {label}")

    def _emergency_stop(self) -> None:
        self.log_text.appendPlainText("[EMERGENCY STOP] All hardware stopped.")
        try:
            from re_gen.hardware.hardware_orchestrator import HardwareOrchestrator
            orch = HardwareOrchestrator()
            orch.emergency_stop()
            self.log_text.appendPlainText("[OK] Emergency stop executed.")
        except Exception as e:
            self.log_text.appendPlainText(f"[WARN] Could not reach orchestrator: {e}")
