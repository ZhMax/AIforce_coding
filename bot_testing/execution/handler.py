"""
Bot Import and Chat Script
===========================

This script demonstrates how to:
1. Create a FAQ bot from JSON
2. Import it to the MWS AI Agents Platform
3. Create a channel for the bot
4. Send messages and chat with the bot

Usage:
    python bot_import_and_chat.py --base-url <platform_url> --token <api_token>
"""

import argparse
import json
import time
from datetime import datetime
from typing import Any, Dict, Optional


import requests

class PlatformHandler:
    """Handles bot import and interaction with MWS AI Agents Platform"""

    def __init__(self, base_url: str, api_token: Optional[str] = None):
        """
        Initialize the bot importer

        Args:
            base_url: Base URL of the platform (e.g., https://platform.example.com)
            api_token: API token for authentication (optional)
        """
        self.base_url = base_url.rstrip("/")
        
        self.headers_get = {
            "X-Ai-Account": "default",
            "X-Ai-Workspace": "00000000-0000-0000-0000-000000000000"            
        }
        
        self.headers_post = {
            "Content-Type": "application/json",
            "X-Ai-Account": "default",
            "X-Ai-Workspace": "00000000-0000-0000-0000-000000000000",
        }

        if api_token:
            self.headers_get["Authorization"] = f"Bearer {api_token}"
            self.headers_post["Authorization"] = f"Bearer {api_token}"

    def get_list_of_bots(self) -> Optional[list]:
        """
        Get list of all bots from the platform.

        Returns:
            A list of bot dictionaries from the API response, or None if the request fails.
        """
        url = f"{self.base_url}/api/v3/nocode/bots/"

        response = requests.get(url, headers=self.headers_get)

        if response.status_code == 200:
            data = response.json()
            bots = data.get("data", [])
            print(f"✓ Got {len(bots)} bots")
            return bots
        else:
            print(f"✗ Error: {response.status_code}")
            print(f"   {response.text}")
            return None

    def bot_exists(self, bot_config: Dict[str, Any]) -> bool:
        """
        Check if a bot with the same name already exists on the platform.

        Args:
            bot_config: Bot configuration dictionary.

        Returns:
            True if a bot with the same name exists, False otherwise.
        """
        
        bot_name = bot_config['data']['attributes'].get('bot_name')

        print(f"\n Checking if bot '{bot_name}' exists on the platform")
        bots_list = self.get_list_of_bots()

        if bots_list is None:
            print("   Unable to verify - failed to retrieve bots list")
            return False

        for item in bots_list:
            if item["attributes"]["name"] == bot_name:
                print(f"   Found existing bot: {item['attributes']['id']}")
                return True

        print(f"   Bot '{bot_name}' not found")
        return False

    def import_bot(self, bot_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Import bot to the platform

        Args:
            bot_config: Bot configuration dictionary

        Returns:
            Response from the server with bot_id and bot_version_id
        """
        url = f"{self.base_url}/api/v3/nocode/bots/import"

        print(f"\n Importing bot to {url}...")

        response = requests.post(url, headers=self.headers_post, json=bot_config)

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"✗ Error importing bot: {response.status_code}")
            print(f"   Response: {response.text}")
            response.raise_for_status()
            return None

    def get_bot_details(self, bot_id: int) -> Dict[str, Any]:
        """
        Get bot details.

        Args:
            bot_id: Bot ID

        Returns:
            Bot details
        """
        url = (
            f"{self.base_url}/api/v3/nocode/bots/{bot_id}/"
        )

        print(f"\n Getting bot details...")
        response = requests.get(url, headers=self.headers_get)

        if response.status_code == 200:
            data = response.json()
            print(f"✓ Bot details retrieved")
            return data
        else:
            print(f"✗ Error getting bot details: {response.status_code}")
            print(f"   Response: {response.text}")
            response.raise_for_status()

    def get_bot_version_details(self, bot_id: int, current_version_id: int) -> Dict[str, Any]:
        """
        Get bot version details

        Args:
            bot_id: Bot ID
            current_version_id: Bot version ID

        Returns:
            Bot version details
        """
        url = (
            f"{self.base_url}/api/v3/nocode/bots/{bot_id}/bot_versions/{current_version_id}"
        )
        params = {
            "with_config": "true",
            "with_layout": "true",
            "with_named_rules": "true",
        }

        print(f"\n Getting bot details...")
        response = requests.get(url, headers=self.headers_get, params=params)

        if response.status_code == 200:
            data = response.json()
            print(f"✓ Bot details retrieved")
            return data
        else:
            print(f"✗ Error getting bot details: {response.status_code}")
            print(f"   Response: {response.text}")
            response.raise_for_status()

    def send_message(
        self,
        bot_id: int,
        current_version_id: int,
        message: str,
        session_id: Optional[str] = None,
        debug: bool = False
    ) -> Dict[str, Any]:
        """
        Send a message to the bot in test mode.

        Args:
            bot_id: Bot ID
            bot_version_id: Bot version ID
            message: Message text to send to the bot
            session_id: Session ID for the conversation (generated if not provided)
            debug: Enable debug mode for detailed response

        Returns:
            Bot response dictionary from the API
        """
        from uuid import uuid4

        url = (
            f"{self.base_url}/api/v3/nocode/bots/{bot_id}/bot_versions/{current_version_id}/engine/"
        )

        # Generate session_id and message_id if not provided
        if session_id is None:
            session_id = str(uuid4())
        message_id = str(uuid4())

        payload = {
            "data": {
                "type": "engine",
                "attributes": {
                    "sessionId": session_id,
                    "messageId": message_id,
                    "callbackUrl": None,
                    "uuid": {
                        "sub": session_id,
                        "userId": session_id,
                    },
                    "payload": {
                        "message": {
                            "originalText": message,
                        }
                    },
                    "userContextData": None,
                    "contextOverride": None,
                    "debug": debug,
                },
            }
        }

        print(f"\n💬 Sending message to bot {bot_id} (version {current_version_id})")
        print(f"   Message: {message}")
        print(f"   Session: {session_id}")

        response = requests.post(url, headers=self.headers_post, json=payload)

        if response.status_code == 200:
            data = response.json()
            print(f"✓ Message sent successfully")
            return data
        else:
            print(f"✗ Error sending message: {response.status_code}")
            print(f"   Response: {response.text}")
            response.raise_for_status()
            return None

    def delete_bot(self, bot_id: int) -> bool:
        """
        Delete a bot from the platform.

        Args:
            bot_id: Bot ID to delete

        Returns:
            True if the bot was deleted successfully, False otherwise.
        """
        url = f"{self.base_url}/api/v3/nocode/bots/{bot_id}"

        print(f"\n🗑️ Deleting bot {bot_id}...")
        response = requests.delete(url, headers=self.headers_get)

        if response.status_code == 200:
            print(f"✓ Bot {bot_id} deleted successfully")
            return True
        else:
            print(f"✗ Error deleting bot: {response.status_code}")
            print(f"   Response: {response.text}")
            return False