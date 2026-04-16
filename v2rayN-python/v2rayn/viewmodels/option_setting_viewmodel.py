"""Option settings ViewModel.

Ported from ServiceLib/ViewModels/OptionSettingViewModel.cs (~447 lines).
Manages option/settings dialog data.
"""

from __future__ import annotations

from typing import Any

from v2rayn.common import logging_config
from v2rayn.handler.config_handler import ConfigHandler
from v2rayn.models.config import Config

_tag = "OptionSettingViewModel"


class OptionSettingViewModel:
    """Option settings ViewModel."""

    def __init__(self, config_handler: ConfigHandler):
        """Initialize option settings ViewModel."""
        self._config_handler = config_handler
        self._config = config_handler.config

    # Inbound settings
    @property
    def local_address(self) -> str:
        return self._config.inbound_item.local_address

    @local_address.setter
    def local_address(self, value: str) -> None:
        self._config.inbound_item.local_address = value

    @property
    def socks_port(self) -> int:
        return self._config.inbound_item.socks_port

    @socks_port.setter
    def socks_port(self, value: int) -> None:
        self._config.inbound_item.socks_port = value

    @property
    def http_port(self) -> int:
        return self._config.inbound_item.http_port

    @http_port.setter
    def http_port(self, value: int) -> None:
        self._config.inbound_item.http_port = value

    @property
    def allow_lan(self) -> bool:
        return self._config.inbound_item.allow_lan

    @allow_lan.setter
    def allow_lan(self, value: bool) -> None:
        self._config.inbound_item.allow_lan = value

    # TUN settings
    @property
    def enable_tun(self) -> bool:
        return self._config.tun_mode_item.enable_tun

    @enable_tun.setter
    def enable_tun(self, value: bool) -> None:
        self._config.tun_mode_item.enable_tun = value

    @property
    def tun_stack(self) -> str:
        return self._config.tun_mode_item.stack

    @tun_stack.setter
    def tun_stack(self, value: str) -> None:
        self._config.tun_mode_item.stack = value

    # GUI settings
    @property
    def auto_run(self) -> bool:
        return self._config.gui_item.auto_run

    @auto_run.setter
    def auto_run(self, value: bool) -> None:
        self._config.gui_item.auto_run = value

    @property
    def enable_statistics(self) -> bool:
        return self._config.gui_item.enable_statistics

    @enable_statistics.setter
    def enable_statistics(self, value: bool) -> None:
        self._config.gui_item.enable_statistics = value

    def save(self) -> bool:
        """Save configuration changes."""
        return self._config_handler.save_config()
