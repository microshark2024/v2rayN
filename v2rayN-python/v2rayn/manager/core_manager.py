"""Core manager.

Ported from ServiceLib/Manager/CoreManager.cs.
Manages core binary information and operations.
"""

from __future__ import annotations

import os
import sys

from v2rayn.common import logging_config
from v2rayn.common.utils import get_bin_path, get_exe_name, get_file_hash
from v2rayn.enums.core_type import ECoreType

_tag = "CoreManager"


class CoreInfo:
    """Information about an installed core binary."""

    def __init__(self):
        self.core_type: ECoreType = ECoreType.Xray
        self.core_exe_name: str = ""
        self.core_url: str = ""
        self.version: str = ""
        self.exists: bool = False
        self.file_path: str = ""


class CoreManager:
    """Manages core binaries."""

    _CORE_MAP = {
        ECoreType.Xray: {
            "name": "xray",
            "url": "https://github.com/XTLS/Xray-core",
        },
        ECoreType.v2fly: {
            "name": "v2ray",
            "url": "https://github.com/v2fly/v2ray-core",
        },
        ECoreType.sing_box: {
            "name": "sing-box",
            "url": "https://github.com/SagerNet/sing-box",
        },
        ECoreType.mihomo: {
            "name": "mihomo",
            "url": "https://github.com/MetaCubeX/mihomo",
        },
    }

    def get_core_info(self, core_type: ECoreType) -> CoreInfo:
        """Get information about a core binary.

        Args:
            core_type: Core type

        Returns:
            CoreInfo instance
        """
        info = CoreInfo()
        info.core_type = core_type

        core_data = self._CORE_MAP.get(core_type, {})
        name = core_data.get("name", "")
        info.core_url = core_data.get("url", "")
        info.core_exe_name = get_exe_name(name)

        file_path = os.path.join(get_bin_path(), info.core_exe_name)
        info.file_path = file_path
        info.exists = os.path.exists(file_path)

        if info.exists:
            info.version = self._get_core_version(file_path, core_type)

        return info

    def get_all_core_info(self) -> list[CoreInfo]:
        """Get information about all core binaries."""
        return [self.get_core_info(ct) for ct in self._CORE_MAP]

    def _get_core_version(self, file_path: str, core_type: ECoreType) -> str:
        """Get version of a core binary."""
        try:
            import subprocess

            result = subprocess.run(
                [file_path, "version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            output = result.stdout.strip()
            if output:
                # Extract version from output
                for line in output.splitlines():
                    if "version" in line.lower() or line[0].isdigit():
                        return line.strip()
            return ""
        except Exception:
            return ""
