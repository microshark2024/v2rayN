"""Notice manager.

Ported from ServiceLib/Manager/NoticeManager.cs.
Manages application notifications and messages.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable


@dataclass
class NoticeItem:
    """A notification item."""

    title: str = ""
    content: str = ""
    level: str = "info"  # info, warning, error
    timestamp: datetime = field(default_factory=datetime.now)
    read: bool = False


class NoticeManager:
    """Manages application notifications."""

    def __init__(self):
        """Initialize notice manager."""
        self._notices: list[NoticeItem] = []
        self._on_notice: Callable[[NoticeItem], None] | None = None
        self._max_notices = 100

    def set_notice_callback(self, callback: Callable[[NoticeItem], None]) -> None:
        """Set callback for new notices."""
        self._on_notice = callback

    def add_notice(self, title: str, content: str = "", level: str = "info") -> None:
        """Add a notification.

        Args:
            title: Notice title
            content: Notice content
            level: Notice level (info, warning, error)
        """
        notice = NoticeItem(title=title, content=content, level=level)
        self._notices.append(notice)

        # Trim old notices
        if len(self._notices) > self._max_notices:
            self._notices = self._notices[-self._max_notices:]

        if self._on_notice:
            self._on_notice(notice)

    def get_all_notices(self) -> list[NoticeItem]:
        """Get all notices."""
        return list(self._notices)

    def get_unread_count(self) -> int:
        """Get unread notice count."""
        return sum(1 for n in self._notices if not n.read)

    def mark_all_read(self) -> None:
        """Mark all notices as read."""
        for n in self._notices:
            n.read = True

    def clear(self) -> None:
        """Clear all notices."""
        self._notices.clear()

    def send_message(self, content: str) -> None:
        """Send a quick message notification."""
        self.add_notice("", content, "info")
