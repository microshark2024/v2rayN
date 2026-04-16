"""Option settings dialog view.

Ported from v2rayN GUI option settings dialog.
Provides configuration options for inbound, outbound, TUN, GUI settings.
"""

from __future__ import annotations

from v2rayn.common import logging_config

_tag = "OptionSettingDialog"


def create_option_setting_dialog(viewmodel, parent=None):
    """Create option settings dialog.

    Args:
        viewmodel: OptionSettingViewModel instance
        parent: Parent widget

    Returns:
        Dialog instance
    """
    try:
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import (
            QCheckBox,
            QComboBox,
            QDialog,
            QDialogButtonBox,
            QFormLayout,
            QGroupBox,
            QLineEdit,
            QSpinBox,
            QTabWidget,
            QVBoxLayout,
            QWidget,
        )
    except ImportError:
        logging_config.save_log("PySide6 not installed")
        return None

    class OptionSettingDialog(QDialog):
        """Option settings dialog."""

        def __init__(self, vm, parent_widget=None):
            super().__init__(parent_widget)
            self._vm = vm
            self.setWindowTitle("Option Settings")
            self.setMinimumSize(500, 400)
            self._setup_ui()
            self._load_data()

        def _setup_ui(self):
            """Setup dialog UI."""
            layout = QVBoxLayout(self)
            tabs = QTabWidget()
            layout.addWidget(tabs)

            # Inbound tab
            inbound = QWidget()
            iform = QFormLayout(inbound)

            self._local_address = QLineEdit()
            iform.addRow("Listen Address:", self._local_address)

            self._socks_port = QSpinBox()
            self._socks_port.setRange(0, 65535)
            iform.addRow("SOCKS Port:", self._socks_port)

            self._http_port = QSpinBox()
            self._http_port.setRange(0, 65535)
            iform.addRow("HTTP Port:", self._http_port)

            self._allow_lan = QCheckBox("Allow LAN Access")
            iform.addRow("", self._allow_lan)

            tabs.addTab(inbound, "Inbound")

            # TUN tab
            tun = QWidget()
            tform = QFormLayout(tun)

            self._enable_tun = QCheckBox("Enable TUN Mode")
            tform.addRow("", self._enable_tun)

            self._tun_stack = QComboBox()
            self._tun_stack.addItems(["system", "gvisor", "mixed"])
            tform.addRow("Stack:", self._tun_stack)

            tabs.addTab(tun, "TUN")

            # GUI tab
            gui = QWidget()
            gform = QFormLayout(gui)

            self._auto_run = QCheckBox("Auto Start on Login")
            gform.addRow("", self._auto_run)

            self._enable_statistics = QCheckBox("Enable Statistics")
            gform.addRow("", self._enable_statistics)

            tabs.addTab(gui, "GUI")

            # Buttons
            buttons = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
            )
            buttons.accepted.connect(self._save_and_close)
            buttons.rejected.connect(self.reject)
            layout.addWidget(buttons)

        def _load_data(self):
            """Load current settings."""
            self._local_address.setText(self._vm.local_address)
            self._socks_port.setValue(self._vm.socks_port)
            self._http_port.setValue(self._vm.http_port)
            self._allow_lan.setChecked(self._vm.allow_lan)
            self._enable_tun.setChecked(self._vm.enable_tun)
            self._auto_run.setChecked(self._vm.auto_run)
            self._enable_statistics.setChecked(self._vm.enable_statistics)

            idx = self._tun_stack.findText(self._vm.tun_stack)
            if idx >= 0:
                self._tun_stack.setCurrentIndex(idx)

        def _save_and_close(self):
            """Save settings and close."""
            self._vm.local_address = self._local_address.text()
            self._vm.socks_port = self._socks_port.value()
            self._vm.http_port = self._http_port.value()
            self._vm.allow_lan = self._allow_lan.isChecked()
            self._vm.enable_tun = self._enable_tun.isChecked()
            self._vm.tun_stack = self._tun_stack.currentText()
            self._vm.auto_run = self._auto_run.isChecked()
            self._vm.enable_statistics = self._enable_statistics.isChecked()

            if self._vm.save():
                self.accept()

    return OptionSettingDialog(viewmodel, parent)
