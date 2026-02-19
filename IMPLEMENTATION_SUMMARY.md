# Bot Testing Framework - Phase 1 & 2 Implementation Summary

## Status: ✅ PHASE 1 COMPLETE | ✅ PHASE 2 IMPLEMENTED

Phase 1 (Structural validation) complete. Phase 2 (Behavioral testing) now implemented with consolidated, config-driven tests.

---

## What Was Implemented

### 1. Core Framework Modules

#### Config Loading (`bot_testing/config/loader.py`)
```python
from bot_testing.config import ConfigLoader

# Load any bot configuration
loader = ConfigLoader("path/to/bot-config.json")
config = loader.load()

# Returns standardized dict, handles nested structures:
# - Raw format: {"scenarios": [...]}
# - Exported format: {"data": {"attributes": {...}}}
```

**Features**:
- Handles both raw and exported bot formats
- Normalizes scenario slugs
- JSON validation

#### Element Extraction (`bot_testing/config/extractor.py`)
```python
from bot_testing.config import ElementExtractor

extractor = ElementExtractor(config)

# Extract different element types
blocks = extractor.extract_blocks()           # All blocks
answer_blocks = extractor.extract_blocks_by_type("answer")
llm_blocks = extractor.extract_blocks_by_type("llm")

edges = extractor.extract_entry_edges()       # All entry edges
match_edges = extractor.extract_entry_edges_by_type("match")

nodes = extractor.extract_nodes()             # All nodes
scenarios = extractor.extract_scenarios()     # All scenarios

# Find specific elements
node = extractor.find_node_by_id("node-123")
scenario = extractor.find_scenario_by_slug("greeting")
```

**Returns**:
- `BlockInfo` - Block with type, data, location, parent info
- `EntryEdgeInfo` - Edge with pattern, target, scenario info
- `NodeInfo` - Node with ID, name, blocks, next_node_id
- `ScenarioInfo` - Scenario with nodes, edges, metadata

#### Data Classes (`bot_testing/config/element_types.py`)
```python
@dataclass
class BlockInfo:
    path: str                      # "scenarios[0].nodes[1].blocks[0]"
    type: str                      # "llm", "answer", "buttons", etc.
    data: Dict[str, Any]          # Full block config
    scenario_slug: str
    node_id: str
    block_id: str

@dataclass
class EntryEdgeInfo:
    path: str
    type: str                      # "match", "event", "manual"
    pattern: str                   # Regex or event name
    target_node_id: str
    scenario_slug: str

@dataclass
class NodeInfo:
    path: str
    node_id: str
    name: str
    scenario_slug: str
    blocks: List[BlockInfo]
    next_node_id: Optional[str]

@dataclass
class ScenarioInfo:
    path: str
    scenario_id: Optional[str]
    name: str
    slug: str
    entry_edges: List[EntryEdgeInfo]
    nodes: List[NodeInfo]
```

### 2. Test Infrastructure

#### Pytest Fixtures (`tests/conftest.py`)
```python
@pytest.fixture(scope="session")
def bot_config(bot_config_path):
    """Load bot configuration from BOT_CONFIG_PATH env var"""
    loader = ConfigLoader(bot_config_path)
    return loader.load()

@pytest.fixture(scope="session")
def element_extractor(bot_config):
    """Create element extractor for this bot"""
    return ElementExtractor(bot_config)

@pytest.fixture(scope="session")
def bot_client():
    """Create bot test client (for Phase 2)"""
    return BotTestClient(
        os.getenv("BOT_API_URL", "http://localhost:8000"),
        os.getenv("BOT_API_TOKEN")
    )
```

**Key Feature**: Same tests work for all bots - configuration injected at runtime!

#### Structural Tests (`tests/test_structural.py`)
```python
# 24 tests organized in 9 test classes

class TestBotConfiguration:
    """3 tests for overall bot structure"""

class TestScenarioStructure:
    """3 tests for scenario definitions"""

class TestNodeStructure:
    """3 tests for node definitions"""

class TestBlockStructure:
    """2 tests for block types and fields"""

class TestEntryEdgeValidation:
    """3 tests for entry edge configuration"""

class TestNodeReferences:
    """3 tests for cross-node references (buttons, if, extend)"""

class TestRegexPatterns:
    """1 test for regex pattern validation"""

class TestVariableUsage:
    """4 tests for variable templates and LLM/HTTP block config"""

class TestScenarioConsistency:
    """2 tests for uniqueness and consistency"""
```

