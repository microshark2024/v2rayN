"""Windows system proxy settings.

Ported from ServiceLib/Handler/SysProxy/ProxySettingWindows.cs.
Uses ctypes to call Windows API for proxy configuration.
"""

from __future__ import annotations

import sys

from v2rayn.common import logging_config

_tag = "ProxySettingWindows"


def set_proxy(address: str, port: int, exceptions: str) -> bool:
    """Set HTTP proxy on Windows.

    Args:
        address: Proxy address
        port: Proxy port
        exceptions: Proxy exception list

    Returns:
        True on success
    """
    if sys.platform != "win32":
        return False

    try:
        import winreg

        proxy_str = f"{address}:{port}"
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
            0,
            winreg.KEY_SET_VALUE,
        )
        winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 1)
        winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, proxy_str)
        if exceptions:
            winreg.SetValueEx(key, "ProxyOverride", 0, winreg.REG_SZ, exceptions)
        winreg.CloseKey(key)

        _refresh_internet_settings()
        return True
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
        return False


def clear_proxy() -> bool:
    """Clear HTTP proxy on Windows.

    Returns:
        True on success
    """
    if sys.platform != "win32":
        return False

    try:
        import winreg

        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
            0,
            winreg.KEY_SET_VALUE,
        )
        winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 0)
        winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, "")
        winreg.SetValueEx(key, "AutoConfigURL", 0, winreg.REG_SZ, "")
        winreg.CloseKey(key)

        _refresh_internet_settings()
        return True
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
        return False


def set_pac_proxy(pac_url: str) -> bool:
    """Set PAC proxy on Windows.

    Args:
        pac_url: PAC file URL

    Returns:
        True on success
    """
    if sys.platform != "win32":
        return False

    try:
        import winreg

        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
            0,
            winreg.KEY_SET_VALUE,
        )
        winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 0)
        winreg.SetValueEx(key, "AutoConfigURL", 0, winreg.REG_SZ, pac_url)
        winreg.CloseKey(key)

        _refresh_internet_settings()
        return True
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
        return False


def _refresh_internet_settings() -> None:
    """Notify Windows that internet settings have changed."""
    try:
        import ctypes

        INTERNET_OPTION_SETTINGS_CHANGED = 39
        INTERNET_OPTION_REFRESH = 37

        internet = ctypes.windll.wininet  # type: ignore[attr-defined]
        internet.InternetSetOptionW(0, INTERNET_OPTION_SETTINGS_CHANGED, 0, 0)
        internet.InternetSetOptionW(0, INTERNET_OPTION_REFRESH, 0, 0)
    except Exception:
        pass
