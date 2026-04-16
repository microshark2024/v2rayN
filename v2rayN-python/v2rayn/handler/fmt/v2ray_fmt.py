"""V2Ray/Xray full config format handler.

Ported from ServiceLib/Handler/Fmt/V2rayFmt.cs.
"""

from __future__ import annotations

from v2rayn.common import json_utils, logging_config
from v2rayn.enums.config_type import EConfigType
from v2rayn.enums.core_type import ECoreType
from v2rayn.handler.fmt.base_fmt import contains, write_all_text
from v2rayn.models.profile_item import ProfileItem

_tag = "V2rayFmt"


def resolve_full_config(str_data: str) -> ProfileItem | None:
    """Detect and resolve a V2Ray/Xray full JSON configuration.

    Args:
        str_data: Raw configuration data

    Returns:
        ProfileItem with Custom config type or None
    """
    try:
        data = json_utils.parse_json(str_data)
        if data is None:
            return None

        if isinstance(data, list):
            # Array format (multi-config)
            if not data:
                return None
            if not _is_v2ray_config(data[0] if isinstance(data[0], dict) else {}):
                return None
        elif isinstance(data, dict):
            if not _is_v2ray_config(data):
                return None
        else:
            return None

        item = ProfileItem()
        item.config_type = EConfigType.Custom
        item.core_type = ECoreType.Xray
        item.address = write_all_text(str_data, "json")
        item.remarks = "V2ray_custom"

        return item
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
        return None


def _is_v2ray_config(data: dict) -> bool:
    """Check if the JSON data looks like a V2Ray configuration."""
    return (
        "inbounds" in data
        and "outbounds" in data
        and ("routing" in data or "dns" in data)
    )
