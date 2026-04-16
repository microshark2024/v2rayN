"""Profile extension manager.

Ported from ServiceLib/Manager/ProfileExManager.cs.
Manages extended profile data (test results, statistics, etc.).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from v2rayn.common import logging_config

_tag = "ProfileExManager"


@dataclass
class ProfileExItem:
    """Extended profile data."""

    index_id: str = ""
    delay: int = 0
    speed: str = ""
    sort: int = 0
    last_test_time: str = ""
    upload: int = 0
    download: int = 0


class ProfileExManager:
    """Manages extended profile data."""

    def __init__(self):
        """Initialize profile extension manager."""
        self._items: dict[str, ProfileExItem] = {}

    def get_item(self, index_id: str) -> ProfileExItem:
        """Get extended data for a profile.

        Args:
            index_id: Profile ID

        Returns:
            ProfileExItem (creates if not exists)
        """
        if index_id not in self._items:
            self._items[index_id] = ProfileExItem(index_id=index_id)
        return self._items[index_id]

    def set_delay(self, index_id: str, delay: int) -> None:
        """Set test delay result."""
        item = self.get_item(index_id)
        item.delay = delay
        item.last_test_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def set_speed(self, index_id: str, speed: str) -> None:
        """Set test speed result."""
        item = self.get_item(index_id)
        item.speed = speed

    def set_statistics(self, index_id: str, upload: int, download: int) -> None:
        """Set traffic statistics."""
        item = self.get_item(index_id)
        item.upload += upload
        item.download += download

    def clear_test_results(self, index_ids: list[str] | None = None) -> None:
        """Clear test results for profiles."""
        if index_ids:
            for id in index_ids:
                if id in self._items:
                    self._items[id].delay = 0
                    self._items[id].speed = ""
        else:
            for item in self._items.values():
                item.delay = 0
                item.speed = ""

    def get_all(self) -> dict[str, ProfileExItem]:
        """Get all extended profile data."""
        return dict(self._items)

    def remove(self, index_id: str) -> None:
        """Remove extended data for a profile."""
        self._items.pop(index_id, None)
