"""HTML page detection utility.

Ported from ServiceLib/Handler/Fmt/HtmlPageFmt.cs.
"""

from __future__ import annotations


def is_html_page(str_data: str) -> bool:
    """Check if the data is an HTML page.

    Args:
        str_data: Raw data string

    Returns:
        True if the data looks like HTML
    """
    if not str_data:
        return False

    lower = str_data.lower().strip()
    return lower.startswith("<!doctype html") or lower.startswith("<html") or "<html" in lower[:500]
