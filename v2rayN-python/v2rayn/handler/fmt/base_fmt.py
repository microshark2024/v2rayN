"""Base format handler.

Ported from ServiceLib/Handler/Fmt/BaseFmt.cs.
Contains common URL parsing and generation utilities for proxy protocol formats.
"""

from __future__ import annotations

import os
from urllib.parse import quote, unquote

from v2rayn.common import json_utils, logging_config
from v2rayn.common.extensions import is_not_empty
from v2rayn.common.utils import is_ipv6, url_decode, url_encode
from v2rayn.enums.config_type import EConfigType
from v2rayn.enums.transport import ETransport
from v2rayn.global_config import (
    ALLOW_INSECURE,
    GRPC_GUN_MODE,
    GRPC_MULTI_MODE,
    NONE,
    PROTOCOL_SHARES,
    STREAM_SECURITY,
    XHTTP_MODE,
)
from v2rayn.models.profile_item import ProfileItem

_tag = "BaseFmt"
_allow_insecure_array = ["insecure", "allowInsecure", "allow_insecure"]


def get_ipv6(address: str) -> str:
    """Format IPv6 address with brackets."""
    if is_ipv6(address):
        if address.startswith("[") and address.endswith("]"):
            return address
        return f"[{address}]"
    return address


def to_uri_query(item: ProfileItem, security_def: str | None, dic_query: dict[str, str]) -> int:
    """Convert ProfileItem transport/security settings to URI query parameters.

    Args:
        item: Profile item
        security_def: Default security value
        dic_query: Dictionary to populate with query parameters

    Returns:
        0 on success
    """
    if is_not_empty(item.stream_security):
        dic_query["security"] = item.stream_security
    elif security_def is not None:
        dic_query["security"] = security_def

    if is_not_empty(item.sni):
        dic_query["sni"] = url_encode(item.sni)
    if is_not_empty(item.fingerprint):
        dic_query["fp"] = url_encode(item.fingerprint)
    if is_not_empty(item.public_key):
        dic_query["pbk"] = url_encode(item.public_key)
    if is_not_empty(item.short_id):
        dic_query["sid"] = url_encode(item.short_id)
    if is_not_empty(item.spider_x):
        dic_query["spx"] = url_encode(item.spider_x)
    if is_not_empty(item.mldsa65_verify):
        dic_query["pqv"] = url_encode(item.mldsa65_verify)

    if item.stream_security == STREAM_SECURITY:
        if is_not_empty(item.alpn):
            dic_query["alpn"] = url_encode(item.alpn)
        _to_uri_query_allow_insecure(item, dic_query)

    if is_not_empty(item.ech_config_list):
        dic_query["ech"] = url_encode(item.ech_config_list)
    if is_not_empty(item.cert_sha):
        dic_query["pcs"] = url_encode(item.cert_sha)
    if is_not_empty(item.finalmask):
        node = json_utils.parse_json(item.finalmask)
        finalmask = json_utils.serialize(node, indented=False, null_value=True) if node else item.finalmask
        dic_query["fm"] = url_encode(finalmask)

    dic_query["type"] = item.network if is_not_empty(item.network) else "tcp"

    network = item.network
    if network == "tcp":
        dic_query["headerType"] = item.header_type if is_not_empty(item.header_type) else NONE
        if is_not_empty(item.request_host):
            dic_query["host"] = url_encode(item.request_host)

    elif network == "kcp":
        dic_query["headerType"] = item.header_type if is_not_empty(item.header_type) else NONE
        if is_not_empty(item.path):
            dic_query["seed"] = url_encode(item.path)

    elif network in ("ws", "httpupgrade"):
        if is_not_empty(item.request_host):
            dic_query["host"] = url_encode(item.request_host)
        if is_not_empty(item.path):
            dic_query["path"] = url_encode(item.path)

    elif network == "xhttp":
        if is_not_empty(item.request_host):
            dic_query["host"] = url_encode(item.request_host)
        if is_not_empty(item.path):
            dic_query["path"] = url_encode(item.path)
        if is_not_empty(item.header_type) and item.header_type in XHTTP_MODE:
            dic_query["mode"] = url_encode(item.header_type)
        if is_not_empty(item.extra):
            node = json_utils.parse_json(item.extra)
            extra = json_utils.serialize(node, indented=False, null_value=True) if node else item.extra
            dic_query["extra"] = url_encode(extra)

    elif network in ("http", "h2"):
        dic_query["type"] = "http"
        if is_not_empty(item.request_host):
            dic_query["host"] = url_encode(item.request_host)
        if is_not_empty(item.path):
            dic_query["path"] = url_encode(item.path)

    elif network == "quic":
        dic_query["headerType"] = item.header_type if is_not_empty(item.header_type) else NONE
        dic_query["quicSecurity"] = url_encode(item.request_host)
        dic_query["key"] = url_encode(item.path)

    elif network == "grpc":
        if is_not_empty(item.path):
            dic_query["authority"] = url_encode(item.request_host)
            dic_query["serviceName"] = url_encode(item.path)
            if item.header_type in (GRPC_GUN_MODE, GRPC_MULTI_MODE):
                dic_query["mode"] = url_encode(item.header_type)

    return 0


def to_uri_query_lite(item: ProfileItem, dic_query: dict[str, str]) -> int:
    """Convert simplified ProfileItem settings to URI query parameters."""
    if is_not_empty(item.sni):
        dic_query["sni"] = url_encode(item.sni)
    if is_not_empty(item.alpn):
        dic_query["alpn"] = url_encode(item.alpn)
    _to_uri_query_allow_insecure(item, dic_query)
    return 0


