"""Speed test action type enum."""

from enum import IntEnum


class ESpeedActionType(IntEnum):
    """Speed test action types."""

    Tcping = 0
    Realping = 1
    Speedtest = 2
    Mixedtest = 3
    FastRealping = 4
