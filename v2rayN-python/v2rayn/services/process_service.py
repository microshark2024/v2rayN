"""Process service.

Ported from ServiceLib/Services/ProcessService.cs.
Manages V2ray/Xray/Sing-box core processes.
"""

from __future__ import annotations

import asyncio
import os
import signal
import subprocess
import sys
from typing import Callable

from v2rayn.common import logging_config
from v2rayn.common.extensions import is_null_or_empty
from v2rayn.common.utils import get_bin_path, get_exe_name
from v2rayn.enums.core_type import ECoreType

_tag = "ProcessService"


class ProcessService:
    """Manages proxy core processes."""

    def __init__(self):
        """Initialize process service."""
        self._process: subprocess.Popen | None = None
        self._core_type: ECoreType = ECoreType.Xray
        self._on_log: Callable[[str], None] | None = None

    @property
    def is_running(self) -> bool:
        """Check if core process is running."""
        return self._process is not None and self._process.poll() is None

    def set_log_callback(self, callback: Callable[[str], None]) -> None:
        """Set log output callback."""
        self._on_log = callback

    async def start_core(self, core_type: ECoreType, config_path: str) -> bool:
        """Start a core process.

        Args:
            core_type: Type of core to start
            config_path: Path to configuration file

        Returns:
            True on success
        """
        try:
            await self.stop_core()

            self._core_type = core_type
            exe_name = self._get_core_exe_name(core_type)
            exe_path = os.path.join(get_bin_path(), exe_name)

            if not os.path.exists(exe_path):
                logging_config.save_log(f"Core executable not found: {exe_path}")
                return False

            args = self._get_core_args(core_type, config_path)

            self._process = subprocess.Popen(
                [exe_path] + args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=get_bin_path(),
            )

            # Start log reading task
            asyncio.create_task(self._read_output())

            logging_config.save_log(f"Core started: {exe_name} (PID: {self._process.pid})")
            return True
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)
            return False

    async def stop_core(self) -> None:
        """Stop the running core process."""
        try:
            if self._process and self._process.poll() is None:
                if sys.platform == "win32":
                    self._process.terminate()
                else:
                    self._process.send_signal(signal.SIGTERM)

                try:
                    self._process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self._process.kill()

                logging_config.save_log("Core stopped")

            self._process = None
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)

    async def _read_output(self) -> None:
        """Read and forward process stdout."""
        try:
            if not self._process or not self._process.stdout:
                return

            while self._process.poll() is None:
                line = self._process.stdout.readline()
                if line:
                    text = line.decode("utf-8", errors="replace").strip()
                    if text and self._on_log:
                        self._on_log(text)
                else:
                    await asyncio.sleep(0.1)
        except Exception:
            pass

    def _get_core_exe_name(self, core_type: ECoreType) -> str:
        """Get executable name for core type."""
        name_map = {
            ECoreType.Xray: "xray",
            ECoreType.v2fly: "v2ray",
            ECoreType.sing_box: "sing-box",
            ECoreType.mihomo: "mihomo",
        }
        name = name_map.get(core_type, "xray")
        return get_exe_name(name)

    def _get_core_args(self, core_type: ECoreType, config_path: str) -> list[str]:
        """Get command line arguments for core type."""
        if core_type == ECoreType.sing_box:
            return ["run", "-c", config_path]
        elif core_type == ECoreType.mihomo:
            return ["-f", config_path]
        else:
            return ["run", "-c", config_path]
