"""YAML utility functions.

Ported from ServiceLib/Common/YamlUtils.cs.
Uses PyYAML library.
"""

from __future__ import annotations

from typing import Any

from v2rayn.common import logging_config

_tag = "YamlUtils"


def deserialize(str_yaml: str | None) -> dict | None:
    """Deserialize YAML string to dictionary.

    Args:
        str_yaml: YAML string to deserialize

    Returns:
        Dictionary or None
    """
    try:
        if not str_yaml or not str_yaml.strip():
            return None
        import yaml

        return yaml.safe_load(str_yaml)
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
        return None


def serialize(obj: Any, indented: bool = True) -> str:
    """Serialize object to YAML string.

    Args:
        obj: Object to serialize
        indented: Whether to use indented format (always true for YAML)

    Returns:
        YAML string
    """
    try:
        if obj is None:
            return ""
        import yaml

        return yaml.dump(
            obj,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
        return ""


def pre_process_yaml(str_yaml: str) -> str:
    """Pre-process YAML string by removing comment-only lines.

    Args:
        str_yaml: Raw YAML string

    Returns:
        Processed YAML string
    """
    if not str_yaml:
        return ""

    lines = []
    for line in str_yaml.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        lines.append(line)
    return "\n".join(lines)
