"""Rule type enum."""

from enum import IntEnum


class ERuleType(IntEnum):
    """Rule types for routing configuration."""

    ALL = 0
    Routing = 1
    DNS = 2
