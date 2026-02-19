"""
Bot configuration loader
Handles loading and parsing bot JSON configurations
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from .element_types import BotInfo


class ConfigLoader:
    """Loads bot configuration file"""

    @staticmethod
    def load(config_path: str) -> Dict[str, Any]:
        """
        Load bot configuration from file

        Args:
            config: Bot configuration dictionary

        Returns:
            Bot configuration dictionary

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config is invalid JSON
        """

        if not Path(config_path).exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")

        return config

        # # Handle nested "data.attributes" structure (from real bot exports)
        # config = self._extract_bot_attributes(config)

        # # Normalize scenario slugs
        # config = self._normalize_scenario_slugs(config)

        # return config

    # def load_as_bot_info(self) -> BotInfo:
    #     """
    #     Load configuration and return as BotInfo object

    #     Returns:
    #         BotInfo object with parsed configuration
    #     """
    #     config = self.load()
    #     return self._build_bot_info(config)

    # @staticmethod
    # def _extract_bot_attributes(config: Dict[str, Any]) -> Dict[str, Any]:
    #     """
    #     Extract bot attributes from nested data structure if present

    #     Handles both formats:
    #     - Raw: {"scenarios": [...], "bot_name": "...", ...}
    #     - Exported: {"data": {"attributes": {...}}}
    #     """
    #     if "data" in config and "attributes" in config.get("data", {}):
    #         return config["data"]["attributes"]
    #     return config

    # @staticmethod
    # def _normalize_scenario_slugs(config: Dict[str, Any]) -> Dict[str, Any]:
    #     """
    #     Ensure all scenarios have slug field

    #     If slug is missing, create from name or id
    #     """
    #     for scenario in config.get("scenarios", []):
    #         if "slug" not in scenario:
    #             name = scenario.get("name", "unknown")
    #             scenario["slug"] = name.lower().replace(" ", "_").replace("_", "")

    #     return config

    # @staticmethod
    # def _build_bot_info(config: Dict[str, Any]) -> BotInfo:
    #     """Build BotInfo object from configuration"""
    #     return BotInfo(
    #         bot_name=config.get("bot_name", "unknown"),
    #         bot_id=config.get("bot_id"),
    #         version_id=config.get("id"),
    #         no_match_stub_answer=config.get("no_match_stub_answer", ""),
    #         request_ttl_in_seconds=config.get("request_ttl_in_seconds", 30),
    #     )
