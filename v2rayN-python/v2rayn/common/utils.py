"""General utility functions.

Ported from ServiceLib/Common/Utils.cs (~1237 lines).
Contains conversion, validation, file path, and network utility functions.
"""

from __future__ import annotations

import base64
import hashlib
import ipaddress
import os
import platform
import re
import socket
import struct
import sys
import uuid
from pathlib import Path
from typing import Any
from urllib.parse import quote, unquote, urlparse

from v2rayn.common import logging_config

_tag = "Utils"

# ============================================================================
# Conversion Functions
# ============================================================================


def list2string(lst: list[str] | None, wrap: bool = False) -> str:
    """Convert list to comma-separated string."""
    if not lst:
        return ""
    try:
        separator = ",\n" if wrap else ","
        return separator.join(lst)
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
        return ""


def string2list(s: str | None) -> list[str] | None:
    """Convert comma-separated string to list."""
    if not s or not s.strip():
        return None
    try:
        s = s.replace("\r\n", "").replace("\n", "")
        return [item.strip() for item in s.split(",") if item.strip()]
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
        return None


def string2list_sorted(s: str) -> list[str] | None:
    """Convert comma-separated string to sorted list."""
    lst = string2list(s)
    if lst:
        lst.sort()
    return lst


def base64_encode(plain_text: str, remove_padding: bool = False) -> str:
    """Base64 encode a string."""
    try:
        encoded = base64.b64encode(plain_text.encode("utf-8")).decode("utf-8")
        if remove_padding:
            encoded = encoded.rstrip("=")
        return encoded
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
        return ""


def base64_decode(plain_text: str | None) -> str:
    """Base64 decode a string, handling URL-safe and padding variations."""
    try:
        if not plain_text or not plain_text.strip():
            return ""

        text = (
            plain_text.strip()
            .replace("\r\n", "")
            .replace("\n", "")
            .replace("\r", "")
            .replace("_", "/")
            .replace("-", "+")
            .replace(" ", "")
        )

        # Add padding if needed
        remainder = len(text) % 4
        if remainder > 0:
            text += "=" * (4 - remainder)

        data = base64.b64decode(text)
        return data.decode("utf-8")
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
        return ""


def to_bool(obj: Any) -> bool:
    """Convert object to boolean."""
    try:
        if isinstance(obj, bool):
            return obj
        if isinstance(obj, str):
            return obj.lower() in ("true", "1", "yes")
        return bool(obj)
    except Exception:
        return False


def to_string(obj: Any) -> str:
    """Convert object to string."""
    try:
        return str(obj) if obj is not None else ""
    except Exception:
        return ""


def human_fy(amount: int) -> str:
    """Human-readable file size."""
    if amount <= 0:
        return f"{amount:.1f} B"

    units = ["KB", "MB", "GB", "TB", "PB"]
    unit_index = 0
    size = float(amount)

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    return f"{size:.1f} {units[unit_index]}"


def url_encode(url: str) -> str:
    """URL encode a string."""
    return quote(url, safe="")


def url_decode(url: str) -> str:
    """URL decode a string."""
    return unquote(url)


def parse_query_string(query: str) -> dict[str, str]:
    """Parse a URL query string into a dictionary.

    Args:
        query: Query string (with or without leading '?')

    Returns:
        Case-insensitive dictionary of parameters
    """
    result: dict[str, str] = {}
    if not query:
        return result

    if query.startswith("?"):
        query = query[1:]

    parts = query.split("&")
    for part in parts:
        if not part:
            continue
        kv = part.split("=", 1)
        if len(kv) != 2:
            continue
        key = unquote(kv[0])
        val = unquote(kv[1])
        if key.lower() not in {k.lower() for k in result}:
            result[key] = val

    return result


def get_md5(s: str) -> str:
    """Get MD5 hash of a string."""
    if not s:
        return ""
    try:
        return hashlib.md5(s.encode("utf-8")).hexdigest()
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
        return ""


def get_file_hash(file_path: str) -> str:
    """Get MD5 hash of a file."""
    if not file_path or not os.path.exists(file_path):
        return ""
    try:
        h = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
        return ""


