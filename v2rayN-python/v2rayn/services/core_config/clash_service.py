"""Clash/Mihomo core configuration service.

Ported from ServiceLib/Services/CoreConfig/clash.
Generates Clash YAML configuration from ProfileItems.
"""

from __future__ import annotations

from typing import Any

from v2rayn.common import logging_config, yaml_utils
from v2rayn.common.extensions import is_not_empty
from v2rayn.enums.config_type import EConfigType
from v2rayn.global_config import STREAM_SECURITY
from v2rayn.models.misc import CoreConfigContext
from v2rayn.models.profile_item import ProfileItem

_tag = "ClashConfigService"


class ClashConfigService:
    """Generates Clash/Mihomo YAML configuration."""

    def __init__(self, context: CoreConfigContext):
        """Initialize service."""
        self._context = context

    def generate_config(self) -> str:
        """Generate complete Clash configuration.

        Returns:
            YAML string of the configuration
        """
        try:
            config: dict[str, Any] = {}

            app_config = self._context.app_config

            # Port settings
            config["port"] = app_config.inbound_item.http_port or 7890
            config["socks-port"] = app_config.inbound_item.socks_port or 7891
            config["allow-lan"] = app_config.inbound_item.allow_lan
            config["mode"] = "rule"
            config["log-level"] = "info"
            config["external-controller"] = "127.0.0.1:9090"

            # DNS
            config["dns"] = self._build_dns()

            # Proxies
            proxies = []
            node = self._context.node
            if node:
                proxy = self._build_proxy(node)
                if proxy:
                    proxies.append(proxy)
            config["proxies"] = proxies

            # Proxy groups
            proxy_names = [p["name"] for p in proxies]
            config["proxy-groups"] = [
                {
                    "name": "Proxy",
                    "type": "select",
                    "proxies": proxy_names + ["DIRECT"],
                }
            ]

            # Rules
            config["rules"] = self._build_rules()

            return yaml_utils.serialize(config)
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)
            return ""

    def _build_dns(self) -> dict[str, Any]:
        """Build DNS section."""
        return {
            "enable": True,
            "nameserver": [
                "https://dns.alidns.com/dns-query",
                "https://doh.pub/dns-query",
            ],
            "fallback": [
                "https://8.8.8.8/dns-query",
                "https://1.1.1.1/dns-query",
            ],
        }

    def _build_proxy(self, node: ProfileItem) -> dict[str, Any] | None:
        """Build a proxy entry for a node."""
        config_type = node.config_type
        proxy: dict[str, Any] = {
            "name": node.remarks or node.address,
            "server": node.address,
            "port": node.port,
        }

        if config_type == EConfigType.VMess:
            proxy["type"] = "vmess"
            proxy["uuid"] = node.password
            extra = node.get_protocol_extra()
            proxy["alterId"] = int(extra.alter_id or 0)
            proxy["cipher"] = extra.vmess_security or "auto"

        elif config_type == EConfigType.VLESS:
            proxy["type"] = "vless"
            proxy["uuid"] = node.password
            extra = node.get_protocol_extra()
            if is_not_empty(extra.flow):
                proxy["flow"] = extra.flow

        elif config_type == EConfigType.Trojan:
            proxy["type"] = "trojan"
            proxy["password"] = node.password

        elif config_type == EConfigType.Shadowsocks:
            proxy["type"] = "ss"
            proxy["password"] = node.password
            extra = node.get_protocol_extra()
            proxy["cipher"] = extra.ss_method or "aes-256-gcm"

        elif config_type == EConfigType.SOCKS:
            proxy["type"] = "socks5"
            if is_not_empty(node.username):
                proxy["username"] = node.username
            if is_not_empty(node.password):
                proxy["password"] = node.password

        elif config_type == EConfigType.Hysteria2:
            proxy["type"] = "hysteria2"
            proxy["password"] = node.password

        else:
            return None

        # TLS
        if node.stream_security == STREAM_SECURITY or node.stream_security == "reality":
            proxy["tls"] = True
            if is_not_empty(node.sni):
                proxy["servername"] = node.sni
            if node.allow_insecure == "true":
                proxy["skip-cert-verify"] = True
            if is_not_empty(node.alpn):
                proxy["alpn"] = node.alpn.split(",")

        # Transport
        network = node.network
        if network == "ws":
            proxy["network"] = "ws"
            ws_opts: dict[str, Any] = {}
            if is_not_empty(node.path):
                ws_opts["path"] = node.path
            if is_not_empty(node.request_host):
                ws_opts["headers"] = {"Host": node.request_host}
            proxy["ws-opts"] = ws_opts

        elif network in ("h2", "http"):
            proxy["network"] = "h2"
            h2_opts: dict[str, Any] = {}
            if is_not_empty(node.path):
                h2_opts["path"] = node.path
            if is_not_empty(node.request_host):
                h2_opts["host"] = node.request_host.split(",")
            proxy["h2-opts"] = h2_opts

        elif network == "grpc":
            proxy["network"] = "grpc"
            grpc_opts: dict[str, Any] = {}
            if is_not_empty(node.path):
                grpc_opts["grpc-service-name"] = node.path
            proxy["grpc-opts"] = grpc_opts

        return proxy

    def _build_rules(self) -> list[str]:
        """Build rules section."""
        rules = [
            "DOMAIN-SUFFIX,local,DIRECT",
            "IP-CIDR,127.0.0.0/8,DIRECT",
            "IP-CIDR,10.0.0.0/8,DIRECT",
            "IP-CIDR,172.16.0.0/12,DIRECT",
            "IP-CIDR,192.168.0.0/16,DIRECT",
            "GEOIP,CN,DIRECT",
            "MATCH,Proxy",
        ]
        return rules
