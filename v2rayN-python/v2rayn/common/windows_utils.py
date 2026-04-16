"""Windows-specific utility functions.

Ported from ServiceLib/Common/WindowsUtils.cs.
Uses ctypes and winreg for Windows API interaction.
"""

from __future__ import annotations

import os
import sys

from v2rayn.common import logging_config

_tag = "WindowsUtils"


def is_windows() -> bool:
    """Check if running on Windows."""
    return sys.platform == "win32"


def set_auto_run(reg_path: str, name: str, exe_path: str, enable: bool) -> None:
    """Set or remove auto-run registry entry on Windows."""
    if not is_windows():
        return

    try:
        import winreg

        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            reg_path,
            0,
            winreg.KEY_SET_VALUE,
        )
        if enable:
            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, exe_path)
        else:
            try:
                winreg.DeleteValue(key, name)
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)


def is_admin() -> bool:
    """Check if the current process has administrator privileges."""
    if not is_windows():
        return os.geteuid() == 0  # type: ignore[attr-defined]

    try:
        import ctypes

        return bool(ctypes.windll.shell32.IsUserAnAdmin())  # type: ignore[attr-defined]
    except Exception:
        return False


def get_clipboard_text() -> str:
    """Get text from system clipboard (Windows)."""
    if not is_windows():
        return ""

    try:
        import ctypes

        user32 = ctypes.windll.user32  # type: ignore[attr-defined]
        kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]

        if not user32.OpenClipboard(0):
            return ""
        try:
            h_data = user32.GetClipboardData(13)  # CF_UNICODETEXT
            if not h_data:
                return ""
            kernel32.GlobalLock.restype = ctypes.c_wchar_p
            text = kernel32.GlobalLock(h_data) or ""
            kernel32.GlobalUnlock(h_data)
            return text
        finally:
            user32.CloseClipboard()
    except Exception:
        return ""


def set_clipboard_text(text: str) -> None:
    """Set text to system clipboard (Windows)."""
    if not is_windows():
        return

    try:
        import ctypes

        user32 = ctypes.windll.user32  # type: ignore[attr-defined]
        kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]

        if not user32.OpenClipboard(0):
            return
        try:
            user32.EmptyClipboard()
            data = text.encode("utf-16-le") + b"\x00\x00"
            h_data = kernel32.GlobalAlloc(0x0042, len(data))
            p_data = kernel32.GlobalLock(h_data)
            ctypes.memmove(p_data, data, len(data))
            kernel32.GlobalUnlock(h_data)
            user32.SetClipboardData(13, h_data)  # CF_UNICODETEXT
        finally:
            user32.CloseClipboard()
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
