"""System proxy type enum."""

from enum import IntEnum


class ESysProxyType(IntEnum):
    """System proxy setting types."""

    ForcedClear = 0
    ForcedChange = 1
    Unchanged = 2
    Pac = 3
