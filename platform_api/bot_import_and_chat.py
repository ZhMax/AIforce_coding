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


class BotImporter:
    """Handles bot import and interaction with MWS AI Agents Platform"""

    def __init__(self, base_url: str, api_token: Optional[str] = None):
        """
        Initialize the bot importer

        Args:
            base_url: Base URL of the platform (e.g., https://platform.example.com)
            api_token: API token for authentication (optional)
        """
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Content-Type": "application/json",
            "X-Ai-Account": "default",
            "X-Ai-Workspace": "00000000-0000-0000-0000-000000000000",
        }

        if api_token:
            self.headers["Authorization"] = f"Bearer {api_token}"

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
        print(f"Bot name: {bot_config['bot_name']}")

        response = requests.post(url, headers=self.headers, json=bot_config)

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Bot imported successfully!")
            print(f"   Bot ID: {data.get('bot_id')}")
            print(f"   Bot Version ID: {data.get('id')}")
            return data
        else:
            print(f"❌ Error importing bot: {response.status_code}")
            print(f"   Response: {response.text}")
            response.raise_for_status()

    def get_bot_details(self, bot_id: int, bot_version_id: int) -> Dict[str, Any]:
        """
        Get bot version details

        Args:
            bot_id: Bot ID
            bot_version_id: Bot version ID

        Returns:
            Bot version details
        """
        url = (
            f"{self.base_url}/api/v3/nocode/bots/{bot_id}/bot_versions/{bot_version_id}"
        )
        params = {
            "with_config": "true",
            "with_layout": "true",
            "with_named_rules": "true",
        }

        print(f"\n📋 Getting bot details...")
        response = requests.get(url, headers=self.headers, params=params)

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Bot details retrieved")
            return data
        else:
            print(f"❌ Error getting bot details: {response.status_code}")
            print(f"   Response: {response.text}")
            response.raise_for_status()

    def publish_bot_version(self, bot_id: int, bot_version_id: int) -> bool:
        """
        Publish bot version

        Args:
            bot_id: Bot ID
            bot_version_id: Bot version ID

        Returns:
            True if successful
        """
        url = f"{self.base_url}/api/v3/nocode/bots/{bot_id}/bot_versions/{bot_version_id}/publish"

        print(f"\n📢 Publishing bot version...")
        response = requests.post(url, headers=self.headers)

        if response.status_code in [200, 201, 204]:
            print(f"✅ Bot version published successfully!")
            return True
        else:
            print(f"⚠️  Warning: Could not publish bot version: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    def create_channel(
        self,
        bot_id: int,
        bot_version_id: int,
        channel_name: str = "Test HTTP Channel",
        channel_type: str = "HTTP",
    ) -> Dict[str, Any]:
        """
        Create a channel for the bot

        Args:
            bot_id: Bot ID
            bot_version_id: Bot version ID
            channel_name: Name of the channel
            channel_type: Type of channel (HTTP, TELEGRAM, WEBIM)

        Returns:
            Channel details including channel_id
        """
        url = f"{self.base_url}/api/v2/nocode/channels/"

        channel_data = {
            "data": {
                "type": "channels",
                "attributes": {
                    "name": channel_name,
                    "type": channel_type,
                    "dialog_ttl_in_seconds": 300,
                    "author": "text2agent",
                },
            }
        }

        print(f"\n🔌 Creating channel '{channel_name}'...")
        response = requests.post(url, headers=self.headers, json=channel_data)

        if response.status_code in [200, 201]:
            data = response.json()
            channel_id = data["data"]["id"]
            print(f"✅ Channel created successfully!")
            print(f"   Channel ID: {channel_id}")

            # Now update channel to attach the bot
            self.update_channel(channel_id, bot_id, bot_version_id, channel_type)

            return data
        else:
            print(f"❌ Error creating channel: {response.status_code}")
            print(f"   Response: {response.text}")
            response.raise_for_status()

    def update_channel(
        self,
        channel_id: str,
        bot_id: int,
        bot_version_id: int,
        channel_type: str = "HTTP",
    ) -> Dict[str, Any]:
        """
        Update channel to attach bot and activate it

        Args:
            channel_id: Channel ID
            bot_id: Bot ID
            bot_version_id: Bot version ID
            channel_type: Type of channel

        Returns:
            Updated channel details
        """
        url = f"{self.base_url}/api/v2/nocode/channels/{channel_id}"

        config = {}
        if channel_type == "HTTP":
            config = {"response_method": "SYNC"}

        update_data = {
            "data": {
                "id": str(channel_id),
                "type": "channels",
                "attributes": {
                    "bot_id": bot_id,
                    "bot_version_id": bot_version_id,
                    "author": "text2agent",
                    "config": config,
                    "is_active": True,
                },
            }
        }

        print(f"\n🔄 Updating channel to attach bot...")
        response = requests.patch(url, headers=self.headers, json=update_data)

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Channel updated and activated!")
            serving_url = data["data"]["attributes"].get("serving_url", "N/A")
            print(f"   Serving URL: {serving_url}")
            return data
        else:
            print(f"❌ Error updating channel: {response.status_code}")
            print(f"   Response: {response.text}")
            response.raise_for_status()

    def send_message(
        self,
        bot_id: int,
        bot_version_id: int,
        message: str,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send a test message to the bot

        Args:
            bot_id: Bot ID
            bot_version_id: Bot version ID
            message: Message text to send
            session_id: Optional session ID for conversation continuity

        Returns:
            Bot response
        """
        url = f"{self.base_url}/api/v3/nocode/bots/{bot_id}/bot_versions/{bot_version_id}/engine/"

        if not session_id:
            session_id = f"test_session_{int(time.time())}"

        message_data = {
            "session_id": session_id,
            "message": message,
            "channel_type": "HTTP",
        }

        print(f"\n💬 You: {message}")
        response = requests.post(url, headers=self.headers, json=message_data)

        if response.status_code == 200:
            data = response.json()
            bot_response = data.get("response", {}).get("text", "No response")
            print(f"🤖 Bot: {bot_response}")
            return data
        else:
            print(f"❌ Error sending message: {response.status_code}")
            print(f"   Response: {response.text}")
            response.raise_for_status()

    def interactive_chat(self, bot_id: int, bot_version_id: int):
        """
        Start an interactive chat session with the bot

        Args:
            bot_id: Bot ID
            bot_version_id: Bot version ID
        """
        session_id = f"interactive_session_{int(time.time())}"

        print("\n" + "=" * 60)
        print("🚀 Starting Interactive Chat Session")
        print("=" * 60)
        print("Type your message and press Enter.")
        print("Type 'exit', 'quit', or 'q' to end the session.")
        print("=" * 60 + "\n")

        # Send init message to start conversation
        try:
            self.send_message(bot_id, bot_version_id, "/start", session_id)
        except Exception as e:
            print(f"⚠️  Could not send init message: {e}")

        while True:
            try:
                user_input = input("\n💬 You: ").strip()

                if user_input.lower() in ["exit", "quit", "q"]:
                    print("\n👋 Ending chat session. Goodbye!")
                    break

                if not user_input:
                    continue

                self.send_message(bot_id, bot_version_id, user_input, session_id)

            except KeyboardInterrupt:
                print("\n\n👋 Chat interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")


def main():
    """Main function to run the bot import and chat workflow"""

    parser = argparse.ArgumentParser(
        description="Import FAQ bot to MWS AI Agents Platform and chat with it"
    )
    parser.add_argument(
        "--base-url",
        required=True,
        help="Base URL of the platform (e.g., https://platform.example.com)",
    )
    parser.add_argument("--token", help="API token for authentication (optional)")
    parser.add_argument(
        "--save-json",
        action="store_true",
        help="Save bot configuration to JSON file instead of importing",
    )
    parser.add_argument(
        "--no-chat", action="store_true", help="Skip interactive chat after import"
    )

    args = parser.parse_args()

    # Initialize importer
    importer = BotImporter(args.base_url, args.token)

    # Create bot configuration
    bot_config = importer.create_faq_bot_json()

    # Save to file if requested
    if args.save_json:
        filename = f"faq_bot_{int(time.time())}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(bot_config, f, ensure_ascii=False, indent=2)
        print(f"✅ Bot configuration saved to {filename}")
        return

    try:
        # Import bot
        import_result = importer.import_bot(bot_config)
        bot_id = import_result.get("bot_id")
        bot_version_id = import_result.get("id")

        if not bot_id or not bot_version_id:
            print("❌ Failed to get bot_id or bot_version_id from import response")
            return

        # Get bot details
        importer.get_bot_details(bot_id, bot_version_id)

        # Try to publish the bot version
        importer.publish_bot_version(bot_id, bot_version_id)

        # Create and configure channel
        importer.create_channel(bot_id, bot_version_id)

        # Test with sample questions
        print("\n" + "=" * 60)
        print("📝 Testing Bot with Sample Questions")
        print("=" * 60)

        test_messages = [
            "Привет!",
            "Какие часы работы?",
            "Как вы доставляете?",
            "Какие способы оплаты?",
        ]

        session_id = f"test_session_{int(time.time())}"
        for msg in test_messages:
            time.sleep(1)  # Small delay between messages
            importer.send_message(bot_id, bot_version_id, msg, session_id)

        # Start interactive chat unless --no-chat flag is set
        if not args.no_chat:
            importer.interactive_chat(bot_id, bot_version_id)

        print("\n✅ All done!")

    except requests.exceptions.RequestException as e:
        print(f"\n❌ API Error: {e}")
    except KeyboardInterrupt:
        print("\n\n👋 Process interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
