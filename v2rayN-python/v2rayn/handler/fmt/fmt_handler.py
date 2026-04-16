"""Format handler dispatcher.

Ported from ServiceLib/Handler/Fmt/FmtHandler.cs.
Routes proxy URLs to appropriate protocol parsers.
"""

from __future__ import annotations

from v2rayn.common import logging_config
from v2rayn.common.extensions import is_not_empty
from v2rayn.enums.config_type import EConfigType
from v2rayn.global_config import (
    HYSTERIA2_PROTOCOL_SHARE,
    NAIVE_HTTPS_PROTOCOL_SHARE,
    NAIVE_QUIC_PROTOCOL_SHARE,
    PROTOCOL_SHARES,
)
from v2rayn.models.profile_item import ProfileItem

_tag = "FmtHandler"


def resolve_config(str_data: str) -> list[ProfileItem]:
    """Resolve proxy URLs to ProfileItem list.

    Parses one or more proxy URLs (line-separated) and returns the corresponding ProfileItem list.

    Args:
        str_data: Raw proxy URL string (may contain multiple URLs separated by newlines)

    Returns:
        List of resolved ProfileItem objects
    """
    results: list[ProfileItem] = []

    for line in str_data.strip().splitlines():
        line = line.strip()
        if not line:
            continue

        item = resolve_single(line)
        if item:
            results.append(item)

    return results


def resolve_single(str_data: str) -> ProfileItem | None:
    """Resolve a single proxy URL to a ProfileItem.

    Args:
        str_data: Single proxy URL string

    Returns:
        Resolved ProfileItem or None
    """
    from v2rayn.handler.fmt import (
        anytls_fmt,
        clash_fmt,
        html_page_fmt,
        hysteria2_fmt,
        naive_fmt,
        shadowsocks_fmt,
        singbox_fmt,
        socks_fmt,
        trojan_fmt,
        tuic_fmt,
        v2ray_fmt,
        vless_fmt,
        vmess_fmt,
        wireguard_fmt,
    )

    try:
        # Check by protocol prefix
        if str_data.startswith(PROTOCOL_SHARES.get(EConfigType.VMess, "vmess://")):
            return vmess_fmt.resolve(str_data)

        if str_data.startswith(PROTOCOL_SHARES.get(EConfigType.Shadowsocks, "ss://")):
            return shadowsocks_fmt.resolve(str_data)

        if str_data.startswith(PROTOCOL_SHARES.get(EConfigType.SOCKS, "socks://")):
            return socks_fmt.resolve(str_data)

        if str_data.startswith(PROTOCOL_SHARES.get(EConfigType.Trojan, "trojan://")):
            return trojan_fmt.resolve(str_data)

        if str_data.startswith(PROTOCOL_SHARES.get(EConfigType.VLESS, "vless://")):
            return vless_fmt.resolve(str_data)

        if str_data.startswith(PROTOCOL_SHARES.get(EConfigType.Hysteria2, "hysteria2://")) or str_data.startswith(
            HYSTERIA2_PROTOCOL_SHARE
        ):
            return hysteria2_fmt.resolve(str_data)

        if str_data.startswith(PROTOCOL_SHARES.get(EConfigType.TUIC, "tuic://")):
            return tuic_fmt.resolve(str_data)

        if str_data.startswith(PROTOCOL_SHARES.get(EConfigType.WireGuard, "wireguard://")):
            return wireguard_fmt.resolve(str_data)

        if str_data.startswith(PROTOCOL_SHARES.get(EConfigType.Anytls, "anytls://")):
            return anytls_fmt.resolve(str_data)

        if str_data.startswith(PROTOCOL_SHARES.get(EConfigType.Naive, "naive://")) or str_data.startswith(
            NAIVE_HTTPS_PROTOCOL_SHARE
        ) or str_data.startswith(NAIVE_QUIC_PROTOCOL_SHARE):
            return naive_fmt.resolve(str_data)

        # Check for full config formats
        result = v2ray_fmt.resolve_full_config(str_data)
        if result:
            return result

        result = singbox_fmt.resolve_full_config(str_data)
        if result:
            return result

        result = clash_fmt.resolve_full_config(str_data)
        if result:
            return result

        # Check for HTML page
        if html_page_fmt.is_html_page(str_data):
            return None

    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)

    return None


def get_share_uri(item: ProfileItem) -> str | None:
    """Generate a share URI for a ProfileItem.

    Args:
        item: ProfileItem to generate URI for

    Returns:
        Share URI string or None
    """
    from v2rayn.handler.fmt import (
        anytls_fmt,
        hysteria2_fmt,
        naive_fmt,
        shadowsocks_fmt,
        socks_fmt,
        trojan_fmt,
        tuic_fmt,
        vless_fmt,
        vmess_fmt,
        wireguard_fmt,
    )

    try:
        ct = item.config_type
        if ct == EConfigType.VMess:
            return vmess_fmt.to_uri(item)
        if ct == EConfigType.Shadowsocks:
            return shadowsocks_fmt.to_uri(item)
        if ct == EConfigType.SOCKS:
            return socks_fmt.to_uri(item)
        if ct == EConfigType.Trojan:
            return trojan_fmt.to_uri(item)
        if ct == EConfigType.VLESS:
            return vless_fmt.to_uri(item)
        if ct == EConfigType.Hysteria2:
            return hysteria2_fmt.to_uri(item)
        if ct == EConfigType.TUIC:
            return tuic_fmt.to_uri(item)
        if ct == EConfigType.WireGuard:
            return wireguard_fmt.to_uri(item)
        if ct == EConfigType.Anytls:
            return anytls_fmt.to_uri(item)
        if ct == EConfigType.Naive:
            return naive_fmt.to_uri(item)
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)

    return None
