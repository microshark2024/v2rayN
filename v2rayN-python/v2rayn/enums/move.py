"""Move direction enum."""

from enum import IntEnum


class EMove(IntEnum):
    """Move direction types for reordering items."""

    Top = 1
    Up = 2
    Down = 3
    Bottom = 4
    Position = 5
