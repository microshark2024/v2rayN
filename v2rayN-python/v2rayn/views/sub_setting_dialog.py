"""Subscription setting dialog.

Ported from v2rayN GUI subscription settings dialog.
"""

from __future__ import annotations

from v2rayn.common import logging_config
from v2rayn.models.routing import SubItem

_tag = "SubSettingDialog"


def create_sub_setting_dialog(subs: list[SubItem], parent=None):
    """Create subscription settings dialog.

    Args:
        subs: Current subscription list
        parent: Parent widget

    Returns:
        Dialog instance
    """
    try:
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import (
            QCheckBox,
            QDialog,
            QDialogButtonBox,
            QHBoxLayout,
            QHeaderView,
            QLineEdit,
            QPushButton,
            QTableWidget,
            QTableWidgetItem,
            QVBoxLayout,
        )
    except ImportError:
        logging_config.save_log("PySide6 not installed")
        return None

    class SubSettingDialog(QDialog):
        """Subscription settings dialog."""

        def __init__(self, sub_list, parent_widget=None):
            super().__init__(parent_widget)
            self._subs = list(sub_list)
            self.setWindowTitle("Subscription Settings")
            self.setMinimumSize(700, 400)
            self._setup_ui()
            self._load_data()

        def _setup_ui(self):
            """Setup dialog UI."""
            layout = QVBoxLayout(self)

            # Toolbar
            toolbar = QHBoxLayout()
            add_btn = QPushButton("Add")
            add_btn.clicked.connect(self._add_sub)
            toolbar.addWidget(add_btn)

            remove_btn = QPushButton("Remove")
            remove_btn.clicked.connect(self._remove_sub)
            toolbar.addWidget(remove_btn)

            toolbar.addStretch()
            layout.addLayout(toolbar)

            # Table
            self._table = QTableWidget()
            self._table.setColumnCount(4)
            self._table.setHorizontalHeaderLabels(["Enabled", "Remarks", "URL", "User Agent"])
            self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
            header = self._table.horizontalHeader()
            if header:
                header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
            layout.addWidget(self._table)

            # Buttons
            buttons = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
            )
            buttons.accepted.connect(self._save_and_close)
            buttons.rejected.connect(self.reject)
            layout.addWidget(buttons)

        def _load_data(self):
            """Load subscription data into table."""
            self._table.setRowCount(len(self._subs))
            for row, sub in enumerate(self._subs):
                # Enabled checkbox
                enabled_item = QTableWidgetItem()
                enabled_item.setCheckState(
                    Qt.CheckState.Checked if sub.enabled else Qt.CheckState.Unchecked
                )
                self._table.setItem(row, 0, enabled_item)

                self._table.setItem(row, 1, QTableWidgetItem(sub.remarks))
                self._table.setItem(row, 2, QTableWidgetItem(sub.url))
                self._table.setItem(row, 3, QTableWidgetItem(sub.user_agent))

        def _add_sub(self):
            """Add a new subscription row."""
            row = self._table.rowCount()
            self._table.insertRow(row)
            enabled_item = QTableWidgetItem()
            enabled_item.setCheckState(Qt.CheckState.Checked)
            self._table.setItem(row, 0, enabled_item)
            self._table.setItem(row, 1, QTableWidgetItem(""))
            self._table.setItem(row, 2, QTableWidgetItem(""))
            self._table.setItem(row, 3, QTableWidgetItem(""))

        def _remove_sub(self):
            """Remove selected subscription rows."""
            rows = set()
            for item in self._table.selectedItems():
                rows.add(item.row())
            for row in sorted(rows, reverse=True):
                self._table.removeRow(row)

        def _save_and_close(self):
            """Save subscriptions and close."""
            self._subs.clear()
            for row in range(self._table.rowCount()):
                sub = SubItem()
                enabled_item = self._table.item(row, 0)
                sub.enabled = enabled_item.checkState() == Qt.CheckState.Checked if enabled_item else True
                remarks_item = self._table.item(row, 1)
                sub.remarks = remarks_item.text() if remarks_item else ""
                url_item = self._table.item(row, 2)
                sub.url = url_item.text() if url_item else ""
                ua_item = self._table.item(row, 3)
                sub.user_agent = ua_item.text() if ua_item else ""
                self._subs.append(sub)
            self.accept()

        def get_subs(self) -> list[SubItem]:
            """Get updated subscription list."""
            return self._subs

    return SubSettingDialog(subs, parent)
