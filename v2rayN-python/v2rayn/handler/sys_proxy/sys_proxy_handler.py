"""System proxy handler dispatcher.

Ported from ServiceLib/Handler/SysProxy/SysProxyHandler.cs.
Routes system proxy configuration to platform-specific implementations.
"""

from __future__ import annotations

import sys

from v2rayn.common import logging_config
from v2rayn.enums.sys_proxy_type import ESysProxyType

_tag = "SysProxyHandler"


def update_sys_proxy(
    proxy_type: ESysProxyType,
    address: str = "",
    port: int = 0,
    pac_url: str = "",
    exceptions: str = "",
) -> bool:
    """Update system proxy settings.

    Args:
        proxy_type: Type of proxy to set
        address: Proxy address
        port: Proxy port
        pac_url: PAC file URL
        exceptions: Proxy exceptions

    Returns:
        True on success
    """
    try:
        if proxy_type == ESysProxyType.ForcedClear:
            return _clear_proxy()
        elif proxy_type == ESysProxyType.ForcedChange:
            return _set_proxy(address, port, exceptions)
        elif proxy_type == ESysProxyType.Pac:
            return _set_pac_proxy(pac_url)
        elif proxy_type == ESysProxyType.Unchanged:
            return True
        return False
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
        return False


def _clear_proxy() -> bool:
    """Clear system proxy settings."""
    if sys.platform == "win32":
        from v2rayn.handler.sys_proxy import proxy_setting_windows

        return proxy_setting_windows.clear_proxy()
    elif sys.platform == "darwin":
        from v2rayn.handler.sys_proxy import proxy_setting_osx

        return proxy_setting_osx.clear_proxy()
    else:
        from v2rayn.handler.sys_proxy import proxy_setting_linux

        return proxy_setting_linux.clear_proxy()


def _set_proxy(address: str, port: int, exceptions: str) -> bool:
    """Set HTTP/SOCKS proxy."""
    if sys.platform == "win32":
        from v2rayn.handler.sys_proxy import proxy_setting_windows

        return proxy_setting_windows.set_proxy(address, port, exceptions)
    elif sys.platform == "darwin":
        from v2rayn.handler.sys_proxy import proxy_setting_osx

        return proxy_setting_osx.set_proxy(address, port, exceptions)
    else:
        from v2rayn.handler.sys_proxy import proxy_setting_linux

        return proxy_setting_linux.set_proxy(address, port, exceptions)


def _set_pac_proxy(pac_url: str) -> bool:
    """Set PAC proxy."""
    if sys.platform == "win32":
        from v2rayn.handler.sys_proxy import proxy_setting_windows

        return proxy_setting_windows.set_pac_proxy(pac_url)
    elif sys.platform == "darwin":
        from v2rayn.handler.sys_proxy import proxy_setting_osx

        return proxy_setting_osx.set_pac_proxy(pac_url)
    else:
        from v2rayn.handler.sys_proxy import proxy_setting_linux

        return proxy_setting_linux.set_pac_proxy(pac_url)
