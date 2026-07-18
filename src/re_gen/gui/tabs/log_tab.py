"""Log tab - view application and pipeline logs."""

from __future__ import annotations

import logging
import sys
from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPlainTextEdit,
    QPushButton, QComboBox, QCheckBox, QFrame,
)
from PyQt5.QtCore import Qt


class _LogHandler(logging.Handler):
    """Logging handler that emits to a QPlainTextEdit widget."""

    def __init__(self, widget: QPlainTextEdit) -> None:
        super().__init__()
        self.widget = widget

    def emit(self, record: logging.LogRecord) -> None:
        msg = self.format(record)
        self.widget.appendPlainText(msg)


class LogTab(QWidget):
    """Tab for viewing application logs."""

    def __init__(self) -> None:
        super().__init__()
        self._setup_ui()
        self._setup_log_capture()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        # Controls
        ctrl = QHBoxLayout()
        self.level_combo = QComboBox()
        self.level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.level_combo.setCurrentText("INFO")
        self.level_combo.currentTextChanged.connect(self._set_level)
        ctrl.addWidget(QLabel("Level:"))
        ctrl.addWidget(self.level_combo)

        self.auto_scroll = QCheckBox("Auto-scroll")
        self.auto_scroll.setChecked(True)
        ctrl.addWidget(self.auto_scroll)

        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(lambda: self.log_text.clear())
        ctrl.addWidget(clear_btn)

        export_btn = QPushButton("Export")
        export_btn.clicked.connect(self._export_log)
        ctrl.addWidget(export_btn)

        ctrl.addStretch()
        layout.addLayout(ctrl)

        # Log display
        self.log_text = QPlainTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setLineWrapMode(QPlainTextEdit.NoWrap)
        layout.addWidget(self.log_text)

        # Stdout/stderr capture
        self.stdout_text = QPlainTextEdit()
        self.stdout_text.setReadOnly(True)
        self.stdout_text.setMaximumHeight(150)
        self.stdout_text.setPlaceholderText("Captured stdout will appear here...")
        layout.addWidget(self.stdout_text)

    def _setup_log_capture(self) -> None:
        handler = _LogHandler(self.log_text)
        handler.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%H:%M:%S",
        ))
        logging.root.addHandler(handler)

        # Capture stdout
        _original_stdout = sys.stdout

        class _StdoutCapture:
            def __init__(self, original, widget):
                self.original = original
                self.widget = widget

            def write(self, text: str) -> None:
                if text.strip():
                    self.widget.appendPlainText(text.rstrip())
                self.original.write(text)

            def flush(self) -> None:
                self.original.flush()

        sys.stdout = _StdoutCapture(_original_stdout, self.stdout_text)  # type: ignore[assignment]

    def _set_level(self, level: str) -> None:
        logging.root.setLevel(getattr(logging, level, logging.INFO))

    def _export_log(self) -> None:
        from PyQt5.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Log", f"re_gen_log_{datetime.now():%Y%m%d_%H%M%S}.txt",
            "Text Files (*.txt)",
        )
        if path:
            with open(path, "w") as f:
                f.write(self.log_text.toPlainText())
