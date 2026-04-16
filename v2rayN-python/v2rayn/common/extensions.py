"""String extension functions.

Ported from ServiceLib/Common/Extension.cs.
Python equivalents of C# extension methods.
"""

from __future__ import annotations

from v2rayn.enums.config_type import EConfigType


def is_null_or_empty(value: str | None) -> bool:
    """Check if string is None, empty, or whitespace only."""
    return value is None or not value.strip()


def is_not_empty(value: str | None) -> bool:
    """Check if string is not None/empty/whitespace."""
    return value is not None and bool(value.strip())


def null_if_empty(value: str | None) -> str | None:
    """Return None if value is empty/whitespace."""
    return None if is_null_or_empty(value) else value


def begin_with_any(s: str | None, chars: str) -> bool:
    """Check if string begins with any of the specified characters."""
    if is_null_or_empty(s):
        return False
    return s[0] in chars  # type: ignore


def trim_ex(value: str | None) -> str:
    """Trim whitespace, returning empty string for None."""
    return "" if value is None else value.strip()


def remove_prefix(value: str, prefix: str) -> str:
    """Remove prefix from string if it starts with it."""
    if value.startswith(prefix):
        return value[len(prefix) :]
    return value


def upper_first_char(value: str) -> str:
    """Capitalize the first character of a string."""
    if not value:
        return ""
    return value[0].upper() + value[1:]


def append_quotes(value: str) -> str:
    """Wrap string in double quotes."""
    if not value:
        return ""
    return f'"{value}"'


def to_int(value: str | None, default_value: int = 0) -> int:
    """Parse string to int, returning default on failure."""
    if value is None:
        return default_value
    try:
        return int(value)
    except (ValueError, TypeError):
        return default_value


def append_empty(source: list[str]) -> list[str]:
    """Append an empty string to the end of a list."""
    return source + [""]


def is_group_type(config_type: EConfigType) -> bool:
    """Check if config type is a group type."""
    return config_type in (EConfigType.PolicyGroup, EConfigType.ProxyChain)


def is_complex_type(config_type: EConfigType) -> bool:
    """Check if config type is a complex type."""
    return config_type in (EConfigType.Custom, EConfigType.PolicyGroup, EConfigType.ProxyChain)
