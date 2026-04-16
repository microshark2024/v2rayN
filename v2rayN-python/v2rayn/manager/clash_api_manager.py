"""Clash API manager.

Ported from ServiceLib/Manager/ClashApiManager.cs.
Interacts with the Clash/Mihomo RESTful API for proxy management.
"""

from __future__ import annotations

from typing import Any

from v2rayn.common import json_utils, logging_config
from v2rayn.helper.http_client import HttpClientHelper

_tag = "ClashApiManager"


class ClashApiManager:
    """Manages Clash RESTful API interaction."""

    def __init__(self, base_url: str = "http://127.0.0.1:9090", secret: str = ""):
        """Initialize Clash API manager.

        Args:
            base_url: Clash API base URL
            secret: API secret key
        """
        self._base_url = base_url.rstrip("/")
        self._secret = secret
        self._client = HttpClientHelper(timeout=10)

    def _get_headers(self) -> dict[str, str]:
        """Get request headers with authorization."""
        headers: dict[str, str] = {}
        if self._secret:
            headers["Authorization"] = f"Bearer {self._secret}"
        return headers

    async def get_proxies(self) -> dict[str, Any]:
        """Get all proxies.

        Returns:
            Proxy data dict
        """
        try:
            resp = await self._client.get_async(
                f"{self._base_url}/proxies",
                headers=self._get_headers(),
            )
            return json_utils.parse_json(resp) or {}
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)
            return {}

    async def get_proxy_delay(self, name: str, url: str = "https://www.google.com/generate_204", timeout: int = 5000) -> int:
        """Test proxy delay.

        Args:
            name: Proxy name
            url: Test URL
            timeout: Timeout in ms

        Returns:
            Delay in ms, or -1 on failure
        """
        try:
            from v2rayn.common.utils import url_encode

            resp = await self._client.get_async(
                f"{self._base_url}/proxies/{url_encode(name)}/delay?url={url_encode(url)}&timeout={timeout}",
                headers=self._get_headers(),
            )
            data = json_utils.parse_json(resp)
            if data:
                return data.get("delay", -1)
            return -1
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)
            return -1

    async def select_proxy(self, group: str, name: str) -> bool:
        """Select a proxy in a group.

        Args:
            group: Group name
            name: Proxy name to select

        Returns:
            True on success
        """
        try:
            from v2rayn.common.utils import url_encode

            resp = await self._client.put_async(
                f"{self._base_url}/proxies/{url_encode(group)}",
                data={"name": name},
                headers=self._get_headers(),
            )
            return True
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)
            return False

    async def get_connections(self) -> dict[str, Any]:
        """Get active connections.

        Returns:
            Connection data dict
        """
        try:
            resp = await self._client.get_async(
                f"{self._base_url}/connections",
                headers=self._get_headers(),
            )
            return json_utils.parse_json(resp) or {}
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)
            return {}

    async def close_connection(self, connection_id: str) -> bool:
        """Close a specific connection.

        Args:
            connection_id: Connection ID

        Returns:
            True on success
        """
        try:
            await self._client.delete_async(
                f"{self._base_url}/connections/{connection_id}",
                headers=self._get_headers(),
            )
            return True
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)
            return False

    async def close_all_connections(self) -> bool:
        """Close all active connections.

        Returns:
            True on success
        """
        try:
            await self._client.delete_async(
                f"{self._base_url}/connections",
                headers=self._get_headers(),
            )
            return True
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)
            return False

    async def get_traffic(self) -> dict[str, int]:
        """Get traffic data.

        Returns:
            Dict with 'up' and 'down' keys
        """
        try:
            resp = await self._client.get_async(
                f"{self._base_url}/traffic",
                headers=self._get_headers(),
            )
            data = json_utils.parse_json(resp)
            if data:
                return {"up": data.get("up", 0), "down": data.get("down", 0)}
            return {"up": 0, "down": 0}
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)
            return {"up": 0, "down": 0}