**All tests use fixtures to access bot configuration**

### 3. Execution Layer (Phase 2 Preview)

#### Bot Test Client (`bot_testing/execution/client.py`)
```python
from bot_testing.execution import BotTestClient, BotResponse

client = BotTestClient("http://platform-url", "api-token")

# Deploy bot
await client.deploy_bot(config)

# Send messages
response = await client.send_message("hello")

# Click buttons
response = await client.click_button("Option 1")

# Parse responses
print(response.text)
print(response.buttons)
print(response.current_node_id)
print(response.session_variables)
```

**Ready for Phase 2 behavioral tests**

### 4. Coverage Tracking (Phase 4 Preview)

#### Coverage Tracker (`bot_testing/coverage/tracker.py`)
```python
from bot_testing.coverage import CoverageTracker

tracker = CoverageTracker()

# Mark elements as tested
tracker.mark_block_tested("scenarios[0].nodes[0].blocks[0]", passed=True)
tracker.mark_edge_tested("scenarios[0].entry_edges[0]", passed=True)
tracker.mark_node_tested("scenarios[0].nodes[0]", passed=True)

# Get summary
summary = tracker.get_coverage_summary(total_elements=50)
# Returns: {
#   "total_elements": 50,
#   "tested_elements": 42,
#   "coverage_percent": 84.0,
#   "untested_elements": 8
# }
```

**Ready for Phase 4 reporting**

---

## How to Run Tests

### Recommended: Full Test Pipeline

**File**: `tests/pipeline.py`

The `pipeline.py` module provides the complete testing workflow:

```python
from tests.pipeline import run_full_pipeline

# Run complete test pipeline for bot-8553
config_path = "/path/to/bot-8553-v8581.json"
success = run_full_pipeline(
    config_path=config_path,
    skip_structural=False,     # Run structural tests
    skip_import=False,          # Import bot on platform
    skip_behavioral=False,      # Run behavioral tests
)
```

**What it does**:
1. ✓ Analyzes and validates bot configuration (BotAnalyzer)
2. ✓ Runs 24 structural tests
3. ✓ Imports bot on platform via API
4. ✓ Runs 33 behavioral tests
5. ✓ Cleans up (removes bot from platform)

**Usage**:
```bash
# Edit pipeline.py main() function with your config path
cd AIforce_coding/tests
python3 pipeline.py
```

Or call individual pipeline functions:
```python
from tests.pipeline import (
    load_and_analyze_bot,
    run_pytest_structural,
    import_bot_on_platform,
    run_pytest_behavioral,
    remove_bot_from_platform
)

# Step 1: Analyze config
success, analyzer = load_and_analyze_bot(config_path)

# Step 2: Run structural tests
run_pytest_structural(config_path)

# Step 3: Import on platform
bot_id, version_id = import_bot_on_platform(config_path)

# Step 4: Run behavioral tests
run_pytest_behavioral(bot_id, version_id, config_path)

# Step 5: Cleanup
remove_bot_from_platform(bot_id, version_id)
```

---

### Alternative: Direct Pytest (Manual Control)

For more control over individual test phases:

```bash
cd AIforce_coding

# Run structural tests only
pytest tests/test_structural.py --bot-config=/path/to/config.json -v

# Run behavioral tests only (requires deployed bot)
pytest tests/ -m behavioral \
  --bot-id=8553 \
  --current-version-id=8581 \
  --bot-config=/path/to/config.json -v

# Run specific test file
pytest tests/test_connectivity.py -v --bot-id=8553 --current-version-id=8581

# Run with coverage
pytest tests/test_structural.py --bot-config=/path/to/config.json \
  --cov=bot_testing --cov-report=html
```

---

## Test Coverage Details

### Bot-8553 Structural Tests (24 total)

| Test Category | Count | Validates |
|---------------|-------|-----------|
| Configuration | 3 | Bot fields, scenarios, no-match answer |
| Scenarios | 3 | Scenario structure, fields, uniqueness |
| Nodes | 3 | Node structure, fields, uniqueness |
| Blocks | 2 | Block type fields, valid types |
| Entry Edges | 3 | Edge fields, types, valid targets |
| References | 3 | Button targets, if targets, extend targets |
| Patterns | 1 | Regex validity |
| Variables | 4 | Answer values, LLM config, HTTP URLs, buttons |
| Consistency | 2 | Scenario ID uniqueness, slug uniqueness |

### Bot-8553 Elements

**Scenarios**: 6
- greeting
- quick_recommendation
- alternative
- recipe
- restart
- default_nomatch

