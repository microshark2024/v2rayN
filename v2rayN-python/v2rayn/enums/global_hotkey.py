"""Global hotkey actions enum."""

from enum import IntEnum


class EGlobalHotkey(IntEnum):
    """Global hotkey action types."""

    ShowForm = 0
    SystemProxyClear = 1
    SystemProxySet = 2
    SystemProxyUnchanged = 3
    SystemProxyPac = 4
