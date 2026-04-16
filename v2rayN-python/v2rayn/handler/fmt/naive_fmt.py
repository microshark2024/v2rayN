"""Naive protocol format handler.

Ported from ServiceLib/Handler/Fmt/NaiveFmt.cs.
"""

from __future__ import annotations

from urllib.parse import urlparse

from v2rayn.common import logging_config
from v2rayn.common.extensions import is_not_empty
from v2rayn.common.utils import parse_query_string, url_decode, url_encode
from v2rayn.enums.config_type import EConfigType
from v2rayn.global_config import NAIVE_HTTPS_PROTOCOL_SHARE, NAIVE_QUIC_PROTOCOL_SHARE, PROTOCOL_SHARES
from v2rayn.handler.fmt.base_fmt import get_ipv6
from v2rayn.models.profile_item import ProfileItem, ProtocolExtraItem

_tag = "NaiveFmt"


def resolve(str_data: str) -> ProfileItem | None:
    """Resolve a Naive URI to ProfileItem."""
    try:
        # Determine if QUIC transport
        is_quic = str_data.startswith(NAIVE_QUIC_PROTOCOL_SHARE)

        # Normalize the URL for parsing
        uri_str = str_data
        for prefix in (NAIVE_HTTPS_PROTOCOL_SHARE, NAIVE_QUIC_PROTOCOL_SHARE,
                       PROTOCOL_SHARES.get(EConfigType.Naive, "naive://")):
            if uri_str.startswith(prefix):
                uri_str = "http://" + uri_str[len(prefix):]
                break

        parsed = urlparse(uri_str)
        if not parsed.hostname:
            return None

        item = ProfileItem()
        item.config_type = EConfigType.Naive
        item.address = parsed.hostname
        item.port = parsed.port or 0
        item.remarks = url_decode(parsed.fragment) if parsed.fragment else ""

        if parsed.username:
            item.username = url_decode(parsed.username)
        if parsed.password:
            item.password = url_decode(parsed.password)

        query = parse_query_string(parsed.query if parsed.query else "")

        extra = ProtocolExtraItem()
        extra.naive_quic = is_quic

        concurrency = query.get("insecure-concurrency", "")
        if concurrency:
            try:
                extra.insecure_concurrency = int(concurrency)
            except ValueError:
                pass

        item.set_protocol_extra(extra)

        return item
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
        return None


def to_uri(item: ProfileItem) -> str | None:
    """Generate a Naive share URI."""
    try:
        extra = item.get_protocol_extra()

        prefix = NAIVE_QUIC_PROTOCOL_SHARE if extra.naive_quic else NAIVE_HTTPS_PROTOCOL_SHARE

        user_info = ""
        if item.username or item.password:
            user_info = f"{url_encode(item.username or '')}:{url_encode(item.password or '')}@"

        remark = f"#{url_encode(item.remarks)}" if item.remarks else ""

        return f"{prefix}{user_info}{get_ipv6(item.address)}:{item.port}{remark}"
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
        return None
