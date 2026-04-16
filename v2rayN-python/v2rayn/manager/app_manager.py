"""Application manager.

Ported from ServiceLib/Manager/AppManager.cs (~538 lines).
Central application lifecycle and state management.
"""

from __future__ import annotations

import os
import sys
from typing import Any

from v2rayn.common import logging_config
from v2rayn.common.utils import get_base_directory, get_config_path, get_runtime_info, get_version, startup_path
from v2rayn.handler.config_handler import ConfigHandler
from v2rayn.handler.connection_handler import ConnectionHandler
from v2rayn.handler.subscription_handler import SubscriptionHandler
from v2rayn.services.process_service import ProcessService

_tag = "AppManager"


class AppManager:
    """Central application manager."""

    _instance: AppManager | None = None

    def __init__(self):
        """Initialize application manager."""
        self._config_handler = ConfigHandler()
        self._connection_handler = ConnectionHandler(self._config_handler)
        self._subscription_handler = SubscriptionHandler(self._config_handler)
        self._process_service = ProcessService()
        self._initialized = False

    @classmethod
    def get_instance(cls) -> AppManager:
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = AppManager()
        return cls._instance

    @property
    def config_handler(self) -> ConfigHandler:
        """Get config handler."""
        return self._config_handler

    @property
    def connection_handler(self) -> ConnectionHandler:
        """Get connection handler."""
        return self._connection_handler

    @property
    def subscription_handler(self) -> SubscriptionHandler:
        """Get subscription handler."""
        return self._subscription_handler

    @property
    def process_service(self) -> ProcessService:
        """Get process service."""
        return self._process_service

    def initialize(self) -> bool:
        """Initialize the application.

        Returns:
            True on success
        """
        try:
            logging_config.setup()
            logging_config.save_log(get_runtime_info())

            # Load config
            if not self._config_handler.load_config():
                logging_config.save_log("Failed to load configuration")
                return False

            self._initialized = True
            return True
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)
            return False

    async def start(self) -> bool:
        """Start the application (connect to default profile).

        Returns:
            True on success
        """
        try:
            profile = self._config_handler.get_default_profile()
            if profile:
                return await self._connection_handler.start_connection(profile)
            return True
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)
            return False

    async def stop(self) -> None:
        """Stop the application."""
        try:
            await self._connection_handler.stop_connection()
            await self._process_service.stop_core()
            self._config_handler.save_config()
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)

    async def restart(self) -> bool:
        """Restart the connection."""
        return await self._connection_handler.restart_connection()
