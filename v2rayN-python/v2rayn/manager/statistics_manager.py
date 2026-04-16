"""Statistics manager.

Ported from ServiceLib/Manager/StatisticsManager.cs.
Manages traffic statistics collection.
"""

from __future__ import annotations

import asyncio
from typing import Any, Callable

from v2rayn.common import logging_config
from v2rayn.enums.core_type import ECoreType
from v2rayn.services.statistics.statistics_service import (
    StatisticsSingboxService,
    StatisticsXrayService,
    TrafficStats,
)

_tag = "StatisticsManager"


class StatisticsManager:
    """Manages traffic statistics."""

    def __init__(self):
        """Initialize statistics manager."""
        self._xray_service: StatisticsXrayService | None = None
        self._singbox_service: StatisticsSingboxService | None = None
        self._on_stats: Callable[[TrafficStats], None] | None = None
        self._running = False

    def set_stats_callback(self, callback: Callable[[TrafficStats], None]) -> None:
        """Set statistics callback."""
        self._on_stats = callback

    async def start(self, core_type: ECoreType, api_port: int = 0) -> None:
        """Start statistics monitoring.

        Args:
            core_type: Core type being used
            api_port: API port for statistics
        """
        self.stop()

        if core_type == ECoreType.Xray or core_type == ECoreType.v2fly:
            self._xray_service = StatisticsXrayService(api_port)
            self._running = True
            asyncio.create_task(
                self._xray_service.start_monitoring(callback=self._on_stats)
            )
        elif core_type in (ECoreType.sing_box, ECoreType.mihomo):
            self._singbox_service = StatisticsSingboxService()
            self._running = True
            asyncio.create_task(
                self._singbox_service.start_monitoring(callback=self._on_stats)
            )

    def stop(self) -> None:
        """Stop statistics monitoring."""
        self._running = False
        if self._xray_service:
            self._xray_service.stop_monitoring()
            self._xray_service = None
        if self._singbox_service:
            self._singbox_service.stop_monitoring()
            self._singbox_service = None
