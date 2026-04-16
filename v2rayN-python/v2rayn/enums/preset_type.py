"""Preset type enum."""

from enum import IntEnum


class EPresetType(IntEnum):
    """Regional preset types for routing rules."""

    Default = 0
    Russia = 1
    Iran = 2
