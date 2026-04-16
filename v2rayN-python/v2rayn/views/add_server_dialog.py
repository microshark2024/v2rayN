"""Server add/edit dialog views.

Ported from v2rayN GUI server dialogs.
Provides dialogs for adding/editing proxy server configurations.
"""

from __future__ import annotations

from typing import Any

from v2rayn.common import logging_config
from v2rayn.enums.config_type import EConfigType
from v2rayn.models.profile_item import ProfileItem, ProtocolExtraItem

_tag = "AddServerDialog"


def create_add_server_dialog(config_type: EConfigType, parent=None, item: ProfileItem | None = None):
    """Create server add/edit dialog.

    Args:
        config_type: Server protocol type
        parent: Parent widget
        item: Existing item to edit (None for new)

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
            QTextEdit,
            QVBoxLayout,
            QWidget,
        )
    except ImportError:
        logging_config.save_log("PySide6 not installed")
        return None

    class AddServerDialog(QDialog):
        """Server add/edit dialog."""

        def __init__(self, cfg_type: EConfigType, parent_widget=None, profile_item=None):
            super().__init__(parent_widget)
            self._config_type = cfg_type
            self._item = profile_item or ProfileItem()
            self._item.config_type = cfg_type

            self.setWindowTitle(f"Add {cfg_type.name} Server")
            self.setMinimumWidth(500)
            self._setup_ui()
            self._load_data()

        def _setup_ui(self):
            """Setup dialog UI."""
            layout = QVBoxLayout(self)

            tabs = QTabWidget()
            layout.addWidget(tabs)

            # General tab
            general = QWidget()
            form = QFormLayout(general)

            self._remarks = QLineEdit()
            form.addRow("Remarks:", self._remarks)

            self._address = QLineEdit()
            form.addRow("Address:", self._address)

            self._port = QSpinBox()
            self._port.setRange(1, 65535)
            self._port.setValue(443)
            form.addRow("Port:", self._port)

            self._password = QLineEdit()
            form.addRow("Password/UUID:", self._password)

            # Type-specific fields
            if self._config_type == EConfigType.VMess:
                self._alter_id = QSpinBox()
                self._alter_id.setRange(0, 65535)
                form.addRow("Alter ID:", self._alter_id)

                self._security = QComboBox()
                self._security.addItems(["auto", "aes-128-gcm", "chacha20-poly1305", "none", "zero"])
                form.addRow("Security:", self._security)

            elif self._config_type == EConfigType.Shadowsocks:
                self._method = QComboBox()
                self._method.addItems([
                    "aes-256-gcm", "aes-128-gcm", "chacha20-ietf-poly1305",
                    "2022-blake3-aes-256-gcm", "2022-blake3-aes-128-gcm",
                    "2022-blake3-chacha20-poly1305",
                ])
                form.addRow("Method:", self._method)

            elif self._config_type == EConfigType.VLESS:
                self._encryption = QComboBox()
                self._encryption.addItems(["none"])
                form.addRow("Encryption:", self._encryption)

                self._flow = QComboBox()
                self._flow.addItems(["", "xtls-rprx-vision"])
                form.addRow("Flow:", self._flow)

            elif self._config_type == EConfigType.SOCKS:
                self._username = QLineEdit()
                form.addRow("Username:", self._username)

            tabs.addTab(general, "General")

            # Transport tab
            transport = QWidget()
            tform = QFormLayout(transport)

            self._network = QComboBox()
            self._network.addItems(["tcp", "ws", "h2", "grpc", "kcp", "quic", "httpupgrade", "xhttp"])
            tform.addRow("Network:", self._network)

            self._stream_security = QComboBox()
            self._stream_security.addItems(["", "tls", "reality"])
            tform.addRow("Security:", self._stream_security)

            self._sni = QLineEdit()
            tform.addRow("SNI:", self._sni)

            self._alpn = QLineEdit()
            tform.addRow("ALPN:", self._alpn)

            self._fingerprint = QComboBox()
            self._fingerprint.addItems(["", "chrome", "firefox", "safari", "randomized"])
            self._fingerprint.setEditable(True)
            tform.addRow("Fingerprint:", self._fingerprint)

            self._request_host = QLineEdit()
            tform.addRow("Host:", self._request_host)

            self._path = QLineEdit()
            tform.addRow("Path:", self._path)

            self._header_type = QComboBox()
            self._header_type.addItems(["none", "http"])
            tform.addRow("Header Type:", self._header_type)

            self._allow_insecure = QCheckBox("Allow Insecure")
            tform.addRow("", self._allow_insecure)

            tabs.addTab(transport, "Transport")

            # Reality tab (for VLESS)
            if self._config_type in (EConfigType.VLESS, EConfigType.Trojan):
                reality = QWidget()
                rform = QFormLayout(reality)

                self._public_key = QLineEdit()
                rform.addRow("Public Key:", self._public_key)

                self._short_id = QLineEdit()
                rform.addRow("Short ID:", self._short_id)

                self._spider_x = QLineEdit()
                rform.addRow("SpiderX:", self._spider_x)

                tabs.addTab(reality, "Reality")

            # Buttons
            buttons = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
            )
            buttons.accepted.connect(self.accept)
            buttons.rejected.connect(self.reject)
            layout.addWidget(buttons)

        def _load_data(self):
            """Load item data into UI."""
            if not self._item:
                return

            self._remarks.setText(self._item.remarks)
            self._address.setText(self._item.address)
            self._port.setValue(self._item.port or 443)
            self._password.setText(self._item.password)

            # Transport
            if self._item.network:
                idx = self._network.findText(self._item.network)
                if idx >= 0:
                    self._network.setCurrentIndex(idx)

            self._sni.setText(self._item.sni)
            self._alpn.setText(self._item.alpn)
            self._request_host.setText(self._item.request_host)
            self._path.setText(self._item.path)

        def get_item(self) -> ProfileItem:
            """Get the configured ProfileItem."""
            self._item.remarks = self._remarks.text()
            self._item.address = self._address.text()
            self._item.port = self._port.value()
            self._item.password = self._password.text()
            self._item.network = self._network.currentText()
            self._item.stream_security = self._stream_security.currentText()
            self._item.sni = self._sni.text()
            self._item.alpn = self._alpn.text()
            self._item.fingerprint = self._fingerprint.currentText()
            self._item.request_host = self._request_host.text()
            self._item.path = self._path.text()
            self._item.header_type = self._header_type.currentText()
            self._item.allow_insecure = "true" if self._allow_insecure.isChecked() else ""

            # Type-specific
            extra = ProtocolExtraItem()
            if self._config_type == EConfigType.VMess:
                extra.alter_id = str(self._alter_id.value())
                extra.vmess_security = self._security.currentText()
            elif self._config_type == EConfigType.Shadowsocks:
                extra.ss_method = self._method.currentText()
            elif self._config_type == EConfigType.VLESS:
                extra.vless_encryption = self._encryption.currentText()
                extra.flow = self._flow.currentText()

            self._item.set_protocol_extra(extra)

            if hasattr(self, "_public_key"):
                self._item.public_key = self._public_key.text()
                self._item.short_id = self._short_id.text()
                self._item.spider_x = self._spider_x.text()

            if self._config_type == EConfigType.SOCKS and hasattr(self, "_username"):
                self._item.username = self._username.text()

            return self._item

    return AddServerDialog(config_type, parent, item)
