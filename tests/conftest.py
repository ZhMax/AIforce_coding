"""
Pytest configuration for bot testing framework

Single conftest.py that works for both structural and deterministic tests.
Fixtures check which CLI options are provided and skip if not available.
"""

import os
import sys
import pathlib

# Add project root to path for imports
project_root = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
from bot_testing.config.extractor import ElementExtractor
from bot_testing.config.loader import ConfigLoader
from bot_testing.execution.client import BotTestClient


# =============================================================================
# CLI Options
# =============================================================================

def pytest_addoption(parser):
    """Add custom CLI options to pytest"""
    # For structural tests
    parser.addoption(
        "--bot-config",
        type=str,
        help="Path to bot configuration JSON file",
    )
    # For deterministic tests
    parser.addoption(
        "--bot-id",
        type=str,
        help="Bot ID on platform (for deterministic tests)",
    )
    parser.addoption(
        "--current-version-id",
        type=str,
        help="Current version ID of deployed bot (for deterministic tests)",
    )


# =============================================================================
# Fixtures - Structural Tests
# =============================================================================

@pytest.fixture(scope="session")
def schema_path():
    """Get JSON schema path for config validation"""
    default_schema = project_root / "platform_api" / "bot_import_schema_v2_improved.json"

    if default_schema.exists():
        return str(default_schema)

    pytest.fail(f"Schema file not found: {default_schema}")


@pytest.fixture(scope="session")
def element_extractor():
    """Create element extractor for the bot configuration"""
    return ElementExtractor()


@pytest.fixture(scope="session")
def bot_config_path(request):
    """Get bot config path from CLI option (for structural tests)"""
    cli_path = request.config.getoption("--bot-config")
    if cli_path:
        return cli_path

    pytest.fail("Bot config path not specified. Use --bot-config option")


@pytest.fixture(scope="session")
def bot_config(bot_config_path, element_extractor):
    """Load bot configuration from file (for structural tests)"""
    loader = ConfigLoader()

    try:
        config = loader.load(bot_config_path)
        element_extractor.set_config_attr(config)
        return element_extractor.config_attrs
    except FileNotFoundError as e:
        pytest.skip(f"Bot config not found: {e}")


# =============================================================================
# Fixtures - Deterministic Tests
# =============================================================================

@pytest.fixture(scope="session")
def bot_id(request):
    """Get bot ID from CLI option (for deterministic tests)"""
    cli_id = request.config.getoption("--bot-id")
    if cli_id:
        return cli_id

    env_id = os.getenv("BOT_ID")
    if env_id:
        return env_id

    pytest.skip("Bot ID not specified. Use --bot-id option")


@pytest.fixture(scope="session")
def current_version_id(request):
    """Get current version ID from CLI option (for deterministic tests)"""
    cli_version = request.config.getoption("--current-version-id")
    if cli_version:
        return cli_version

    env_version = os.getenv("CURRENT_VERSION_ID")
    if env_version:
        return env_version

    pytest.skip("Current version ID not specified. Use --current-version-id option")


@pytest.fixture(scope="session")
def bot_client(bot_id, current_version_id):
    """
    Create bot test client connected to deployed bot (for deterministic tests)
    """
    api_url = os.getenv("BOT_API_URL")
    api_token = os.getenv("BOT_API_TOKEN")

    if not api_url:
        pytest.skip("BOT_API_URL not set")

    client = BotTestClient(api_url, api_token)
    client.bot_id = bot_id
    client.current_version_id = current_version_id

    yield client


# =============================================================================
# Config Loading for Behavioral Tests
# =============================================================================

# Cache for loaded bot configs (avoid fetching multiple times)
_BOT_CONFIG_CACHE = {}


def _load_bot_config(pytest_config):
    """
    Load bot config either from file (--bot-config) or from API (--bot-id + --current-version-id).

    Returns:
        Dict[str, Any] | None: Bot configuration dictionary or None if not available
    """
    cache_key = "bot_config"
    if cache_key in _BOT_CONFIG_CACHE:
        return _BOT_CONFIG_CACHE[cache_key]

    # Try loading from file first
    bot_config_path = pytest_config.getoption("--bot-config", default=None)
    if bot_config_path:
        try:
            loader = ConfigLoader()
            config = loader.load(bot_config_path)
            _BOT_CONFIG_CACHE[cache_key] = config
            return config
        except Exception as e:
            print(f"Warning: Failed to load config from file: {e}")

    # # Try fetching from API
    # bot_id = pytest_config.getoption("--bot-id", default=None) or os.getenv("BOT_ID")
    # version_id = pytest_config.getoption("--current-version-id", default=None) or os.getenv("CURRENT_VERSION_ID")
    # api_url = os.getenv("BOT_API_URL")

    # if bot_id and version_id and api_url:
    #     try:
    #         from bot_testing.execution.handler import PlatformHandler

    #         api_token = os.getenv("BOT_API_TOKEN")
    #         handler = PlatformHandler(api_url, api_token)

    #         response = handler.get_bot_version_details(int(bot_id), int(version_id))
    #         if response:
    #             config = response  # API returns config in same format
    #             _BOT_CONFIG_CACHE[cache_key] = config
    #             return config
    #     except Exception as e:
    #         print(f"Warning: Failed to fetch config from API: {e}")

    return None


