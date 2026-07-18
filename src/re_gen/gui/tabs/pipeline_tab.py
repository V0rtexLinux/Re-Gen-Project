"""Pipeline tab - run v2 or v3 genome reconstruction pipelines."""

from __future__ import annotations

import threading
from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QTextEdit, QProgressBar, QSpinBox,
    QFrame, QGroupBox, QFormLayout, QCheckBox,
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject


class _WorkerSignals(QObject):
    """Signals for pipeline worker thread."""
    log = pyqtSignal(str)
    progress = pyqtSignal(int)
    finished = pyqtSignal(int, str)


class _PipelineWorker(threading.Thread):
    """Run pipeline in background thread."""

    def __init__(self, signals: _WorkerSignals, mode: str, params: dict) -> None:
        super().__init__(daemon=True)
        self.signals = signals
        self.mode = mode
        self.params = params

    def run(self) -> None:
        try:
            import sys
            from io import StringIO

            old_stdout = sys.stdout
            sys.stdout = captured = StringIO()

            if self.mode == "v2":
                sys.argv = ["re-gen", "v2"] + self._build_v2_args()
                from re_gen.pipeline.main import main as v2_main
                result = v2_main()
            else:
                sys.argv = ["re-gen", "v3"] + self._build_v3_args()
                from re_gen.pipeline.main_v3 import main as v3_main
                result = v3_main()

            sys.stdout = old_stdout
            output = captured.getvalue()
            self.signals.log.emit(output)
            self.signals.finished.emit(result, "Success" if result == 0 else f"Exit code: {result}")
        except Exception as e:
            sys.stdout = old_stdout
            self.signals.log.emit(f"ERROR: {e}")
            self.signals.finished.emit(1, str(e))

    def _build_v2_args(self) -> list[str]:
        args = []
        if self.params.get("gene"):
            args += ["--gene", self.params["gene"]]
        if self.params.get("host"):
            args += ["--host-species", self.params["host"]]
        if self.params.get("email"):
            args += ["--ncbi-email", self.params["email"]]
        if self.params.get("dinosaur"):
            args += ["--dinosaur", self.params["dinosaur"]]
        if self.params.get("ai_report"):
            args += ["--gerar-relatorio-ia"]
        return args

    def _build_v3_args(self) -> list[str]:
        args = []
        if self.params.get("species"):
            args += ["--species", self.params["species"]]
        if self.params.get("email"):
            args += ["--ncbi-email", self.params["email"]]
        if self.params.get("genome_size"):
            args += ["--genome-size", str(self.params["genome_size"])]
        if self.params.get("chunk_size"):
            args += ["--chunk-size", str(self.params["chunk_size"])]
        if self.params.get("ai"):
            args += ["--use-ai-orchestration"]
        if self.params.get("model"):
            args += ["--modelo-ollama", self.params["model"]]
        return args


