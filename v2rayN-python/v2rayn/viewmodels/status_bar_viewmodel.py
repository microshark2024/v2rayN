"""Status bar ViewModel.

Ported from ServiceLib/ViewModels/StatusBarViewModel.cs (~570 lines).
Manages status bar display data.
"""

from __future__ import annotations

from typing import Any

from v2rayn.common import logging_config
from v2rayn.common.utils import human_fy
from v2rayn.enums.rule_mode import ERuleMode
from v2rayn.enums.sys_proxy_type import ESysProxyType
from v2rayn.services.statistics.statistics_service import TrafficStats

_tag = "StatusBarViewModel"


class StatusBarViewModel:
    """Status bar ViewModel."""

    def __init__(self):
        """Initialize status bar ViewModel."""
        self._running_server: str = ""
        self._running_info: str = ""
        self._speed_proxy_text: str = ""
        self._speed_direct_text: str = ""
        self._sys_proxy_type: ESysProxyType = ESysProxyType.ForcedClear
        self._rule_mode: ERuleMode = ERuleMode.Rule
        self._notify_callback: Any = None

    def set_notify_callback(self, callback: Any) -> None:
        """Set notification callback."""
        self._notify_callback = callback

    @property
    def running_server(self) -> str:
        return self._running_server

    @running_server.setter
    def running_server(self, value: str) -> None:
        self._running_server = value
        self._notify("running_server")

    @property
    def running_info(self) -> str:
        return self._running_info

    @running_info.setter
    def running_info(self, value: str) -> None:
        self._running_info = value
        self._notify("running_info")

    @property
    def speed_proxy_text(self) -> str:
        return self._speed_proxy_text

    @property
    def speed_direct_text(self) -> str:
        return self._speed_direct_text

    @property
    def sys_proxy_text(self) -> str:
        """Get display text for current system proxy type."""
        text_map = {
            ESysProxyType.ForcedClear: "Clear",
            ESysProxyType.ForcedChange: "Set",
            ESysProxyType.Unchanged: "Unchanged",
            ESysProxyType.Pac: "PAC",
        }
        return text_map.get(self._sys_proxy_type, "Unknown")

    @property
    def rule_mode_text(self) -> str:
        """Get display text for current rule mode."""
        text_map = {
            ERuleMode.Rule: "Rule",
            ERuleMode.Direct: "Direct",
            ERuleMode.Global: "Global",
        }
        return text_map.get(self._rule_mode, "Unknown")

    def update_traffic(self, stats: TrafficStats) -> None:
        """Update traffic display.

        Args:
            stats: Current traffic statistics
        """
        self._speed_proxy_text = f"↑{human_fy(stats.up)}/s ↓{human_fy(stats.down)}/s"
        self._notify("speed_proxy_text")

    def set_sys_proxy_type(self, proxy_type: ESysProxyType) -> None:
        """Update system proxy type display."""
        self._sys_proxy_type = proxy_type
        self._notify("sys_proxy_text")

    def set_rule_mode(self, rule_mode: ERuleMode) -> None:
        """Update rule mode display."""
        self._rule_mode = rule_mode
        self._notify("rule_mode_text")

    def _notify(self, prop: str) -> None:
        """Notify of property change."""
        if self._notify_callback:
            try:
                self._notify_callback(prop)
            except Exception:
                pass
