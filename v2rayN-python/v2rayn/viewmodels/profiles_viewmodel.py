"""Profiles ViewModel.

Ported from ServiceLib/ViewModels/ProfilesViewModel.cs (~879 lines).
Manages the profile list display, filtering, and operations.
"""

from __future__ import annotations

from typing import Any, Callable

from v2rayn.common import logging_config
from v2rayn.enums.move import EMove
from v2rayn.enums.speed_action_type import ESpeedActionType
from v2rayn.handler.config_handler import ConfigHandler
from v2rayn.handler.fmt.fmt_handler import get_share_uri
from v2rayn.manager.profile_ex_manager import ProfileExManager
from v2rayn.models.profile_item import ProfileItem
from v2rayn.services.speedtest_service import SpeedtestService

_tag = "ProfilesViewModel"


class ProfilesViewModel:
    """Manages profile list data and operations."""

    def __init__(self, config_handler: ConfigHandler):
        """Initialize profiles ViewModel."""
        self._config_handler = config_handler
        self._profile_ex = ProfileExManager()
        self._speedtest = SpeedtestService()
        self._selected_ids: list[str] = []
        self._filter_sub_id: str = ""
        self._filter_text: str = ""
        self._sort_column: str = ""
        self._sort_ascending: bool = True
        self._on_refresh: Callable[[], None] | None = None

    def set_refresh_callback(self, callback: Callable[[], None]) -> None:
        """Set callback for list refresh."""
        self._on_refresh = callback

    @property
    def filter_sub_id(self) -> str:
        return self._filter_sub_id

    @filter_sub_id.setter
    def filter_sub_id(self, value: str) -> None:
        self._filter_sub_id = value
        self._refresh()

    @property
    def filter_text(self) -> str:
        return self._filter_text

    @filter_text.setter
    def filter_text(self, value: str) -> None:
        self._filter_text = value
        self._refresh()

    def get_profiles(self) -> list[dict[str, Any]]:
        """Get filtered and sorted profile list for display.

        Returns:
            List of profile data dicts
        """
        profiles = self._config_handler.get_all_profiles(self._filter_sub_id)

        # Apply text filter
        if self._filter_text:
            ft = self._filter_text.lower()
            profiles = [
                p
                for p in profiles
                if ft in (p.remarks or "").lower()
                or ft in (p.address or "").lower()
            ]

        # Build display data
        result = []
        for p in profiles:
            ex = self._profile_ex.get_item(p.index_id)
            result.append(
                {
                    "index_id": p.index_id,
                    "config_type": p.config_type.name if p.config_type else "",
                    "remarks": p.remarks,
                    "address": p.address,
                    "port": p.port,
                    "network": p.network or "",
                    "tls": p.stream_security or "",
                    "delay": ex.delay,
                    "speed": ex.speed,
                    "subid": p.subid,
                }
            )

        # Sort
        if self._sort_column:
            result.sort(
                key=lambda x: x.get(self._sort_column, ""),
                reverse=not self._sort_ascending,
            )

        return result

    def set_sort(self, column: str) -> None:
        """Set sort column."""
        if self._sort_column == column:
            self._sort_ascending = not self._sort_ascending
        else:
            self._sort_column = column
            self._sort_ascending = True
        self._refresh()

    def set_selected(self, ids: list[str]) -> None:
        """Set selected profile IDs."""
        self._selected_ids = ids

    def add_profile(self, item: ProfileItem) -> int:
        """Add a profile."""
        result = self._config_handler.add_profile(item)
        if result == 0:
            self._refresh()
        return result

    def remove_selected(self) -> int:
        """Remove selected profiles."""
        count = 0
        for id in self._selected_ids:
            if self._config_handler.remove_profile(id) == 0:
                self._profile_ex.remove(id)
                count += 1
        if count > 0:
            self._refresh()
        return count

    def move_selected(self, move_type: EMove) -> None:
        """Move selected profiles."""
        for id in self._selected_ids:
            self._config_handler.move_profile(id, move_type)
        self._refresh()

    def get_share_uris(self) -> list[str]:
        """Get share URIs for selected profiles."""
        uris = []
        for id in self._selected_ids:
            profile = self._config_handler.get_profile(id)
            if profile:
                uri = get_share_uri(profile)
                if uri:
                    uris.append(uri)
        return uris

    async def run_speed_test(self, action_type: ESpeedActionType) -> None:
        """Run speed test on selected profiles."""
        profiles = [
            self._config_handler.get_profile(id)
            for id in self._selected_ids
            if self._config_handler.get_profile(id)
        ]

        self._speedtest.set_result_callback(
            lambda id, delay, speed: self._on_test_result(id, delay, speed)
        )

        await self._speedtest.run_test(profiles, action_type)  # type: ignore[arg-type]
        self._refresh()

    def _on_test_result(self, index_id: str, delay: int, speed: str) -> None:
        """Handle speed test result."""
        if delay >= 0:
            self._profile_ex.set_delay(index_id, delay)
        if speed:
            self._profile_ex.set_speed(index_id, speed)

    def _refresh(self) -> None:
        """Trigger list refresh."""
        if self._on_refresh:
            self._on_refresh()

    def add_batch_profiles(self, data: str, sub_id: str = "") -> int:
        """Add profiles from batch data."""
        count = self._config_handler.add_batch_profiles(data, sub_id)
        if count > 0:
            self._refresh()
        return count
