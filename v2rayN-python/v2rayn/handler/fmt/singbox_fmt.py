"""Sing-box full config format handler.

Ported from ServiceLib/Handler/Fmt/SingboxFmt.cs.
"""

from __future__ import annotations

from v2rayn.common import json_utils, logging_config
from v2rayn.enums.config_type import EConfigType
from v2rayn.enums.core_type import ECoreType
from v2rayn.handler.fmt.base_fmt import write_all_text
from v2rayn.models.profile_item import ProfileItem

_tag = "SingboxFmt"


def resolve_full_config(str_data: str) -> ProfileItem | None:
    """Detect and resolve a Sing-box full JSON configuration.

    Args:
        str_data: Raw configuration data

    Returns:
        ProfileItem with Custom config type or None
    """
    try:
        data = json_utils.parse_json(str_data)
        if not data or not isinstance(data, dict):
            return None

        if not _is_singbox_config(data):
            return None

        item = ProfileItem()
        item.config_type = EConfigType.Custom
        item.core_type = ECoreType.sing_box
        item.address = write_all_text(str_data, "json")
        item.remarks = "Singbox_custom"

        return item
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
        return None


def _is_singbox_config(data: dict) -> bool:
    """Check if the JSON data looks like a Sing-box configuration."""
    return (
        "inbounds" in data
        and "outbounds" in data
        and ("route" in data or "dns" in data)
    )
