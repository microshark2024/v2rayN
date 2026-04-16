"""Hysteria2 protocol format handler.

Ported from ServiceLib/Handler/Fmt/Hysteria2Fmt.cs.
"""

from __future__ import annotations

from urllib.parse import urlparse

from v2rayn.common import logging_config
from v2rayn.common.extensions import is_not_empty
from v2rayn.common.utils import parse_query_string, url_decode, url_encode
from v2rayn.enums.config_type import EConfigType
from v2rayn.global_config import HYSTERIA2_PROTOCOL_SHARE, PROTOCOL_SHARES, STREAM_SECURITY
from v2rayn.handler.fmt.base_fmt import get_ipv6, to_uri_query_lite
from v2rayn.models.profile_item import ProfileItem, ProtocolExtraItem

_tag = "Hysteria2Fmt"


def resolve(str_data: str) -> ProfileItem | None:
    """Resolve a Hysteria2 URI to ProfileItem."""
    try:
        prefix = PROTOCOL_SHARES.get(EConfigType.Hysteria2, "hysteria2://")
        uri_str = str_data
        for p in (prefix, HYSTERIA2_PROTOCOL_SHARE):
            if uri_str.startswith(p):
                uri_str = "http://" + uri_str[len(p):]
                break

        parsed = urlparse(uri_str)
        if not parsed.hostname:
            return None

        item = ProfileItem()
        item.config_type = EConfigType.Hysteria2
        item.address = parsed.hostname
        item.port = parsed.port or 0
        item.password = url_decode(parsed.username or "")
        item.remarks = url_decode(parsed.fragment) if parsed.fragment else ""
        item.stream_security = STREAM_SECURITY

        query = parse_query_string(parsed.query if parsed.query else "")

        item.sni = query.get("sni", "")
        item.alpn = url_decode(query.get("alpn", ""))
        item.cert_sha = url_decode(query.get("pcs", query.get("pinSHA256", "")))

        # Allow insecure
        insecure = query.get("insecure", "0")
        if insecure == "1":
            item.allow_insecure = "true"

        extra = ProtocolExtraItem()
        obfs = query.get("obfs", "")
        if obfs == "salamander":
            extra.salamander_pass = url_decode(query.get("obfs-password", ""))
        extra.ports = url_decode(query.get("mport", ""))
        item.set_protocol_extra(extra)

        return item
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
        return None


def to_uri(item: ProfileItem) -> str | None:
    """Generate a Hysteria2 share URI."""
    try:
        dic_query: dict[str, str] = {}

        to_uri_query_lite(item, dic_query)

        extra = item.get_protocol_extra()
        if is_not_empty(extra.salamander_pass):
            dic_query["obfs"] = "salamander"
            dic_query["obfs-password"] = url_encode(extra.salamander_pass)
        if is_not_empty(extra.ports):
            dic_query["mport"] = url_encode(extra.ports)
        if is_not_empty(item.cert_sha):
            dic_query["pinSHA256"] = url_encode(item.cert_sha)

        query = "?" + "&".join(f"{k}={v}" for k, v in dic_query.items()) if dic_query else ""
        remark = f"#{url_encode(item.remarks)}" if item.remarks else ""

        prefix = PROTOCOL_SHARES.get(EConfigType.Hysteria2, "hysteria2://")
        return f"{prefix}{url_encode(item.password)}@{get_ipv6(item.address)}:{item.port}{query}{remark}"
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
        return None
