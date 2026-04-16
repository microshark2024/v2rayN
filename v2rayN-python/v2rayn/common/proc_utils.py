"""Process utility functions.

Ported from ServiceLib/Common/ProcUtils.cs.
"""

from __future__ import annotations

import os
import subprocess
import sys

from v2rayn.common import logging_config
from v2rayn.common.extensions import is_null_or_empty

_tag = "ProcUtils"


def process_start(file_name: str | None, arguments: str = "", directory: str | None = None) -> int | None:
    """Start a process.

    Args:
        file_name: Executable file path
        arguments: Command line arguments
        directory: Working directory

    Returns:
        Process ID if directory was specified, None otherwise
    """
    if is_null_or_empty(file_name):
        return None

    try:
        args = [file_name]  # type: ignore
        if arguments:
            args.extend(arguments.split())

        proc = subprocess.Popen(
            args,
            cwd=directory or None,
            shell=False,
        )
        return proc.pid if directory else None
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
        return None


def reboot_as_admin(as_admin: bool = True) -> None:
    """Reboot the application with optional admin privileges.

    Args:
        as_admin: Whether to request admin privileges
    """
    try:
        exe_path = sys.executable
        startup_path = os.path.dirname(os.path.abspath(sys.argv[0]))

        if sys.platform == "win32" and as_admin:
            import ctypes

            ctypes.windll.shell32.ShellExecuteW(  # type: ignore[attr-defined]
                None, "runas", exe_path, f'"{sys.argv[0]}" rebootas', startup_path, 1
            )
        else:
            subprocess.Popen(
                [exe_path, sys.argv[0], "rebootas"],
                cwd=startup_path,
            )
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
