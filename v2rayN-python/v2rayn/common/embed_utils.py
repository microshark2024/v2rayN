"""Embedded resource utilities.

Ported from ServiceLib/Common/EmbedUtils.cs.
Handles loading embedded resources (sample configs, templates).
"""

from __future__ import annotations

import os
from functools import lru_cache

from v2rayn.common import logging_config

_tag = "EmbedUtils"


@lru_cache(maxsize=128)
def get_embed_text(res: str) -> str:
    """Get embedded text resource.

    In Python, resources are loaded from the resources/sample directory
    instead of .NET embedded resources.

    Args:
        res: Resource name (e.g., 'ServiceLib.Sample.SampleClientConfig')

    Returns:
        Resource text content or empty string
    """
    try:
        # Convert .NET resource name to file path
        # e.g., "ServiceLib.Sample.SampleClientConfig" -> "SampleClientConfig"
        parts = res.split(".")
        if len(parts) >= 3 and parts[1] == "Sample":
            file_name = ".".join(parts[2:])
        else:
            file_name = parts[-1] if parts else res

        # Look for the resource file
        resource_dir = os.path.join(os.path.dirname(__file__), "..", "resources", "sample")
        resource_path = os.path.join(resource_dir, file_name)

        # Try with common extensions
        for ext in ["", ".json", ".yaml", ".yml", ".txt", ".sh", ".conf"]:
            full_path = resource_path + ext
            if os.path.exists(full_path):
                with open(full_path, "r", encoding="utf-8") as f:
                    return f.read()

        return ""
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
        return ""


def load_resource(res: str | None) -> str | None:
    """Load a file resource from disk.

    Args:
        res: File path

    Returns:
        File content or None
    """
    try:
        if res and os.path.exists(res):
            with open(res, "r", encoding="utf-8") as f:
                return f.read()
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
    return None
