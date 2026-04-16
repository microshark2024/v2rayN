"""SOCKS protocol format handler.

Ported from ServiceLib/Handler/Fmt/SocksFmt.cs.
"""

from __future__ import annotations

from urllib.parse import urlparse

from v2rayn.common import logging_config
from v2rayn.common.utils import base64_decode, parse_query_string, url_decode, url_encode
from v2rayn.enums.config_type import EConfigType
from v2rayn.global_config import PROTOCOL_SHARES
from v2rayn.handler.fmt.base_fmt import get_ipv6
from v2rayn.models.profile_item import ProfileItem

_tag = "SocksFmt"


def resolve(str_data: str) -> ProfileItem | None:
    """Resolve a SOCKS URI to ProfileItem."""
    try:
        prefix = PROTOCOL_SHARES.get(EConfigType.SOCKS, "socks://")
        uri_str = str_data.replace(prefix, "http://")
        parsed = urlparse(uri_str)

        if not parsed.hostname:
            return None

        item = ProfileItem()
        item.config_type = EConfigType.SOCKS
        item.address = parsed.hostname
        item.port = parsed.port or 0
        item.remarks = url_decode(parsed.fragment) if parsed.fragment else ""

        # Handle credentials
        if parsed.username:
            user_info = url_decode(parsed.username)
            if parsed.password:
                item.username = user_info
                item.password = url_decode(parsed.password)
            else:
                # May be base64 encoded user:pass
                decoded = base64_decode(user_info)
                if ":" in decoded:
                    parts = decoded.split(":", 1)
                    item.username = parts[0]
                    item.password = parts[1]

        return item
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
        return None


def to_uri(item: ProfileItem) -> str | None:
    """Generate a SOCKS share URI."""
    try:
        remark = f"#{url_encode(item.remarks)}" if item.remarks else ""
        user_info = ""
        if item.username or item.password:
            user_info = f"{url_encode(item.username or '')}:{url_encode(item.password or '')}@"

        prefix = PROTOCOL_SHARES.get(EConfigType.SOCKS, "socks://")
        return f"{prefix}{user_info}{get_ipv6(item.address)}:{item.port}{remark}"
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
        return None
