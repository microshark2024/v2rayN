"""Speed test service.

Ported from ServiceLib/Services/SpeedtestService.cs.
Tests proxy node latency and download speed.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any, Callable

from v2rayn.common import logging_config
from v2rayn.common.utils import get_free_port
from v2rayn.enums.speed_action_type import ESpeedActionType
from v2rayn.models.profile_item import ProfileItem

_tag = "SpeedtestService"

# Test URLs
SPEED_PING_URL = "https://www.google.com/generate_204"
SPEED_TEST_URL = "https://speed.cloudflare.com/__down?bytes=10000000"


class SpeedtestService:
    """Proxy speed test service."""

    def __init__(self):
        """Initialize speed test service."""
        self._on_result: Callable[[str, int, str], None] | None = None
        self._testing = False

    def set_result_callback(self, callback: Callable[[str, int, str], None]) -> None:
        """Set result callback(index_id, delay_ms, speed_str)."""
        self._on_result = callback

    async def run_test(
        self,
        items: list[ProfileItem],
        action_type: ESpeedActionType,
    ) -> dict[str, dict[str, Any]]:
        """Run speed tests on multiple nodes.

        Args:
            items: List of profile items to test
            action_type: Type of speed test

        Returns:
            Dictionary of index_id -> result dict
        """
        results: dict[str, dict[str, Any]] = {}
        self._testing = True

        try:
            if action_type == ESpeedActionType.Tcping:
                tasks = [self._tcping(item) for item in items]
            elif action_type == ESpeedActionType.Realping:
                tasks = [self._real_ping(item) for item in items]
            elif action_type == ESpeedActionType.Speedtest:
                tasks = [self._speed_test(item) for item in items]
            elif action_type == ESpeedActionType.Mixedtest:
                tasks = [self._mixed_test(item) for item in items]
            else:
                return results

            completed = await asyncio.gather(*tasks, return_exceptions=True)
            for item, result in zip(items, completed):
                if isinstance(result, dict):
                    results[item.index_id] = result
                elif isinstance(result, Exception):
                    results[item.index_id] = {"delay": -1, "speed": "", "error": str(result)}
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)
        finally:
            self._testing = False

        return results

    async def _tcping(self, item: ProfileItem) -> dict[str, Any]:
        """TCP ping test."""
        import socket

        try:
            start = time.monotonic()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((item.address, item.port))
            sock.close()
            delay = int((time.monotonic() - start) * 1000)

            self._notify(item.index_id, delay, "")
            return {"delay": delay, "speed": ""}
        except Exception:
            self._notify(item.index_id, -1, "")
            return {"delay": -1, "speed": ""}

    async def _real_ping(self, item: ProfileItem) -> dict[str, Any]:
        """Real HTTP ping test through proxy."""
        try:
            port = get_free_port()
            # Start a temporary proxy and test through it
            import httpx

            start = time.monotonic()
            proxy = f"socks5://127.0.0.1:{item.port}"
            async with httpx.AsyncClient(proxy=proxy, timeout=10, verify=False) as client:
                response = await client.get(SPEED_PING_URL)
                delay = int((time.monotonic() - start) * 1000)

            self._notify(item.index_id, delay, "")
            return {"delay": delay, "speed": ""}
        except Exception:
            self._notify(item.index_id, -1, "")
            return {"delay": -1, "speed": ""}

    async def _speed_test(self, item: ProfileItem) -> dict[str, Any]:
        """Download speed test."""
        try:
            import httpx

            proxy = f"socks5://127.0.0.1:{item.port}"
            start = time.monotonic()
            total_bytes = 0

            async with httpx.AsyncClient(proxy=proxy, timeout=30, verify=False) as client:
                async with client.stream("GET", SPEED_TEST_URL) as response:
                    async for chunk in response.aiter_bytes(8192):
                        total_bytes += len(chunk)
                        elapsed = time.monotonic() - start
                        if elapsed > 10:
                            break

            elapsed = time.monotonic() - start
            if elapsed > 0:
                speed_mbps = (total_bytes * 8) / (elapsed * 1_000_000)
                speed_str = f"{speed_mbps:.1f} Mbps"
            else:
                speed_str = "0 Mbps"

            self._notify(item.index_id, 0, speed_str)
            return {"delay": 0, "speed": speed_str}
        except Exception:
            self._notify(item.index_id, -1, "")
            return {"delay": -1, "speed": ""}

    async def _mixed_test(self, item: ProfileItem) -> dict[str, Any]:
        """Combined ping + speed test."""
        ping_result = await self._tcping(item)
        speed_result = await self._speed_test(item)
        return {
            "delay": ping_result.get("delay", -1),
            "speed": speed_result.get("speed", ""),
        }

    def _notify(self, index_id: str, delay: int, speed: str) -> None:
        """Notify test result."""
        if self._on_result:
            self._on_result(index_id, delay, speed)

    def cancel(self) -> None:
        """Cancel running tests."""
        self._testing = False
