"""
Pipeline helpers for bot testing workflow

This module provides functions to orchestrate the bot testing pipeline:
1. Analyze and validate JSON config (BotAnalyzer)
2. Run pytest structural tests
3. Import bot on platform
4. Run pytest behavioral tests
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import Optional, Tuple

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# Load environment variables
load_dotenv(project_root / ".env")

from bot_testing.config import BotAnalyzer
from bot_testing.execution import BotTestClient

# Default schema path
DEFAULT_JSON_SCHEMA = str(
    project_root / "platform_api" / "bot_import_schema_v2_improved.json"
)


def print_header(text: str, char: str = "=") -> None:
    """Print a formatted header"""
    print(f"\n{char * 50}")
    print(f"  {text}")
    print(f"{char * 50}\n")


def print_section(text: str, char: str = "-") -> None:
    """Print a formatted section header"""
    print(f"\n{char * 50}")
    print(f"  {text}")
    print(f"{char * 50}")


def load_and_analyze_bot(
    config_path: str,
    schema_path: Optional[str] = None,
) -> Tuple[bool, Optional[BotAnalyzer]]:
    """
    Step 1: Load and analyze bot configuration

    Validates the JSON config against the schema and extracts element information.

    Args:
        config_path: Path to bot configuration JSON file
        schema_path: Optional path to JSON schema (uses default if not provided)

    Returns:
        Tuple of (success: bool, analyzer: Optional[BotAnalyzer])
        analyzer is returned if validation passed
    """
    schema_path = schema_path or DEFAULT_JSON_SCHEMA
    print_section("Step 1: Analyzing Bot Configuration")
    print(f"Config: {config_path}")
    print(f"Schema: {schema_path}")

    if not Path(config_path).exists():
        print(f"\n✗ Config file not found: {config_path}")
        return False, None

    if not Path(schema_path).exists():
        print(f"\n✗ Schema file not found: {schema_path}")
        return False, None

    try:
        analyzer = BotAnalyzer(config_path, schema_path)
        analyzer.load_and_validate()

        # Check if validation passed
        if not analyzer._is_loaded:
            print("\n✗ Validation failed!")
            return False, None

        print("\n✓ Configuration analyzed successfully")
        return True, analyzer

    except Exception as e:
        print(f"\n✗ Error analyzing configuration: {e}")
        return False, None


def run_pytest_structural(
    config_path: str,
    project_root_path: Optional[Path] = None,
) -> bool:
    """
    Step 2: Run pytest structural tests

    Runs unit tests that validate the JSON configuration structure
    without requiring a deployed bot.

    Args:
        config_path: Path to bot configuration JSON file
        project_root_path: Optional path to project root (auto-detected if not provided)

    Returns:
        True if all tests passed, False otherwise
    """
    project_root_path = project_root_path or project_root
    tests_dir = project_root_path / "tests"
    print_section("Step 2: Running Structural Tests")

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(tests_dir / "test_structural.py"),
        "-v",
        "--tb=short",
        "-o", "testpaths=.",
        "-o", f"pythonpath={project_root}",
        "--bot-config",
        config_path,
    ]

    print(f"Running: {' '.join(cmd)}\n")

    # Run from tests/ directory so conftest.py is loaded
    result = subprocess.run(
        cmd,
        cwd=str(tests_dir),
        env=os.environ,
    )

    if result.returncode == 0:
        print("\n✓ All structural tests passed!")
        return True
    else:
        print("\n✗ Some structural tests failed")
        return False


def import_bot_on_platform(
    config_path: str,
    api_url: Optional[str] = None,
    api_token: Optional[str] = None,
) -> Optional[BotTestClient]:
    """
    Step 3: Import bot on platform

    Imports the bot configuration to the platform using BotTestClient.

    Args:
        config_path: Path to bot configuration JSON file
        api_url: API URL (uses BOT_API_URL env var if not provided)
        api_token: Optional API token (uses BOT_API_TOKEN env var if not provided)

    Returns:
        BotTestClient instance if import succeeded, None otherwise
    """
    print_section("Step 3: Importing Bot on Platform")

    api_url = api_url or os.getenv("BOT_API_URL")
    api_token = api_token or os.getenv("BOT_API_TOKEN")

    if not api_url:
        print("\n✗ BOT_API_URL not set")
        return None
    print(f"API URL: {api_url}")
    
    try:
        bot_client = BotTestClient(api_url, api_token)
        bot_id, current_version_id = bot_client.import_bot_from_config(config_path)
        # response = bot_client.send_message("Hi", True)
        return bot_id, current_version_id

    except Exception as e:
        print(f"\n✗ Error importing bot: {e}")
        return None


def remove_bot_from_platform(
    bot_id: str,
    current_version_id: str,
    api_url: Optional[str] = None,
    api_token: Optional[str] = None,
) -> bool:
    """
    Step 5: Remove bot from platform

    Deletes the imported bot from the platform.

    Args:
        bot_id: Bot ID on the platform
        current_version_id: Current version ID of the deployed bot
        api_url: API URL (uses BOT_API_URL env var if not provided)
        api_token: Optional API token (uses BOT_API_TOKEN env var if not provided)

    Returns:
        True if bot was deleted successfully, False otherwise
    """
    print_section("Cleanup: Removing Bot from Platform")

    if bot_id is None:
        print("\n✗ No bot to remove (bot_id is None)")
        return False

    api_url = api_url or os.getenv("BOT_API_URL")
    api_token = api_token or os.getenv("BOT_API_TOKEN")

    try:
        bot_client = BotTestClient(api_url, api_token)
        bot_client.bot_id = bot_id
        bot_client.current_version_id = current_version_id
        return bot_client.handler.delete_bot(int(bot_id))
    except Exception as e:
        print(f"\n✗ Error removing bot: {e}")
        return False

def run_pytest_behavioral(
    bot_id: str,
    current_version_id: str,
    config_path: Optional[str] = None,
    project_root_path: Optional[Path] = None,
) -> bool:
    """
    Step 4: Run pytest behavioral tests

    Runs tests that verify bot behavior by sending messages via API
    and checking responses. Requires a deployed bot.

    Args:
        bot_id: Bot ID on the platform
        current_version_id: Current version ID of the deployed bot
        config_path: Optional path to bot config (for config-driven tests)
        project_root_path: Optional path to project root (auto-detected if not provided)

    Returns:
        True if all tests passed, False otherwise
    """
    project_root_path = project_root_path or project_root
    tests_dir = project_root_path / "tests"
    print_section("Step 4: Running Behavioral Tests")

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(tests_dir),
        "-m", "behavioral",  # Run all tests marked as behavioral
        "-v",
        "--tb=short",
        "-o", "testpaths=.",
        "-o", f"pythonpath={project_root}",
        "--bot-id",
        str(bot_id),
        "--current-version-id",
        str(current_version_id),
    ]

    # Add config path if provided
    if config_path:
        cmd.extend(["--bot-config", config_path])

    print(f"Running: {' '.join(cmd)}\n")

    # Run from tests/ directory so conftest.py is loaded
    result = subprocess.run(
        cmd,
        cwd=str(tests_dir),
        env=os.environ,
    )

    if result.returncode == 0:
        print("\n✓ All behavioral tests passed!")
        return True
    else:
        print("\n✗ Some behavioral tests failed")
        return False


def run_full_pipeline(
    config_path: str,
    schema_path: Optional[str] = None,
    skip_structural: bool = False,
    skip_import: bool = False,
    skip_behavioral: bool = False,
    project_root_path: Optional[Path] = None,
) -> bool:
    """
    Run the full bot testing pipeline

    Orchestrates all four steps:
    1. Analyze and validate JSON config
    2. Run pytest structural tests
    3. Import bot on platform
    4. Run pytest behavioral tests

    Args:
        config_path: Path to bot configuration JSON file
        schema_path: Optional path to JSON schema
        skip_structural: Skip step 2 (structural tests)
        skip_import: Skip step 3 (import on platform)
        skip_behavioral: Skip step 4 (behavioral tests)
        project_root_path: Optional path to project root

    Returns:
        True if all executed steps passed, False otherwise
    """
    project_root_path = project_root_path or project_root
    print_header("Bot Testing Pipeline")

    # Step 1: Analyze config
    success, analyzer = load_and_analyze_bot(config_path, schema_path)
    if not success:
        print("\n✗ Pipeline failed at Step 1: Config Analysis")
        return False

    # Step 2: Run structural tests
    if not skip_structural:
        if not run_pytest_structural(config_path, project_root_path):
            print("\n✗ Pipeline failed at Step 2: Structural Tests")
            return False

    # Step 3: Import on platform
    bot_id = None
    current_version_id = None
    if not skip_import:
        result = import_bot_on_platform(config_path)
        if result is None:
            print("\n✗ Pipeline failed at Step 3: Platform Import")
            return False
        bot_id, current_version_id = result

    # Step 4: Run behavioral tests
    try:
        if not skip_behavioral:
            if not run_pytest_behavioral(bot_id, current_version_id, config_path, project_root_path):
                print("\n✗ Pipeline failed at Step 4: Behavioral Tests")
                if not skip_import and bot_id is not None:
                    print("⚠️ Tests failed - cleaning up...")
                    remove_bot_from_platform(bot_id, current_version_id)
                return False
    except Exception:
        if not skip_import and bot_id is not None:
            print("⚠️ Tests failed - cleaning up...")
            remove_bot_from_platform(bot_id, current_version_id)
        return False

    # All steps passed
    print_header("✓ Pipeline Completed Successfully!", "=")
    return True


def main():
    parser = argparse.ArgumentParser(description="Bot Testing Pipeline")
    parser.add_argument(
        "--config_path",
        type=str,
        required=True,
        help="Path to the bot configuration JSON file"
    )
    args = parser.parse_args()

    run_full_pipeline(
        config_path=args.config_path,
    )


if __name__ == "__main__":
    main()