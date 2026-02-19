"""
Bot test client - wrapper around BotImporter for testing
"""

import re
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .handler import PlatformHandler
from bot_testing.config import ConfigLoader


@dataclass
class Button:
    """Represents a button in a bot response"""

    title: str
    action: Optional[Dict] = None


@dataclass
class BotResponse:
    """Represents a response from the bot"""

    text: str
    buttons: List[Button]
    # scenario_slug: str = ""
    # current_node_id: str = ""
    # session_variables: Dict[str, Any] = None
    # request_variables: Dict[str, Any] = None
    raw_response: Dict[str, Any] = None

    # def __post_init__(self):
    #     if self.session_variables is None:
    #         self.session_variables = {}
    #     if self.request_variables is None:
    #         self.request_variables = {}
    #     if self.raw_response is None:
    #         self.raw_response = {}

    @classmethod
    def parse(cls, raw_response: Dict[str, Any]) -> "BotResponse":
        """
        Parse raw API response into BotResponse

        Args:
            raw_response: Raw response from API

        Returns:
            BotResponse object
        """

        text = ""
        buttons = []
        try:
            items = raw_response["data"]["attributes"]["payload"].get("items", [])
            text_parts = []
            for item in items:
                bubble = item.get("bubble", {})
                if bubble.get("type", "") == "text":
                    value = bubble.get("value", "")
                    if value:
                        text_parts.append(value)
            text = "\n".join(text_parts)

            suggestions = raw_response["data"]["attributes"]["payload"].get("suggestions")
            if suggestions:
                button_list = suggestions.get("buttons", [])
                if button_list:
                    buttons = [
                        Button(
                            title=btn.get("title", ""),
                            action=btn.get("action", {}),
                        )
                        for btn in button_list
                    ]

        except (AttributeError, KeyError, TypeError):
            # If structure doesn't match, use raw_response as-is
            pass

        return cls(
            text=text,
            buttons=buttons,
            raw_response=raw_response,
        )


class BotTestClient:
    """Client for testing bots via API"""

    def __init__(self, base_url: str, api_token: Optional[str] = None):
        """
        Initialize bot test client

        Args:
            base_url: Base URL of the platform
            api_token: API token for authentication
        """
        self.handler = PlatformHandler(base_url, api_token)
        self.current_session: Optional[str] = None

        self.bot_name: Optional[str] = None
        self.bot_id: Optional[str] = None
        self.current_version_id: Optional[str] = None

    def import_bot_from_config(self, config_path: str) -> tuple[str, str]:
        """
        Deploy bot configuration to platform.

        Loads the bot configuration from a JSON file, checks if a bot with
        the same name already exists on the platform, imports the bot,
        and retrieves its current version ID.

        Args:
            config_path: Path to the bot configuration JSON file.

        Returns:
            Tuple of (bot_id, version_id).

        Raises:
            RuntimeError: If a bot with the same name already exists or
                          if the import fails.
        """
        # Load bot configuration from file
        bot_config = ConfigLoader.load(config_path)

        # Check if bot with same name already exists
        if self.handler.bot_exists(bot_config):
            raise RuntimeError(
                "Failed to import bot. A bot with the same name already exists on the platform"
            )

        # Import bot to platform
        result = self.handler.import_bot(bot_config)
        if result is None:
            raise RuntimeError("Failed to import bot")

        # Extract bot info from import response
        self.bot_id = result["data"]["attributes"]["bot_id"]
        self.bot_name = result["data"]["attributes"]["bot_name"]

        # Get full bot details to retrieve current_version_id
        details = self.handler.get_bot_details(self.bot_id)

        # Verify bot details match the imported bot
        assert details["data"]["attributes"]["id"] == self.bot_id, (
            f"Bot ID mismatch: expected {self.bot_id}, got {details['data']['attributes']['bot_id']}"
        )
        assert details["data"]["attributes"]["name"] == self.bot_name, (
            f"Bot name mismatch: expected {self.bot_name}, got {details['data']['attributes']['name']}"
        )

        self.current_version_id = details["data"]["attributes"]["current_version_id"]

        print(f"✓ Bot imported successfully!")
        print(f"   Bot name: {self.bot_name}")
        print(f"   Bot ID: {self.bot_id}")
        print(f"   Bot Current Version ID: {self.current_version_id}")

        return self.bot_id, self.current_version_id

    async def send_message(
        self, message: str, new_session: bool = False
    ) -> BotResponse:
        """
        Send a message to the bot

        Args:
            message: Message to send
            new_session: If True, create new session

        Returns:
            BotResponse from the bot
        """
        if new_session or not self.current_session:
            self.current_session = str(uuid.uuid4())

        try:
            response = self.handler.send_message(
                bot_id=int(self.bot_id),
                current_version_id=int(self.current_version_id),
                message=message,
                session_id=self.current_session,
            )
            return BotResponse.parse(response)
        except Exception as e:
            raise RuntimeError(f"Failed to send message: {e}")

    async def click_button(self, button_title: str) -> BotResponse:
        """
        Simulate clicking a button

        Args:
            button_title: Title of button to click

        Returns:
            BotResponse from the bot
        """
        return await self.send_message(button_title)

    async def navigate_to_scenario(self, scenario_slug: str) -> BotResponse:
        """
        Navigate to a scenario by sending a message that matches an entry edge

        Args:
            scenario_slug: Slug of scenario to navigate to

        Returns:
            BotResponse from the scenario
        """
        # Try to find an entry edge that matches this scenario
        # For now, just send a test message
        message = f"test_{scenario_slug}"
        return await self.send_message(message)

    async def set_session_variable(self, var_name: str, value: Any) -> None:
        """
        Set a session variable (for future use)

        Args:
            var_name: Variable name
            value: Variable value
        """
        # This would require API support for setting variables
        # For now, placeholder
        pass

    async def cleanup(self) -> None:
        """Clean up test resources"""
        # Placeholder for cleanup logic
        pass
