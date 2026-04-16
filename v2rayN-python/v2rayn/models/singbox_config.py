"""Sing-box configuration models.

Ported from ServiceLib/Models/SingboxConfig.cs.
Contains all the data structures for Sing-box JSON configuration.
"""

from __future__ import annotations

from dataclasses import dataclass, field


# ============================================================================
# Base classes
# ============================================================================


@dataclass
class Tls4Sbox:
    """Sing-box TLS settings."""

    enabled: bool = False
    server_name: str | None = None
    insecure: bool | None = None
    alpn: list[str] | None = None
    utls: Utls4Sbox | None = None
    reality: Reality4Sbox | None = None
    fragment: bool | None = None
    fragment_fallback_delay: str | None = None
    record_fragment: bool | None = None
    certificate: list[str] | None = None
    ech: Ech4Sbox | None = None


@dataclass
class Ech4Sbox:
    """Sing-box ECH configuration."""

    enabled: bool = False
    config: list[str] | None = None
    query_server_name: str | None = None


@dataclass
class Multiplex4Sbox:
    """Sing-box multiplex configuration."""

    enabled: bool = False
    protocol: str = ""
    max_connections: int = 0
    padding: bool | None = None


@dataclass
class Utls4Sbox:
    """Sing-box uTLS configuration."""

    enabled: bool = False
    fingerprint: str = ""


@dataclass
class Reality4Sbox:
    """Sing-box Reality configuration."""

    enabled: bool = False
    public_key: str = ""
    short_id: str = ""


@dataclass
class Transport4Sbox:
    """Sing-box transport configuration."""

    type: str | None = None
    host: object | None = None
    path: str | None = None
    headers: Headers4Sbox | None = None
    service_name: str | None = None
    idle_timeout: str | None = None
    ping_timeout: str | None = None
    permit_without_stream: bool | None = None
    max_early_data: int | None = None
    early_data_header_name: str | None = None


@dataclass
class Headers4Sbox:
    """Sing-box headers."""

    host: str | None = None


@dataclass
class HyObfs4Sbox:
    """Sing-box Hysteria obfuscation."""

    type: str | None = None
    password: str | None = None


@dataclass
class Rule4Sbox:
    """Sing-box rule configuration."""

    outbound: str | None = None
    server: str | None = None
    disable_cache: bool | None = None
    type: str | None = None
    mode: str | None = None
    ip_is_private: bool | None = None
    client_subnet: str | None = None
    rewrite_ttl: int | None = None
    invert: bool | None = None
    clash_mode: str | None = None
    inbound: list[str] | None = None
    protocol: list[str] | None = None
    network: list[str] | None = None
    port: list[int] | None = None
    port_range: list[str] | None = None
    geosite: list[str] | None = None
    domain: list[str] | None = None
    domain_suffix: list[str] | None = None
    domain_keyword: list[str] | None = None
    domain_regex: list[str] | None = None
    geoip: list[str] | None = None
    ip_cidr: list[str] | None = None
    source_ip_cidr: list[str] | None = None
    process_name: list[str] | None = None
    process_path: list[str] | None = None
    rule_set: list[str] | None = None
    rules: list[Rule4Sbox] | None = None
    action: str | None = None
    strategy: str | None = None
    sniffer: list[str] | None = None
    rcode: str | None = None
    query_type: list[int] | None = None
    answer: list[str] | None = None
    ns: list[str] | None = None
    extra: list[str] | None = None
    method: str | None = None
    no_drop: bool | None = None
    source_ip_is_private: bool | None = None
    ip_accept_any: bool | None = None
    source_port: int | None = None
    source_port_range: list[str] | None = None
    network_type: list[str] | None = None
    network_is_expensive: bool | None = None
    network_is_constrained: bool | None = None
    wifi_ssid: list[str] | None = None
    wifi_bssid: list[str] | None = None
    rule_set_ip_cidr_match_source: bool | None = None
    rule_set_ip_cidr_accept_empty: bool | None = None


# ============================================================================
# Core Configuration
# ============================================================================


@dataclass
class Log4Sbox:
    """Sing-box log configuration."""

    disabled: bool | None = None
    level: str = ""
    output: str = ""
    timestamp: bool | None = None


@dataclass
class Server4Sbox:
    """Sing-box DNS server configuration."""

    type: str = ""
    tag: str = ""
    detour: str | None = None
    inet4_range: str | None = None
    inet6_range: str | None = None
    client_subnet: str | None = None
    server: str | None = None
    domain_resolver: str | None = None
    interface: str | None = None
    server_port: int | None = None
    path: str | None = None
    headers: Headers4Sbox | None = None
    predefined: dict[str, list[str]] | None = None
    # Deprecated in sing-box 1.12.0, kept for backward compatibility
    address: str | None = None
    address_resolver: str | None = None
    address_strategy: str | None = None
    strategy: str | None = None
    # DialFields
    tls: Tls4Sbox | None = None
    multiplex: Multiplex4Sbox | None = None
    transport: Transport4Sbox | None = None
    obfs: HyObfs4Sbox | None = None
    bind_interface: str | None = None
    inet4_bind_address: str | None = None
    inet6_bind_address: str | None = None
    routing_mark: int | None = None
    reuse_addr: bool | None = None
    netns: str | None = None
    connect_timeout: str | None = None
    tcp_fast_open: bool | None = None
    tcp_multi_path: bool | None = None
    udp_fragment: bool | None = None
    network_strategy: str | None = None
    fallback_network_type: list[str] | None = None
    fallback_delay: str | None = None


@dataclass
class Dns4Sbox:
    """Sing-box DNS configuration."""

    servers: list[Server4Sbox] = field(default_factory=list)
    rules: list[Rule4Sbox] = field(default_factory=list)
    final: str | None = None
    strategy: str | None = None
    disable_cache: bool | None = None
    disable_expire: bool | None = None
    independent_cache: bool | None = None
    cache_capacity: int | None = None
    reverse_mapping: bool | None = None
    client_subnet: str | None = None


