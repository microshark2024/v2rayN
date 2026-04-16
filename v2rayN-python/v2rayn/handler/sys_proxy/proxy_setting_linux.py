"""Linux system proxy settings.

Ported from ServiceLib/Handler/SysProxy/ProxySettingLinux.cs.
Uses gsettings or environment variables for proxy configuration.
"""

from __future__ import annotations

import os
import subprocess

from v2rayn.common import logging_config

_tag = "ProxySettingLinux"


def set_proxy(address: str, port: int, exceptions: str) -> bool:
    """Set HTTP proxy on Linux.

    Args:
        address: Proxy address
        port: Proxy port
        exceptions: Proxy exception list (comma-separated)

    Returns:
        True on success
    """
    try:
        # Try gsettings (GNOME)
        if _has_gsettings():
            _gsettings_set("org.gnome.system.proxy", "mode", "manual")
            _gsettings_set("org.gnome.system.proxy.http", "host", address)
            _gsettings_set("org.gnome.system.proxy.http", "port", str(port))
            _gsettings_set("org.gnome.system.proxy.https", "host", address)
            _gsettings_set("org.gnome.system.proxy.https", "port", str(port))
            _gsettings_set("org.gnome.system.proxy.socks", "host", address)
            _gsettings_set("org.gnome.system.proxy.socks", "port", str(port))
            if exceptions:
                hosts = [h.strip() for h in exceptions.split(",") if h.strip()]
                hosts_str = "[" + ",".join(f"'{h}'" for h in hosts) + "]"
                _gsettings_set("org.gnome.system.proxy", "ignore-hosts", hosts_str)
            return True

        # Fallback: set environment variables
        os.environ["http_proxy"] = f"http://{address}:{port}"
        os.environ["https_proxy"] = f"http://{address}:{port}"
        os.environ["all_proxy"] = f"socks5://{address}:{port}"
        if exceptions:
            os.environ["no_proxy"] = exceptions
        return True
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
        return False


def clear_proxy() -> bool:
    """Clear HTTP proxy on Linux.

    Returns:
        True on success
    """
    try:
        if _has_gsettings():
            _gsettings_set("org.gnome.system.proxy", "mode", "none")
            return True

        for var in ("http_proxy", "https_proxy", "all_proxy", "no_proxy"):
            os.environ.pop(var, None)
        return True
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
        return False


def set_pac_proxy(pac_url: str) -> bool:
    """Set PAC proxy on Linux.

    Args:
        pac_url: PAC file URL

    Returns:
        True on success
    """
    try:
        if _has_gsettings():
            _gsettings_set("org.gnome.system.proxy", "mode", "auto")
            _gsettings_set("org.gnome.system.proxy", "autoconfig-url", pac_url)
            return True
        return False
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
        return False


def _has_gsettings() -> bool:
    """Check if gsettings is available."""
    try:
        result = subprocess.run(
            ["which", "gsettings"],
            capture_output=True,
            timeout=5,
        )
        return result.returncode == 0
    except Exception:
        return False


def _gsettings_set(schema: str, key: str, value: str) -> None:
    """Set a gsettings value."""
    try:
        subprocess.run(
            ["gsettings", "set", schema, key, value],
            capture_output=True,
            timeout=5,
        )
    except Exception:
        pass
