"""Configuration handler.

Ported from ServiceLib/Handler/ConfigHandler.cs (~2628 lines).
Core configuration CRUD operations for profiles, subscriptions, routing, etc.
"""

from __future__ import annotations

import json
import os
from typing import Any

from v2rayn.common import json_utils, logging_config
from v2rayn.common.extensions import is_not_empty, is_null_or_empty
from v2rayn.common.utils import get_config_path, get_guid, is_guid_by_parse
from v2rayn.enums.config_type import EConfigType
from v2rayn.enums.move import EMove
from v2rayn.global_config import CONFIG_FILE_NAME
from v2rayn.models.config import Config
from v2rayn.models.profile_item import ProfileItem, ProtocolExtraItem
from v2rayn.models.routing import DNSItem, RoutingItem, RulesItem, SubItem

_tag = "ConfigHandler"


class ConfigHandler:
    """Handles all configuration CRUD operations."""

    def __init__(self):
        """Initialize the config handler."""
        self._config: Config | None = None
        self._profiles: list[ProfileItem] = []
        self._subs: list[SubItem] = []
        self._routing_items: list[RoutingItem] = []
        self._dns_items: list[DNSItem] = []

    @property
    def config(self) -> Config:
        """Get the current configuration."""
        if self._config is None:
            self._config = Config()
        return self._config

    # ========================================================================
    # Configuration Load/Save
    # ========================================================================

    def load_config(self) -> bool:
        """Load configuration from file.

        Returns:
            True on success
        """
        try:
            config_path = get_config_path(CONFIG_FILE_NAME)
            if not os.path.exists(config_path):
                self._config = Config()
                return self.save_config()

            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self._config = Config()
            # Populate config from loaded data
            if isinstance(data, dict):
                for key, value in data.items():
                    attr_name = self._camel_to_snake(key)
                    if hasattr(self._config, attr_name):
                        setattr(self._config, attr_name, value)

            return True
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)
            self._config = Config()
            return False

    def save_config(self) -> bool:
        """Save configuration to file.

        Returns:
            True on success
        """
        try:
            config_path = get_config_path(CONFIG_FILE_NAME)
            json_str = json_utils.serialize(self.config, indented=True)
            with open(config_path, "w", encoding="utf-8") as f:
                f.write(json_str)
            return True
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)
            return False

    # ========================================================================
    # Profile CRUD
    # ========================================================================

    def add_profile(self, item: ProfileItem) -> int:
        """Add a new profile.

        Args:
            item: Profile to add

        Returns:
            0 on success, -1 on failure
        """
        try:
            if is_null_or_empty(item.index_id):
                item.index_id = get_guid()

            self._profiles.append(item)
            return 0
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)
            return -1

    def remove_profile(self, index_id: str) -> int:
        """Remove a profile by ID.

        Args:
            index_id: Profile index ID

        Returns:
            0 on success, -1 on failure
        """
        try:
            self._profiles = [p for p in self._profiles if p.index_id != index_id]
            return 0
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)
            return -1

    def get_profile(self, index_id: str) -> ProfileItem | None:
        """Get a profile by ID.

        Args:
            index_id: Profile index ID

        Returns:
            ProfileItem or None
        """
        for p in self._profiles:
            if p.index_id == index_id:
                return p
        return None

    def get_all_profiles(self, sub_id: str = "") -> list[ProfileItem]:
        """Get all profiles, optionally filtered by subscription ID.

        Args:
            sub_id: Optional subscription ID filter

        Returns:
            List of profiles
        """
        if sub_id:
            return [p for p in self._profiles if p.subid == sub_id]
        return list(self._profiles)

    def update_profile(self, item: ProfileItem) -> int:
        """Update an existing profile.

        Args:
            item: Updated profile

        Returns:
            0 on success, -1 on failure
        """
        try:
            for i, p in enumerate(self._profiles):
                if p.index_id == item.index_id:
                    self._profiles[i] = item
                    return 0
            return -1
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)
            return -1

    def move_profile(self, index_id: str, move_type: EMove) -> int:
        """Move a profile in the list.

        Args:
            index_id: Profile index ID
            move_type: Direction to move

        Returns:
            0 on success, -1 on failure
        """
        try:
            idx = next(
                (i for i, p in enumerate(self._profiles) if p.index_id == index_id),
                -1,
            )
            if idx < 0:
                return -1

            if move_type == EMove.Top and idx > 0:
                item = self._profiles.pop(idx)
                self._profiles.insert(0, item)
            elif move_type == EMove.Up and idx > 0:
                self._profiles[idx], self._profiles[idx - 1] = (
                    self._profiles[idx - 1],
                    self._profiles[idx],
                )
            elif move_type == EMove.Down and idx < len(self._profiles) - 1:
                self._profiles[idx], self._profiles[idx + 1] = (
                    self._profiles[idx + 1],
                    self._profiles[idx],
                )
            elif move_type == EMove.Bottom and idx < len(self._profiles) - 1:
                item = self._profiles.pop(idx)
                self._profiles.append(item)

            return 0
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)
            return -1

    def set_default_profile(self, index_id: str) -> int:
        """Set the default/active profile.

        Args:
            index_id: Profile index ID

        Returns:
            0 on success
        """
        self.config.index_id = index_id
        return 0

    def get_default_profile(self) -> ProfileItem | None:
        """Get the current default/active profile."""
        return self.get_profile(self.config.index_id)

    # ========================================================================
    # Subscription CRUD
    # ========================================================================

    def add_sub(self, item: SubItem) -> int:
        """Add a subscription.

        Args:
            item: Subscription to add

        Returns:
            0 on success
        """
        if is_null_or_empty(item.id):
            item.id = get_guid()
        self._subs.append(item)
        return 0

    def remove_sub(self, sub_id: str) -> int:
        """Remove a subscription.

        Args:
            sub_id: Subscription ID

        Returns:
            0 on success
        """
        self._subs = [s for s in self._subs if s.id != sub_id]
        # Also remove associated profiles
        self._profiles = [p for p in self._profiles if p.subid != sub_id]
        return 0

    def get_all_subs(self) -> list[SubItem]:
        """Get all subscriptions."""
        return list(self._subs)

    def get_sub(self, sub_id: str) -> SubItem | None:
        """Get a subscription by ID."""
        for s in self._subs:
            if s.id == sub_id:
                return s
        return None

    # ========================================================================
    # Routing CRUD
    # ========================================================================

    def add_routing_item(self, item: RoutingItem) -> int:
        """Add a routing item."""
        if is_null_or_empty(item.id):
            item.id = get_guid()
        self._routing_items.append(item)
        return 0

    def remove_routing_item(self, routing_id: str) -> int:
        """Remove a routing item."""
        self._routing_items = [r for r in self._routing_items if r.id != routing_id]
        return 0

    def get_all_routing_items(self) -> list[RoutingItem]:
        """Get all routing items."""
        return list(self._routing_items)

    def get_routing_item(self, routing_id: str) -> RoutingItem | None:
        """Get a routing item by ID."""
        for r in self._routing_items:
            if r.id == routing_id:
                return r
        return None

    # ========================================================================
    # Import/Export
    # ========================================================================

    def add_batch_profiles(self, data: str, sub_id: str = "", is_sub: bool = True) -> int:
        """Add profiles from batch data (subscription content or multiple URLs).

        Args:
            data: Raw data (base64, URLs, JSON, etc.)
            sub_id: Subscription ID
            is_sub: Whether this is from a subscription

        Returns:
            Number of profiles added
        """
        from v2rayn.common.utils import base64_decode
        from v2rayn.handler.fmt.fmt_handler import resolve_config

        count = 0
        try:
            # Try base64 decode first
            decoded = base64_decode(data)
            if decoded and ("\n" in decoded or "://" in decoded):
                data = decoded

            items = resolve_config(data)
            for item in items:
                item.subid = sub_id
                item.is_sub = is_sub
                if self.add_profile(item) == 0:
                    count += 1
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)

        return count

    # ========================================================================
    # Helpers
    # ========================================================================

    @staticmethod
    def _camel_to_snake(name: str) -> str:
        """Convert camelCase to snake_case."""
        import re

        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
