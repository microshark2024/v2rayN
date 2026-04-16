"""Main window ViewModel.

Ported from ServiceLib/ViewModels/MainWindowViewModel.cs (~624 lines).
Uses Qt signals/slots pattern instead of ReactiveUI.
"""

from __future__ import annotations

from typing import Any

from v2rayn.common import logging_config
from v2rayn.enums.rule_mode import ERuleMode
from v2rayn.enums.sys_proxy_type import ESysProxyType
from v2rayn.manager.app_manager import AppManager

_tag = "MainWindowViewModel"


class MainWindowViewModel:
    """Main window ViewModel using observer pattern."""

    def __init__(self):
        """Initialize main window ViewModel."""
        self._app = AppManager.get_instance()
        self._sys_proxy_type: ESysProxyType = ESysProxyType.ForcedClear
        self._rule_mode: ERuleMode = ERuleMode.Rule
        self._is_running: bool = False
        self._selected_profile_id: str = ""
        self._status_text: str = ""
        self._speed_text: str = ""
        self._listeners: list[Any] = []

    @property
    def is_running(self) -> bool:
        return self._is_running

    @property
    def status_text(self) -> str:
        return self._status_text

    @status_text.setter
    def status_text(self, value: str) -> None:
        self._status_text = value
        self._notify("status_text", value)

    @property
    def speed_text(self) -> str:
        return self._speed_text

    @speed_text.setter
    def speed_text(self, value: str) -> None:
        self._speed_text = value
        self._notify("speed_text", value)

    @property
    def sys_proxy_type(self) -> ESysProxyType:
        return self._sys_proxy_type

    @property
    def rule_mode(self) -> ERuleMode:
        return self._rule_mode

    def add_listener(self, callback: Any) -> None:
        """Add property change listener."""
        self._listeners.append(callback)

    async def initialize(self) -> None:
        """Initialize ViewModel data."""
        self._app.initialize()

    async def start_connection(self, profile_id: str = "") -> None:
        """Start proxy connection."""
        try:
            if profile_id:
                self._selected_profile_id = profile_id
                self._app.config_handler.set_default_profile(profile_id)

            profile = self._app.config_handler.get_default_profile()
            if profile:
                self._is_running = await self._app.connection_handler.start_connection(profile)
                self.status_text = f"Connected: {profile.remarks}" if self._is_running else "Connection failed"
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)
            self.status_text = "Connection error"

    async def stop_connection(self) -> None:
        """Stop proxy connection."""
        await self._app.connection_handler.stop_connection()
        self._is_running = False
        self.status_text = "Disconnected"

    async def restart_connection(self) -> None:
        """Restart proxy connection."""
        await self.stop_connection()
        await self.start_connection()

    def set_sys_proxy_type(self, proxy_type: ESysProxyType) -> None:
        """Set system proxy type."""
        self._sys_proxy_type = proxy_type
        self._notify("sys_proxy_type", proxy_type)

    def set_rule_mode(self, rule_mode: ERuleMode) -> None:
        """Set routing rule mode."""
        self._rule_mode = rule_mode
        self._notify("rule_mode", rule_mode)

    async def update_subscriptions(self) -> int:
        """Update all subscriptions."""
        return await self._app.subscription_handler.update_all_subscriptions()

    def _notify(self, prop: str, value: Any) -> None:
        """Notify listeners of property change."""
        for listener in self._listeners:
            try:
                listener(prop, value)
            except Exception:
                pass
