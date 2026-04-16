"""Download helper.

Ported from ServiceLib/Helper/DownloaderHelper.cs.
Manages file downloads with progress reporting and proxy support.
"""

from __future__ import annotations

import os
from typing import Callable

from v2rayn.common import logging_config
from v2rayn.helper.http_client import HttpClientHelper

_tag = "DownloaderHelper"


class DownloaderHelper:
    """File download helper with progress tracking."""

    def __init__(self, proxy_port: int = 0, user_agent: str = ""):
        """Initialize downloader.

        Args:
            proxy_port: Local SOCKS proxy port (0 to disable)
            user_agent: User-Agent header
        """
        self._proxy = f"socks5://127.0.0.1:{proxy_port}" if proxy_port > 0 else None
        self._user_agent = user_agent

    async def download_string_async(
        self,
        url: str,
        use_proxy: bool = True,
        user_agent: str = "",
    ) -> str:
        """Download URL content as string.

        Args:
            url: Download URL
            use_proxy: Whether to use proxy
            user_agent: Optional user agent override

        Returns:
            Content string or empty string on failure
        """
        try:
            headers = {}
            ua = user_agent or self._user_agent
            if ua:
                headers["User-Agent"] = ua

            proxy = self._proxy if use_proxy else None
            client = HttpClientHelper(timeout=30, proxy=proxy)
            return await client.get_async(url, headers=headers or None)
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)
            return ""

    async def download_data_async(
        self,
        url: str,
        use_proxy: bool = True,
        user_agent: str = "",
    ) -> bytes:
        """Download URL content as bytes.

        Args:
            url: Download URL
            use_proxy: Whether to use proxy
            user_agent: Optional user agent override

        Returns:
            Content bytes or empty bytes on failure
        """
        try:
            headers = {}
            ua = user_agent or self._user_agent
            if ua:
                headers["User-Agent"] = ua

            proxy = self._proxy if use_proxy else None
            client = HttpClientHelper(timeout=60, proxy=proxy)
            return await client.get_bytes_async(url, headers=headers or None)
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)
            return b""

    async def download_file_async(
        self,
        url: str,
        file_path: str,
        use_proxy: bool = True,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> bool:
        """Download a file.

        Args:
            url: Download URL
            file_path: Local destination path
            use_proxy: Whether to use proxy
            progress_callback: Optional progress callback(downloaded, total)

        Returns:
            True on success, False on failure
        """
        try:
            headers = {}
            if self._user_agent:
                headers["User-Agent"] = self._user_agent

            proxy = self._proxy if use_proxy else None
            client = HttpClientHelper(timeout=300, proxy=proxy)
            return await client.download_file_async(url, file_path, progress_callback, headers or None)
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)
            return False
