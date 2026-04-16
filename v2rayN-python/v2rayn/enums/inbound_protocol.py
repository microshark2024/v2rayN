"""Inbound protocol enum."""

from enum import IntEnum


class EInboundProtocol(IntEnum):
    """Inbound protocol types for local proxy listeners."""

    socks = 0
    socks2 = 1
    socks3 = 2
    pac = 3
    api = 4
    api2 = 5
    mixed = 6
    speedtest = 21