def _to_uri_query_allow_insecure(item: ProfileItem, dic_query: dict[str, str]) -> int:
    """Add allow insecure parameters to query."""
    if item.allow_insecure == ALLOW_INSECURE[0]:  # "true"
        dic_query["insecure"] = "1"
        dic_query["allowInsecure"] = "1"
    else:
        dic_query["insecure"] = "0"
        dic_query["allowInsecure"] = "0"
    return 0


def resolve_uri_query(query: dict[str, str], item: ProfileItem) -> int:
    """Parse URI query parameters into ProfileItem.

    Args:
        query: Dictionary of query parameters
        item: ProfileItem to populate

    Returns:
        0 on success
    """
    item.stream_security = _get_query_value(query, "security")
    item.sni = _get_query_value(query, "sni")
    item.alpn = _get_query_decoded(query, "alpn")
    item.fingerprint = _get_query_decoded(query, "fp")
    item.public_key = _get_query_decoded(query, "pbk")
    item.short_id = _get_query_decoded(query, "sid")
    item.spider_x = _get_query_decoded(query, "spx")
    item.mldsa65_verify = _get_query_decoded(query, "pqv")
    item.ech_config_list = _get_query_decoded(query, "ech")
    item.cert_sha = _get_query_decoded(query, "pcs")

    finalmask_decoded = _get_query_decoded(query, "fm")
    if is_not_empty(finalmask_decoded):
        node = json_utils.parse_json(finalmask_decoded)
        item.finalmask = json_utils.serialize(node, indented=True, null_value=True) if node else finalmask_decoded
    else:
        item.finalmask = ""

    # Check allow insecure
    if any(_get_query_decoded(query, k) == "1" for k in _allow_insecure_array):
        item.allow_insecure = ALLOW_INSECURE[0]  # "true"
    elif any(_get_query_decoded(query, k) == "0" for k in _allow_insecure_array):
        item.allow_insecure = ALLOW_INSECURE[1] if len(ALLOW_INSECURE) > 1 else ""  # "false"
    else:
        item.allow_insecure = ""

    item.network = _get_query_value(query, "type", "tcp")
    network = item.network

    if network == "tcp":
        item.header_type = _get_query_value(query, "headerType", NONE)
        item.request_host = _get_query_decoded(query, "host")

    elif network == "kcp":
        item.header_type = _get_query_value(query, "headerType", NONE)
        item.path = _get_query_decoded(query, "seed")

    elif network in ("ws", "httpupgrade"):
        item.request_host = _get_query_decoded(query, "host")
        item.path = _get_query_decoded(query, "path", "/")

    elif network == "xhttp":
        item.request_host = _get_query_decoded(query, "host")
        item.path = _get_query_decoded(query, "path", "/")
        item.header_type = _get_query_decoded(query, "mode")
        extra_decoded = _get_query_decoded(query, "extra")
        if is_not_empty(extra_decoded):
            node = json_utils.parse_json(extra_decoded)
            if node:
                extra_decoded = json_utils.serialize(node, indented=True, null_value=True)
        item.extra = extra_decoded

    elif network in ("http", "h2"):
        item.network = "h2"
        item.request_host = _get_query_decoded(query, "host")
        item.path = _get_query_decoded(query, "path", "/")

    elif network == "quic":
        item.header_type = _get_query_value(query, "headerType", NONE)
        item.request_host = _get_query_value(query, "quicSecurity", NONE)
        item.path = _get_query_decoded(query, "key")

    elif network == "grpc":
        item.request_host = _get_query_decoded(query, "authority")
        item.path = _get_query_decoded(query, "serviceName")
        item.header_type = _get_query_decoded(query, "mode", GRPC_GUN_MODE)

    return 0


def contains(s: str, *args: str) -> bool:
    """Check if string contains all specified substrings (case-insensitive)."""
    s_lower = s.lower()
    return all(item.lower() in s_lower for item in args)


def write_all_text(str_data: str, ext: str = "json") -> str:
    """Write data to a temp file and return the path."""
    from v2rayn.common.utils import get_guid, get_temp_path

    file_name = get_temp_path(f"{get_guid(False)}.{ext}")
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(str_data)
    return file_name


def to_uri(
    config_type: EConfigType,
    address: str,
    port: int | str,
    user_info: str,
    dic_query: dict[str, str] | None = None,
    remark: str | None = None,
) -> str:
    """Build a complete proxy URI string.

    Args:
        config_type: Proxy config type
        address: Server address
        port: Server port
        user_info: User info (password/UUID)
        dic_query: Query parameters
        remark: Remark/comment fragment

    Returns:
        Complete proxy URI
    """
    query = ""
    if dic_query:
        query = "?" + "&".join(f"{k}={v}" for k, v in dic_query.items())

    url = f"{url_encode(user_info)}@{get_ipv6(address)}:{port}"
    return f"{PROTOCOL_SHARES[config_type]}{url}{query}{remark or ''}"


def _get_query_value(query: dict[str, str], key: str, default_value: str = "") -> str:
    """Get a query parameter value (case-insensitive key lookup)."""
    # Try exact match first
    if key in query:
        return query[key]
    # Case-insensitive fallback
    key_lower = key.lower()
    for k, v in query.items():
        if k.lower() == key_lower:
            return v
    return default_value


def _get_query_decoded(query: dict[str, str], key: str, default_value: str = "") -> str:
    """Get a URL-decoded query parameter value."""
    return url_decode(_get_query_value(query, key, default_value))
