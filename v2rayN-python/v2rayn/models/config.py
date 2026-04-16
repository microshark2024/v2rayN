"""Configuration data models.

Ported from ServiceLib/Models/Config.cs and ServiceLib/Models/ConfigItems.cs.
Contains the main application configuration and all related sub-configuration items.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from v2rayn.enums.config_type import EConfigType
from v2rayn.enums.core_type import ECoreType
from v2rayn.enums.gird_orientation import EGirdOrientation
from v2rayn.enums.global_hotkey import EGlobalHotkey
from v2rayn.enums.multiple_load import EMultipleLoad
from v2rayn.enums.rule_mode import ERuleMode
from v2rayn.enums.sys_proxy_type import ESysProxyType


@dataclass
class CoreBasicItem:
    """Core basic configuration."""

    log_enabled: bool = False
    loglevel: str = ""
    mux_enabled: bool = False
    def_allow_insecure: bool = False
    def_fingerprint: str = ""
    def_user_agent: str = ""
    enable_fragment: bool = False
    enable_cache_file_4sbox: bool = True


@dataclass
class InItem:
    """Inbound configuration item."""

    local_port: int = 0
    protocol: str = ""
    udp_enabled: bool = False
    sniffing_enabled: bool = True
    dest_override: list[str] | None = field(default_factory=lambda: ["http", "tls"])
    route_only: bool = False
    allow_lan_conn: bool = False
    new_port_4lan: bool = False
    user: str = ""
    pass_: str = ""
    second_local_port_enabled: bool = False


@dataclass
class KcpItem:
    """KCP transport configuration."""

    mtu: int = 0
    tti: int = 0
    uplink_capacity: int = 0
    downlink_capacity: int = 0
    congestion: bool = False
    read_buffer_size: int = 0
    write_buffer_size: int = 0


@dataclass
class GrpcItem:
    """gRPC transport configuration."""

    idle_timeout: int | None = None
    health_check_timeout: int | None = None
    permit_without_stream: bool | None = None
    initial_windows_size: int | None = None


@dataclass
class GUIItem:
    """GUI configuration."""

    auto_run: bool = False
    enable_statistics: bool = False
    display_real_time_speed: bool = False
    keep_older_dedupl: bool = False
    auto_update_interval: int = 0
    tray_menu_servers_limit: int = 20
    enable_hwa: bool = False
    enable_log: bool = True


@dataclass
class MsgUIItem:
    """Message UI configuration."""

    main_msg_filter: str | None = None
    auto_refresh: bool | None = None


@dataclass
class ColumnItem:
    """Column configuration for list display."""

    name: str = ""
    width: int = 0
    index: int = 0


@dataclass
class WindowSizeItem:
    """Window size configuration."""

    type_name: str = ""
    width: int = 0
    height: int = 0


@dataclass
class UIItem:
    """UI configuration."""

    enable_auto_adjust_main_lv_col_width: bool = False
    main_gird_height1: int = 0
    main_gird_height2: int = 0
    main_gird_orientation: EGirdOrientation = EGirdOrientation.Vertical
    color_primary_name: str | None = None
    current_theme: str | None = None
    current_language: str = ""
    current_font_family: str = ""
    current_font_size: int = 0
    enable_drag_drop_sort: bool = False
    double_click_2_activate: bool = False
    auto_hide_startup: bool = False
    hide_2_tray_when_close: bool = False
    macos_show_in_dock: bool = False
    main_column_item: list[ColumnItem] | None = None
    window_size_item: list[WindowSizeItem] | None = None


@dataclass
class ConstItem:
    """Constant URL configuration."""

    sub_convert_url: str | None = None
    geo_source_url: str | None = None
    srs_source_url: str | None = None
    route_rules_template_source_url: str | None = None


@dataclass
class KeyEventItem:
    """Global hotkey event configuration."""

    e_global_hotkey: EGlobalHotkey = EGlobalHotkey.ShowForm
    alt: bool = False
    control: bool = False
    shift: bool = False
    key_code: int | None = None


@dataclass
class CoreTypeItem:
    """Core type mapping for config types."""

    config_type: EConfigType = EConfigType.VMess
    core_type: ECoreType = ECoreType.Xray


@dataclass
class TunModeItem:
    """TUN mode configuration."""

    enable_tun: bool = False
    auto_route: bool = True
    strict_route: bool = True
    stack: str = ""
    mtu: int = 0
    enable_ipv6_address: bool = False
    icmp_routing: str = ""


@dataclass
class SpeedTestItem:
    """Speed test configuration."""

    speed_test_timeout: int = 0
    speed_test_url: str = ""
    speed_ping_test_url: str = ""
    mixed_concurrency_count: int = 0
    ipapi_url: str = ""


@dataclass
class RoutingBasicItem:
    """Routing basic configuration."""

    domain_strategy: str = ""
    domain_strategy_4singbox: str = ""
    routing_index_id: str = ""


@dataclass
class Mux4RayItem:
    """Mux configuration for V2Ray/Xray."""

    concurrency: int | None = None
    xudp_concurrency: int | None = None
    xudp_proxy_udp443: str | None = None


@dataclass
class Mux4SboxItem:
    """Mux configuration for Sing-box."""

    protocol: str = ""
    max_connections: int = 0
    padding: bool | None = None


@dataclass
class HysteriaItem:
    """Hysteria configuration."""

    up_mbps: int = 0
    down_mbps: int = 0
    hop_interval: int = 30


@dataclass
class ClashUIItem:
    """Clash UI configuration."""

    rule_mode: ERuleMode = ERuleMode.Rule
    enable_ipv6: bool = False
    enable_mixin_content: bool = False
    proxies_sorting: int = 0
    proxies_auto_refresh: bool = False
    proxies_auto_delay_test_interval: int = 10
    connections_auto_refresh: bool = False
    connections_refresh_interval: int = 2
    connections_column_item: list[ColumnItem] | None = None


@dataclass
class SystemProxyItem:
    """System proxy configuration."""

    sys_proxy_type: ESysProxyType = ESysProxyType.ForcedClear
    system_proxy_exceptions: str = ""
    not_proxy_local_address: bool = True
    system_proxy_advanced_protocol: str = ""
    custom_system_proxy_pac_path: str | None = None
    custom_system_proxy_script_path: str | None = None


@dataclass
class WebDavItem:
    """WebDAV backup configuration."""

    url: str | None = None
    user_name: str | None = None
    password: str | None = None
    dir_name: str | None = None


@dataclass
class CheckUpdateItem:
    """Check update configuration."""

    check_pre_release_update: bool = False
    selected_core_types: list[str] | None = None


@dataclass
class Fragment4RayItem:
    """Fragment configuration for V2Ray/Xray."""

    packets: str | None = None
    length: str | None = None
    interval: str | None = None


@dataclass
class SimpleDNSItem:
    """Simple DNS configuration."""

    use_system_hosts: bool | None = None
    add_common_hosts: bool | None = None
    fake_ip: bool | None = None
    global_fake_ip: bool | None = None
    block_binding_query: bool | None = None
    direct_dns: str | None = None
    remote_dns: str | None = None
    bootstrap_dns: str | None = None
    strategy_4freedom: str | None = None
    strategy_4proxy: str | None = None
    serve_stale: bool | None = None
    parallel_query: bool | None = None
    hosts: str | None = None
    direct_expected_ips: str | None = None


@dataclass
class Config:
    """Main application configuration.

    Ported from ServiceLib/Models/Config.cs.
    """

    index_id: str = ""
    sub_index_id: str = ""

    core_basic_item: CoreBasicItem = field(default_factory=CoreBasicItem)
    tun_mode_item: TunModeItem = field(default_factory=TunModeItem)
    kcp_item: KcpItem = field(default_factory=KcpItem)
    grpc_item: GrpcItem = field(default_factory=GrpcItem)
    routing_basic_item: RoutingBasicItem = field(default_factory=RoutingBasicItem)
    gui_item: GUIItem = field(default_factory=GUIItem)
    msg_ui_item: MsgUIItem = field(default_factory=MsgUIItem)
    ui_item: UIItem = field(default_factory=UIItem)
    const_item: ConstItem = field(default_factory=ConstItem)
    speed_test_item: SpeedTestItem = field(default_factory=SpeedTestItem)
    mux_4ray_item: Mux4RayItem = field(default_factory=Mux4RayItem)
    mux_4sbox_item: Mux4SboxItem = field(default_factory=Mux4SboxItem)
    hysteria_item: HysteriaItem = field(default_factory=HysteriaItem)
    clash_ui_item: ClashUIItem = field(default_factory=ClashUIItem)
    system_proxy_item: SystemProxyItem = field(default_factory=SystemProxyItem)
    web_dav_item: WebDavItem = field(default_factory=WebDavItem)
    check_update_item: CheckUpdateItem = field(default_factory=CheckUpdateItem)
    fragment_4ray_item: Fragment4RayItem | None = None
    inbound: list[InItem] = field(default_factory=list)
    global_hotkeys: list[KeyEventItem] = field(default_factory=list)
    core_type_item: list[CoreTypeItem] = field(default_factory=list)
    simple_dns_item: SimpleDNSItem = field(default_factory=SimpleDNSItem)
