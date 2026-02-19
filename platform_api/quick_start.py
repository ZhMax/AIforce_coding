#!/usr/bin/env python3
"""
Quick Start Example - Bot Import and Chat
==========================================

This is a simplified example showing how to quickly import a bot and chat with it.

Usage:
    python quick_start.py
"""

import json
import os
import time
from uuid import uuid4

import requests

try:
    from tgbot_unittests.AIforce_coding.bot_testing.config.validator import BotConfigValidator
except ImportError:
    print("⚠️  Warning: bot_config_validator module not found")
    print("   Install jsonschema: pip install jsonschema")
    BotConfigValidator = None

# Configuration
BASE_URL = "https://web-backend-demo.apps.k8s.mars.dev.mts.ai"
API_TOKEN = None

# BASE_JSON_CONFIG = (
#     "/Users/m.zhelnin/Documents/tgbot_unittests/mws_api/test_api/faq_bot_example.json"
# )
BASE_JSON_CONFIG = (
    "/Users/m.zhelnin/Documents/tgbot_unittests/mws_api/test_api/bot-8553-v8581.json"
)
# BASE_JSON_CONFIG = "/Users/m.zhelnin/Documents/tgbot_unittests/mws_api/test_api/faq_bot_example_claude.json"
# BASE_JSON_CONFIG = (
#     "/Users/m.zhelnin/Documents/tgbot_unittests/mws_api/test_api/test_example_faq.json"
# )


def get_list_of_bots(base_url, token=None):
    """Get list of bots from the platform"""
    url = f"{base_url}/api/v3/nocode/bots/"

    headers = {
        "X-Ai-Account": "default",
        "X-Ai-Workspace": "00000000-0000-0000-0000-000000000000",
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        data = data.get("data", [])
        print(f"✅ Got {len(data)} bots")
        return data
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"   {response.text}")
        return None


def validate_bot_config(bot_config, schema_path):
    """
    Validate bot_config against JSON Schema using BotConfigValidator

    Args:
        bot_config (dict): Bot configuration to validate
        schema_path (str): Path to JSON Schema file

    Returns:
        tuple: (is_valid, error_messages)
    """

    if BotConfigValidator is None:
        print("⚠️  Skipping validation - BotConfigValidator not available")
        return True, None

    try:
        validator = BotConfigValidator(schema_path)
        is_valid = validator.print_validation_report(bot_config, show_valid=True)

        if is_valid:
            return True, None
        else:
            _, errors = validator.validate(bot_config, verbose=True)
            return False, errors

    except FileNotFoundError as e:
        print(f"⚠️  Warning: {e}")
        print("   Skipping validation")
        return True, None
    except Exception as e:
        error_msg = f"Unexpected validation error: {e}"
        print(f"❌ {error_msg}")
        return False, [error_msg]


def load_bot_config(filepath):
    """Load JSON file with config"""

    config = None

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")

    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in '{filepath}': {e}")

    except Exception as e:
        print(f"Unexpected error loading '{filepath}': {e}")

    return config


def save_platform_response(response):
    bot_name = response["data"]["attributes"]["name"]
    bot_id = response["data"]["attributes"]["id"]
    file_path = f"{bot_name}_{bot_id}.json"

    # Save only if file does not already exist
    if os.path.exists(file_path):
        # Optionally log/print something here instead of overwriting
        print(f"File '{file_path}' already exists. Skipping save.")
        return

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(response, f, indent=4, ensure_ascii=False)


def export_bot(base_url, bot_id, token=None):
    """Import json config for a bot from platform"""
    url = f"{base_url}/api/v3/nocode/bots/{bot_id}"

    headers = {
        "X-Ai-Account": "default",
        "X-Ai-Workspace": "00000000-0000-0000-0000-000000000000",
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"   {response.text}")
        return None


def import_bot(base_url, bot_config, token=None):
    """Import bot to platform"""
    url = f"{base_url}/api/v3/nocode/bots/import"

    headers = {
        "Content-Type": "application/json",
        "X-Ai-Account": "default",
        "X-Ai-Workspace": "00000000-0000-0000-0000-000000000000",
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"

    print(f"📤 Importing bot to {url}...")
    response = requests.post(url, headers=headers, json=bot_config)

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Bot imported!")
        print(f"   Bot ID: {data.get('bot_id')}")
        print(f"   Version ID: {data.get('id')}")
        return data
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"   {response.text}")
        raise Exception(f"Failed to import bot: {response.status_code}")