class PipelineTab(QWidget):
    """Tab for running genome reconstruction pipelines."""

    def __init__(self) -> None:
        super().__init__()
        self._worker: _PipelineWorker | None = None
        self._signals = _WorkerSignals()
        self._signals.log.connect(self._append_log)
        self._signals.finished.connect(self._on_finished)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        # Pipeline selector
        top = QHBoxLayout()
        top.addWidget(QLabel("Pipeline:"))
        self.pipeline_combo = QComboBox()
        self.pipeline_combo.addItems(["v3 - AI-Orchestrated Synthesis", "v2 - Reference Search + CRISPR"])
        self.pipeline_combo.currentIndexChanged.connect(self._toggle_params)
        top.addWidget(self.pipeline_combo)
        top.addStretch()
        layout.addLayout(top)

        # V3 params
        self.v3_group = QGroupBox("Pipeline v3 Parameters")
        v3_form = QFormLayout(self.v3_group)
        self.species_input = QLineEdit()
        self.species_input.setPlaceholderText("e.g. Tyrannosaurus rex")
        v3_form.addRow("Species:", self.species_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("your.email@example.com")
        v3_form.addRow("NCBI Email:", self.email_input)

        self.genome_size_spin = QSpinBox()
        self.genome_size_spin.setRange(1_000_000, 100_000_000_000)
        self.genome_size_spin.setValue(3_000_000_000)
        self.genome_size_spin.setSingleStep(100_000_000)
        v3_form.addRow("Genome Size (bp):", self.genome_size_spin)

        self.chunk_size_spin = QSpinBox()
        self.chunk_size_spin.setRange(10_000, 10_000_000)
        self.chunk_size_spin.setValue(100_000)
        self.chunk_size_spin.setSingleStep(10_000)
        v3_form.addRow("Chunk Size (bp):", self.chunk_size_spin)

        self.ai_checkbox = QCheckBox("Enable AI Orchestration")
        v3_form.addRow("", self.ai_checkbox)

        self.model_input = QLineEdit("mistral")
        v3_form.addRow("Ollama Model:", self.model_input)

        layout.addWidget(self.v3_group)

        # V2 params (hidden by default)
        self.v2_group = QGroupBox("Pipeline v2 Parameters")
        v2_form = QFormLayout(self.v2_group)
        self.gene_input = QLineEdit()
        self.gene_input.setPlaceholderText("e.g. cytochrome b")
        v2_form.addRow("Gene:", self.gene_input)

        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("e.g. Struthio camelus")
        v2_form.addRow("Host Species:", self.host_input)

        self.v2_email_input = QLineEdit()
        self.v2_email_input.setPlaceholderText("your.email@example.com")
        v2_form.addRow("NCBI Email:", self.v2_email_input)

        self.dinosaur_input = QLineEdit()
        self.dinosaur_input.setPlaceholderText("e.g. Tyrannosaurus rex")
        v2_form.addRow("Dinosaur:", self.dinosaur_input)

        self.ai_report_checkbox = QCheckBox("Generate AI Report (requires Ollama)")
        v2_form.addRow("", self.ai_report_checkbox)

        self.v2_group.setVisible(False)
        layout.addWidget(self.v2_group)

        # Controls
        ctrl = QHBoxLayout()
        self.run_btn = QPushButton("Run Pipeline")
        self.run_btn.setMinimumHeight(40)
        self.run_btn.clicked.connect(self._run_pipeline)
        ctrl.addWidget(self.run_btn)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setMinimumHeight(40)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._stop_pipeline)
        ctrl.addWidget(self.stop_btn)
        ctrl.addStretch()
        layout.addLayout(ctrl)

        # Progress
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # indeterminate
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        # Output log
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        # Status
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #a6e3a1; font-weight: bold;")
        layout.addWidget(self.status_label)

    def _toggle_params(self, index: int) -> None:
        self.v3_group.setVisible(index == 0)
        self.v2_group.setVisible(index == 1)

    def _run_pipeline(self) -> None:
        self.output.clear()
        self.progress.setVisible(True)
        self.run_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_label.setText("Running...")
        self.status_label.setStyleSheet("color: #f9e2af; font-weight: bold;")

        self._append_log(f"[{datetime.now():%H:%M:%S}] Pipeline started\n")

        params = {}
        if self.pipeline_combo.currentIndex() == 0:
            mode = "v3"
            params = {
                "species": self.species_input.text(),
                "email": self.email_input.text(),
                "genome_size": self.genome_size_spin.value(),
                "chunk_size": self.chunk_size_spin.value(),
                "ai": self.ai_checkbox.isChecked(),
                "model": self.model_input.text(),
            }
        else:
            mode = "v2"
            params = {
                "gene": self.gene_input.text(),
                "host": self.host_input.text(),
                "email": self.v2_email_input.text(),
                "dinosaur": self.dinosaur_input.text(),
                "ai_report": self.ai_report_checkbox.isChecked(),
            }

        self._worker = _PipelineWorker(self._signals, mode, params)
        self._worker.start()

    def _stop_pipeline(self) -> None:
        if self._worker and self._worker.is_alive():
            self._append_log("\n[STOP] Pipeline stopped by user\n")
            self._on_finished(1, "Stopped")

    def _append_log(self, text: str) -> None:
        self.output.append(text)

    def _on_finished(self, code: int, msg: str) -> None:
        self.progress.setVisible(False)
        self.run_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        if code == 0:
            self.status_label.setText(f"Completed: {msg}")
            self.status_label.setStyleSheet("color: #a6e3a1; font-weight: bold;")
        else:
            self.status_label.setText(f"Failed: {msg}")
            self.status_label.setStyleSheet("color: #f38ba8; font-weight: bold;")
        self._append_log(f"\n[{datetime.now():%H:%M:%S}] Pipeline finished (code={code}): {msg}\n")
