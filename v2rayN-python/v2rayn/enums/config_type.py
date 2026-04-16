"""Configuration types for proxy protocols."""

from enum import IntEnum


class EConfigType(IntEnum):
    """Proxy protocol configuration types."""

    VMess = 1
    Custom = 2
    Shadowsocks = 3
    SOCKS = 4
    VLESS = 5
    Trojan = 6
    Hysteria2 = 7
    TUIC = 8
    WireGuard = 9
    HTTP = 10
    Anytls = 11
    Naive = 12
    PolicyGroup = 101
    ProxyChain = 102

    def is_complex_type(self) -> bool:
        """Check if this config type is a complex type (PolicyGroup or ProxyChain)."""
        return self in (EConfigType.PolicyGroup, EConfigType.ProxyChain)