def send_message(base_url, bot_id, bot_version_id, message, session_id, token=None):
    """Send message to bot"""
    url = (
        f"{base_url}/api/v3/nocode/bots/{bot_id}/bot_versions/{bot_version_id}/engine/"
    )

    headers = {
        "Content-Type": "application/json",
        "X-Ai-Account": "default",
        "X-Ai-Workspace": "00000000-0000-0000-0000-000000000000",
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"

    # messageId must be unique per message – use UUID
    message_id = str(uuid4())

    payload = {
        "data": {
            "type": "engine",
            "attributes": {
                "sessionId": session_id,
                "messageId": message_id,
                "callbackUrl": None,
                "uuid": {
                    # for a simple quickstart we can reuse session_id as both
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
                "debug": True,
            },
        }
    }

    print(f"\n💬 You: {message}")
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        data = response.json()
        breakpoint()
        bot_response = data["data"]["attributes"]["payload"]["items"][0]["bubble"][
            "value"
        ]

        print(f"🤖 Bot: {bot_response}")
        return data
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"   {response.text}")
        return None


def import_bot_from_config():

    # Step 1: Load bot configuration
    print("\n📝 Step 1: Loading bot configuration...")
    bot_config = load_bot_config(BASE_JSON_CONFIG)

    if not bot_config:
        print("❌ Failed to load bot configuration")
        return

    bot_name = bot_config["data"]["attributes"]["bot_name"]

    # Step 1: Validate bot configuration
    print("\n🔍 Step 1: Validating bot configuration...")
    schema_path = os.path.join(
        os.path.dirname(BASE_JSON_CONFIG), "bot_import_schema_v2_improved.json"
    )

    # schema_path = os.path.join(
    #     os.path.dirname(BASE_JSON_CONFIG), "bot_import_schema_v2_improved.json"
    # )

    is_valid, errors = validate_bot_config(bot_config, schema_path)
    if not is_valid:
        print(f"\n❌ Bot configuration is invalid!")
        if errors:
            print(f"   Found {len(errors)} error(s):")
            for idx, error in enumerate(errors[:5], 1):  # Show first 5 errors
                print(f"   {idx}. {error}")
        print("\n💡 Please fix the configuration and try again.")
        return

    print(f"✅ Bot config loaded: {bot_config['data']['attributes']['bot_name']}")

    # Step 2: Import bot
    print("\n📤 Step 2: Importing bot to platform...")
    bots_list = get_list_of_bots(BASE_URL)
    bot_exists = False

    for item in bots_list:
        if item["attributes"]["name"] == bot_name:
            bot_exists = True
            bot_params = export_bot(BASE_URL, item["attributes"]["id"])

    if not bot_exists:
        result = import_bot(BASE_URL, bot_config, API_TOKEN)
        bot_params = export_bot(BASE_URL, result["data"]["attributes"]["bot_id"])
    else:
        print("Bot already exists on the platform")

    return bot_params


def main():
    """Main function"""
    print("=" * 60)
    print("🚀 Quick Start: Bot Import and Chat")
    print("=" * 60)

    bot_params = import_bot_from_config()

    if bot_params is None:
        return

    save_platform_response(bot_params)

    # if not :
    #     print("❌ Failed to get bot_id or bot_version_id")
    #     return

    # Step 3: Test with messages
    print("\n💬 Step 3: Testing bot with sample messages...")
    print("=" * 60)

    session_id = f"quickstart_{int(time.time())}"

    # Test messages
    test_messages = ["привет!", "часы работы", "доставка"]
    breakpoint()
    for msg in test_messages:
        bot_id = bot_params["data"]["id"]
        bot_version_id = bot_params["data"]["attributes"]["current_version_id"]
        send_message(BASE_URL, bot_id, bot_version_id, msg, session_id, API_TOKEN)
        time.sleep(1)


if __name__ == "__main__":
    main()
