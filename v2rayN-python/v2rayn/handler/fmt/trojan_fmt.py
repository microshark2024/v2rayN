"""Trojan protocol format handler.

Ported from ServiceLib/Handler/Fmt/TrojanFmt.cs.
"""

from __future__ import annotations

from urllib.parse import urlparse

from v2rayn.common import logging_config
from v2rayn.common.extensions import is_not_empty
from v2rayn.common.utils import parse_query_string, url_decode, url_encode
from v2rayn.enums.config_type import EConfigType
from v2rayn.global_config import PROTOCOL_SHARES, STREAM_SECURITY
from v2rayn.handler.fmt.base_fmt import resolve_uri_query, to_uri, to_uri_query
from v2rayn.models.profile_item import ProfileItem, ProtocolExtraItem

_tag = "TrojanFmt"


def resolve(str_data: str) -> ProfileItem | None:
    """Resolve a Trojan URI to ProfileItem."""
    try:
        prefix = PROTOCOL_SHARES.get(EConfigType.Trojan, "trojan://")
        uri_str = str_data.replace(prefix, "http://")
        parsed = urlparse(uri_str)

        if not parsed.hostname:
            return None

        item = ProfileItem()
        item.config_type = EConfigType.Trojan
        item.address = parsed.hostname
        item.port = parsed.port or 0
        item.password = url_decode(parsed.username or "")
        item.remarks = url_decode(parsed.fragment) if parsed.fragment else ""

        query = parse_query_string(parsed.query if parsed.query else "")

        extra = ProtocolExtraItem()
        extra.flow = query.get("flow", "")
        item.set_protocol_extra(extra)

        resolve_uri_query(query, item)

        # Default to TLS if no security is specified
        if not item.stream_security:
            item.stream_security = STREAM_SECURITY

        return item
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
        return None


def to_uri(item: ProfileItem) -> str | None:
    """Generate a Trojan share URI."""
    try:
        dic_query: dict[str, str] = {}

        extra = item.get_protocol_extra()
        if is_not_empty(extra.flow):
            dic_query["flow"] = url_encode(extra.flow)

        to_uri_query(item, STREAM_SECURITY, dic_query)

        remark = f"#{url_encode(item.remarks)}" if item.remarks else ""
        return to_uri(EConfigType.Trojan, item.address, item.port, item.password, dic_query, remark)
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
        return None