def get_punycode(url: str) -> str:
    """Convert internationalized domain names to punycode."""
    if not url:
        return url
    try:
        parsed = urlparse(url)
        if parsed.hostname:
            idn_host = parsed.hostname.encode("idna").decode("ascii")
            if parsed.hostname != idn_host:
                return url.replace(parsed.hostname, idn_host)
        return url
    except Exception:
        return url


def is_base64_string(plain_text: str | None) -> bool:
    """Check if a string is valid base64."""
    if not plain_text or not plain_text.strip():
        return False
    try:
        base64.b64decode(plain_text, validate=True)
        return True
    except Exception:
        return False


def convert2comma(text: str) -> str:
    """Convert Chinese comma and newlines to comma."""
    if not text:
        return text
    return text.replace("\uff0c", ",").replace("\r\n", ",").replace("\n", ",")


def get_enum_names(enum_class: type) -> list[str]:
    """Get list of enum member names."""
    return [e.name for e in enum_class]


def parse_hosts_to_dictionary(hosts_content: str | None) -> dict[str, list[str]]:
    """Parse hosts file content to a dictionary."""
    if not hosts_content:
        return {}

    result: dict[str, list[str]] = {}
    for line in hosts_content.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Remove inline comments
        comment_idx = line.find("#")
        if comment_idx >= 0:
            line = line[:comment_idx].strip()
        if not line or " " not in line and "\t" not in line:
            continue

        parts = line.split()
        if len(parts) < 2:
            continue

        key = parts[0]
        values = parts[1:]
        if key in result:
            result[key].extend(values)
        else:
            result[key] = values

    return result


def parse_url(url: str) -> tuple[str, str, int, str]:
    """Parse a URL into (domain, scheme, port, path).

    Args:
        url: URL string

    Returns:
        Tuple of (domain, scheme, port, path)
    """
    if not url or not url.strip():
        return ("", "", 0, "")

    # Try standard URL parsing
    try:
        parsed = urlparse(url)
        if parsed.hostname:
            port = parsed.port or 0
            path = parsed.path
            if parsed.query:
                path += f"?{parsed.query}"
            return (parsed.hostname, parsed.scheme, port, path)
    except Exception:
        pass

    # Regex fallback for non-standard URLs
    match = re.match(r"^(?:([a-zA-Z][a-zA-Z0-9+.-]*):/{2,})?([^/?#]+)([^?#]*)?.*$", url)
    if match:
        scheme = match.group(1) or ""
        authority = match.group(2) or ""
        path = match.group(3) or ""

        # Remove userinfo
        at_idx = authority.rfind("@")
        if at_idx > 0:
            authority = authority[at_idx + 1:]

        domain, port = _parse_authority(authority)
        if domain:
            return (domain, scheme, port, path)

    return (url, "", 0, "")


def _parse_authority(authority: str) -> tuple[str, int]:
    """Parse domain and port from authority string."""
    if not authority:
        return ("", 0)

    port = 0
    domain = authority

    if authority.startswith("[") and "]" in authority:
        # IPv6 handling
        closing = authority.rfind("]")
        if closing < len(authority) - 1 and authority[closing + 1] == ":":
            port_str = authority[closing + 2:]
            try:
                port = int(port_str)
            except ValueError:
                pass
            domain = authority[: closing + 1]
        else:
            domain = authority
    else:
        last_colon = authority.rfind(":")
        if last_colon > 0 and last_colon < len(authority) - 1:
            port_str = authority[last_colon + 1:]
            if port_str.isdigit():
                try:
                    port = int(port_str)
                    domain = authority[:last_colon]
                except ValueError:
                    pass

    return (domain, port)


def domain_strategy_4sbox(strategy: str | None) -> str | None:
    """Convert V2Ray domain strategy to Sing-box format."""
    if strategy is None:
        return None
    if strategy.startswith("UseIPv4"):
        return "prefer_ipv4"
    if strategy.startswith("UseIPv6"):
        return "prefer_ipv6"
    if strategy.startswith("ForceIPv4"):
        return "ipv4_only"
    if strategy.startswith("ForceIPv6"):
        return "ipv6_only"
    return None


