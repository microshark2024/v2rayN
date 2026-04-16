"""Core configuration context builder.

Ported from ServiceLib/Handler/Builder/CoreConfigContextBuilder.cs.
Builds the configuration context for core process initialization.
"""

from __future__ import annotations

from v2rayn.common import logging_config
from v2rayn.enums.core_type import ECoreType
from v2rayn.handler.config_handler import ConfigHandler
from v2rayn.models.config import Config
from v2rayn.models.misc import CoreConfigContext
from v2rayn.models.profile_item import ProfileItem

_tag = "CoreConfigContextBuilder"


class CoreConfigContextBuilder:
    """Builds CoreConfigContext for generating core configurations."""

    def __init__(self, config_handler: ConfigHandler):
        """Initialize builder."""
        self._config_handler = config_handler

    def build(self, node: ProfileItem, core_type: ECoreType) -> CoreConfigContext:
        """Build a core configuration context.

        Args:
            node: Target profile node
            core_type: Core type to use

        Returns:
            CoreConfigContext instance
        """
        config = self._config_handler.config

        context = CoreConfigContext()
        context.node = node
        context.run_core_type = core_type
        context.app_config = config
        context.is_tun_enabled = config.tun_mode_item.enable_tun

        # Set routing item
        routing_id = config.routing_basic_item.routing_index_id
        if routing_id:
            context.routing_item = self._config_handler.get_routing_item(routing_id)

        # Set DNS item
        context.simple_dns_item = config.simple_dns_item

        # Build proxy map
        context.all_proxies_map = {}
        for profile in self._config_handler.get_all_profiles():
            if profile.index_id:
                context.all_proxies_map[profile.index_id] = profile

        return context
