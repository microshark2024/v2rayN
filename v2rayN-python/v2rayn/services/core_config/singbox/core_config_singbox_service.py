"""Sing-box core configuration service.

Ported from ServiceLib/Services/CoreConfig/Singbox/.
Generates Sing-box JSON configuration from ProfileItems.
"""

from __future__ import annotations

from typing import Any

from v2rayn.common import json_utils, logging_config
from v2rayn.common.extensions import is_not_empty, is_null_or_empty
from v2rayn.enums.config_type import EConfigType
from v2rayn.global_config import STREAM_SECURITY
from v2rayn.models.config import Config
from v2rayn.models.misc import CoreConfigContext
from v2rayn.models.profile_item import ProfileItem

_tag = "CoreConfigSingboxService"


class CoreConfigSingboxService:
    """Generates Sing-box JSON configuration."""

    def __init__(self, context: CoreConfigContext):
        """Initialize service."""
        self._context = context

    def generate_config(self) -> str:
        """Generate complete Sing-box configuration.

        Returns:
            JSON string of the configuration
        """
        try:
            config: dict[str, Any] = {}

            # Log
            config["log"] = self._build_log()

            # DNS
            config["dns"] = self._build_dns()

            # Inbounds
            config["inbounds"] = self._build_inbounds()

            # Outbounds
            config["outbounds"] = self._build_outbounds()

            # Route
            config["route"] = self._build_route()

            # Experimental
            if self._context.is_tun_enabled:
                config["experimental"] = self._build_experimental()

            return json_utils.serialize(config, indented=True)
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)
            return ""

    def _build_log(self) -> dict[str, Any]:
        """Build log section."""
        return {
            "disabled": False,
            "level": "warn",
            "timestamp": True,
        }

    def _build_dns(self) -> dict[str, Any]:
        """Build DNS section."""
        dns: dict[str, Any] = {
            "servers": [
                {
                    "tag": "remote",
                    "address": "https://8.8.8.8/dns-query",
                    "detour": "proxy",
                },
                {
                    "tag": "local",
                    "address": "https://223.5.5.5/dns-query",
                    "detour": "direct",
                },
                {
                    "tag": "block",
                    "address": "rcode://success",
                },
            ],
            "rules": [
                {
                    "geosite": "cn",
                    "server": "local",
                },
            ],
        }
        return dns

    def _build_inbounds(self) -> list[dict[str, Any]]:
        """Build inbound section."""
        app_config = self._context.app_config
        inbounds: list[dict[str, Any]] = []

        # Mixed (SOCKS + HTTP) inbound
        socks_port = app_config.inbound_item.socks_port
        if socks_port > 0:
            inbounds.append(
                {
                    "type": "mixed",
                    "tag": "mixed-in",
                    "listen": app_config.inbound_item.local_address or "127.0.0.1",
                    "listen_port": socks_port,
                    "sniff": True,
                    "sniff_override_destination": False,
                }
            )

        # TUN inbound
        if self._context.is_tun_enabled:
            tun_config = app_config.tun_mode_item
            inbounds.append(
                {
                    "type": "tun",
                    "tag": "tun-in",
                    "interface_name": "tun0",
                    "inet4_address": "172.19.0.1/30",
                    "auto_route": True,
                    "strict_route": tun_config.strict_route,
                    "stack": tun_config.stack or "system",
                    "sniff": True,
                }
            )

        return inbounds

    def _build_outbounds(self) -> list[dict[str, Any]]:
        """Build outbound section."""
        outbounds: list[dict[str, Any]] = []

        # Main proxy outbound
        node = self._context.node
        if node:
            proxy = self._build_proxy_outbound(node)
            if proxy:
                outbounds.append(proxy)

        # Direct outbound
        outbounds.append(
            {
                "type": "direct",
                "tag": "direct",
            }
        )

        # Block outbound
        outbounds.append(
            {
                "type": "block",
                "tag": "block",
            }
        )

        # DNS outbound
        outbounds.append(
            {
                "type": "dns",
                "tag": "dns-out",
            }
        )

        return outbounds

    def _build_proxy_outbound(self, node: ProfileItem) -> dict[str, Any] | None:
        """Build a proxy outbound for a node."""
        config_type = node.config_type

        outbound: dict[str, Any] = {
            "tag": "proxy",
        }

        if config_type == EConfigType.VMess:
            outbound["type"] = "vmess"
            outbound["server"] = node.address
            outbound["server_port"] = node.port
            outbound["uuid"] = node.password
            extra = node.get_protocol_extra()
            outbound["alter_id"] = int(extra.alter_id or 0)
            outbound["security"] = extra.vmess_security or "auto"

        elif config_type == EConfigType.VLESS:
            outbound["type"] = "vless"
            outbound["server"] = node.address
            outbound["server_port"] = node.port
            outbound["uuid"] = node.password
            extra = node.get_protocol_extra()
            if is_not_empty(extra.flow):
                outbound["flow"] = extra.flow

        elif config_type == EConfigType.Trojan:
            outbound["type"] = "trojan"
            outbound["server"] = node.address
            outbound["server_port"] = node.port
            outbound["password"] = node.password

        elif config_type == EConfigType.Shadowsocks:
            outbound["type"] = "shadowsocks"
            outbound["server"] = node.address
            outbound["server_port"] = node.port
            outbound["password"] = node.password
            extra = node.get_protocol_extra()
            outbound["method"] = extra.ss_method or "aes-256-gcm"

        elif config_type == EConfigType.Hysteria2:
            outbound["type"] = "hysteria2"
            outbound["server"] = node.address
            outbound["server_port"] = node.port
            outbound["password"] = node.password
            extra = node.get_protocol_extra()
            if is_not_empty(extra.ports):
                outbound["ports"] = extra.ports
            if is_not_empty(extra.salamander_pass):
                outbound["obfs"] = {
                    "type": "salamander",
                    "password": extra.salamander_pass,
                }

        elif config_type == EConfigType.TUIC:
            outbound["type"] = "tuic"
            outbound["server"] = node.address
            outbound["server_port"] = node.port
            # TUIC uses uuid:password format
            if ":" in (node.password or ""):
                parts = node.password.split(":", 1)
                outbound["uuid"] = parts[0]
                outbound["password"] = parts[1]
            else:
                outbound["uuid"] = node.password
            extra = node.get_protocol_extra()
            if is_not_empty(extra.congestion_control):
                outbound["congestion_control"] = extra.congestion_control

        elif config_type == EConfigType.WireGuard:
            outbound["type"] = "wireguard"
            outbound["server"] = node.address
            outbound["server_port"] = node.port
            outbound["private_key"] = node.password
            extra = node.get_protocol_extra()
            if is_not_empty(extra.wg_public_key):
                outbound["peer_public_key"] = extra.wg_public_key
            if is_not_empty(extra.wg_reserved):
                reserved = extra.wg_reserved.split(",")
                outbound["reserved"] = [int(x.strip()) for x in reserved if x.strip().isdigit()]
            if is_not_empty(extra.wg_interface_address):
                outbound["local_address"] = extra.wg_interface_address.split(",")
            if extra.wg_mtu and extra.wg_mtu > 0:
                outbound["mtu"] = extra.wg_mtu

        elif config_type == EConfigType.SOCKS:
            outbound["type"] = "socks"
            outbound["server"] = node.address
            outbound["server_port"] = node.port
            if is_not_empty(node.username):
                outbound["username"] = node.username
            if is_not_empty(node.password):
                outbound["password"] = node.password

        else:
            return None

        # TLS
        self._build_tls(node, outbound)

        # Transport
        self._build_transport(node, outbound)

        return outbound

    def _build_tls(self, node: ProfileItem, outbound: dict[str, Any]) -> None:
        """Build TLS settings for an outbound."""
        if is_null_or_empty(node.stream_security):
            return

        tls: dict[str, Any] = {"enabled": True}

        if is_not_empty(node.sni):
            tls["server_name"] = node.sni
        if is_not_empty(node.alpn):
            tls["alpn"] = node.alpn.split(",")
        if is_not_empty(node.fingerprint):
            tls["utls"] = {"enabled": True, "fingerprint": node.fingerprint}
        if node.allow_insecure == "true":
            tls["insecure"] = True

        if node.stream_security == "reality":
            reality: dict[str, Any] = {"enabled": True}
            if is_not_empty(node.public_key):
                reality["public_key"] = node.public_key
            if is_not_empty(node.short_id):
                reality["short_id"] = node.short_id
            tls["reality"] = reality

        outbound["tls"] = tls

    def _build_transport(self, node: ProfileItem, outbound: dict[str, Any]) -> None:
        """Build transport settings for an outbound."""
        network = node.network
        if is_null_or_empty(network) or network == "tcp":
            return

        transport: dict[str, Any] = {}

        if network == "ws":
            transport["type"] = "ws"
            if is_not_empty(node.path):
                transport["path"] = node.path
            if is_not_empty(node.request_host):
                transport["headers"] = {"Host": node.request_host}

        elif network in ("h2", "http"):
            transport["type"] = "http"
            if is_not_empty(node.path):
                transport["path"] = node.path
            if is_not_empty(node.request_host):
                transport["host"] = node.request_host.split(",")

        elif network == "grpc":
            transport["type"] = "grpc"
            if is_not_empty(node.path):
                transport["service_name"] = node.path

        elif network == "quic":
            transport["type"] = "quic"

        elif network == "httpupgrade":
            transport["type"] = "httpupgrade"
            if is_not_empty(node.path):
                transport["path"] = node.path
            if is_not_empty(node.request_host):
                transport["host"] = node.request_host

        if transport:
            outbound["transport"] = transport

    def _build_route(self) -> dict[str, Any]:
        """Build route section."""
        route: dict[str, Any] = {
            "auto_detect_interface": True,
            "rules": [
                {
                    "protocol": "dns",
                    "outbound": "dns-out",
                },
                {
                    "ip_is_private": True,
                    "outbound": "direct",
                },
            ],
        }

        # Add custom routing rules
        if self._context.routing_item and self._context.routing_item.rules:
            for rule in self._context.routing_item.rules:
                sbox_rule: dict[str, Any] = {}
                outbound_tag = rule.outbound_tag or "proxy"
                sbox_rule["outbound"] = outbound_tag
                if rule.domain:
                    sbox_rule["domain"] = rule.domain
                if rule.ip:
                    sbox_rule["ip_cidr"] = rule.ip
                if rule.port:
                    sbox_rule["port"] = rule.port
                route["rules"].append(sbox_rule)

        return route

    def _build_experimental(self) -> dict[str, Any]:
        """Build experimental section."""
        return {
            "clash_api": {
                "external_controller": "127.0.0.1:9090",
                "external_ui": "ui",
            }
        }
