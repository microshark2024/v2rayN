"""Subscription and routing models.

Ported from ServiceLib/Models/SubItem.cs, RoutingItem.cs, RulesItem.cs, DNSItem.cs, etc.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from v2rayn.enums.core_type import ECoreType
from v2rayn.enums.rule_type import ERuleType


@dataclass
class SubItem:
    """Subscription item.

    Ported from ServiceLib/Models/SubItem.cs.
    """

    id: str = ""
    remarks: str = ""
    url: str = ""
    more_url: str = ""
    enabled: bool = True
    user_agent: str = ""
    sort: int = 0
    filter: str | None = None
    auto_update_interval: int = 0
    update_time: int = 0
    convert_target: str | None = None
    prev_profile: str | None = None
    next_profile: str | None = None
    pre_socks_port: int | None = None
    memo: str | None = None


@dataclass
class RoutingItem:
    """Routing item.

    Ported from ServiceLib/Models/RoutingItem.cs.
    """

    id: str = ""
    remarks: str = ""
    url: str = ""
    rule_set: str = ""
    rule_num: int = 0
    enabled: bool = True
    locked: bool = False
    custom_icon: str = ""
    custom_ruleset_path_4singbox: str = ""
    domain_strategy: str = ""
    domain_strategy_4singbox: str = ""
    sort: int = 0
    is_active: bool = False


@dataclass
class RoutingItemModel(RoutingItem):
    """Routing item view model."""

    pass


@dataclass
class RoutingTemplate:
    """Routing template.

    Ported from ServiceLib/Models/RoutingTemplate.cs.
    """

    version: str = ""
    routing_items: list[RoutingItem] = field(default_factory=list)


@dataclass
class RulesItem:
    """Routing rule item.

    Ported from ServiceLib/Models/RulesItem.cs.
    """

    id: str = ""
    type: str | None = None
    port: str | None = None
    network: str | None = None
    inbound_tag: list[str] | None = None
    outbound_tag: str | None = None
    ip: list[str] | None = None
    domain: list[str] | None = None
    protocol: list[str] | None = None
    process: list[str] | None = None
    enabled: bool = True
    remarks: str | None = None
    rule_type: ERuleType | None = None


@dataclass
class RulesItemModel(RulesItem):
    """Rules item view model."""

    inbound_tags: str = ""
    ips: str = ""
    domains: str = ""
    protocols: str = ""
    rule_type_name: str = ""


@dataclass
class DNSItem:
    """DNS configuration item.

    Ported from ServiceLib/Models/DNSItem.cs.
    """

    id: str = ""
    remarks: str = ""
    enabled: bool = False
    core_type: ECoreType = ECoreType.Xray
    use_system_hosts: bool = False
    normal_dns: str | None = None
    tun_dns: str | None = None
    domain_strategy_4freedom: str | None = None
    domain_dns_address: str | None = None


@dataclass
class FullConfigTemplateItem:
    """Full config template item.

    Ported from ServiceLib/Models/FullConfigTemplateItem.cs.
    """

    id: str = ""
    remarks: str = ""
    enabled: bool = False
    core_type: ECoreType = ECoreType.Xray
    config: str | None = None
    tun_config: str | None = None
    add_proxy_only: bool | None = False
    proxy_detour: str | None = None
