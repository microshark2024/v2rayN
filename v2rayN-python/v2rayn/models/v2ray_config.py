"""V2Ray/Xray configuration models.

Ported from ServiceLib/Models/V2rayConfig.cs.
Contains all the data structures for V2Ray/Xray JSON configuration.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Stats4Ray:
    """V2Ray stats configuration (empty marker class)."""

    pass


@dataclass
class Metrics4Ray:
    """V2Ray metrics configuration."""

    tag: str = ""


@dataclass
class SystemPolicy4Ray:
    """V2Ray system policy."""

    stats_outbound_uplink: bool = False
    stats_outbound_downlink: bool = False


@dataclass
class Policy4Ray:
    """V2Ray policy configuration."""

    system: SystemPolicy4Ray | None = None


@dataclass
class Log4Ray:
    """V2Ray log configuration."""

    access: str | None = None
    error: str | None = None
    loglevel: str | None = None


@dataclass
class UsersItem4Ray:
    """V2Ray users item."""

    id: str | None = None
    alter_id: int | None = None
    email: str | None = None
    security: str | None = None
    encryption: str | None = None
    flow: str | None = None


@dataclass
class Sniffing4Ray:
    """V2Ray sniffing configuration."""

    enabled: bool = False
    dest_override: list[str] | None = None
    route_only: bool = False


@dataclass
class AccountsItem4Ray:
    """V2Ray accounts item."""

    user: str = ""
    pass_: str = ""


@dataclass
class Inboundsettings4Ray:
    """V2Ray inbound settings."""

    auth: str | None = None
    udp: bool | None = None
    ip: str | None = None
    address: str | None = None
    clients: list[UsersItem4Ray] | None = None
    decryption: str | None = None
    allow_transparent: bool | None = None
    accounts: list[AccountsItem4Ray] | None = None


@dataclass
class Inbounds4Ray:
    """V2Ray inbound configuration."""

    tag: str = ""
    port: int = 0
    listen: str = ""
    protocol: str = ""
    sniffing: Sniffing4Ray | None = None
    settings: Inboundsettings4Ray | None = None


@dataclass
class WireguardPeer4Ray:
    """V2Ray WireGuard peer."""

    endpoint: str = ""
    public_key: str = ""


@dataclass
class FragmentItem4Ray:
    """V2Ray fragment configuration."""

    packets: str | None = None
    length: str | None = None
    interval: str | None = None


@dataclass
class Response4Ray:
    """V2Ray response."""

    type: str = ""


@dataclass
class Outboundsettings4Ray:
    """V2Ray outbound settings."""

    vnext: list[VnextItem4Ray] | None = None
    servers: list[ServersItem4Ray] | None = None
    response: Response4Ray | None = None
    domain_strategy: str = ""
    user_level: int | None = None
    fragment: FragmentItem4Ray | None = None
    secret_key: str | None = None
    address: object | None = None
    port: int | None = None
    peers: list[WireguardPeer4Ray] | None = None
    no_kernel_tun: bool | None = None
    mtu: int | None = None
    reserved: list[int] | None = None
    workers: int | None = None
    version: int | None = None


@dataclass
class Mux4Ray:
    """V2Ray mux configuration."""

    enabled: bool = False
    concurrency: int | None = None
    xudp_concurrency: int | None = None
    xudp_proxy_udp443: str | None = None


@dataclass
class TlsSettings4Ray:
    """V2Ray TLS settings."""

    allow_insecure: bool | None = None
    server_name: str | None = None
    alpn: list[str] | None = None
    fingerprint: str | None = None
    show: bool | None = None
    public_key: str | None = None
    short_id: str | None = None
    spider_x: str | None = None
    mldsa65_verify: str | None = None
    certificates: list[CertificateSettings4Ray] | None = None
    pinned_peer_cert_sha256: str | None = None
    disable_system_root: bool | None = None
    ech_config_list: str | None = None
    ech_force_query: str | None = None
    ech_sockopt: Sockopt4Ray | None = None


@dataclass
class CertificateSettings4Ray:
    """V2Ray certificate settings."""

    certificate: list[str] | None = None
    usage: str | None = None


@dataclass
class Header4Ray:
    """V2Ray header configuration."""

    type: str = ""
    request: object | None = None
    response: object | None = None


@dataclass
class TcpSettings4Ray:
    """V2Ray TCP settings."""

    header: Header4Ray | None = None


@dataclass
class KcpSettings4Ray:
    """V2Ray KCP settings."""

    mtu: int = 0
    tti: int = 0
    uplink_capacity: int = 0
    downlink_capacity: int = 0
    congestion: bool = False
    read_buffer_size: int = 0
    write_buffer_size: int = 0


@dataclass
class Headers4Ray:
    """V2Ray headers (for WebSocket)."""

    user_agent: str = ""


@dataclass
class WsSettings4Ray:
    """V2Ray WebSocket settings."""

    path: str | None = None
    host: str | None = None
    headers: Headers4Ray | None = None


@dataclass
class HttpupgradeSettings4Ray:
    """V2Ray HTTPUpgrade settings."""

    path: str | None = None
    host: str | None = None


@dataclass
class XhttpSettings4Ray:
    """V2Ray XHTTP settings."""

    path: str | None = None
    host: str | None = None
    mode: str | None = None
    extra: object | None = None


@dataclass
class HttpSettings4Ray:
    """V2Ray HTTP/2 settings."""

    path: str | None = None
    host: list[str] | None = None


@dataclass
class QuicSettings4Ray:
    """V2Ray QUIC settings."""

    security: str = ""
    key: str = ""
    header: Header4Ray | None = None


@dataclass
class GrpcSettings4Ray:
    """V2Ray gRPC settings."""

    authority: str | None = None
    service_name: str | None = None
    multi_mode: bool = False
    idle_timeout: int | None = None
    health_check_timeout: int | None = None
    permit_without_stream: bool | None = None
    initial_windows_size: int | None = None


@dataclass
class HysteriaUdpHop4Ray:
    """V2Ray Hysteria UDP hop."""

    port: str | None = None
    interval: str | None = None


@dataclass
class HysteriaSettings4Ray:
    """V2Ray Hysteria settings."""

    version: int = 0
    auth: str | None = None
    up: str | None = None
    down: str | None = None
    udphop: HysteriaUdpHop4Ray | None = None


@dataclass
class Mask4Ray:
    """V2Ray mask configuration."""

    type: str = ""
    settings: object | None = None


@dataclass
class MaskSettings4Ray:
    """V2Ray mask settings."""

    password: str | None = None
    domain: str | None = None


@dataclass
class Finalmask4Ray:
    """V2Ray finalmask configuration."""

    tcp: list[Mask4Ray] | None = None
    udp: list[Mask4Ray] | None = None


@dataclass
class Sockopt4Ray:
    """V2Ray socket options."""

    dialer_proxy: str | None = None


@dataclass
class StreamSettings4Ray:
    """V2Ray stream settings."""

    network: str = ""
    security: str = ""
    tls_settings: TlsSettings4Ray | None = None
    tcp_settings: TcpSettings4Ray | None = None
    kcp_settings: KcpSettings4Ray | None = None
    ws_settings: WsSettings4Ray | None = None
    httpupgrade_settings: HttpupgradeSettings4Ray | None = None
    xhttp_settings: XhttpSettings4Ray | None = None
    http_settings: HttpSettings4Ray | None = None
    quic_settings: QuicSettings4Ray | None = None
    reality_settings: TlsSettings4Ray | None = None
    grpc_settings: GrpcSettings4Ray | None = None
    hysteria_settings: HysteriaSettings4Ray | None = None
    finalmask: Finalmask4Ray | None = None
    sockopt: Sockopt4Ray | None = None


@dataclass
class Outbounds4Ray:
    """V2Ray outbound configuration."""

    tag: str = ""
    protocol: str = ""
    target_strategy: str | None = None
    settings: Outboundsettings4Ray | None = None
    stream_settings: StreamSettings4Ray | None = None
    mux: Mux4Ray | None = None


@dataclass
class VnextItem4Ray:
    """V2Ray vnext item."""

    address: str = ""
    port: int = 0
    users: list[UsersItem4Ray] = field(default_factory=list)


@dataclass
class SocksUsersItem4Ray:
    """V2Ray SOCKS users item."""

    user: str = ""
    pass_: str = ""
    level: int | None = None


@dataclass
class ServersItem4Ray:
    """V2Ray servers item."""

    email: str = ""
    address: str = ""
    method: str | None = None
    ota: bool | None = None
    password: str | None = None
    port: int = 0
    level: int | None = None
    flow: str = ""
    uot: bool | None = None
    users: list[SocksUsersItem4Ray] = field(default_factory=list)


@dataclass
class DnsServer4Ray:
    """V2Ray DNS server."""

    address: str | None = None
    port: int | None = None
    domains: list[str] | None = None
    skip_fallback: bool | None = None
    expected_ips: list[str] | None = None
    tag: str | None = None


@dataclass
class Dns4Ray:
    """V2Ray DNS configuration."""

    hosts: dict[str, object] | None = None
    servers: list[object] = field(default_factory=list)
    serve_stale: bool | None = None
    enable_parallel_query: bool | None = None
    tag: str | None = None


@dataclass
class RulesItem4Ray:
    """V2Ray routing rules item."""

    type: str | None = None
    port: str | None = None
    network: str | None = None
    inbound_tag: list[str] | None = None
    outbound_tag: str | None = None
    balancer_tag: str | None = None
    ip: list[str] | None = None
    domain: list[str] | None = None
    protocol: list[str] | None = None
    process: list[str] | None = None


@dataclass
class BalancersStrategySettingsCosts4Ray:
    """V2Ray balancer strategy settings costs."""

    regexp: bool | None = None
    match: str | None = None
    value: float | None = None


@dataclass
class BalancersStrategySettings4Ray:
    """V2Ray balancer strategy settings."""

    expected: int | None = None
    max_rtt: str | None = None
    tolerance: float | None = None
    baselines: list[str] | None = None
    costs: list[BalancersStrategySettingsCosts4Ray] | None = None


@dataclass
class BalancersStrategy4Ray:
    """V2Ray balancer strategy."""

    type: str | None = None
    settings: BalancersStrategySettings4Ray | None = None


@dataclass
class BalancersItem4Ray:
    """V2Ray balancers item."""

    selector: list[str] | None = None
    strategy: BalancersStrategy4Ray | None = None
    tag: str | None = None


@dataclass
class Routing4Ray:
    """V2Ray routing configuration."""

    domain_strategy: str = ""
    rules: list[RulesItem4Ray] = field(default_factory=list)
    balancers: list[BalancersItem4Ray] | None = None


@dataclass
class BurstObservatoryPingConfig4Ray:
    """V2Ray burst observatory ping config."""

    destination: str | None = None
    connectivity: str | None = None
    interval: str | None = None
    sampling: int | None = None
    timeout: str | None = None


@dataclass
class BurstObservatory4Ray:
    """V2Ray burst observatory."""

    subject_selector: list[str] | None = None
    ping_config: BurstObservatoryPingConfig4Ray | None = None


@dataclass
class Observatory4Ray:
    """V2Ray observatory."""

    subject_selector: list[str] | None = None
    probe_url: str | None = None
    probe_interval: str | None = None
    enable_concurrency: bool | None = None


@dataclass
class V2rayConfig:
    """V2Ray/Xray complete configuration.

    Ported from ServiceLib/Models/V2rayConfig.cs.
    """

    log: Log4Ray | None = None
    dns: object | None = None
    inbounds: list[Inbounds4Ray] = field(default_factory=list)
    outbounds: list[Outbounds4Ray] = field(default_factory=list)
    routing: Routing4Ray | None = None
    metrics: Metrics4Ray | None = None
    policy: Policy4Ray | None = None
    stats: Stats4Ray | None = None
    observatory: Observatory4Ray | None = None
    burst_observatory: BurstObservatory4Ray | None = None
    remarks: str | None = None


@dataclass
class V2rayTcpRequest:
    """V2Ray TCP request for HTTP header."""

    headers: RequestHeaders | None = None


@dataclass
class RequestHeaders:
    """Request headers."""

    host: list[str] = field(default_factory=list)


@dataclass
class V2rayMetricsVarsLink:
    """V2Ray metrics link stats."""

    downlink: int = 0
    uplink: int = 0


@dataclass
class V2rayMetricsVarsStats:
    """V2Ray metrics stats."""

    outbound: dict | None = None


@dataclass
class V2rayMetricsVars:
    """V2Ray metrics variables."""

    stats: V2rayMetricsVarsStats | None = None