@pytest.fixture(scope="session")
def bot_config_extractor(request):
    """
    Create element extractor with bot configuration (for behavioral tests).

    Returns None if config is not available (tests should skip).
    """
    config = _load_bot_config(request.config)
    if not config:
        return None

    extractor = ElementExtractor()
    extractor.set_config_attr(config)
    return extractor


# =============================================================================
# Helper Fixtures for Behavioral Tests
# =============================================================================

@pytest.fixture(scope="session")
def match_edges(bot_config_extractor):
    """Get all match-type entry edges from config"""
    if not bot_config_extractor:
        return []
    return bot_config_extractor.extract_entry_edges_by_type("match")


@pytest.fixture(scope="session")
def event_edges(bot_config_extractor):
    """Get all event-type entry edges from config"""
    if not bot_config_extractor:
        return []
    return bot_config_extractor.extract_entry_edges_by_type("event")


@pytest.fixture
def has_block_type(bot_config_extractor):
    """
    Factory fixture that returns a function to check if bot has blocks of given type.

    Usage in tests:
        def test_llm(has_block_type):
            if not has_block_type("llm"):
                pytest.skip("Bot has no LLM blocks")
    """
    def _check(block_type: str) -> bool:
        if not bot_config_extractor:
            return False
        blocks = bot_config_extractor.extract_blocks_by_type(block_type)
        return len(blocks) > 0
    return _check


# =============================================================================
# Dynamic Parametrization
# =============================================================================

def _make_test_id(pattern: str, index: int) -> str:
    """Create readable test ID from regex pattern."""
    import re
    
    # Extract meaningful words (including Russian characters)
    words = re.findall(r'[\wа-яА-ЯёЁ]+', pattern)
    
    if words:
        # Use first 2-3 words, max 50 chars
        meaningful = '_'.join(words[:3])[:50]
        return f"match_{index}_{meaningful}"
    else:
        return f"match_{index}_pattern"


def pytest_generate_tests(metafunc):
    """
    Dynamically parametrize tests based on bot configuration.

    This hook runs during test collection and parametrizes tests over:
    - match edges (for test_match_edge_activates, etc.)
    - event edges (for test_init_event, test_no_match, etc.)
    - block types (for block-specific tests)
    """
    # Load config if available
    config = _load_bot_config(metafunc.config)
    if not config:
        return  # No parametrization if config unavailable

    extractor = ElementExtractor()
    extractor.set_config_attr(config)

    # Parametrize over match edges
    if "match_edge" in metafunc.fixturenames:
        edges = extractor.extract_entry_edges_by_type("match")
        if edges:
            ids = [_make_test_id(e.pattern, i) for i, e in enumerate(edges)]
            metafunc.parametrize("match_edge", edges, ids=ids)

            # metafunc.parametrize("match_edge", edges, ids=[e.pattern for e in edges])
        else:
            # No match edges - skip these tests
            metafunc.parametrize("match_edge", [pytest.param(None, marks=pytest.mark.skip("No match edges"))])

    # Parametrize over scenarios with specific block types
    if "buttons_scenario" in metafunc.fixturenames:
        # Find scenarios containing buttons blocks
        scenarios_with_buttons = []
        for scenario in extractor.extract_scenarios():
            for node in scenario.nodes:
                if any(b.type == "buttons" for b in node.blocks):
                    scenarios_with_buttons.append(scenario)
                    break

        if scenarios_with_buttons:
            metafunc.parametrize("buttons_scenario", scenarios_with_buttons,
                               ids=[s.slug for s in scenarios_with_buttons])
        else:
            metafunc.parametrize("buttons_scenario",
                               [pytest.param(None, marks=pytest.mark.skip("No buttons blocks"))])


# =============================================================================
# Pytest Configuration
# =============================================================================

def pytest_configure(config):
    """Configure pytest and add custom markers"""
    config.addinivalue_line("markers", "slow: marks tests as slow (calls external APIs)")
    config.addinivalue_line("markers", "structural: marks tests as structural validation")
    config.addinivalue_line("markers", "behavioral: marks tests as behavioral testing")
    config.addinivalue_line("markers", "asyncio: marks tests as async")