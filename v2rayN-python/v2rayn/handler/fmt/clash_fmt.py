"""Clash/Mihomo full config format handler.

Ported from ServiceLib/Handler/Fmt/ClashFmt.cs.
"""

from __future__ import annotations

from v2rayn.common import logging_config, yaml_utils
from v2rayn.enums.config_type import EConfigType
from v2rayn.enums.core_type import ECoreType
from v2rayn.handler.fmt.base_fmt import write_all_text
from v2rayn.models.profile_item import ProfileItem

_tag = "ClashFmt"


def resolve_full_config(str_data: str) -> ProfileItem | None:
    """Detect and resolve a Clash/Mihomo YAML configuration.

    Args:
        str_data: Raw configuration data

    Returns:
        ProfileItem with Custom config type or None
    """
    try:
        data = yaml_utils.deserialize(str_data)
        if not data or not isinstance(data, dict):
            return None

        if "proxies" not in data and "proxy-groups" not in data:
            return None

        item = ProfileItem()
        item.config_type = EConfigType.Custom
        item.core_type = ECoreType.mihomo
        item.address = write_all_text(str_data, "yaml")
        item.remarks = "Clash_custom"

        return item
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
        return None
