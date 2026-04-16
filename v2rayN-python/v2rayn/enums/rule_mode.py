"""Rule mode enum."""

from enum import IntEnum


class ERuleMode(IntEnum):
    """Routing rule modes."""

    Rule = 0
    Global = 1
    Direct = 2
    Unchanged = 3
