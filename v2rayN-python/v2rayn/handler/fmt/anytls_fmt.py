"""Anytls protocol format handler.

Ported from ServiceLib/Handler/Fmt/AnytlsFmt.cs.
"""

from __future__ import annotations

from urllib.parse import urlparse

from v2rayn.common import logging_config
from v2rayn.common.extensions import is_not_empty
from v2rayn.common.utils import parse_query_string, url_decode, url_encode
from v2rayn.enums.config_type import EConfigType
from v2rayn.global_config import PROTOCOL_SHARES
from v2rayn.handler.fmt.base_fmt import get_ipv6, to_uri_query_lite
from v2rayn.models.profile_item import ProfileItem

_tag = "AnytlsFmt"


def resolve(str_data: str) -> ProfileItem | None:
    """Resolve an Anytls URI to ProfileItem."""
    try:
        prefix = PROTOCOL_SHARES.get(EConfigType.Anytls, "anytls://")
        uri_str = str_data.replace(prefix, "http://")
        parsed = urlparse(uri_str)

        if not parsed.hostname:
            return None

        item = ProfileItem()
        item.config_type = EConfigType.Anytls
        item.address = parsed.hostname
        item.port = parsed.port or 0
        item.password = url_decode(parsed.username or "")
        item.remarks = url_decode(parsed.fragment) if parsed.fragment else ""
        item.stream_security = "tls"

        query = parse_query_string(parsed.query if parsed.query else "")

        item.sni = query.get("sni", "")
        item.fingerprint = url_decode(query.get("fp", ""))
        item.public_key = url_decode(query.get("pbk", ""))
        item.alpn = url_decode(query.get("alpn", ""))

        return item
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
        return None


def to_uri(item: ProfileItem) -> str | None:
    """Generate an Anytls share URI."""
    try:
        dic_query: dict[str, str] = {}

        to_uri_query_lite(item, dic_query)

        if is_not_empty(item.fingerprint):
            dic_query["fp"] = url_encode(item.fingerprint)
        if is_not_empty(item.public_key):
            dic_query["pbk"] = url_encode(item.public_key)

        query = "?" + "&".join(f"{k}={v}" for k, v in dic_query.items()) if dic_query else ""
        remark = f"#{url_encode(item.remarks)}" if item.remarks else ""

        prefix = PROTOCOL_SHARES.get(EConfigType.Anytls, "anytls://")
        return f"{prefix}{url_encode(item.password)}@{get_ipv6(item.address)}:{item.port}{query}{remark}"
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
        return None
