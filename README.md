# Bot Testing Framework (Phase 1 - MVP)

A generic, reusable testing framework for validating chatbot configurations and behaviors on a no-code platform.

## Overview

This framework enables **automated testing of bots** through:

- **Structural Validation**: Validate bot configuration files before deployment (Tier 1)
- **Behavioral Testing**: Test bot responses via platform API (Tier 2-3)
- **Coverage Tracking**: Track which bot elements are tested
- **Generic Tests**: One set of tests works with any bot configuration

## Quick Start

### Installation

```bash
cd AIforce_coding
pip install -r requirements.txt
```

### Run Full Test Pipeline

```bash
cd tests
# Edit pipeline.py with your config path
python3 pipeline.py
```

This runs:
1. Config analysis and validation
2. Structural tests (24 tests)
3. Bot import on platform
4. Behavioral tests (33 tests)
5. Cleanup

### Run Tests Individually

```bash
# Structural tests only
cd AIforce_coding
pytest tests/test_structural.py --bot-config=/path/to/config.json -v

# Behavioral tests only (requires deployed bot)
pytest tests/ -m behavioral \
  --bot-id=8553 \
  --current-version-id=8581 \
  --bot-config=/path/to/config.json -v
```

## Framework Status

### Phase 1: Structural Validation ✅ COMPLETE

Tests bot configuration without deployment (< 1 second):
- Bot configuration structure
- Scenario structure
- Node and block definitions
- Entry edge patterns
- Node references
- Regex validation
- Variable usage

**24 tests per bot**

### Phase 2: Behavioral Testing ✅ COMPLETE

Tests deployed bot behavior via API:
- Universal connectivity tests (10 tests - work for any bot)
- Config-driven entry edge tests (8 tests - parametrized over edges in bot)
- Block-type-specific tests (15 tests - auto-skip for missing blocks)

**33 behavioral tests total**
- Config loads from `--bot-config` file OR platform API
- Dynamic parametrization via `pytest_generate_tests`
- Auto-skip for bots lacking specific block types

### Phase 3-4: Advanced Testing & Reporting (Upcoming)

Advanced behavioral tests with external services, coverage tracking, and reporting.

## Project Structure

```
AIforce_coding/
├── bot_testing/
│   ├── utils.py                    # Utility functions
│   ├── config/                     # Configuration loading
│   ├── execution/                  # API client and handler
│   └── coverage/                   # Coverage tracking
├── tests/
│   ├── conftest.py                 # Pytest fixtures + parametrization
│   ├── test_structural.py          # 24 structural tests
│   ├── test_connectivity.py        # 10 universal connectivity tests
│   ├── test_entry_edges.py         # 8 parametrized entry edge tests
│   └── test_blocks.py              # 15 block-type-specific tests
├── requirements.txt
├── pytest.ini
└── .env.example
```

## Test Execution

### Recommended: Full Pipeline

Use `tests/pipeline.py` to run the complete testing workflow:

```bash
cd AIforce_coding/tests
# Edit pipeline.py with your config path
python3 pipeline.py
```

Or call it programmatically:
```python
from tests.pipeline import run_full_pipeline

success = run_full_pipeline(
    config_path="/path/to/config.json",
    skip_structural=False,   # Run structural tests
    skip_import=False,       # Import bot on platform
    skip_behavioral=False,   # Run behavioral tests
)
```

### Manual Test Control

**Structural Tests** (Phase 1 - no deployment required):
```bash
cd AIforce_coding
pytest tests/test_structural.py --bot-config=/path/to/config.json -v

# Test all bots
for bot in ../mws_api/test_api/bot-*.json; do
    pytest tests/test_structural.py --bot-config=$bot -v
done
```

**Behavioral Tests** (Phase 2 - requires deployed bot):
```bash
# With local config file
pytest tests/ -m behavioral \
  --bot-id=8553 \
  --current-version-id=8581 \
  --bot-config=/path/to/config.json -v

# Run specific behavioral test file
pytest tests/test_connectivity.py -v --bot-id=8553 --current-version-id=8581
pytest tests/test_entry_edges.py -v --bot-id=8553 --current-version-id=8581 --bot-config=/path/to/config.json
pytest tests/test_blocks.py -v --bot-id=8553 --current-version-id=8581 --bot-config=/path/to/config.json
```

## Core Classes

**ConfigLoader**: Load and parse bot configurations
**ElementExtractor**: Extract blocks, edges, nodes, scenarios
**BotTestClient**: API client for behavioral tests (Phase 2)
**CoverageTracker**: Track test coverage (Phase 4)

## Supported Elements

**Block Types**: answer, buttons, llm, http_request, script, single_if, extend, variables, and others

**Edge Types**: match (regex), event (init/no_match), manual

## Environment Variables

**Structural Tests (Phase 1)**:
- `BOT_CONFIG_PATH` - Bot configuration file path (required for structural tests)

**Behavioral Tests (Phase 2)**:
- `BOT_API_URL` - Platform API URL (required for behavioral tests)
- `BOT_API_TOKEN` - API authentication token (optional)
- `BOT_ID` - Bot ID (fallback if `--bot-id` not provided)
- `CURRENT_VERSION_ID` - Version ID (fallback if `--current-version-id` not provided)

**CLI Options (Behavioral Tests)**:
- `--bot-id` - Bot ID on platform
- `--current-version-id` - Current version ID of deployed bot
- `--bot-config` - Path to bot configuration JSON (loads locally or from API)

## Next Steps

1. **Run Full Test Pipeline**:
   ```bash
   cd AIforce_coding/tests
   # Edit pipeline.py with your config path
   python3 pipeline.py
   ```

2. **Run Individual Test Phases**:
   ```bash
   # Structural tests
   pytest tests/test_structural.py --bot-config=/path/to/config.json -v

   # Behavioral tests
   pytest tests/ -m behavioral --bot-id=8553 --current-version-id=8581 --bot-config=/path/to/config.json -v
   ```

3. **Phase 3** (Upcoming): Advanced behavioral tests with external services (LLM, HTTP, Script blocks)

4. **Phase 4** (Upcoming): Coverage tracking and HTML reports