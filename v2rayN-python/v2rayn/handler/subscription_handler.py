"""Subscription handler.

Ported from ServiceLib/Handler/SubscriptionHandler.cs.
Manages subscription updates and profile synchronization.
"""

from __future__ import annotations

from v2rayn.common import logging_config
from v2rayn.common.extensions import is_not_empty, is_null_or_empty
from v2rayn.common.utils import base64_decode
from v2rayn.global_config import USER_AGENT_TEXTS
from v2rayn.handler.config_handler import ConfigHandler
from v2rayn.models.routing import SubItem

_tag = "SubscriptionHandler"


class SubscriptionHandler:
    """Handles subscription updates."""

    def __init__(self, config_handler: ConfigHandler):
        """Initialize subscription handler."""
        self._config_handler = config_handler

    async def update_subscription(self, sub_item: SubItem) -> int:
        """Update a single subscription.

        Args:
            sub_item: Subscription to update

        Returns:
            Number of profiles added/updated
        """
        if is_null_or_empty(sub_item.url):
            return 0

        try:
            from v2rayn.helper.downloader import DownloaderHelper

            # Determine user agent
            user_agent = ""
            if is_not_empty(sub_item.user_agent) and sub_item.user_agent in USER_AGENT_TEXTS:
                user_agent = USER_AGENT_TEXTS[sub_item.user_agent]

            downloader = DownloaderHelper(user_agent=user_agent)
            content = await downloader.download_string_async(sub_item.url)

            if is_null_or_empty(content):
                return 0

            # Try base64 decode
            decoded = base64_decode(content)
            if decoded and ("://" in decoded or "\n" in decoded):
                content = decoded

            # Remove old profiles for this subscription
            old_profiles = self._config_handler.get_all_profiles(sub_item.id)
            for p in old_profiles:
                self._config_handler.remove_profile(p.index_id)

            # Add new profiles
            count = self._config_handler.add_batch_profiles(content, sub_item.id, is_sub=True)
            return count
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)
            return 0

    async def update_all_subscriptions(self) -> int:
        """Update all enabled subscriptions.

        Returns:
            Total number of profiles added/updated
        """
        total = 0
        for sub in self._config_handler.get_all_subs():
            if sub.enabled:
                count = await self.update_subscription(sub)
                total += count
        return total
