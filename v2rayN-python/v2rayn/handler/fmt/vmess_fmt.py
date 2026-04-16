"""VMess protocol format handler.

Ported from ServiceLib/Handler/Fmt/VmessFmt.cs.
"""

from __future__ import annotations

from v2rayn.common import json_utils, logging_config
from v2rayn.common.extensions import is_not_empty
from v2rayn.common.utils import base64_decode, base64_encode, get_guid, parse_query_string, url_decode
from v2rayn.enums.config_type import EConfigType
from v2rayn.global_config import PROTOCOL_SHARES
from v2rayn.handler.fmt.base_fmt import get_ipv6, resolve_uri_query, to_uri_query
from v2rayn.models.misc import VmessQRCode
from v2rayn.models.profile_item import ProfileItem, ProtocolExtraItem

_tag = "VmessFmt"


def resolve(str_data: str) -> ProfileItem | None:
    """Resolve a VMess URI to ProfileItem."""
    try:
        prefix = PROTOCOL_SHARES.get(EConfigType.VMess, "vmess://")
        raw = str_data[len(prefix):]

        # Try standard URL format first
        item = _resolve_standard_url(str_data)
        if item:
            return item

        # Try base64 JSON format
        return _resolve_vmess_json(raw)
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
        return None


def _resolve_vmess_json(raw: str) -> ProfileItem | None:
    """Resolve VMess base64-encoded JSON."""
    try:
        decoded = base64_decode(raw)
        if not decoded:
            return None

        qr_code = json_utils.deserialize(decoded)
        if not qr_code or not isinstance(qr_code, dict):
            return None

        item = ProfileItem()
        item.config_type = EConfigType.VMess
        item.address = qr_code.get("add", "")
        item.port = int(qr_code.get("port", 0))
        item.password = qr_code.get("id", "")
        item.remarks = qr_code.get("ps", "")
        item.network = qr_code.get("net", "tcp")
        item.header_type = qr_code.get("type", "none")
        item.request_host = qr_code.get("host", "")
        item.path = qr_code.get("path", "")
        item.stream_security = qr_code.get("tls", "")
        item.sni = qr_code.get("sni", "")
        item.alpn = qr_code.get("alpn", "")
        item.fingerprint = qr_code.get("fp", "")

        extra = ProtocolExtraItem()
        extra.alter_id = str(qr_code.get("aid", 0))
        extra.vmess_security = qr_code.get("scy", "auto")
        item.set_protocol_extra(extra)

        return item
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
        return None


def _resolve_standard_url(str_data: str) -> ProfileItem | None:
    """Resolve VMess standard URL format (vless-like URL)."""
    try:
        from urllib.parse import urlparse

        prefix = PROTOCOL_SHARES.get(EConfigType.VMess, "vmess://")
        if not str_data.startswith(prefix):
            return None

        uri_str = str_data.replace(prefix, "http://")
        parsed = urlparse(uri_str)
        if not parsed.hostname or not parsed.username:
            return None

        item = ProfileItem()
        item.config_type = EConfigType.VMess
        item.address = parsed.hostname
        item.port = parsed.port or 0
        item.password = url_decode(parsed.username)
        item.remarks = url_decode(parsed.fragment) if parsed.fragment else ""

        query = parse_query_string(parsed.query if parsed.query else "")
        resolve_uri_query(query, item)

        extra = ProtocolExtraItem()
        extra.vmess_security = query.get("encryption", "auto")
        item.set_protocol_extra(extra)

        return item
    except Exception:
        return None


def to_uri(item: ProfileItem) -> str | None:
    """Generate a VMess share URI (base64 JSON format)."""
    try:
        extra = item.get_protocol_extra()

        qr_code = {
            "v": 2,
            "ps": item.remarks,
            "add": item.address,
            "port": item.port,
            "id": item.password,
            "aid": int(extra.alter_id or 0),
            "scy": extra.vmess_security or "auto",
            "net": item.network or "tcp",
            "type": item.header_type or "none",
            "host": item.request_host or "",
            "path": item.path or "",
            "tls": item.stream_security or "",
            "sni": item.sni or "",
            "alpn": item.alpn or "",
            "fp": item.fingerprint or "",
        }

        json_str = json_utils.serialize(qr_code, indented=False, null_value=True)
        return f"{PROTOCOL_SHARES[EConfigType.VMess]}{base64_encode(json_str)}"
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
        return None
