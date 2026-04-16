"""V2ray/Xray core configuration service.

Ported from ServiceLib/Services/CoreConfig/V2ray/.
Generates V2ray/Xray JSON configuration from ProfileItems.
"""

from __future__ import annotations

from typing import Any

from v2rayn.common import json_utils, logging_config
from v2rayn.common.extensions import is_not_empty, is_null_or_empty
from v2rayn.enums.config_type import EConfigType
from v2rayn.enums.transport import ETransport
from v2rayn.global_config import NONE, STREAM_SECURITY
from v2rayn.models.config import Config
from v2rayn.models.misc import CoreConfigContext
from v2rayn.models.profile_item import ProfileItem
from v2rayn.models.v2ray_config import (
    Inbound,
    Outbound,
    StreamSettings,
    TlsSettings,
    V2rayConfig,
    WsSettings,
)

_tag = "CoreConfigV2rayService"


class CoreConfigV2rayService:
    """Generates V2ray/Xray JSON configuration."""

    def __init__(self, context: CoreConfigContext):
        """Initialize service."""
        self._context = context

    def generate_config(self) -> str:
        """Generate complete V2ray/Xray configuration.

        Returns:
            JSON string of the configuration
        """
        try:
            config = V2rayConfig()

            # Build log
            config.log = self._build_log()

            # Build inbounds
            config.inbounds = self._build_inbounds()

            # Build outbounds
            config.outbounds = self._build_outbounds()

            # Build routing
            config.routing = self._build_routing()

            # Build DNS
            config.dns = self._build_dns()

            return json_utils.serialize(config, indented=True)
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)
            return ""

    def _build_log(self) -> dict[str, Any]:
        """Build log configuration."""
        return {
            "loglevel": "warning",
            "access": "",
            "error": "",
        }

    def _build_inbounds(self) -> list[dict[str, Any]]:
        """Build inbound configurations."""
        app_config = self._context.app_config
        inbounds = []

        # SOCKS inbound
        socks_port = app_config.inbound_item.socks_port
        if socks_port > 0:
            inbounds.append(
                {
                    "tag": "socks",
                    "port": socks_port,
                    "listen": app_config.inbound_item.local_address or "127.0.0.1",
                    "protocol": "socks",
                    "sniffing": {
                        "enabled": True,
                        "destOverride": ["http", "tls"],
                    },
                    "settings": {
                        "auth": "noauth",
                        "udp": True,
                    },
                }
            )

        # HTTP inbound
        http_port = app_config.inbound_item.http_port
        if http_port > 0:
            inbounds.append(
                {
                    "tag": "http",
                    "port": http_port,
                    "listen": app_config.inbound_item.local_address or "127.0.0.1",
                    "protocol": "http",
                    "settings": {},
                }
            )

        return inbounds

    def _build_outbounds(self) -> list[dict[str, Any]]:
        """Build outbound configurations."""
        outbounds = []

        # Main proxy outbound
        node = self._context.node
        if node:
            proxy_outbound = self._build_proxy_outbound(node)
            if proxy_outbound:
                outbounds.append(proxy_outbound)

        # Direct outbound
        outbounds.append(
            {
                "tag": "direct",
                "protocol": "freedom",
                "settings": {},
            }
        )

        # Block outbound
        outbounds.append(
            {
                "tag": "block",
                "protocol": "blackhole",
                "settings": {
                    "response": {
                        "type": "http",
                    }
                },
            }
        )

        return outbounds

    def _build_proxy_outbound(self, node: ProfileItem) -> dict[str, Any] | None:
        """Build proxy outbound from a profile node."""
        config_type = node.config_type

        outbound: dict[str, Any] = {
            "tag": "proxy",
            "settings": {},
        }

        if config_type == EConfigType.VMess:
            outbound["protocol"] = "vmess"
            extra = node.get_protocol_extra()
            outbound["settings"] = {
                "vnext": [
                    {
                        "address": node.address,
                        "port": node.port,
                        "users": [
                            {
                                "id": node.password,
                                "alterId": int(extra.alter_id or 0),
                                "security": extra.vmess_security or "auto",
                            }
                        ],
                    }
                ]
            }

        elif config_type == EConfigType.VLESS:
            outbound["protocol"] = "vless"
            extra = node.get_protocol_extra()
            user: dict[str, Any] = {
                "id": node.password,
                "encryption": extra.vless_encryption or "none",
            }
            if is_not_empty(extra.flow):
                user["flow"] = extra.flow
            outbound["settings"] = {
                "vnext": [
                    {
                        "address": node.address,
                        "port": node.port,
                        "users": [user],
                    }
                ]
            }

        elif config_type == EConfigType.Trojan:
            outbound["protocol"] = "trojan"
            outbound["settings"] = {
                "servers": [
                    {
                        "address": node.address,
                        "port": node.port,
                        "password": node.password,
                    }
                ]
            }

        elif config_type == EConfigType.Shadowsocks:
            outbound["protocol"] = "shadowsocks"
            extra = node.get_protocol_extra()
            outbound["settings"] = {
                "servers": [
                    {
                        "address": node.address,
                        "port": node.port,
                        "password": node.password,
                        "method": extra.ss_method or "aes-256-gcm",
                    }
                ]
            }

        elif config_type == EConfigType.SOCKS:
            outbound["protocol"] = "socks"
            server: dict[str, Any] = {
                "address": node.address,
                "port": node.port,
            }
            if is_not_empty(node.username) or is_not_empty(node.password):
                server["users"] = [
                    {
                        "user": node.username or "",
                        "pass": node.password or "",
                    }
                ]
            outbound["settings"] = {"servers": [server]}

        else:
            return None

        # Add stream settings
        stream = self._build_stream_settings(node)
        if stream:
            outbound["streamSettings"] = stream

        return outbound

    def _build_stream_settings(self, node: ProfileItem) -> dict[str, Any] | None:
        """Build stream settings for an outbound."""
        if is_null_or_empty(node.network) and is_null_or_empty(node.stream_security):
            return None

        stream: dict[str, Any] = {}

        network = node.network or "tcp"
        stream["network"] = network

        # Security
        if is_not_empty(node.stream_security):
            stream["security"] = node.stream_security

            if node.stream_security == STREAM_SECURITY:
                tls: dict[str, Any] = {}
                if is_not_empty(node.sni):
                    tls["serverName"] = node.sni
                if is_not_empty(node.alpn):
                    tls["alpn"] = node.alpn.split(",")
                if is_not_empty(node.fingerprint):
                    tls["fingerprint"] = node.fingerprint
                if node.allow_insecure == "true":
                    tls["allowInsecure"] = True
                stream["tlsSettings"] = tls

            elif node.stream_security == "reality":
                reality: dict[str, Any] = {}
                if is_not_empty(node.sni):
                    reality["serverName"] = node.sni
                if is_not_empty(node.fingerprint):
                    reality["fingerprint"] = node.fingerprint
                if is_not_empty(node.public_key):
                    reality["publicKey"] = node.public_key
                if is_not_empty(node.short_id):
                    reality["shortId"] = node.short_id
                if is_not_empty(node.spider_x):
                    reality["spiderX"] = node.spider_x
                stream["realitySettings"] = reality

        # Transport
        if network == "ws":
            ws: dict[str, Any] = {}
            if is_not_empty(node.path):
                ws["path"] = node.path
            if is_not_empty(node.request_host):
                ws["headers"] = {"Host": node.request_host}
            stream["wsSettings"] = ws

        elif network == "h2" or network == "http":
            h2: dict[str, Any] = {}
            if is_not_empty(node.path):
                h2["path"] = node.path
            if is_not_empty(node.request_host):
                h2["host"] = node.request_host.split(",")
            stream["httpSettings"] = h2

        elif network == "grpc":
            grpc: dict[str, Any] = {}
            if is_not_empty(node.path):
                grpc["serviceName"] = node.path
            if is_not_empty(node.header_type):
                grpc["mode"] = node.header_type
            if is_not_empty(node.request_host):
                grpc["authority"] = node.request_host
            stream["grpcSettings"] = grpc

        elif network == "kcp":
            kcp: dict[str, Any] = {}
            if is_not_empty(node.header_type) and node.header_type != NONE:
                kcp["header"] = {"type": node.header_type}
            if is_not_empty(node.path):
                kcp["seed"] = node.path
            stream["kcpSettings"] = kcp

        elif network == "quic":
            quic: dict[str, Any] = {}
            if is_not_empty(node.header_type) and node.header_type != NONE:
                quic["header"] = {"type": node.header_type}
            if is_not_empty(node.request_host):
                quic["security"] = node.request_host
            if is_not_empty(node.path):
                quic["key"] = node.path
            stream["quicSettings"] = quic

        elif network in ("httpupgrade", "xhttp"):
            settings: dict[str, Any] = {}
            if is_not_empty(node.path):
                settings["path"] = node.path
            if is_not_empty(node.request_host):
                settings["host"] = node.request_host
            stream[f"{network}Settings"] = settings

        return stream

    def _build_routing(self) -> dict[str, Any]:
        """Build routing configuration."""
        routing: dict[str, Any] = {
            "domainStrategy": "IPIfNonMatch",
            "rules": [],
        }

        rules: list[dict[str, Any]] = []

        # Private IP direct
        rules.append(
            {
                "type": "field",
                "ip": ["geoip:private"],
                "outboundTag": "direct",
            }
        )

        # Add routing rules from context
        if self._context.routing_item and self._context.routing_item.rules:
            for rule in self._context.routing_item.rules:
                v2ray_rule: dict[str, Any] = {
                    "type": "field",
                    "outboundTag": rule.outbound_tag or "proxy",
                }
                if rule.domain:
                    v2ray_rule["domain"] = rule.domain
                if rule.ip:
                    v2ray_rule["ip"] = rule.ip
                if rule.port:
                    v2ray_rule["port"] = rule.port
                rules.append(v2ray_rule)

        routing["rules"] = rules
        return routing

    def _build_dns(self) -> dict[str, Any]:
        """Build DNS configuration."""
        dns: dict[str, Any] = {
            "servers": [
                "8.8.8.8",
                "1.1.1.1",
                {
                    "address": "114.114.114.114",
                    "port": 53,
                    "domains": ["geosite:cn"],
                    "expectIPs": ["geoip:cn"],
                },
            ]
        }
        return dns
