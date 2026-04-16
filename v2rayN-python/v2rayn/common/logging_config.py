"""Logging configuration module.

Ported from ServiceLib/Common/Logging.cs.
Uses Python's built-in logging module instead of NLog.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path


_logger = logging.getLogger("v2rayn")
_debug_logger = logging.getLogger("v2rayn.debug")
_logging_enabled = True


def setup(log_dir: str | None = None) -> None:
    """Setup logging configuration."""
    if log_dir is None:
        log_dir = os.path.join(os.path.expanduser("~"), ".v2rayn", "logs")

    Path(log_dir).mkdir(parents=True, exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(log_dir, f"{today}.txt")

    formatter = logging.Formatter("%(asctime)s-%(levelname)s %(message)s")

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    _logger.addHandler(file_handler)
    _logger.addHandler(console_handler)
    _logger.setLevel(logging.DEBUG)

    _debug_logger.addHandler(file_handler)
    _debug_logger.setLevel(logging.DEBUG)


def logging_enabled(enable: bool) -> None:
    """Enable or disable logging."""
    global _logging_enabled
    _logging_enabled = enable
    if not enable:
        _logger.setLevel(logging.CRITICAL + 1)
        _debug_logger.setLevel(logging.CRITICAL + 1)
    else:
        _logger.setLevel(logging.DEBUG)
        _debug_logger.setLevel(logging.DEBUG)


def save_log(content: str) -> None:
    """Save an info log message."""
    if not _logging_enabled:
        return
    _logger.info(content)


def save_log_ex(title: str, ex: Exception) -> None:
    """Save an error log with exception details."""
    if not _logging_enabled:
        return
    _debug_logger.debug(f"{title},{ex}")
    import traceback

    _debug_logger.debug(traceback.format_exc())