**Blocks**: ~31
- Answer: 8
- Buttons: 8
- Extend: 7
- LLM: 3
- Single-If: 2
- Wait for User: 3

**Entry Edges**: 6
- Match: 5
- Event: 1

**Nodes**: ~15

---

## File Structure Created

```
AIforce_coding/
├── QUICK_START.md                  # Start here!
├── README.md                        # Full documentation
├── IMPLEMENTATION_SUMMARY.md        # This file
├── requirements.txt                 # pip install -r requirements.txt
├── pytest.ini                       # Pytest configuration
├── .env.example                     # Environment template
│
├── bot_testing/                     # Main package
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── loader.py               # ConfigLoader (60 lines)
│   │   ├── extractor.py            # ElementExtractor (250 lines)
│   │   └── element_types.py        # Data classes (120 lines)
│   ├── execution/
│   │   ├── __init__.py
│   │   └── client.py               # BotTestClient (140 lines)
│   └── coverage/
│       ├── __init__.py
│       └── tracker.py              # CoverageTracker (70 lines)
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                 # Pytest fixtures + parametrization (300 lines)
│   ├── pipeline.py                 # Primary test runner (350 lines) ⭐
│   ├── test_structural.py          # 24 structural tests (700+ lines)
│   ├── test_connectivity.py        # 10 universal behavioral tests
│   ├── test_entry_edges.py         # 8 config-driven entry edge tests
│   └── test_blocks.py              # 15 block-type-specific tests
│
└── examples/
    ├── bot-8553-v8581.json          # Sample bot configuration
    └── ...                          # (legacy test scripts - use pipeline.py instead)
```

**Total Implementation**:
- **10+ Python modules** (~1500 lines total)
- **24 structural tests** (test_structural.py)
- **3 runnable examples** (bash, python, api)
- **5 documentation files** (README, QUICK_START, USAGE, etc.)
- **Pytest fixtures** for automatic parametrization
- **Data classes** for type safety

---

## Key Design Principles

### 1. Generic Tests

Same test code works for **any bot**:
```python
# This test works for bot-97, bot-8553, or any bot
@pytest.mark.structural
def test_all_blocks_have_type(self, bot_config):
    """Generic: works for any bot"""
    for scenario in bot_config['scenarios']:
        for node in scenario['nodes']:
            for block in node['blocks']:
                assert 'type' in block  # Works for any bot!
```

The bot is injected via `BOT_CONFIG_PATH` environment variable.

### 2. Runtime Parametrization

Tests read config and extract elements dynamically:
```python
# conftest.py
@pytest.fixture
def bot_config(bot_config_path):
    return ConfigLoader(bot_config_path).load()

# test_structural.py - uses injected config
def test_example(self, bot_config):
    # bot_config = whatever is in BOT_CONFIG_PATH
    assert bot_config['bot_name']  # Works for any bot!
```

### 3. No Code Generation

No need to generate test files per bot. Same tests, different configs!

### 4. Reusable Components

- `ConfigLoader` - Use anywhere to load bot configs
- `ElementExtractor` - Use anywhere to parse bot structure
- `BotTestClient` - Will use for behavioral tests
- `CoverageTracker` - Will use for coverage reports

---

## How to Extend

### Adding a New Structural Test

1. Open `tests/test_structural.py`
2. Find or create appropriate test class
3. Add new test method:

```python
@pytest.mark.structural
def test_my_validation(self, bot_config, element_extractor):
    """Description of what you're testing"""
    # Your assertion logic
    assert condition
```

4. Run tests:
```bash
BOT_CONFIG_PATH=../mws_api/test_api/bot-8553-v8581.json pytest tests/test_structural.py -v
```

### Using ConfigLoader in Your Code

```python
from bot_testing.config import ConfigLoader, ElementExtractor

# Load config
loader = ConfigLoader("path/to/bot.json")
config = loader.load()

# Extract elements
extractor = ElementExtractor(config)
blocks = extractor.extract_blocks()
scenarios = extractor.extract_scenarios()

# Work with elements
for block in blocks:
    print(f"{block.type} block at {block.path}")
```

---

## Testing Workflow

### Quick Validation Loop

```bash
cd AIforce_coding

# 1. Make changes to bot JSON

# 2. Run structural tests (1 second)
BOT_CONFIG_PATH=../mws_api/test_api/bot-8553-v8581.json \
    pytest tests/test_structural.py -v

# 3. See which fields are missing or broken
# 4. Fix and repeat
```