@dataclass
class User4Sbox:
    """Sing-box user configuration."""

    username: str = ""
    password: str = ""


@dataclass
class Inbound4Sbox:
    """Sing-box inbound configuration."""

    type: str = ""
    tag: str = ""
    listen: str = ""
    listen_port: int | None = None
    interface_name: str = ""
    address: list[str] | None = None
    mtu: int | None = None
    auto_route: bool | None = None
    strict_route: bool | None = None
    endpoint_independent_nat: bool | None = None
    stack: str | None = None
    users: list[User4Sbox] | None = None


@dataclass
class Outbound4Sbox:
    """Sing-box outbound configuration."""

    type: str = ""
    tag: str = ""
    server: str | None = None
    server_port: int | None = None
    server_ports: list[str] | None = None
    uuid: str | None = None
    security: str | None = None
    alter_id: int | None = None
    flow: str | None = None
    hop_interval: str | None = None
    up_mbps: int | None = None
    down_mbps: int | None = None
    auth_str: str | None = None
    recv_window_conn: int | None = None
    recv_window: int | None = None
    disable_mtu_discovery: bool | None = None
    insecure_concurrency: int | None = None
    udp_over_tcp: bool | None = None
    method: str | None = None
    username: str | None = None
    password: str | None = None
    congestion_control: str | None = None
    quic: bool | None = None
    quic_congestion_control: str | None = None
    version: str | None = None
    network: str | None = None
    packet_encoding: str | None = None
    plugin: str | None = None
    plugin_opts: str | None = None
    outbounds: list[str] | None = None
    interrupt_exist_connections: bool | None = None
    tolerance: int | None = None
    # DialFields
    detour: str | None = None
    tls: Tls4Sbox | None = None
    multiplex: Multiplex4Sbox | None = None
    transport: Transport4Sbox | None = None
    obfs: HyObfs4Sbox | None = None
    bind_interface: str | None = None
    inet4_bind_address: str | None = None
    inet6_bind_address: str | None = None
    routing_mark: int | None = None
    reuse_addr: bool | None = None
    netns: str | None = None
    connect_timeout: str | None = None
    tcp_fast_open: bool | None = None
    tcp_multi_path: bool | None = None
    udp_fragment: bool | None = None
    domain_resolver: Rule4Sbox | None = None
    network_strategy: str | None = None
    network_type: list[str] | None = None
    fallback_network_type: list[str] | None = None
    fallback_delay: str | None = None


@dataclass
class Peer4Sbox:
    """Sing-box WireGuard peer."""

    address: str = ""
    port: int = 0
    public_key: str = ""
    pre_shared_key: str | None = None
    allowed_ips: list[str] = field(default_factory=list)
    persistent_keepalive_interval: int | None = None
    reserved: list[int] = field(default_factory=list)


@dataclass
class Endpoints4Sbox:
    """Sing-box WireGuard endpoints."""

    type: str = ""
    tag: str = ""
    system: bool | None = None
    name: str | None = None
    mtu: int | None = None
    address: list[str] = field(default_factory=list)
    private_key: str = ""
    listen_port: int | None = None
    udp_timeout: str | None = None
    workers: int | None = None
    peers: list[Peer4Sbox] = field(default_factory=list)
    # DialFields
    detour: str | None = None
    tls: Tls4Sbox | None = None
    multiplex: Multiplex4Sbox | None = None
    transport: Transport4Sbox | None = None
    obfs: HyObfs4Sbox | None = None


@dataclass
class Ruleset4Sbox:
    """Sing-box rule set."""

    tag: str | None = None
    type: str | None = None
    format: str | None = None
    path: str | None = None
    url: str | None = None
    download_detour: str | None = None
    update_interval: str | None = None


@dataclass
class Route4Sbox:
    """Sing-box route configuration."""

    default_domain_resolver: Rule4Sbox | None = None
    auto_detect_interface: bool | None = None
    rules: list[Rule4Sbox] = field(default_factory=list)
    rule_set: list[Ruleset4Sbox] | None = None
    final: str | None = None


@dataclass
class Stats4Sbox:
    """Sing-box statistics configuration."""

    enabled: bool = False
    inbounds: list[str] | None = None
    outbounds: list[str] | None = None
    users: list[str] | None = None


@dataclass
class V2ray_Api4Sbox:
    """Sing-box V2Ray API configuration."""

    listen: str = ""
    stats: Stats4Sbox | None = None


@dataclass
class Clash_Api4Sbox:
    """Sing-box Clash API configuration."""

    external_controller: str | None = None
    store_selected: bool | None = None


@dataclass
class CacheFile4Sbox:
    """Sing-box cache file configuration."""

    enabled: bool = False
    path: str | None = None
    cache_id: str | None = None
    store_fakeip: bool | None = None


@dataclass
class Experimental4Sbox:
    """Sing-box experimental configuration."""

    cache_file: CacheFile4Sbox | None = None
    v2ray_api: V2ray_Api4Sbox | None = None
    clash_api: Clash_Api4Sbox | None = None


@dataclass
class SingboxConfig:
    """Sing-box complete configuration.

    Ported from ServiceLib/Models/SingboxConfig.cs.
    """

    log: Log4Sbox | None = None
    dns: Dns4Sbox | None = None
    inbounds: list[Inbound4Sbox] = field(default_factory=list)
    outbounds: list[Outbound4Sbox] = field(default_factory=list)
    endpoints: list[Endpoints4Sbox] | None = None
    route: Route4Sbox | None = None
    experimental: Experimental4Sbox | None = None
