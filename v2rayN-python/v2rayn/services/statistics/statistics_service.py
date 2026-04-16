"""Statistics services.

Ported from ServiceLib/Services/Statistics/.
Collects traffic statistics from Xray (gRPC) and Sing-box (API).
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

from v2rayn.common import json_utils, logging_config

_tag = "StatisticsService"


@dataclass
class TrafficStats:
    """Traffic statistics data."""

    up: int = 0
    down: int = 0
    total_up: int = 0
    total_down: int = 0


class StatisticsXrayService:
    """Xray traffic statistics via gRPC API.

    Ported from ServiceLib/Services/Statistics/StatisticsXrayService.cs.
    """

    def __init__(self, api_port: int = 0):
        """Initialize Xray statistics service.

        Args:
            api_port: gRPC API port
        """
        self._api_port = api_port
        self._running = False

    async def get_traffic_stats(self) -> TrafficStats:
        """Get current traffic statistics.

        Returns:
            TrafficStats with current stats
        """
        stats = TrafficStats()
        if self._api_port <= 0:
            return stats

        try:
            # gRPC query for Xray stats
            # In a full implementation, this would use grpcio to query
            # the Xray gRPC API at 127.0.0.1:{api_port}
            pass
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)

        return stats

    async def start_monitoring(self, interval: float = 1.0, callback: Any = None) -> None:
        """Start periodic traffic monitoring.

        Args:
            interval: Polling interval in seconds
            callback: Callback function(TrafficStats)
        """
        self._running = True
        while self._running:
            try:
                stats = await self.get_traffic_stats()
                if callback:
                    callback(stats)
            except Exception:
                pass
            await asyncio.sleep(interval)

    def stop_monitoring(self) -> None:
        """Stop traffic monitoring."""
        self._running = False


class StatisticsSingboxService:
    """Sing-box traffic statistics via REST API.

    Ported from ServiceLib/Services/Statistics/StatisticsSingboxService.cs.
    """

    def __init__(self, api_url: str = "http://127.0.0.1:9090"):
        """Initialize Sing-box statistics service.

        Args:
            api_url: Clash API URL
        """
        self._api_url = api_url
        self._running = False

    async def get_traffic_stats(self) -> TrafficStats:
        """Get current traffic statistics from Clash API.

        Returns:
            TrafficStats with current stats
        """
        stats = TrafficStats()
        try:
            import httpx

            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self._api_url}/traffic")
                if response.status_code == 200:
                    data = json_utils.parse_json(response.text)
                    if data:
                        stats.up = data.get("up", 0)
                        stats.down = data.get("down", 0)
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)

        return stats

    async def start_monitoring(self, interval: float = 1.0, callback: Any = None) -> None:
        """Start periodic traffic monitoring."""
        self._running = True
        while self._running:
            try:
                stats = await self.get_traffic_stats()
                if callback:
                    callback(stats)
            except Exception:
                pass
            await asyncio.sleep(interval)

    def stop_monitoring(self) -> None:
        """Stop traffic monitoring."""
        self._running = False
