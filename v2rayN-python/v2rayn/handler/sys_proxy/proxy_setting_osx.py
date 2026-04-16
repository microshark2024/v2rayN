"""macOS system proxy settings.

Ported from ServiceLib/Handler/SysProxy/ProxySettingOSX.cs.
Uses networksetup command for proxy configuration.
"""

from __future__ import annotations

import subprocess

from v2rayn.common import logging_config

_tag = "ProxySettingOSX"


def set_proxy(address: str, port: int, exceptions: str) -> bool:
    """Set HTTP proxy on macOS.

    Args:
        address: Proxy address
        port: Proxy port
        exceptions: Proxy exception list

    Returns:
        True on success
    """
    try:
        services = _get_network_services()
        for service in services:
            _run_networksetup(["-setwebproxy", service, address, str(port)])
            _run_networksetup(["-setsecurewebproxy", service, address, str(port)])
            _run_networksetup(["-setsocksfirewallproxy", service, address, str(port)])
            _run_networksetup(["-setwebproxystate", service, "on"])
            _run_networksetup(["-setsecurewebproxystate", service, "on"])
            _run_networksetup(["-setsocksfirewallproxystate", service, "on"])
            if exceptions:
                domains = [d.strip() for d in exceptions.split(",") if d.strip()]
                _run_networksetup(["-setproxybypassdomains", service] + domains)
        return True
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
        return False


def clear_proxy() -> bool:
    """Clear HTTP proxy on macOS.

    Returns:
        True on success
    """
    try:
        services = _get_network_services()
        for service in services:
            _run_networksetup(["-setwebproxystate", service, "off"])
            _run_networksetup(["-setsecurewebproxystate", service, "off"])
            _run_networksetup(["-setsocksfirewallproxystate", service, "off"])
            _run_networksetup(["-setautoproxystate", service, "off"])
        return True
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
        return False


def set_pac_proxy(pac_url: str) -> bool:
    """Set PAC proxy on macOS.

    Args:
        pac_url: PAC file URL

    Returns:
        True on success
    """
    try:
        services = _get_network_services()
        for service in services:
            _run_networksetup(["-setautoproxyurl", service, pac_url])
            _run_networksetup(["-setautoproxystate", service, "on"])
        return True
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
        return False


def _get_network_services() -> list[str]:
    """Get list of network services."""
    try:
        result = subprocess.run(
            ["networksetup", "-listallnetworkservices"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        services = []
        for line in result.stdout.strip().split("\n"):
            line = line.strip()
            if line and not line.startswith("*") and not line.startswith("An asterisk"):
                services.append(line)
        return services
    except Exception:
        return ["Wi-Fi", "Ethernet"]


def _run_networksetup(args: list[str]) -> None:
    """Run a networksetup command."""
    try:
        subprocess.run(
            ["networksetup"] + args,
            capture_output=True,
            timeout=10,
        )
    except Exception:
        pass
