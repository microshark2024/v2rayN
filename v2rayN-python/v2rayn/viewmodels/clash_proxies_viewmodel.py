"""Clash proxies ViewModel.

Ported from ServiceLib/ViewModels/ClashProxiesViewModel.cs (~459 lines).
Manages Clash proxy groups and proxy selection.
"""

from __future__ import annotations

from typing import Any, Callable

from v2rayn.common import logging_config
from v2rayn.manager.clash_api_manager import ClashApiManager

_tag = "ClashProxiesViewModel"


class ClashProxiesViewModel:
    """Clash proxies ViewModel."""

    def __init__(self, api_url: str = "http://127.0.0.1:9090", secret: str = ""):
        """Initialize Clash proxies ViewModel."""
        self._api = ClashApiManager(api_url, secret)
        self._groups: list[dict[str, Any]] = []
        self._proxies: dict[str, Any] = {}
        self._selected_group: str = ""
        self._on_refresh: Callable[[], None] | None = None

    def set_refresh_callback(self, callback: Callable[[], None]) -> None:
        """Set refresh callback."""
        self._on_refresh = callback

    async def refresh_proxies(self) -> None:
        """Refresh proxy data from Clash API."""
        try:
            data = await self._api.get_proxies()
            proxies = data.get("proxies", {})
            self._proxies = proxies

            # Extract groups
            self._groups = []
            for name, proxy in proxies.items():
                proxy_type = proxy.get("type", "")
                if proxy_type in ("Selector", "URLTest", "Fallback", "LoadBalance"):
                    self._groups.append(
                        {
                            "name": name,
                            "type": proxy_type,
                            "now": proxy.get("now", ""),
                            "all": proxy.get("all", []),
                        }
                    )

            if self._on_refresh:
                self._on_refresh()
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)

    def get_groups(self) -> list[dict[str, Any]]:
        """Get proxy groups."""
        return self._groups

    def get_group_proxies(self, group_name: str) -> list[dict[str, Any]]:
        """Get proxies in a group."""
        result = []
        for group in self._groups:
            if group["name"] == group_name:
                for proxy_name in group.get("all", []):
                    proxy_data = self._proxies.get(proxy_name, {})
                    result.append(
                        {
                            "name": proxy_name,
                            "type": proxy_data.get("type", ""),
                            "history": proxy_data.get("history", []),
                            "selected": proxy_name == group.get("now", ""),
                        }
                    )
                break
        return result

    async def select_proxy(self, group_name: str, proxy_name: str) -> bool:
        """Select a proxy in a group."""
        success = await self._api.select_proxy(group_name, proxy_name)
        if success:
            await self.refresh_proxies()
        return success

    async def test_proxy_delay(self, proxy_name: str) -> int:
        """Test proxy delay."""
        return await self._api.get_proxy_delay(proxy_name)
