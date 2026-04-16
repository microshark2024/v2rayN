"""Shadowsocks protocol format handler.

Ported from ServiceLib/Handler/Fmt/ShadowsocksFmt.cs.
"""

from __future__ import annotations

from urllib.parse import urlparse

from v2rayn.common import json_utils, logging_config
from v2rayn.common.extensions import is_not_empty
from v2rayn.common.utils import base64_decode, base64_encode, parse_query_string, url_decode, url_encode
from v2rayn.enums.config_type import EConfigType
from v2rayn.global_config import PROTOCOL_SHARES
from v2rayn.handler.fmt.base_fmt import get_ipv6, resolve_uri_query, to_uri_query
from v2rayn.models.profile_item import ProfileItem, ProtocolExtraItem

_tag = "ShadowsocksFmt"


def resolve(str_data: str) -> ProfileItem | None:
    """Resolve a Shadowsocks URI to ProfileItem."""
    try:
        prefix = PROTOCOL_SHARES.get(EConfigType.Shadowsocks, "ss://")
        raw = str_data[len(prefix):]

        # Try SIP002 format first
        result = _resolve_sip002(str_data)
        if result:
            return result

        # Try legacy format
        return _resolve_legacy(raw)
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
        return None


def _resolve_sip002(str_data: str) -> ProfileItem | None:
    """Resolve SIP002 format."""
    try:
        prefix = PROTOCOL_SHARES.get(EConfigType.Shadowsocks, "ss://")
        uri_str = str_data.replace(prefix, "http://")
        parsed = urlparse(uri_str)

        if not parsed.hostname or not parsed.username:
            return None

        item = ProfileItem()
        item.config_type = EConfigType.Shadowsocks
        item.address = parsed.hostname
        item.port = parsed.port or 0
        item.remarks = url_decode(parsed.fragment) if parsed.fragment else ""

        # Username may be base64 encoded method:password
        user_info = url_decode(parsed.username)
        if parsed.password:
            user_info += f":{url_decode(parsed.password)}"

        decoded = base64_decode(user_info) if ":" not in user_info else user_info
        if ":" in decoded:
            parts = decoded.split(":", 1)
            extra = ProtocolExtraItem()
            extra.ss_method = parts[0]
            item.password = parts[1]
            item.set_protocol_extra(extra)
        else:
            return None

        # Parse query parameters
        if parsed.query:
            query = parse_query_string(parsed.query)
            plugin = query.get("plugin", "")
            if plugin:
                _resolve_plugin(plugin, item)

        return item
    except Exception:
        return None


def _resolve_legacy(raw: str) -> ProfileItem | None:
    """Resolve legacy Shadowsocks format."""
    try:
        # Split by # for remarks
        remark = ""
        if "#" in raw:
            raw, remark = raw.rsplit("#", 1)
            remark = url_decode(remark)

        decoded = base64_decode(raw)
        if not decoded or ":" not in decoded or "@" not in decoded:
            return None

        # Format: method:password@host:port
        method_pass, host_port = decoded.rsplit("@", 1)
        method, password = method_pass.split(":", 1)

        if ":" in host_port:
            host, port_str = host_port.rsplit(":", 1)
        else:
            return None

        item = ProfileItem()
        item.config_type = EConfigType.Shadowsocks
        item.address = host.strip("[]")
        item.port = int(port_str)
        item.password = password
        item.remarks = remark

        extra = ProtocolExtraItem()
        extra.ss_method = method
        item.set_protocol_extra(extra)

        return item
    except Exception:
        return None


def _resolve_plugin(plugin: str, item: ProfileItem) -> None:
    """Resolve Shadowsocks plugin settings."""
    # Plugin format: plugin_name;key=value;key=value
    parts = plugin.split(";")
    if not parts:
        return

    plugin_name = parts[0]
    opts: dict[str, str] = {}
    for part in parts[1:]:
        if "=" in part:
            k, v = part.split("=", 1)
            opts[k] = v

    if plugin_name in ("obfs-local", "simple-obfs"):
        obfs_type = opts.get("obfs", "http")
        if obfs_type == "http":
            item.network = "tcp"
            item.header_type = "http"
        elif obfs_type == "tls":
            item.stream_security = "tls"
        item.request_host = opts.get("obfs-host", "")

    elif plugin_name == "v2ray-plugin":
        mode = opts.get("mode", "")
        if mode == "websocket" or "ws" in mode:
            item.network = "ws"
        elif mode == "quic":
            item.network = "quic"
        if "tls" in opts:
            item.stream_security = "tls"
        item.request_host = opts.get("host", "")
        item.path = opts.get("path", "")


def to_uri(item: ProfileItem) -> str | None:
    """Generate a Shadowsocks share URI."""
    try:
        extra = item.get_protocol_extra()
        method = extra.ss_method or "aes-256-gcm"

        user_info = base64_encode(f"{method}:{item.password}")
        remark = f"#{url_encode(item.remarks)}" if item.remarks else ""

        prefix = PROTOCOL_SHARES.get(EConfigType.Shadowsocks, "ss://")
        return f"{prefix}{user_info}@{get_ipv6(item.address)}:{item.port}{remark}"
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
        return None


def resolve_sip008(str_data: str) -> list[ProfileItem]:
    """Resolve SIP008 multi-server JSON format."""
    results: list[ProfileItem] = []
    try:
        data = json_utils.parse_json(str_data)
        if not data or not isinstance(data, dict):
            return results

        servers = data.get("servers", [])
        for server in servers:
            item = ProfileItem()
            item.config_type = EConfigType.Shadowsocks
            item.address = server.get("server", "")
            item.port = int(server.get("server_port", 0))
            item.password = server.get("password", "")
            item.remarks = server.get("remarks", "")

            extra = ProtocolExtraItem()
            extra.ss_method = server.get("method", "")
            item.set_protocol_extra(extra)

            results.append(item)
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)

    return results
