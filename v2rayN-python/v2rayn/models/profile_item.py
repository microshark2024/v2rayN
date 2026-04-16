"""Profile item models.

Ported from ServiceLib/Models/ProfileItem.cs and related files.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from v2rayn.enums.config_type import EConfigType
from v2rayn.enums.core_type import ECoreType
from v2rayn.enums.multiple_load import EMultipleLoad


@dataclass
class ProtocolExtraItem:
    """Protocol-specific extra configuration fields.

    Ported from ServiceLib/Models/ProtocolExtraItem.cs.
    """

    uot: bool | None = None
    congestion_control: str | None = None

    # vmess
    alter_id: str | None = None
    vmess_security: str | None = None

    # vless
    flow: str | None = None
    vless_encryption: str | None = None

    # shadowsocks
    ss_method: str | None = None

    # wireguard
    wg_public_key: str | None = None
    wg_preshared_key: str | None = None
    wg_interface_address: str | None = None
    wg_reserved: str | None = None
    wg_mtu: int | None = None

    # hysteria2
    salamander_pass: str | None = None
    up_mbps: int | None = None
    down_mbps: int | None = None
    ports: str | None = None
    hop_interval: str | None = None

    # naiveproxy
    insecure_concurrency: int | None = None
    naive_quic: bool | None = None

    # group profile
    group_type: str | None = None
    child_items: str | None = None
    sub_child_items: str | None = None
    filter: str | None = None
    multiple_load: EMultipleLoad | None = None


@dataclass
class ProfileItem:
    """Server profile item.

    Ported from ServiceLib/Models/ProfileItem.cs.
    This is the core model representing a single proxy server configuration.
    """

    index_id: str = ""
    config_type: EConfigType = EConfigType.VMess
    core_type: ECoreType | None = None
    config_version: int = 3
    subid: str = ""
    is_sub: bool = True
    pre_socks_port: int | None = None
    display_log: bool = True
    remarks: str = ""
    address: str = ""
    port: int = 0
    password: str = ""
    username: str = ""
    network: str = ""
    header_type: str = ""
    request_host: str = ""
    path: str = ""
    stream_security: str = ""
    allow_insecure: str = ""
    sni: str = ""
    alpn: str = ""
    fingerprint: str = ""
    public_key: str = ""
    short_id: str = ""
    spider_x: str = ""
    mldsa65_verify: str = ""
    extra: str = ""
    mux_enabled: bool | None = None
    cert: str = ""
    cert_sha: str = ""
    ech_config_list: str = ""
    ech_force_query: str = ""
    finalmask: str = ""
    proto_extra: str = ""

    # Deprecated fields (kept for backward compatibility)
    ports: str = ""
    alter_id: int = 0
    flow: str = ""
    id: str = ""
    security: str = ""

    _protocol_extra_cache: ProtocolExtraItem | None = field(default=None, init=False, repr=False)

    def get_summary(self) -> str:
        """Get a human-readable summary of this profile."""
        summary = f"[{self.config_type.name}] "
        if self.is_complex():
            core_name = self.core_type.name if self.core_type else "Unknown"
            summary += f"[{core_name}]{self.remarks}"
        else:
            arr_addr = self.address.split(":") if ":" in self.address else self.address.split(".")
            if len(arr_addr) > 2:
                addr = f"{arr_addr[0]}***{arr_addr[-1]}"
            elif len(arr_addr) > 1:
                addr = f"***{arr_addr[-1]}"
            else:
                addr = self.address
            summary += f"{self.remarks}({addr}:{self.port})"
        return summary

    def get_alpn(self) -> list[str] | None:
        """Get ALPN list from the alpn string."""
        if not self.alpn:
            return None
        return [a.strip() for a in self.alpn.split(",") if a.strip()]

    def get_network(self) -> str:
        """Get the network type, defaulting to 'tcp'."""
        from v2rayn.global_config import DEFAULT_NETWORK, NETWORKS

        if not self.network or self.network not in NETWORKS:
            return DEFAULT_NETWORK
        return self.network.strip()

    def is_complex(self) -> bool:
        """Check if this is a complex config type."""
        return self.config_type.is_complex_type()

    def is_valid(self) -> bool:
        """Validate this profile item."""
        from v2rayn.global_config import (
            FLOWS,
            SS_SECURITIES_IN_SINGBOX,
            STREAM_SECURITY_REALITY,
        )

        if self.is_complex():
            return True

        if not self.address or self.port <= 0 or self.port >= 65536:
            return False

        if self.config_type == EConfigType.VMess:
            if not self.password or not _is_guid(self.password):
                return False

        elif self.config_type == EConfigType.VLESS:
            if not self.password or (not _is_guid(self.password) and len(self.password) > 30):
                return False
            extra = self.get_protocol_extra()
            if (extra.flow or "") not in FLOWS:
                return False

        elif self.config_type == EConfigType.Shadowsocks:
            if not self.password:
                return False
            extra = self.get_protocol_extra()
            if not extra.ss_method or extra.ss_method not in SS_SECURITIES_IN_SINGBOX:
                return False

        if (
            self.config_type in (EConfigType.VLESS, EConfigType.Trojan)
            and self.stream_security == STREAM_SECURITY_REALITY
            and not self.public_key
        ):
            return False

        return True

    def set_protocol_extra(self, extra_item: ProtocolExtraItem) -> None:
        """Set protocol extra data and serialize to JSON."""
        self._protocol_extra_cache = extra_item
        self.proto_extra = json.dumps(
            {k: v for k, v in extra_item.__dict__.items() if v is not None},
            ensure_ascii=False,
        )

    def get_protocol_extra(self) -> ProtocolExtraItem:
        """Get protocol extra data, deserializing from JSON if needed."""
        if self._protocol_extra_cache is not None:
            return self._protocol_extra_cache
        if self.proto_extra:
            try:
                data = json.loads(self.proto_extra)
                self._protocol_extra_cache = ProtocolExtraItem(**{
                    k: v for k, v in data.items()
                    if hasattr(ProtocolExtraItem, k)
                })
            except (json.JSONDecodeError, TypeError):
                self._protocol_extra_cache = ProtocolExtraItem()
        else:
            self._protocol_extra_cache = ProtocolExtraItem()
        return self._protocol_extra_cache


@dataclass
class ProfileItemModel:
    """Profile item view model for display in server list.

    Ported from ServiceLib/Models/ProfileItemModel.cs.
    """

    is_active: bool = False
    index_id: str = ""
    config_type: EConfigType = EConfigType.VMess
    remarks: str = ""
    address: str = ""
    port: int = 0
    network: str = ""
    stream_security: str = ""
    subid: str = ""
    sub_remarks: str = ""
    sort: int = 0
    delay: int = 0
    speed: float = 0.0
    delay_val: str = ""
    speed_val: str = ""
    today_up: str = ""
    today_down: str = ""
    total_up: str = ""
    total_down: str = ""

    def get_summary(self) -> str:
        """Get a human-readable summary."""
        summary = f"[{self.config_type.name}] {self.remarks}"
        if not self.config_type.is_complex_type():
            summary += f"({self.address}:{self.port})"
        return summary


@dataclass
class ProfileExItem:
    """Profile extended item for statistics.

    Ported from ServiceLib/Models/ProfileExItem.cs.
    """

    index_id: str = ""
    delay: int = 0
    speed: float = 0.0
    sort: int = 0
    message: str | None = None


def _is_guid(s: str) -> bool:
    """Check if a string is a valid GUID/UUID."""
    import re

    pattern = r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
    return bool(re.match(pattern, s))
