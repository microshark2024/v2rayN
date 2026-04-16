"""Node validator.

Ported from ServiceLib/Handler/Builder/NodeValidator.cs.
Validates proxy nodes before use.
"""

from __future__ import annotations

from v2rayn.common.extensions import is_not_empty, is_null_or_empty
from v2rayn.enums.config_type import EConfigType
from v2rayn.global_config import MAX_PORT
from v2rayn.models.profile_item import ProfileItem


def validate_node(item: ProfileItem) -> bool:
    """Validate a proxy node.

    Args:
        item: Profile item to validate

    Returns:
        True if valid
    """
    if item.is_complex():
        return True

    if is_null_or_empty(item.address):
        return False

    if item.port <= 0 or item.port >= MAX_PORT:
        return False

    config_type = item.config_type

    if config_type in (EConfigType.VMess, EConfigType.VLESS, EConfigType.Trojan):
        if is_null_or_empty(item.password):
            return False

    if config_type == EConfigType.Shadowsocks:
        if is_null_or_empty(item.password):
            return False
        extra = item.get_protocol_extra()
        if is_null_or_empty(extra.ss_method):
            return False

    return True
