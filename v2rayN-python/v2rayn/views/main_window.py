"""Main window view.

Ported from v2rayN GUI main window.
Uses PySide6 for the Qt6 GUI.
"""

from __future__ import annotations

import asyncio
import sys
from typing import Any

from v2rayn.common import logging_config

_tag = "MainWindow"


def create_main_window():
    """Create and return the main application window.

    Returns PySide6 QMainWindow instance.
    """
    try:
        from PySide6.QtCore import QSize, Qt, Signal
        from PySide6.QtGui import QAction, QIcon
        from PySide6.QtWidgets import (
            QApplication,
            QHBoxLayout,
            QHeaderView,
            QLabel,
            QMainWindow,
            QMenu,
            QMenuBar,
            QSplitter,
            QStatusBar,
            QSystemTrayIcon,
            QTableWidget,
            QTableWidgetItem,
            QTabWidget,
            QToolBar,
            QVBoxLayout,
            QWidget,
        )
    except ImportError:
        logging_config.save_log("PySide6 not installed. Run: pip install PySide6")
        return None

    class MainWindow(QMainWindow):
        """Main application window."""

        def __init__(self):
            super().__init__()
            self.setWindowTitle("v2rayN")
            self.setMinimumSize(QSize(900, 600))

            self._setup_menu_bar()
            self._setup_toolbar()
            self._setup_central_widget()
            self._setup_status_bar()
            self._setup_tray_icon()

        def _setup_menu_bar(self):
            """Setup menu bar."""
            menu_bar = self.menuBar()

            # Server menu
            server_menu = menu_bar.addMenu("&Server")
            server_menu.addAction("Add VMess Server")
            server_menu.addAction("Add VLESS Server")
            server_menu.addAction("Add Shadowsocks Server")
            server_menu.addAction("Add SOCKS Server")
            server_menu.addAction("Add Trojan Server")
            server_menu.addAction("Add Hysteria2 Server")
            server_menu.addAction("Add TUIC Server")
            server_menu.addAction("Add WireGuard Server")
            server_menu.addSeparator()
            server_menu.addAction("Import from Clipboard")
            server_menu.addAction("Import from File")
            server_menu.addAction("Export to Clipboard")
            server_menu.addSeparator()
            server_menu.addAction("Remove Selected")
            server_menu.addAction("Remove Duplicates")

            # Subscription menu
            sub_menu = menu_bar.addMenu("S&ubscription")
            sub_menu.addAction("Subscription Settings")
            sub_menu.addAction("Update All Subscriptions")
            sub_menu.addAction("Update Selected Subscription")

            # Setting menu
            setting_menu = menu_bar.addMenu("Se&tting")
            setting_menu.addAction("Option Settings")
            setting_menu.addAction("Routing Settings")
            setting_menu.addAction("DNS Settings")
            setting_menu.addAction("Reboot as Admin")

            # Check update menu
            update_menu = menu_bar.addMenu("Check &Update")
            update_menu.addAction("Update v2rayN")
            update_menu.addAction("Update Xray Core")
            update_menu.addAction("Update Sing-box Core")
            update_menu.addAction("Update Mihomo Core")
            update_menu.addAction("Update Geo Files")

            # Help menu
            help_menu = menu_bar.addMenu("&Help")
            help_menu.addAction("Telegram Channel")
            help_menu.addAction("GitHub Repository")
            help_menu.addAction("About")

        def _setup_toolbar(self):
            """Setup toolbar."""
            toolbar = QToolBar("Main Toolbar")
            self.addToolBar(toolbar)

            toolbar.addAction("Connect")
            toolbar.addAction("Disconnect")
            toolbar.addSeparator()
            toolbar.addAction("Speed Test")
            toolbar.addAction("Real Ping")
            toolbar.addSeparator()
            toolbar.addAction("Clear Proxy")
            toolbar.addAction("Set Proxy")
            toolbar.addAction("PAC Proxy")

        def _setup_central_widget(self):
            """Setup central widget with profile table and tabs."""
            central = QWidget()
            self.setCentralWidget(central)
            layout = QVBoxLayout(central)

            # Main splitter
            splitter = QSplitter(Qt.Orientation.Vertical)
            layout.addWidget(splitter)

            # Profile table
            self._profile_table = QTableWidget()
            self._profile_table.setColumnCount(9)
            self._profile_table.setHorizontalHeaderLabels(
                [
                    "Type",
                    "Remarks",
                    "Address",
                    "Port",
                    "Network",
                    "TLS",
                    "Subscription",
                    "Delay",
                    "Speed",
                ]
            )
            self._profile_table.setSelectionBehavior(
                QTableWidget.SelectionBehavior.SelectRows
            )
            self._profile_table.setSelectionMode(
                QTableWidget.SelectionMode.ExtendedSelection
            )
            header = self._profile_table.horizontalHeader()
            if header:
                header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
                header.setStretchLastSection(True)
            splitter.addWidget(self._profile_table)

            # Bottom tabs
            tab_widget = QTabWidget()

            # Log tab
            self._log_text = QLabel("Ready")
            tab_widget.addTab(self._log_text, "Log")

            # Clash Proxies tab
            self._clash_proxies = QLabel("Clash Proxies")
            tab_widget.addTab(self._clash_proxies, "Clash Proxies")

            # Clash Connections tab
            self._clash_connections = QLabel("Clash Connections")
            tab_widget.addTab(self._clash_connections, "Clash Connections")

            splitter.addWidget(tab_widget)
            splitter.setSizes([400, 200])

        def _setup_status_bar(self):
            """Setup status bar."""
            status_bar = QStatusBar()
            self.setStatusBar(status_bar)

            self._status_label = QLabel("Ready")
            status_bar.addWidget(self._status_label, 1)

            self._proxy_type_label = QLabel("Proxy: Clear")
            status_bar.addPermanentWidget(self._proxy_type_label)

            self._rule_mode_label = QLabel("Rule: Rule")
            status_bar.addPermanentWidget(self._rule_mode_label)

            self._speed_label = QLabel("")
            status_bar.addPermanentWidget(self._speed_label)

        def _setup_tray_icon(self):
            """Setup system tray icon."""
            self._tray_icon = QSystemTrayIcon(self)
            self._tray_icon.setToolTip("v2rayN")

            tray_menu = QMenu()
            tray_menu.addAction("Show")
            tray_menu.addSeparator()
            tray_menu.addAction("Connect")
            tray_menu.addAction("Disconnect")
            tray_menu.addSeparator()
            tray_menu.addAction("Clear Proxy")
            tray_menu.addAction("Set Proxy")
            tray_menu.addSeparator()
            tray_menu.addAction("Exit")

            self._tray_icon.setContextMenu(tray_menu)
            self._tray_icon.show()

            self._tray_icon.activated.connect(self._tray_activated)

        def _tray_activated(self, reason):
            """Handle tray icon activation."""
            from PySide6.QtWidgets import QSystemTrayIcon

            if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
                self.show()
                self.activateWindow()

        def update_profile_list(self, profiles: list[dict[str, Any]]):
            """Update the profile table with new data."""
            self._profile_table.setRowCount(len(profiles))
            for row, profile in enumerate(profiles):
                self._profile_table.setItem(
                    row, 0, QTableWidgetItem(str(profile.get("config_type", "")))
                )
                self._profile_table.setItem(
                    row, 1, QTableWidgetItem(str(profile.get("remarks", "")))
                )
                self._profile_table.setItem(
                    row, 2, QTableWidgetItem(str(profile.get("address", "")))
                )
                self._profile_table.setItem(
                    row, 3, QTableWidgetItem(str(profile.get("port", "")))
                )
                self._profile_table.setItem(
                    row, 4, QTableWidgetItem(str(profile.get("network", "")))
                )
                self._profile_table.setItem(
                    row, 5, QTableWidgetItem(str(profile.get("tls", "")))
                )
                self._profile_table.setItem(
                    row, 6, QTableWidgetItem(str(profile.get("subid", "")))
                )
                delay = profile.get("delay", 0)
                delay_text = f"{delay}ms" if delay > 0 else ("-" if delay < 0 else "")
                self._profile_table.setItem(
                    row, 7, QTableWidgetItem(delay_text)
                )
                self._profile_table.setItem(
                    row, 8, QTableWidgetItem(str(profile.get("speed", "")))
                )

        def update_status(self, text: str):
            """Update status bar text."""
            self._status_label.setText(text)

        def closeEvent(self, event):
            """Handle window close - hide to tray instead."""
            event.ignore()
            self.hide()

    return MainWindow()