---

## Phase 2: Behavioral Tests ✅ IMPLEMENTED

### What Was Added

#### 1. Utility Module (`bot_testing/utils.py`)
```python
from bot_testing.utils import regex_to_sample_message

# Generate sample messages from regex patterns
message = regex_to_sample_message("/start|начать|привет")  # "/start"
message = regex_to_sample_message("^help$")                  # "help"
message = regex_to_sample_message("test.*value")             # "test value"
```

#### 2. Enhanced conftest.py
- **Config Loading**: Load from `--bot-config` file OR fetch from API via `--bot-id` + `--current-version-id`
- **Dynamic Parametrization**: `pytest_generate_tests` hook parametrizes tests over match edges and block types
- **Helper Fixtures**: `bot_config_extractor`, `match_edges`, `event_edges`, `has_block_type()`

#### 3. Three Consolidated Behavioral Test Files

**test_connectivity.py** (10 universal tests)
- No config needed, works for any bot
- Basic connectivity, input edge cases, session management, resilience

**test_entry_edges.py** (8 config-driven tests)
- **Parametrized** over match edges in bot config
- Tests: match activation, case-insensitivity, init event, no_match fallback
- Button navigation tests (click, multi-step, branching)

**test_blocks.py** (15 block-type-specific test classes)
- Tests for each block type: answer, buttons, llm, http_request, extend, variables, script, agent, etc.
- **Auto-skips** when bot doesn't have specific block type
- Parametrized over scenarios containing each block type

#### 4. Improved BotResponse Parser
- Concatenates text from all items (not just first)
- Gracefully handles missing/None suggestions

### Files Modified/Created/Deleted

**Created**:
- `bot_testing/utils.py` - regex_to_sample_message utility
- `tests/test_connectivity.py` - universal connectivity tests
- `tests/test_entry_edges.py` - config-driven entry edge tests
- `tests/test_blocks.py` - config-driven block behavior tests

**Modified**:
- `tests/conftest.py` - added config loading, parametrization, helper fixtures
- `bot_testing/execution/client.py` - improved BotResponse.parse()

**Deleted**:
- `test_behavioral_deterministic.py` (consolidated)
- `test_commands.py` (consolidated)
- `test_filters.py` (consolidated)
- `test_scenarios.py` (consolidated)
- `test_state.py` (consolidated)

### Test Summary

**Before**: 5 overlapping test files (~120 tests) with generic hardcoded messages

**After**: 3 focused test files
- 10 universal connectivity tests
- 8 entry edge tests (parametrized over edges in config)
- 15 block behavior tests (auto-skip for missing blocks)

---

## Next Phases

### Phase 3: Advanced Behavioral Tests (Upcoming)
- Test LLM block execution with real models
- Test HTTP request blocks
- Test Script block execution
- Coverage tracking for executed paths
- **Est. effort**: 1 week

### Phase 4: Coverage & Reporting (Upcoming)
- HTML coverage reports
- CLI tool for easy test running
- CI/CD integration
- Coverage dashboard
- **Files to create**: `reporter.py`, `cli.py`
- **Est. effort**: 1 week

---

## Validation Checklist

- ✅ ConfigLoader loads both raw and exported bot formats
- ✅ ElementExtractor extracts all element types
- ✅ Data classes provide type safety
- ✅ Pytest fixtures inject configurations
- ✅ 24 structural tests cover bot structure
- ✅ Tests work with bot-97 and bot-8553
- ✅ 3 different ways to run tests (bash, python, pytest)
- ✅ Examples included and executable
- ✅ Documentation complete and comprehensive
- ✅ Framework is reusable and extensible

---

## Summary

**Phase 1 Complete** ✅

You now have:
- A working testing framework
- 24 structural validation tests
- Tests for bot-97 (simple) and bot-8553 (complex)
- 3 different ways to run tests
- Complete documentation
- Ready for Phase 2 (behavioral testing)

**Next step**: Run the full test pipeline:

```bash
# Recommended: Full pipeline (structural + behavioral)
cd AIforce_coding/tests
# Edit pipeline.py main() with your config path, then:
python3 pipeline.py

# Alternative: Direct pytest (manual control)
cd AIforce_coding
pytest tests/test_structural.py --bot-config=/path/to/config.json -v
pytest tests/ -m behavioral --bot-id=8553 --current-version-id=8581 --bot-config=/path/to/config.json -v
```

This validates bot configuration and tests deployed behavior! 🚀
