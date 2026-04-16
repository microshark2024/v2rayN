"""HTTP client helper.

Ported from ServiceLib/Helper/HttpClientHelper.cs.
Uses httpx for async HTTP requests.
"""

from __future__ import annotations

import asyncio
from typing import Any, Callable

from v2rayn.common import logging_config
from v2rayn.common.extensions import is_null_or_empty

_tag = "HttpClientHelper"


class HttpClientHelper:
    """Async HTTP client wrapper using httpx."""

    def __init__(self, timeout: int = 30, proxy: str | None = None):
        """Initialize HTTP client.

        Args:
            timeout: Request timeout in seconds
            proxy: Optional proxy URL (e.g., socks5://127.0.0.1:10808)
        """
        self._timeout = timeout
        self._proxy = proxy

    async def get_async(self, url: str, headers: dict[str, str] | None = None) -> str:
        """Make an async GET request.

        Args:
            url: Request URL
            headers: Optional HTTP headers

        Returns:
            Response text
        """
        try:
            import httpx

            async with httpx.AsyncClient(
                timeout=self._timeout,
                proxy=self._proxy,
                follow_redirects=True,
                verify=False,
            ) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                return response.text
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)
            return ""

    async def get_bytes_async(self, url: str, headers: dict[str, str] | None = None) -> bytes:
        """Make an async GET request for binary data.

        Args:
            url: Request URL
            headers: Optional HTTP headers

        Returns:
            Response bytes
        """
        try:
            import httpx

            async with httpx.AsyncClient(
                timeout=self._timeout,
                proxy=self._proxy,
                follow_redirects=True,
                verify=False,
            ) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                return response.content
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)
            return b""

    async def download_file_async(
        self,
        url: str,
        file_path: str,
        progress_callback: Callable[[int, int], None] | None = None,
        headers: dict[str, str] | None = None,
    ) -> bool:
        """Download a file with optional progress reporting.

        Args:
            url: Download URL
            file_path: Local file path to save
            progress_callback: Optional callback(downloaded_bytes, total_bytes)
            headers: Optional HTTP headers

        Returns:
            True on success, False on failure
        """
        try:
            import httpx

            async with httpx.AsyncClient(
                timeout=self._timeout * 10,
                proxy=self._proxy,
                follow_redirects=True,
                verify=False,
            ) as client:
                async with client.stream("GET", url, headers=headers) as response:
                    response.raise_for_status()
                    total = int(response.headers.get("content-length", 0))
                    downloaded = 0

                    with open(file_path, "wb") as f:
                        async for chunk in response.aiter_bytes(8192):
                            f.write(chunk)
                            downloaded += len(chunk)
                            if progress_callback:
                                progress_callback(downloaded, total)

            return True
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)
            return False

    async def patch_async(
        self,
        url: str,
        data: Any = None,
        headers: dict[str, str] | None = None,
    ) -> str:
        """Make an async PATCH request.

        Args:
            url: Request URL
            data: Request body data
            headers: Optional HTTP headers

        Returns:
            Response text
        """
        try:
            import httpx

            async with httpx.AsyncClient(
                timeout=self._timeout,
                proxy=self._proxy,
                follow_redirects=True,
                verify=False,
            ) as client:
                response = await client.patch(url, json=data, headers=headers)
                response.raise_for_status()
                return response.text
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)
            return ""

    async def put_async(
        self,
        url: str,
        data: Any = None,
        headers: dict[str, str] | None = None,
    ) -> str:
        """Make an async PUT request.

        Args:
            url: Request URL
            data: Request body data
            headers: Optional HTTP headers

        Returns:
            Response text
        """
        try:
            import httpx

            async with httpx.AsyncClient(
                timeout=self._timeout,
                proxy=self._proxy,
                follow_redirects=True,
                verify=False,
            ) as client:
                response = await client.put(url, json=data, headers=headers)
                response.raise_for_status()
                return response.text
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)
            return ""

    async def delete_async(
        self,
        url: str,
        headers: dict[str, str] | None = None,
    ) -> str:
        """Make an async DELETE request.

        Args:
            url: Request URL
            headers: Optional HTTP headers

        Returns:
            Response text
        """
        try:
            import httpx

            async with httpx.AsyncClient(
                timeout=self._timeout,
                proxy=self._proxy,
                follow_redirects=True,
                verify=False,
            ) as client:
                response = await client.delete(url, headers=headers)
                response.raise_for_status()
                return response.text
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)
            return ""