# ============================================================================
# Data Checks
# ============================================================================


def is_numeric(text: str) -> bool:
    """Check if string is all digits."""
    return text.isdigit()


def is_domain(domain: str | None) -> bool:
    """Validate domain name."""
    if not domain or not domain.strip():
        return False

    # Check for file extensions
    ext = os.path.splitext(domain)[1]
    if ext:
        ext_lower = ext[1:].lower()
        if ext_lower in ("json", "txt", "xml", "cfg", "ini", "log", "yaml", "yml", "toml"):
            return False

    # Simple domain validation
    pattern = r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
    return bool(re.match(pattern, domain))


def is_ipv6(ip: str) -> bool:
    """Check if an IP address is IPv6."""
    try:
        addr = ipaddress.ip_address(ip)
        return isinstance(addr, ipaddress.IPv6Address)
    except ValueError:
        return False


def is_ip_address(ip: str | None) -> bool:
    """Check if a string is a valid IP address."""
    if not ip or not ip.strip():
        return False
    try:
        ip = ip.strip()
        addr = ipaddress.ip_address(ip)
        # For IPv4, ensure it has exactly 3 dots
        if isinstance(addr, ipaddress.IPv4Address):
            return ip.count(".") == 3
        return True
    except ValueError:
        return False


def try_uri(url: str) -> Any | None:
    """Try to parse a URL."""
    try:
        result = urlparse(url)
        if result.scheme and result.netloc:
            return result
        return None
    except Exception:
        return None


def is_private_network(ip: str) -> bool:
    """Check if an IP address is in a private/local range."""
    try:
        addr = ipaddress.ip_address(ip)
        return addr.is_private or addr.is_loopback
    except ValueError:
        return False


# ============================================================================
# Network / Port Functions
# ============================================================================


