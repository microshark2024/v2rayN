"""Update service.

Ported from ServiceLib/Services/UpdateService.cs.
Handles checking and downloading application and core updates.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Any, Callable

from v2rayn.common import json_utils, logging_config
from v2rayn.common.extensions import is_not_empty
from v2rayn.common.utils import get_temp_path, get_version_info
from v2rayn.enums.core_type import ECoreType

_tag = "UpdateService"

# Update URLs
V2RAYN_RELEASE_URL = "https://api.github.com/repos/2dust/v2rayN/releases/latest"
XRAY_RELEASE_URL = "https://api.github.com/repos/XTLS/Xray-core/releases/latest"
SINGBOX_RELEASE_URL = "https://api.github.com/repos/SagerNet/sing-box/releases/latest"
MIHOMO_RELEASE_URL = "https://api.github.com/repos/MetaCubeX/mihomo/releases/latest"


@dataclass
class UpdateResult:
    """Update check result."""

    has_update: bool = False
    version: str = ""
    download_url: str = ""
    changelog: str = ""
    error: str = ""


class UpdateService:
    """Application and core update service."""

    def __init__(self, proxy_port: int = 0):
        """Initialize update service.

        Args:
            proxy_port: Local proxy port for downloading updates
        """
        self._proxy_port = proxy_port

    async def check_update_gui(self) -> UpdateResult:
        """Check for v2rayN GUI updates.

        Returns:
            UpdateResult with update information
        """
        return await self._check_github_release(
            V2RAYN_RELEASE_URL,
            get_version_info(),
        )

    async def check_update_core(self, core_type: ECoreType) -> UpdateResult:
        """Check for core updates.

        Args:
            core_type: Core type to check

        Returns:
            UpdateResult with update information
        """
        url_map = {
            ECoreType.Xray: XRAY_RELEASE_URL,
            ECoreType.sing_box: SINGBOX_RELEASE_URL,
            ECoreType.mihomo: MIHOMO_RELEASE_URL,
        }

        url = url_map.get(core_type)
        if not url:
            return UpdateResult(error=f"Unsupported core type: {core_type}")

        return await self._check_github_release(url, "")

    async def download_update(
        self,
        url: str,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> str:
        """Download an update file.

        Args:
            url: Download URL
            progress_callback: Progress callback

        Returns:
            Local file path or empty string on failure
        """
        try:
            from v2rayn.helper.downloader import DownloaderHelper

            file_name = url.split("/")[-1]
            file_path = get_temp_path(file_name)

            downloader = DownloaderHelper(proxy_port=self._proxy_port)
            success = await downloader.download_file_async(
                url,
                file_path,
                use_proxy=self._proxy_port > 0,
                progress_callback=progress_callback,
            )

            return file_path if success else ""
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)
            return ""

    async def _check_github_release(self, url: str, current_version: str) -> UpdateResult:
        """Check GitHub release for updates."""
        try:
            from v2rayn.helper.downloader import DownloaderHelper

            downloader = DownloaderHelper(proxy_port=self._proxy_port)
            response = await downloader.download_string_async(url, use_proxy=self._proxy_port > 0)

            if not response:
                return UpdateResult(error="Failed to check for updates")

            data = json_utils.parse_json(response)
            if not data or not isinstance(data, dict):
                return UpdateResult(error="Invalid response format")

            tag_name = data.get("tag_name", "")
            body = data.get("body", "")

            # Extract version number
            version = tag_name.lstrip("v")
            if current_version and version <= current_version:
                return UpdateResult(has_update=False, version=version)

            # Find download URL for current platform
            assets = data.get("assets", [])
            download_url = ""
            import platform as plat
            import sys

            system = sys.platform
            arch = plat.machine().lower()

            for asset in assets:
                name = asset.get("name", "").lower()
                if system == "win32" and "windows" in name:
                    if arch in ("amd64", "x86_64") and ("64" in name or "amd64" in name):
                        download_url = asset.get("browser_download_url", "")
                        break
                elif system == "linux" and "linux" in name:
                    if arch in ("amd64", "x86_64") and ("64" in name or "amd64" in name):
                        download_url = asset.get("browser_download_url", "")
                        break
                elif system == "darwin" and ("macos" in name or "darwin" in name):
                    download_url = asset.get("browser_download_url", "")
                    break

            return UpdateResult(
                has_update=True,
                version=version,
                download_url=download_url,
                changelog=body,
            )
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)
            return UpdateResult(error=str(ex))
