"""TUIC protocol format handler.

Ported from ServiceLib/Handler/Fmt/TuicFmt.cs.
"""

from __future__ import annotations

from urllib.parse import urlparse

from v2rayn.common import logging_config
from v2rayn.common.extensions import is_not_empty
from v2rayn.common.utils import parse_query_string, url_decode, url_encode
from v2rayn.enums.config_type import EConfigType
from v2rayn.global_config import PROTOCOL_SHARES, STREAM_SECURITY
from v2rayn.handler.fmt.base_fmt import get_ipv6, to_uri_query_lite
from v2rayn.models.profile_item import ProfileItem, ProtocolExtraItem

_tag = "TuicFmt"


def resolve(str_data: str) -> ProfileItem | None:
    """Resolve a TUIC URI to ProfileItem."""
    try:
        prefix = PROTOCOL_SHARES.get(EConfigType.TUIC, "tuic://")
        uri_str = str_data.replace(prefix, "http://")
        parsed = urlparse(uri_str)

        if not parsed.hostname:
            return None

        item = ProfileItem()
        item.config_type = EConfigType.TUIC
        item.address = parsed.hostname
        item.port = parsed.port or 0
        item.password = url_decode(parsed.username or "")
        item.remarks = url_decode(parsed.fragment) if parsed.fragment else ""
        item.stream_security = STREAM_SECURITY

        # TUIC uses username:password format (UUID:password)
        if parsed.password:
            item.password = url_decode(parsed.username or "")
            # Store the actual password in the password field, UUID in the id-like field
            # TUIC format: uuid:password@host:port
            raw_password = url_decode(parsed.password)
            item.password = f"{url_decode(parsed.username or '')}:{raw_password}"

        query = parse_query_string(parsed.query if parsed.query else "")

        item.sni = query.get("sni", "")
        item.alpn = url_decode(query.get("alpn", ""))

        extra = ProtocolExtraItem()
        extra.congestion_control = query.get("congestion_control", "bbr")
        item.set_protocol_extra(extra)

        return item
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
        return None


def to_uri(item: ProfileItem) -> str | None:
    """Generate a TUIC share URI."""
    try:
        dic_query: dict[str, str] = {}

        to_uri_query_lite(item, dic_query)

        extra = item.get_protocol_extra()
        if is_not_empty(extra.congestion_control):
            dic_query["congestion_control"] = url_encode(extra.congestion_control)

        query = "?" + "&".join(f"{k}={v}" for k, v in dic_query.items()) if dic_query else ""
        remark = f"#{url_encode(item.remarks)}" if item.remarks else ""

        prefix = PROTOCOL_SHARES.get(EConfigType.TUIC, "tuic://")
        return f"{prefix}{url_encode(item.password)}@{get_ipv6(item.address)}:{item.port}{query}{remark}"
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
        return None
