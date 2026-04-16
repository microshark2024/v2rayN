"""Clash-related models.

Ported from ServiceLib/Models/ClashConnections.cs, ClashProxies.cs,
ClashProviders.cs, ClashConnectionModel.cs, ClashProxyModel.cs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


# ============================================================================
# Clash Connections
# ============================================================================


@dataclass
class MetadataItem:
    """Connection metadata."""

    network: str | None = None
    type: str | None = None
    source_ip: str | None = None
    destination_ip: str | None = None
    source_port: str | None = None
    destination_port: str | None = None
    host: str | None = None
    ns_mode: str | None = None
    uid: object | None = None
    process: str | None = None
    process_path: str | None = None
    remote_destination: str | None = None


@dataclass
class ConnectionItem:
    """Individual connection item."""

    id: str | None = None
    metadata: MetadataItem | None = None
    upload: int = 0
    download: int = 0
    start: datetime | None = None
    chains: list[str] | None = None
    rule: str | None = None
    rule_payload: str | None = None


@dataclass
class ClashConnections:
    """Clash connections response."""

    download_total: int = 0
    upload_total: int = 0
    connections: list[ConnectionItem] | None = None


@dataclass
class ClashConnectionModel:
    """Clash connection display model."""

    id: str | None = None
    network: str | None = None
    type: str | None = None
    host: str | None = None
    upload: int = 0
    download: int = 0
    upload_traffic: str | None = None
    download_traffic: str | None = None
    time: float = 0.0
    elapsed: str | None = None
    chain: str | None = None


# ============================================================================
# Clash Proxies
# ============================================================================


@dataclass
class HistoryItem:
    """Proxy history item."""

    time: str | None = None
    delay: int = 0


@dataclass
class ProxiesItem:
    """Proxy item."""

    all: list[str] | None = None
    history: list[HistoryItem] | None = None
    name: str | None = None
    type: str | None = None
    udp: bool = False
    now: str | None = None
    delay: int = 0


@dataclass
class ClashProxies:
    """Clash proxies response."""

    proxies: dict[str, ProxiesItem] | None = None


@dataclass
class ClashProxyModel:
    """Clash proxy display model."""

    name: str | None = None
    type: str | None = None
    now: str | None = None
    delay: int = 0
    delay_name: str | None = None
    is_active: bool = False


# ============================================================================
# Clash Providers
# ============================================================================


@dataclass
class ProvidersItem:
    """Provider item."""

    name: str | None = None
    proxies: list[ProxiesItem] | None = None
    type: str | None = None
    vehicle_type: str | None = None


@dataclass
class ClashProviders:
    """Clash providers response."""

    providers: dict[str, ProvidersItem] | None = None
