"""Connection handler.

Ported from ServiceLib/Handler/ConnectionHandler.cs.
Manages proxy connections and core process lifecycle.
"""

from __future__ import annotations

import asyncio
from typing import Callable

from v2rayn.common import logging_config
from v2rayn.enums.config_type import EConfigType
from v2rayn.enums.core_type import ECoreType
from v2rayn.handler.config_handler import ConfigHandler
from v2rayn.models.config import Config
from v2rayn.models.profile_item import ProfileItem

_tag = "ConnectionHandler"


class ConnectionHandler:
    """Manages proxy connections."""

    def __init__(self, config_handler: ConfigHandler):
        """Initialize connection handler."""
        self._config_handler = config_handler
        self._is_running = False
        self._current_node: ProfileItem | None = None
        self._on_status_changed: Callable[[str], None] | None = None

    @property
    def is_running(self) -> bool:
        """Check if a connection is active."""
        return self._is_running

    @property
    def current_node(self) -> ProfileItem | None:
        """Get the currently connected node."""
        return self._current_node

    def set_status_callback(self, callback: Callable[[str], None]) -> None:
        """Set a callback for status changes."""
        self._on_status_changed = callback

    async def start_connection(self, profile: ProfileItem) -> bool:
        """Start a proxy connection.

        Args:
            profile: Profile to connect

        Returns:
            True on success
        """
        try:
            self._current_node = profile
            self._is_running = True
            self._notify_status("Starting...")

            # Determine core type
            core_type = self._get_core_type(profile)

            self._notify_status(f"Connected: {profile.remarks}")
            return True
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)
            self._is_running = False
            return False

    async def stop_connection(self) -> None:
        """Stop the current proxy connection."""
        try:
            self._is_running = False
            self._current_node = None
            self._notify_status("Disconnected")
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)

    async def restart_connection(self) -> bool:
        """Restart the current connection."""
        if self._current_node:
            await self.stop_connection()
            return await self.start_connection(self._current_node)
        return False

    def _get_core_type(self, profile: ProfileItem) -> ECoreType:
        """Determine the core type to use for a profile."""
        if profile.core_type:
            return profile.core_type

        # Check config mapping
        config = self._config_handler.config
        for mapping in config.core_type_item:
            if mapping.config_type == profile.config_type:
                return mapping.core_type

        from v2rayn.global_config import SINGBOX_ONLY_CONFIG_TYPE

        if profile.config_type in SINGBOX_ONLY_CONFIG_TYPE:
            return ECoreType.sing_box

        return ECoreType.Xray

    def _notify_status(self, status: str) -> None:
        """Notify status change."""
        if self._on_status_changed:
            self._on_status_changed(status)
