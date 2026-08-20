#!/usr/bin/env python3
"""Re-Gen GUI - Main application window with tabbed interface."""

from __future__ import annotations

import sys
import logging
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QLabel,
    QStatusBar,
    QMenuBar,
    QMenu,
    QAction,
    QMessageBox,
    QSplashScreen,
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPixmap, QIcon

from re_gen import __version__

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window with tabbed interface."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"Re-Gen v{__version__} - Paleontological Genome Reconstruction")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)

        self._setup_menu()
        self._setup_tabs()
        self._setup_statusbar()

    def _setup_menu(self) -> None:
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")
        file_menu.addAction("Export Report...", self._export_report)
        file_menu.addSeparator()
        quit_action = QAction("&Quit", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # Pipeline menu
        pipeline_menu = menubar.addMenu("&Pipeline")
        pipeline_menu.addAction("Run v2 Pipeline", self._run_v2)
        pipeline_menu.addAction("Run v3 Pipeline", self._run_v3)

        # Hardware menu
        hw_menu = menubar.addMenu("&Hardware")
        hw_menu.addAction("Hardware Status", self._show_hw_status)
        hw_menu.addAction("Emergency Stop", self._emergency_stop)

        # Help menu
        help_menu = menubar.addMenu("&Help")
        help_menu.addAction("About", self._show_about)

    def _setup_tabs(self) -> None:
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Lazy import tabs to avoid circular imports
        from re_gen.gui.tabs.home_tab import HomeTab
        from re_gen.gui.tabs.dinosaur_tab import DinosaurBrowserTab
        from re_gen.gui.tabs.pipeline_tab import PipelineTab
        from re_gen.gui.tabs.crispr_tab import CRISPRDesignTab
        from re_gen.gui.tabs.hardware_tab import HardwareMonitorTab
        from re_gen.gui.tabs.log_tab import LogTab

        self.tabs.addTab(HomeTab(), "Home")
        self.tabs.addTab(DinosaurBrowserTab(), "Dinosaurs")
        self.tabs.addTab(PipelineTab(), "Pipeline")
        self.tabs.addTab(CRISPRDesignTab(), "CRISPR")
        self.tabs.addTab(HardwareMonitorTab(), "Hardware")
        self.tabs.addTab(LogTab(), "Logs")

    def _setup_statusbar(self) -> None:
        self.statusBar().showMessage(f"Re-Gen v{__version__} Ready")

    def _export_report(self) -> None:
        QMessageBox.information(self, "Export", "Export functionality coming soon.")

    def _run_v2(self) -> None:
        self.tabs.setCurrentIndex(2)
        QMessageBox.information(self, "Pipeline v2", "Switch to Pipeline tab and select v2 mode.")

    def _run_v3(self) -> None:
        self.tabs.setCurrentIndex(2)
        QMessageBox.information(self, "Pipeline v3", "Switch to Pipeline tab and select v3 mode.")

    def _show_hw_status(self) -> None:
        self.tabs.setCurrentIndex(4)

    def _emergency_stop(self) -> None:
        reply = QMessageBox.warning(
            self,
            "Emergency Stop",
            "This will stop all hardware operations immediately.\nContinue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            try:
                from re_gen.hardware.hardware_orchestrator import HardwareOrchestrator
                orch = HardwareOrchestrator()
                orch.emergency_stop()
                self.statusBar().showMessage("EMERGENCY STOP executed")
            except Exception as e:
                self.statusBar().showMessage(f"Stop failed: {e}")

    def _show_about(self) -> None:
        QMessageBox.about(
            self,
            "About Re-Gen",
            f"<h2>Re-Gen v{__version__}</h2>"
            "<p>Paleontological Genome Reconstruction Pipeline</p>"
            "<p>Ancestral sequence reconstruction, CRISPR design,<br>"
            "and phylogenetic bracketing for de-extinction research.</p>"
            "<p>License: MIT</p>",
        )


def run_gui() -> int:
    """Launch the GUI application."""
    app = QApplication(sys.argv)
    app.setApplicationName("Re-Gen")
    app.setApplicationVersion(__version__)

    # Dark theme
    app.setStyleSheet("""
        QMainWindow { background-color: #1e1e2e; }
        QTabWidget::pane { border: 1px solid #45475a; background-color: #1e1e2e; }
        QTabBar::tab {
            background-color: #313244; color: #cdd6f4;
            padding: 8px 20px; margin-right: 2px; border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        QTabBar::tab:selected { background-color: #45475a; color: #f5c2e7; }
        QTabBar::tab:hover { background-color: #585b70; }
        QLabel { color: #cdd6f4; }
        QPushButton {
            background-color: #89b4fa; color: #1e1e2e; border: none;
            padding: 8px 16px; border-radius: 4px; font-weight: bold;
        }
        QPushButton:hover { background-color: #b4befe; }
        QPushButton:pressed { background-color: #74c7ec; }
        QPushButton:disabled { background-color: #45475a; color: #6c7086; }
        QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
            background-color: #313244; color: #cdd6f4; border: 1px solid #45475a;
            padding: 6px; border-radius: 4px;
        }
        QTextEdit, QPlainTextEdit {
            background-color: #181825; color: #a6e3a1; border: 1px solid #45475a;
            font-family: 'JetBrains Mono', 'Fira Code', monospace; font-size: 12px;
        }
        QTableWidget {
            background-color: #181825; color: #cdd6f4;
            gridline-color: #313244; border: 1px solid #45475a;
        }
        QTableWidget::item:selected { background-color: #45475a; }
        QHeaderView::section { background-color: #313244; color: #cdd6f4; padding: 4px; }
        QProgressBar {
            border: 1px solid #45475a; border-radius: 4px; text-align: center;
            background-color: #313244; color: #cdd6f4;
        }
        QProgressBar::chunk { background-color: #a6e3a1; border-radius: 3px; }
        QScrollBar:vertical { background-color: #1e1e2e; width: 12px; }
        QScrollBar::handle:vertical { background-color: #45475a; border-radius: 6px; min-height: 20px; }
        QStatusBar { background-color: #181825; color: #6c7086; }
        QMenuBar { background-color: #181825; color: #cdd6f4; }
        QMenuBar::item:selected { background-color: #45475a; }
        QMenu { background-color: #1e1e2e; color: #cdd6f4; }
        QMenu::item:selected { background-color: #45475a; }
    """)

    window = MainWindow()
    window.show()
    return app.exec_()