def port_in_use(port: int) -> bool:
    """Check if a port is currently in use."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            result = s.connect_ex(("127.0.0.1", port))
            return result == 0
    except Exception:
        return False


def get_free_port(default_port: int = 0) -> int:
    """Get a free TCP port.

    Args:
        default_port: Preferred port to use if available

    Returns:
        Available port number
    """
    try:
        if default_port != 0 and not port_in_use(default_port):
            return default_port

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 0))
            return s.getsockname()[1]
    except Exception:
        return 59090


# ============================================================================
# File / Path Functions
# ============================================================================


def startup_path() -> str:
    """Get the application startup directory."""
    return os.path.dirname(os.path.abspath(sys.argv[0]))


def get_exe_path() -> str:
    """Get the current executable path."""
    return sys.executable


def get_base_directory() -> str:
    """Get the base directory for the application."""
    return startup_path()


def get_bin_path(name: str = "") -> str:
    """Get the bin directory path."""
    path = os.path.join(get_base_directory(), "bin")
    if name:
        path = os.path.join(path, name)
    os.makedirs(os.path.dirname(path) if name else path, exist_ok=True)
    return path


def get_bin_config_path(name: str = "") -> str:
    """Get the bin config directory path."""
    path = os.path.join(get_base_directory(), "bin")
    if name:
        path = os.path.join(path, name)
    return path


def get_log_path(name: str = "") -> str:
    """Get the log directory path."""
    path = os.path.join(get_base_directory(), "guiLogs")
    if name:
        path = os.path.join(path, name)
    os.makedirs(os.path.dirname(path) if name else path, exist_ok=True)
    return path


def get_config_path(name: str = "") -> str:
    """Get the config directory path."""
    path = os.path.join(get_base_directory(), "guiConfigs")
    if name:
        path = os.path.join(path, name)
    os.makedirs(os.path.dirname(path) if name else path, exist_ok=True)
    return path


def get_temp_path(name: str = "") -> str:
    """Get the temp directory path."""
    path = os.path.join(get_base_directory(), "guiTemps")
    if name:
        path = os.path.join(path, name)
    os.makedirs(os.path.dirname(path) if name else path, exist_ok=True)
    return path


def get_backup_path(name: str = "") -> str:
    """Get the backup directory path."""
    path = os.path.join(get_base_directory(), "guiBackups")
    if name:
        path = os.path.join(path, name)
    os.makedirs(os.path.dirname(path) if name else path, exist_ok=True)
    return path


def get_fonts_path(name: str = "") -> str:
    """Get the fonts directory path."""
    path = os.path.join(get_base_directory(), "guiFonts")
    if name:
        path = os.path.join(path, name)
    return path


def get_exe_name(name: str) -> str:
    """Get executable name with platform extension."""
    if sys.platform == "win32":
        return f"{name}.exe"
    return name


# ============================================================================
# Miscellaneous
# ============================================================================


def get_version(full: bool = True) -> str:
    """Get application version string."""
    from v2rayn import __version__
    from v2rayn.global_config import APP_NAME

    try:
        arch = platform.machine()
        if full:
            return f"{APP_NAME} - V{__version__} - {arch}"
        return f"{APP_NAME}/{__version__}"
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
        return APP_NAME


def get_version_info() -> str:
    """Get version number string."""
    from v2rayn import __version__

    return __version__


def get_runtime_info() -> str:
    """Get runtime information string."""
    return f"{get_version()} | {startup_path()} | {get_exe_path()} | {platform.platform()}"


def get_guid(full: bool = True) -> str:
    """Generate a GUID/UUID string."""
    try:
        if full:
            return str(uuid.uuid4())
        return str(struct.unpack("q", uuid.uuid4().bytes[:8])[0])
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
        return ""


def is_guid_by_parse(src: str) -> bool:
    """Check if a string is a valid GUID/UUID."""
    try:
        uuid.UUID(src)
        return True
    except (ValueError, AttributeError):
        return False


def get_system_hosts(host_file: str | None = None) -> dict[str, str]:
    """Read system hosts file into a dictionary."""
    system_hosts: dict[str, str] = {}
    if host_file is None:
        if sys.platform == "win32":
            host_file = r"C:\Windows\System32\drivers\etc\hosts"
        else:
            host_file = "/etc/hosts"

    try:
        if not os.path.exists(host_file):
            return system_hosts

        with open(host_file, "r", encoding="utf-8") as f:
            content = f.read()

        for line in content.split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Remove inline comments
            comment_idx = line.find("#")
            if comment_idx >= 0:
                line = line[:comment_idx].strip()
            if not line:
                continue

            parts = line.split()
            if len(parts) < 2:
                continue

            ip_addr = parts[0]
            domain_name = parts[1]

            if not is_ip_address(ip_addr):
                continue

            system_hosts[domain_name] = ip_addr
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)

    return system_hosts


def is_admin_account() -> bool:
    """Check if the current process has admin privileges."""
    try:
        if sys.platform == "win32":
            import ctypes

            return ctypes.windll.shell32.IsUserAnAdmin() != 0  # type: ignore[attr-defined]
        else:
            return os.geteuid() == 0
    except Exception:
        return False


async def set_linux_chmod(file_path: str) -> None:
    """Set execute permissions on a Linux file."""
    import asyncio
    import stat

    try:
        st = os.stat(file_path)
        os.chmod(file_path, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)


def is_windows() -> bool:
    """Check if running on Windows."""
    return sys.platform == "win32"


def is_linux() -> bool:
    """Check if running on Linux."""
    return sys.platform == "linux"


def is_osx() -> bool:
    """Check if running on macOS."""
    return sys.platform == "darwin"


def auto_start_check() -> bool:
    """Check if auto-start is enabled."""
    if is_windows():
        try:
            import winreg

            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_READ,
            )
            try:
                winreg.QueryValueEx(key, "v2rayNAutoRun")
                return True
            except FileNotFoundError:
                return False
            finally:
                winreg.CloseKey(key)
        except Exception:
            return False
    return False


def auto_start_set(enable: bool) -> None:
    """Enable or disable auto-start."""
    if is_windows():
        try:
            import winreg

            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE,
            )
            if enable:
                winreg.SetValueEx(key, "v2rayNAutoRun", 0, winreg.REG_SZ, get_exe_path())
            else:
                try:
                    winreg.DeleteValue(key, "v2rayNAutoRun")
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)
