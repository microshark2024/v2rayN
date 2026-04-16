"""WireGuard protocol format handler.

Ported from ServiceLib/Handler/Fmt/WireguardFmt.cs.
"""

from __future__ import annotations

from urllib.parse import urlparse

from v2rayn.common import logging_config
from v2rayn.common.extensions import is_not_empty
from v2rayn.common.utils import parse_query_string, url_decode, url_encode
from v2rayn.enums.config_type import EConfigType
from v2rayn.global_config import PROTOCOL_SHARES
from v2rayn.handler.fmt.base_fmt import get_ipv6
from v2rayn.models.profile_item import ProfileItem, ProtocolExtraItem

_tag = "WireguardFmt"


def resolve(str_data: str) -> ProfileItem | None:
    """Resolve a WireGuard URI to ProfileItem."""
    try:
        prefix = PROTOCOL_SHARES.get(EConfigType.WireGuard, "wireguard://")
        uri_str = str_data.replace(prefix, "http://")
        parsed = urlparse(uri_str)

        if not parsed.hostname:
            return None

        item = ProfileItem()
        item.config_type = EConfigType.WireGuard
        item.address = parsed.hostname
        item.port = parsed.port or 0
        item.password = url_decode(parsed.username or "")  # Private key
        item.remarks = url_decode(parsed.fragment) if parsed.fragment else ""

        query = parse_query_string(parsed.query if parsed.query else "")

        extra = ProtocolExtraItem()
        extra.wg_public_key = url_decode(query.get("publickey", ""))
        extra.wg_preshared_key = url_decode(query.get("presharedkey", ""))
        extra.wg_reserved = url_decode(query.get("reserved", ""))
        extra.wg_interface_address = url_decode(query.get("address", ""))
        mtu = query.get("mtu", "")
        if mtu:
            try:
                extra.wg_mtu = int(mtu)
            except ValueError:
                pass
        item.set_protocol_extra(extra)

        return item
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
        return None


def to_uri(item: ProfileItem) -> str | None:
    """Generate a WireGuard share URI."""
    try:
        dic_query: dict[str, str] = {}

        extra = item.get_protocol_extra()
        if is_not_empty(extra.wg_public_key):
            dic_query["publickey"] = url_encode(extra.wg_public_key)
        if is_not_empty(extra.wg_preshared_key):
            dic_query["presharedkey"] = url_encode(extra.wg_preshared_key)
        if is_not_empty(extra.wg_reserved):
            dic_query["reserved"] = url_encode(extra.wg_reserved)
        if is_not_empty(extra.wg_interface_address):
            dic_query["address"] = url_encode(extra.wg_interface_address)
        if extra.wg_mtu and extra.wg_mtu > 0:
            dic_query["mtu"] = str(extra.wg_mtu)

        query = "?" + "&".join(f"{k}={v}" for k, v in dic_query.items()) if dic_query else ""
        remark = f"#{url_encode(item.remarks)}" if item.remarks else ""

        prefix = PROTOCOL_SHARES.get(EConfigType.WireGuard, "wireguard://")
        return f"{prefix}{url_encode(item.password)}@{get_ipv6(item.address)}:{item.port}{query}{remark}"
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
        return None
