"""Multiple load balancing strategy enum."""

from enum import IntEnum


class EMultipleLoad(IntEnum):
    """Load balancing strategies for proxy groups."""

    LeastPing = 0
    Fallback = 1
    Random = 2
    RoundRobin = 3
    LeastLoad = 4
