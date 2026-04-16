"""WebDAV backup manager.

Ported from ServiceLib/Manager/WebDavManager.cs.
Manages configuration backup/restore via WebDAV.
"""

from __future__ import annotations

import os
from typing import Any

from v2rayn.common import logging_config
from v2rayn.common.file_utils import create_from_directory, zip_extract_to_file
from v2rayn.common.utils import get_backup_path, get_config_path, get_temp_path

_tag = "WebDavManager"


class WebDavManager:
    """Manages WebDAV-based configuration backup."""

    def __init__(self, url: str = "", username: str = "", password: str = ""):
        """Initialize WebDAV manager.

        Args:
            url: WebDAV server URL
            username: WebDAV username
            password: WebDAV password
        """
        self._url = url
        self._username = username
        self._password = password

    async def backup(self) -> bool:
        """Backup configuration to WebDAV.

        Returns:
            True on success
        """
        try:
            # Create backup archive
            config_dir = get_config_path()
            backup_file = get_temp_path("v2rayn_backup.zip")

            if not create_from_directory(config_dir, backup_file):
                return False

            # Upload to WebDAV
            return await self._upload_file(backup_file, "v2rayn_backup.zip")
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)
            return False

    async def restore(self) -> bool:
        """Restore configuration from WebDAV.

        Returns:
            True on success
        """
        try:
            backup_file = get_temp_path("v2rayn_backup_restore.zip")

            # Download from WebDAV
            if not await self._download_file("v2rayn_backup.zip", backup_file):
                return False

            # Extract to config directory
            config_dir = get_config_path()
            return zip_extract_to_file(backup_file, config_dir, "")
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)
            return False

    async def _upload_file(self, local_path: str, remote_name: str) -> bool:
        """Upload a file to WebDAV."""
        try:
            import httpx

            url = f"{self._url.rstrip('/')}/{remote_name}"
            with open(local_path, "rb") as f:
                data = f.read()

            async with httpx.AsyncClient(timeout=60, verify=False) as client:
                response = await client.put(
                    url,
                    content=data,
                    auth=(self._username, self._password),
                )
                return response.status_code in (200, 201, 204)
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)
            return False

    async def _download_file(self, remote_name: str, local_path: str) -> bool:
        """Download a file from WebDAV."""
        try:
            import httpx

            url = f"{self._url.rstrip('/')}/{remote_name}"
            async with httpx.AsyncClient(timeout=60, verify=False) as client:
                response = await client.get(
                    url,
                    auth=(self._username, self._password),
                )
                if response.status_code == 200:
                    with open(local_path, "wb") as f:
                        f.write(response.content)
                    return True
                return False
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)
            return False
